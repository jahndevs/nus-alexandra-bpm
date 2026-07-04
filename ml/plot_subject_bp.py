import argparse
import numpy as np
import matplotlib.pyplot as plt

from loaders.pulsedb import load_data
from models.eval import calibrate_per_subject
from ml_pipeline import (
    TRAIN_PATH, TEST_PATH, build_matrices, _train_model,
)


def _pick_subject(subjects, prefer=None):
    uniq, counts = np.unique(subjects, return_counts=True)
    if prefer is not None:
        for s in uniq:
            if str(s) == str(prefer):
                return s
        raise SystemExit(f"subject {prefer!r} not in test set")
    return uniq[np.argmax(counts)]


def main(n_train, n_test, model_type, n_estimators, random_state,
         calibrate, subject, out):
    print(f"loading train: {TRAIN_PATH}")
    ppg_tr, fs, labels_tr = load_data(TRAIN_PATH, n=n_train, random_state=random_state)
    X_tr, y_tr, _ = build_matrices(ppg_tr, fs, labels_tr)

    print(f"training {model_type} (n_estimators={n_estimators})")
    model = _train_model(model_type, X_tr, y_tr, n_estimators, random_state)

    print(f"loading test:  {TEST_PATH}")
    ppg_te, fs, labels_te = load_data(TEST_PATH, n=n_test, random_state=random_state)
    X_te, y_te, subj_te = build_matrices(ppg_te, fs, labels_te)
    preds = model.predict(X_te)

    if calibrate > 0:
        cal_preds, eval_mask, _ = calibrate_per_subject(
            preds, y_te, subj_te, k=calibrate, random_state=random_state,
        )
        preds = cal_preds
        # restrict to subjects that survived calibration
        X_te, y_te, subj_te, preds = (
            X_te[eval_mask], y_te[eval_mask], subj_te[eval_mask], preds[eval_mask],
        )

    subj = _pick_subject(subj_te, prefer=subject)
    mask = subj_te == subj
    y_subj = y_te[mask]
    p_subj = preds[mask]
    n = len(y_subj)
    print(f"plotting subject={subj}  windows={n}")

    t = np.arange(n) * 10.0

    sbp_mae = float(np.mean(np.abs(p_subj[:, 0] - y_subj[:, 0])))
    dbp_mae = float(np.mean(np.abs(p_subj[:, 1] - y_subj[:, 1])))

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    axes[0].plot(t, y_subj[:, 0], "o-", color="#1f77b4", label="actual (cuff)", linewidth=2)
    axes[0].plot(t, p_subj[:, 0], "s--", color="#d62728", label="estimated (PPG)", linewidth=2)
    axes[0].set_ylabel("SBP (mmHg)")
    axes[0].set_title(f"Subject {subj} — SBP  (MAE = {sbp_mae:.1f} mmHg, n={n} windows)")
    axes[0].grid(alpha=0.3)
    axes[0].legend(loc="best")

    axes[1].plot(t, y_subj[:, 1], "o-", color="#1f77b4", label="actual (cuff)", linewidth=2)
    axes[1].plot(t, p_subj[:, 1], "s--", color="#d62728", label="estimated (PPG)", linewidth=2)
    axes[1].set_ylabel("DBP (mmHg)")
    axes[1].set_xlabel("time (s)")
    axes[1].set_title(f"Subject {subj} — DBP  (MAE = {dbp_mae:.1f} mmHg)")
    axes[1].grid(alpha=0.3)
    axes[1].legend(loc="best")

    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")
    plt.show()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=["rf", "gb"], default="rf")
    p.add_argument("--n-train", type=int, default=15000)
    p.add_argument("--n-test", type=int, default=3000)
    p.add_argument("--n-estimators", type=int, default=300)
    p.add_argument("--random-state", type=int, default=42)
    p.add_argument("--calibrate", type=int, default=1,
                   help="per-subject mean-offset calibration windows (0=off)")
    p.add_argument("--subject", default=None,
                   help="specific subject id to plot; default = subject with most test windows")
    p.add_argument("--out", default="subject_bp.png")
    args = p.parse_args()
    main(
        n_train=args.n_train,
        n_test=args.n_test,
        model_type=args.model,
        n_estimators=args.n_estimators,
        random_state=args.random_state,
        calibrate=args.calibrate,
        subject=args.subject,
        out=args.out,
    )
