import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score


# evaluate any fitted regressor that maps X -> [SBP, DBP] and return per-target
# metrics
def evaluate(model, X, y):
    return metrics_pair(y, model.predict(X))


# compute metrics from arbitrary (y_true, y_pred) pairs
def metrics_pair(y_true, y_pred):
    return {
        "sbp": _metrics(y_true[:, 0], y_pred[:, 0]),
        "dbp": _metrics(y_true[:, 1], y_pred[:, 1]),
    }


def _metrics(y_true, y_pred):
    err = y_pred - y_true
    r, _ = pearsonr(y_true, y_pred)
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(root_mean_squared_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
        "pearson_r": float(r),
        "me": float(np.mean(err)),
        "sd": float(np.std(err, ddof=1)),
        "n": int(len(y_true)),
    }

def calibrate_per_subject(preds, y, subjects, k=1, random_state=42):
    rng = np.random.default_rng(random_state)
    calibrated = preds.copy()
    eval_mask = np.zeros(len(preds), dtype=bool)
    n_used = 0

    for subj in np.unique(subjects):
        idx = np.where(subjects == subj)[0]
        # need at least k+1 windows: k for calibration
        if len(idx) < k + 1:
            continue
        cal_pos = rng.choice(len(idx), size=k, replace=False)
        cal_idx = idx[cal_pos]
        eval_idx = np.array([i for i in idx if i not in set(cal_idx.tolist())])

        offset = np.mean(preds[cal_idx] - y[cal_idx], axis=0)
        calibrated[eval_idx] = preds[eval_idx] - offset
        eval_mask[eval_idx] = True
        n_used += 1

    return calibrated, eval_mask, n_used
