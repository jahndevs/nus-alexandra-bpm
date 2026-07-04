import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from .cnn import make_backbone

# the model learns to predict target_BP given the calibration anchor
class AnchorBP1DCNN(nn.Module):
    def __init__(self, feat_dim=128, bp_emb=32):
        super().__init__()
        # one trunk reused for both branches (weight sharing)
        self.body = make_backbone()
        self.bp_mlp = nn.Sequential(
            nn.Linear(2, bp_emb), nn.ReLU(),
            nn.Linear(bp_emb, bp_emb), nn.ReLU(),
        )
        self.head = nn.Sequential(
            nn.Linear(feat_dim * 3 + bp_emb, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 2),
        )

    def forward(self, target_x, cal_x, cal_bp_n):
        target_f = self.body(target_x)
        cal_f = self.body(cal_x)
        diff_f = (target_f - cal_f).abs()
        bp_f = self.bp_mlp(cal_bp_n)
        z = torch.cat([target_f, cal_f, diff_f, bp_f], dim=1)
        return self.head(z)


# enumerate same-subject (target, anchor) pairs once at construction
class _PairedDataset(Dataset):
    def __init__(self, X, y, subjects, anchors_per_target=1, random_state=42):
        rng = np.random.default_rng(random_state)
        pairs = []
        for subj in np.unique(subjects):
            idx = np.where(subjects == subj)[0]
            if len(idx) < 2:
                continue
            for ti in idx:
                others = idx[idx != ti]
                for _ in range(anchors_per_target):
                    ai = int(rng.choice(others))
                    pairs.append((int(ti), ai))
        self.pairs = pairs
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, i):
        ti, ai = self.pairs[i]
        return self.X[ti], self.X[ai], self.y[ai], self.y[ti]


def _collate(batch):
    ts = torch.tensor(np.stack([b[0] for b in batch]), dtype=torch.float32).unsqueeze(1)
    aa = torch.tensor(np.stack([b[1] for b in batch]), dtype=torch.float32).unsqueeze(1)
    ab = torch.tensor(np.stack([b[2] for b in batch]), dtype=torch.float32)
    tb = torch.tensor(np.stack([b[3] for b in batch]), dtype=torch.float32)
    return ts, aa, ab, tb


# train the anchor CNN.
def train(
    X,
    y,
    subjects,
    n_epochs=30,
    batch_size=128,
    lr=1e-3,
    weight_decay=1e-4,
    val_split=0.1,
    anchors_per_target=1,
    random_state=42,
    device=None,
    verbose=True,
):
    if device is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"

    rng = np.random.default_rng(random_state)
    unique_subj = np.unique(subjects)
    rng.shuffle(unique_subj)
    n_val_subj = max(1, int(len(unique_subj) * val_split))
    val_subj = set(unique_subj[:n_val_subj].tolist())
    val_mask = np.array([s in val_subj for s in subjects])
    tr_mask = ~val_mask

    y_mean = y[tr_mask].mean(axis=0)
    y_std = y[tr_mask].std(axis=0) + 1e-6
    y_norm = (y - y_mean) / y_std

    train_ds = _PairedDataset(X[tr_mask], y_norm[tr_mask], subjects[tr_mask],
                              anchors_per_target=anchors_per_target, random_state=random_state)
    val_ds = _PairedDataset(X[val_mask], y_norm[val_mask], subjects[val_mask],
                            anchors_per_target=anchors_per_target, random_state=random_state + 1)

    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                          collate_fn=_collate, drop_last=False)
    val_dl = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                        collate_fn=_collate, drop_last=False)

    torch.manual_seed(random_state)
    net = AnchorBP1DCNN().to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=n_epochs)
    loss_fn = nn.SmoothL1Loss()

    best_val = float("inf")
    best_state = None

    for ep in range(n_epochs):
        net.train()
        run = 0.0; n_seen = 0
        for ts, aa, ab, tb in train_dl:
            ts, aa, ab, tb = ts.to(device), aa.to(device), ab.to(device), tb.to(device)
            opt.zero_grad()
            loss = loss_fn(net(ts, aa, ab), tb)
            loss.backward()
            opt.step()
            run += loss.item() * ts.size(0); n_seen += ts.size(0)
        sched.step()
        train_loss = run / max(1, n_seen)

        net.eval()
        run_v = 0.0; n_v = 0
        with torch.no_grad():
            for ts, aa, ab, tb in val_dl:
                ts, aa, ab, tb = ts.to(device), aa.to(device), ab.to(device), tb.to(device)
                run_v += loss_fn(net(ts, aa, ab), tb).item() * ts.size(0); n_v += ts.size(0)
        val_loss = run_v / max(1, n_v)

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().clone().cpu() for k, v in net.state_dict().items()}

        if verbose and ((ep + 1) % 5 == 0 or ep == 0):
            print(f"  epoch {ep+1:3d}/{n_epochs}  train={train_loss:.4f}  val={val_loss:.4f}  best={best_val:.4f}")

    net.load_state_dict(best_state)
    return _AnchorWrapper(net, y_mean, y_std, device)


