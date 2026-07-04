import argparse
import numpy as np

from features.extract import extract
from loaders.pulsedb import load_data
from models import gbr, rfg
from models.anchor import build_train_pairs, predict_with_anchor
from models.eval import calibrate_per_subject, evaluate, metrics_pair
from preprocessing.process import preprocess
from preprocessing.segment import split_beats

TRAIN_PATH = "data/pulsedb/VitalDB_Train_Subset.mat"
TEST_PATH = "data/pulsedb/VitalDB_CalFree_Test_Subset.mat"

# minimum valid beats per 10s window to keep the window
MIN_BEATS_PER_WINDOW = 3
# robust-z threshold for dropping outlier beats within a window
OUTLIER_MAD_K = 3.0


# extract features for each beat, drop unstable beats, return median feature
# vector for the window
def _aggregate_window(beats, fs):
    feats = []
    for beat in beats:
        try:
            f = extract(beat, fs)
        except Exception:
            continue
        v = np.array(list(f.values()), dtype=float)
        if not np.all(np.isfinite(v)):
            continue
        feats.append(v)

    if len(feats) < MIN_BEATS_PER_WINDOW:
        return None

    feats = np.stack(feats)
    med = np.median(feats, axis=0)
    mad = np.median(np.abs(feats - med), axis=0)
    rz = np.abs(feats - med) / (mad + 1e-9)
    keep = np.median(rz, axis=1) < OUTLIER_MAD_K

    if keep.sum() < MIN_BEATS_PER_WINDOW:
        return None

    return np.median(feats[keep], axis=0)


# one feature row per 10s window (median of valid beats), one [SBP, DBP] label,
# and the subject id (carried through so per-subject calibration is possible)
def build_matrices(ppg_segments, fs, labels):
    feature_matrix, target_matrix, subjects = [], [], []

    for i, raw in enumerate(ppg_segments):
        clean = preprocess(raw, fs)
        beats = split_beats(clean, fs)

        agg = _aggregate_window(beats, fs)
        if agg is None:
            continue

        feature_matrix.append(agg)
        target_matrix.append([labels["sbp"][i], labels["dbp"][i]])
        subjects.append(labels["subject"][i])

    return np.array(feature_matrix), np.array(target_matrix), np.array(subjects)


# raw-signal counterpart for the CNN path: returns the cleaned 10s PPG window
def build_signal_matrices(ppg_segments, fs, labels):
    signals, target_matrix, subjects = [], [], []

    for i, raw in enumerate(ppg_segments):
        clean = preprocess(raw, fs)
        beats = split_beats(clean, fs)

        if _aggregate_window(beats, fs) is None:
            continue

        signals.append(clean)
        target_matrix.append([labels["sbp"][i], labels["dbp"][i]])
        subjects.append(labels["subject"][i])

    return np.array(signals), np.array(target_matrix), np.array(subjects)


# predict (SBP, DBP) for a raw PPG window by aggregating per-beat predictions
def predict_bp_window(model, ppg, fs):
    clean = preprocess(ppg, fs)
    beats = split_beats(clean, fs)

    preds = []
    for beat in beats:
        try:
            feats = extract(beat, fs)
        except Exception:
            continue
        x = np.array(list(feats.values())).reshape(1, -1)
        preds.append(model.predict(x)[0])

    if not preds:
        return None

    preds = np.array(preds)
    return float(np.median(preds[:, 0])), float(np.median(preds[:, 1]))


def _label_stats(name, labels):
    sbp, dbp = labels["sbp"], labels["dbp"]
    print(
        f"  {name}: SBP {sbp.mean():.1f}±{sbp.std():.1f} "
        f"[{sbp.min():.0f},{sbp.max():.0f}]  "
        f"DBP {dbp.mean():.1f}±{dbp.std():.1f} "
        f"[{dbp.min():.0f},{dbp.max():.0f}]"
    )


def _print_metrics(metrics):
    header = f"{'target':<6}{'n':>8}{'MAE':>10}{'RMSE':>10}{'R^2':>10}{'r':>10}{'ME':>10}{'SD':>10}"
    print(header)
    print("-" * len(header))
    for target in ("sbp", "dbp"):
        m = metrics[target]
        print(
            f"{target.upper():<6}{m['n']:>8d}"
            f"{m['mae']:>10.3f}{m['rmse']:>10.3f}"
            f"{m['r2']:>10.3f}{m['pearson_r']:>10.3f}"
            f"{m['me']:>+10.3f}{m['sd']:>10.3f}"
        )


