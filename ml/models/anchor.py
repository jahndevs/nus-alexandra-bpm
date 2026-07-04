import numpy as np

def make_anchor_input(X_target, X_anchor, y_anchor):
    X_target = np.atleast_2d(X_target)
    X_anchor = np.atleast_2d(X_anchor)
    y_anchor = np.atleast_2d(y_anchor)
    if X_anchor.shape[0] == 1 and X_target.shape[0] > 1:
        X_anchor = np.broadcast_to(X_anchor, X_target.shape)
        y_anchor = np.broadcast_to(y_anchor, (X_target.shape[0], y_anchor.shape[1]))
    return np.concatenate([X_target, X_target - X_anchor, y_anchor], axis=1)


# build (X_pair, y_pair) for training the anchor model.
def build_train_pairs(X, y, subjects, random_state=42, anchors_per_target=1):
    rng = np.random.default_rng(random_state)
    X_in, y_out = [], []
    for subj in np.unique(subjects):
        idx = np.where(subjects == subj)[0]
        if len(idx) < 2:
            continue
        for ti in idx:
            others = idx[idx != ti]
            for _ in range(anchors_per_target):
                ai = int(rng.choice(others))
                X_in.append(make_anchor_input(X[ti], X[ai], y[ai]).ravel())
                y_out.append(y[ti])
    return np.array(X_in), np.array(y_out)


# evaluate an anchor-trained model with k cal-windows per subject.
def predict_with_anchor(model, X, y, subjects, k=1, random_state=42):
    rng = np.random.default_rng(random_state)
    preds = np.zeros_like(y, dtype=float)
    eval_mask = np.zeros(len(y), dtype=bool)
    n_used = 0

    for subj in np.unique(subjects):
        idx = np.where(subjects == subj)[0]
        if len(idx) < k + 1:
            continue
        cal_pos = rng.choice(len(idx), size=k, replace=False)
        cal_idx = idx[cal_pos]
        cal_set = set(cal_idx.tolist())
        eval_idx = np.array([i for i in idx if i not in cal_set])

        X_anc = X[cal_idx].mean(axis=0, keepdims=True)
        y_anc = y[cal_idx].mean(axis=0, keepdims=True)

        X_in = make_anchor_input(X[eval_idx], X_anc, y_anc)
        preds[eval_idx] = model.predict(X_in)
        eval_mask[eval_idx] = True
        n_used += 1

    return preds, eval_mask, n_used