class _AnchorWrapper:
    def __init__(self, net, y_mean, y_std, device):
        self.net = net
        self.y_mean = np.asarray(y_mean, dtype=np.float32)
        self.y_std = np.asarray(y_std, dtype=np.float32)
        self.device = device

    def save(self, path):
        torch.save({
            "state_dict": self.net.state_dict(),
            "y_mean": self.y_mean,
            "y_std": self.y_std,
        }, path)

    @classmethod
    def load(cls, path, device=None):
        if device is None:
            device = "mps" if torch.backends.mps.is_available() else "cpu"
        ckpt = torch.load(path, map_location=device, weights_only=False)
        net = AnchorBP1DCNN().to(device)
        net.load_state_dict(ckpt["state_dict"])
        net.eval()
        return cls(net, ckpt["y_mean"], ckpt["y_std"], device)

    # single-window inference for live use
    def predict_one(self, target_signal, anchor_signal, anchor_bp):
        target_signal = np.asarray(target_signal, dtype=np.float32)
        anchor_signal = np.asarray(anchor_signal, dtype=np.float32)
        anchor_bp = np.asarray(anchor_bp, dtype=np.float32)

        y_mean_t = torch.tensor(self.y_mean, device=self.device)
        y_std_t = torch.tensor(self.y_std, device=self.device)

        target_x = torch.tensor(target_signal, device=self.device).view(1, 1, -1)
        anchor_x = torch.tensor(anchor_signal, device=self.device).view(1, 1, -1)
        anchor_n = (torch.tensor(anchor_bp, device=self.device) - y_mean_t) / y_std_t
        anchor_n = anchor_n.unsqueeze(0)

        self.net.eval()
        with torch.no_grad():
            out_n = self.net(target_x, anchor_x, anchor_n)
        out = out_n * y_std_t + y_mean_t
        sbp, dbp = out.cpu().numpy().ravel().tolist()
        return float(sbp), float(dbp)

    # for each subject, hold out k cal-windows.
    def predict_with_anchor(self, X, y, subjects, k=1, random_state=42):
        rng = np.random.default_rng(random_state)
        preds = np.zeros_like(y, dtype=float)
        eval_mask = np.zeros(len(y), dtype=bool)
        n_used = 0

        y_mean_t = torch.tensor(self.y_mean, dtype=torch.float32, device=self.device)
        y_std_t = torch.tensor(self.y_std, dtype=torch.float32, device=self.device)

        self.net.eval()
        with torch.no_grad():
            for subj in np.unique(subjects):
                idx = np.where(subjects == subj)[0]
                if len(idx) < k + 1:
                    continue
                cal_pos = rng.choice(len(idx), size=k, replace=False)
                cal_idx = idx[cal_pos]
                cal_set = set(cal_idx.tolist())
                eval_idx = np.array([i for i in idx if i not in cal_set])

                target_x = torch.tensor(X[eval_idx], dtype=torch.float32,
                                        device=self.device).unsqueeze(1)

                acc = torch.zeros(len(eval_idx), 2, device=self.device)
                for ci in cal_idx:
                    anc_x = torch.tensor(X[ci], dtype=torch.float32,
                                         device=self.device).unsqueeze(0).unsqueeze(0)
                    anc_x = anc_x.expand(len(eval_idx), -1, -1)
                    cal_bp = (torch.tensor(y[ci], dtype=torch.float32,
                                           device=self.device) - y_mean_t) / y_std_t
                    cal_bp = cal_bp.unsqueeze(0).expand(len(eval_idx), -1)
                    acc = acc + self.net(target_x, anc_x, cal_bp)
                out_n = acc / k
                out = out_n * y_std_t + y_mean_t
                preds[eval_idx] = out.cpu().numpy()
                eval_mask[eval_idx] = True
                n_used += 1

        return preds, eval_mask, n_used
