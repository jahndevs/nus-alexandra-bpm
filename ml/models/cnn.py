import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# five strided conv blocks down to a 128-d global feature vector.
def make_backbone():
    return nn.Sequential(
        nn.Conv1d(1, 32, 7, stride=2, padding=3),
        nn.BatchNorm1d(32), nn.ReLU(),
        nn.Conv1d(32, 32, 5, stride=2, padding=2),
        nn.BatchNorm1d(32), nn.ReLU(),
        nn.Conv1d(32, 64, 5, stride=2, padding=2),
        nn.BatchNorm1d(64), nn.ReLU(),
        nn.Conv1d(64, 64, 3, stride=2, padding=1),
        nn.BatchNorm1d(64), nn.ReLU(),
        nn.Conv1d(64, 128, 3, stride=2, padding=1),
        nn.BatchNorm1d(128), nn.ReLU(),
        nn.AdaptiveAvgPool1d(1),
        nn.Flatten(),
    )


# 1D CNN regressor: 10s preprocessed PPG window -> [SBP, DBP].
class BP1DCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.body = make_backbone()
        self.head = nn.Sequential(
            nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(64, 2),
        )

    def forward(self, x):
        return self.head(self.body(x))


# wrap the trained CNN in an sklearn-like .predict interface so the rest of
# the pipeline works unchanged
class _CNNWrapper:
    def __init__(self, net, y_mean, y_std, device):
        self.net = net
        self.y_mean = y_mean.numpy()
        self.y_std = y_std.numpy()
        self.device = device

    def predict(self, X):
        self.net.eval()
        x = torch.tensor(np.asarray(X), dtype=torch.float32).unsqueeze(1).to(self.device)
        with torch.no_grad():
            out = self.net(x).cpu().numpy()
        return out * self.y_std + self.y_mean


# train the CNN.
def train(
    X,
    y,
    n_epochs=30,
    batch_size=128,
    lr=1e-3,
    weight_decay=1e-4,
    val_split=0.1,
    random_state=42,
    device=None,
    verbose=True,
):
    if device is None:
        device = "mps" if torch.backends.mps.is_available() else "cpu"

    rng = np.random.default_rng(random_state)
    idx = rng.permutation(len(X))
    n_val = max(1, int(len(X) * val_split))
    val_idx, tr_idx = idx[:n_val], idx[n_val:]

    Xt_tr = torch.tensor(X[tr_idx], dtype=torch.float32).unsqueeze(1)
    yt_tr = torch.tensor(y[tr_idx], dtype=torch.float32)
    Xt_val = torch.tensor(X[val_idx], dtype=torch.float32).unsqueeze(1)
    yt_val = torch.tensor(y[val_idx], dtype=torch.float32)

    y_mean = yt_tr.mean(dim=0)
    y_std = yt_tr.std(dim=0).clamp(min=1e-6)
    yt_tr_n = (yt_tr - y_mean) / y_std
    yt_val_n = (yt_val - y_mean) / y_std

    torch.manual_seed(random_state)
    net = BP1DCNN().to(device)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=n_epochs)
    loss_fn = nn.SmoothL1Loss()

    train_dl = DataLoader(
        TensorDataset(Xt_tr, yt_tr_n),
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
    )

    best_val = float("inf")
    best_state = None
    Xt_val_d = Xt_val.to(device)
    yt_val_d = yt_val_n.to(device)

    for ep in range(n_epochs):
        net.train()
        running = 0.0
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = loss_fn(net(xb), yb)
            loss.backward()
            opt.step()
            running += loss.item() * xb.size(0)
        sched.step()
        train_loss = running / len(Xt_tr)

        net.eval()
        with torch.no_grad():
            val_loss = loss_fn(net(Xt_val_d), yt_val_d).item()

        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().clone().cpu() for k, v in net.state_dict().items()}

        if verbose and ((ep + 1) % 5 == 0 or ep == 0):
            print(f"  epoch {ep+1:3d}/{n_epochs}  train={train_loss:.4f}  val={val_loss:.4f}  best={best_val:.4f}")

    net.load_state_dict(best_state)
    return _CNNWrapper(net, y_mean, y_std, device)