def _train_model(model_type, X, y, n_estimators, random_state):
    if model_type == "rf":
        return rfg.train(X, y, n_estimators=n_estimators, random_state=random_state)
    if model_type == "gb":
        # n_estimators reuses the same knob as RF for CLI parity (HistGB calls it max_iter)
        return gbr.train(X, y, max_iter=n_estimators, random_state=random_state)
    raise ValueError(f"unknown model_type: {model_type!r} (expected 'rf' or 'gb')")


def main(
    n_train=15000,
    n_test=3000,
    n_estimators=300,
    random_state=42,
    model_type="rf",
    calibrate=0,
    anchor=False,
):
    # random_state on the loader => sample across the full file
    print(f"loading train: {TRAIN_PATH}")
    ppg_tr, fs, labels_tr = load_data(TRAIN_PATH, n=n_train, random_state=random_state)
    _label_stats("train labels", labels_tr)
    X_tr, y_tr, subj_tr = build_matrices(ppg_tr, fs, labels_tr)
    print(f"  segments={len(ppg_tr)}  windows_kept={len(X_tr)}  features={X_tr.shape[1]}")

    print(f"training model={model_type} (n_estimators={n_estimators})")
    model = _train_model(model_type, X_tr, y_tr, n_estimators, random_state)

    anchor_model = None
    if anchor:
        print("building anchor pairs and training anchor-paired model")
        X_pair, y_pair = build_train_pairs(X_tr, y_tr, subj_tr, random_state=random_state)
        print(f"  pairs={len(X_pair)}  anchor_features={X_pair.shape[1]}")
        anchor_model = _train_model(model_type, X_pair, y_pair, n_estimators, random_state)

    print(f"loading test:  {TEST_PATH}")
    ppg_te, fs, labels_te = load_data(TEST_PATH, n=n_test, random_state=random_state)
    _label_stats("test  labels", labels_te)
    X_te, y_te, subj_te = build_matrices(ppg_te, fs, labels_te)
    print(f"  segments={len(ppg_te)}  windows_kept={len(X_te)}  subjects={len(np.unique(subj_te))}")

    print()
    print("=== uncalibrated ===")
    metrics = evaluate(model, X_te, y_te)
    _print_metrics(metrics)

    metrics_cal = None
    if calibrate > 0:
        preds = model.predict(X_te)
        cal_preds, eval_mask, n_used = calibrate_per_subject(
            preds, y_te, subj_te, k=calibrate, random_state=random_state
        )
        print()
        print(f"=== mean-offset calibrated (k={calibrate} cal-windows/subject, "
              f"{n_used} subjects, eval n={int(eval_mask.sum())}) ===")
        metrics_cal = metrics_pair(y_te[eval_mask], cal_preds[eval_mask])
        _print_metrics(metrics_cal)

    metrics_anchor = None
    if anchor:
        k = max(1, calibrate)
        a_preds, a_mask, a_used = predict_with_anchor(
            anchor_model, X_te, y_te, subj_te, k=k, random_state=random_state
        )
        print()
        print(f"=== anchor-paired model (k={k} cal-windows/subject, "
              f"{a_used} subjects, eval n={int(a_mask.sum())}) ===")
        metrics_anchor = metrics_pair(y_te[a_mask], a_preds[a_mask])
        _print_metrics(metrics_anchor)

    return model, metrics, metrics_cal, metrics_anchor


