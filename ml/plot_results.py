import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

from loaders.pulsedb import load_data
from models.eval import calibrate_per_subject
from ml_pipeline import (
    TRAIN_PATH, TEST_PATH, build_matrices, _train_model,
)

# AAMI/ISO 81060-2 acceptance thresholds for cuffless BP
AAMI_ME_LIMIT = 5.0
AAMI_SD_LIMIT = 8.0


def _run_pipeline(n_train, n_test, model_type, n_estimators, random_state, calibrate):
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
        cal_preds, eval_mask, n_used = calibrate_per_subject(
            preds, y_te, subj_te, k=calibrate, random_state=random_state,
        )
        print(f"calibration: k={calibrate}, subjects_used={n_used}, eval_n={int(eval_mask.sum())}")
        y_te = y_te[eval_mask]
        subj_te = subj_te[eval_mask]
        preds = cal_preds[eval_mask]

    return y_te, preds, subj_te


def _scatter_panel(ax, y_true, y_pred, label):
    mae = float(np.mean(np.abs(y_pred - y_true)))
    rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))
    r, _ = pearsonr(y_true, y_pred)

    lo = float(min(y_true.min(), y_pred.min())) - 5
    hi = float(max(y_true.max(), y_pred.max())) + 5

    ax.scatter(y_true, y_pred, s=10, alpha=0.35, color="#1f77b4", edgecolors="none")
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="identity")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel(f"actual {label} (mmHg)")
    ax.set_ylabel(f"estimated {label} (mmHg)")
    ax.set_title(f"{label}: r = {r:.2f}, MAE = {mae:.1f}, RMSE = {rmse:.1f}  (n = {len(y_true)})")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")


def _bland_altman_panel(ax, y_true, y_pred, label):
    diff = y_pred - y_true
    mean = (y_pred + y_true) / 2.0
    me = float(np.mean(diff))
    sd = float(np.std(diff, ddof=1))
    loa_hi = me + 1.96 * sd
    loa_lo = me - 1.96 * sd

    aami_pass = abs(me) <= AAMI_ME_LIMIT and sd <= AAMI_SD_LIMIT
    verdict = "PASS" if aami_pass else "FAIL"
    verdict_color = "#2ca02c" if aami_pass else "#d62728"

    ax.scatter(mean, diff, s=10, alpha=0.35, color="#1f77b4", edgecolors="none")
    ax.axhline(me, color="#d62728", linewidth=1.5, label=f"bias = {me:+.2f}")
    ax.axhline(loa_hi, color="#d62728", linestyle="--", linewidth=1,
               label=f"+1.96 SD = {loa_hi:+.2f}")
    ax.axhline(loa_lo, color="#d62728", linestyle="--", linewidth=1,
               label=f"-1.96 SD = {loa_lo:+.2f}")

    # AAMI bias band: |ME| ≤ 5 mmHg
    ax.axhspan(-AAMI_ME_LIMIT, AAMI_ME_LIMIT, color="#2ca02c", alpha=0.08,
               label=f"AAMI bias band (±{AAMI_ME_LIMIT:.0f})")

    ax.axhline(0, color="k", linewidth=0.6)
    ax.set_xlabel(f"mean of estimated and actual {label} (mmHg)")
    ax.set_ylabel(f"estimated − actual {label} (mmHg)")
    ax.set_title(
        f"{label} Bland-Altman: ME = {me:+.2f}, SD = {sd:.2f}  "
        f"[AAMI ≤{AAMI_ME_LIMIT:.0f}/{AAMI_SD_LIMIT:.0f}: {verdict}]",
        color=verdict_color,
    )
    ax.grid(alpha=0.3)
    ax.legend(loc="best", fontsize=8)


def plot_scatter(y_te, preds, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    _scatter_panel(axes[0], y_te[:, 0], preds[:, 0], "SBP")
    _scatter_panel(axes[1], y_te[:, 1], preds[:, 1], "DBP")
    fig.suptitle("Estimated vs Actual Blood Pressure", fontsize=14)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")


def plot_bland_altman(y_te, preds, out):
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    _bland_altman_panel(axes[0], y_te[:, 0], preds[:, 0], "SBP")
    _bland_altman_panel(axes[1], y_te[:, 1], preds[:, 1], "DBP")
    fig.suptitle("Agreement with Cuff Reference (Bland–Altman)", fontsize=14)
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"wrote {out}")


def main(n_train, n_test, model_type, n_estimators, random_state, calibrate,
         out_scatter, out_ba):
    y_te, preds, _ = _run_pipeline(
        n_train, n_test, model_type, n_estimators, random_state, calibrate,
    )
    plot_scatter(y_te, preds, out_scatter)
    plot_bland_altman(y_te, preds, out_ba)
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
    p.add_argument("--out-scatter", default="bp_scatter.png")
    p.add_argument("--out-ba", default="bp_bland_altman.png")
    args = p.parse_args()
    main(
        n_train=args.n_train,
        n_test=args.n_test,
        model_type=args.model,
        n_estimators=args.n_estimators,
        random_state=args.random_state,
        calibrate=args.calibrate,
        out_scatter=args.out_scatter,
        out_ba=args.out_ba,
    )