# CNN runs on raw signal windows
def main_cnn(
    n_train=15000,
    n_test=3000,
    n_epochs=30,
    batch_size=128,
    lr=1e-3,
    random_state=42,
    calibrate=0,
    anchor=False,
    save_anchor=None,
):
    from models import cnn  # imported lazily so non-CNN runs don't pay the torch import cost

    print(f"loading train: {TRAIN_PATH}")
    ppg_tr, fs, labels_tr = load_data(TRAIN_PATH, n=n_train, random_state=random_state)
    _label_stats("train labels", labels_tr)
    Xs_tr, ys_tr, subj_tr = build_signal_matrices(ppg_tr, fs, labels_tr)
    print(f"  segments={len(ppg_tr)}  windows_kept={len(Xs_tr)}  signal_len={Xs_tr.shape[1]}")

    print(f"training 1D CNN (epochs={n_epochs}, batch={batch_size}, lr={lr})")
    model = cnn.train(
        Xs_tr, ys_tr,
        n_epochs=n_epochs, batch_size=batch_size, lr=lr,
        random_state=random_state,
    )

    anchor_model = None
    if anchor:
        from models import cnn_anchor
        print(f"training anchor 1D CNN (epochs={n_epochs}, batch={batch_size}, lr={lr})")
        anchor_model = cnn_anchor.train(
            Xs_tr, ys_tr, subj_tr,
            n_epochs=n_epochs, batch_size=batch_size, lr=lr,
            random_state=random_state,
        )

    print(f"loading test:  {TEST_PATH}")
    ppg_te, fs, labels_te = load_data(TEST_PATH, n=n_test, random_state=random_state)
    _label_stats("test  labels", labels_te)
    Xs_te, ys_te, subjs_te = build_signal_matrices(ppg_te, fs, labels_te)
    print(f"  segments={len(ppg_te)}  windows_kept={len(Xs_te)}  subjects={len(np.unique(subjs_te))}")

    print()
    print("=== CNN uncalibrated ===")
    metrics = evaluate(model, Xs_te, ys_te)
    _print_metrics(metrics)

    metrics_cal = None
    if calibrate > 0:
        preds = model.predict(Xs_te)
        cal_preds, eval_mask, n_used = calibrate_per_subject(
            preds, ys_te, subjs_te, k=calibrate, random_state=random_state
        )
        print()
        print(f"=== CNN mean-offset calibrated (k={calibrate} cal-windows/subject, "
              f"{n_used} subjects, eval n={int(eval_mask.sum())}) ===")
        metrics_cal = metrics_pair(ys_te[eval_mask], cal_preds[eval_mask])
        _print_metrics(metrics_cal)

    metrics_anchor = None
    if anchor:
        k = max(1, calibrate)
        a_preds, a_mask, a_used = anchor_model.predict_with_anchor(
            Xs_te, ys_te, subjs_te, k=k, random_state=random_state
        )
        print()
        print(f"=== CNN anchor-paired (k={k} cal-windows/subject, "
              f"{a_used} subjects, eval n={int(a_mask.sum())}) ===")
        metrics_anchor = metrics_pair(ys_te[a_mask], a_preds[a_mask])
        _print_metrics(metrics_anchor)

    if anchor and save_anchor is not None:
        anchor_model.save(save_anchor)
        print(f"saved anchor CNN to {save_anchor}")

    return model, metrics, metrics_cal, metrics_anchor


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--model", choices=["rf", "gb"], default="rf")
    p.add_argument("--n-train", type=int, default=15000)
    p.add_argument("--n-test", type=int, default=3000)
    p.add_argument("--n-estimators", type=int, default=300)
    p.add_argument("--random-state", type=int, default=42)
    p.add_argument("--calibrate", type=int, default=0,
                   help="mean-offset calibration: K cuff-readings held out per subject (0=off)")
    p.add_argument("--anchor", action="store_true",
                   help="also train and evaluate an anchor-paired model (one-time calibration)")
    p.add_argument("--cnn", action="store_true",
                   help="use the 1D CNN pipeline instead (raw signal in, separate from RF/GB)")
    p.add_argument("--cnn-epochs", type=int, default=30)
    p.add_argument("--cnn-batch", type=int, default=128)
    p.add_argument("--cnn-lr", type=float, default=1e-3)
    p.add_argument("--save-anchor", type=str, default=None,
                   help="path to save the trained anchor CNN (requires --cnn --anchor)")
    args = p.parse_args()
    if args.cnn:
        main_cnn(
            n_train=args.n_train,
            n_test=args.n_test,
            n_epochs=args.cnn_epochs,
            batch_size=args.cnn_batch,
            lr=args.cnn_lr,
            random_state=args.random_state,
            calibrate=args.calibrate,
            anchor=args.anchor,
            save_anchor=args.save_anchor,
        )
    else:
        main(
            n_train=args.n_train,
            n_test=args.n_test,
            n_estimators=args.n_estimators,
            random_state=args.random_state,
            model_type=args.model,
            calibrate=args.calibrate,
            anchor=args.anchor,
        )
