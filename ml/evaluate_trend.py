import os
import joblib
import numpy as np
from collections import defaultdict
from loaders.pulsedb import load_data
from ml_pipeline import predict_bp_window, calibrate, predict_calibrated

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "pulsedb")
TEST_FILE = os.path.join(DATA_DIR, "VitalDB_CalFree_Test_Subset.mat")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "models", "rfg.joblib")


def main(n=2000, min_segments=5, min_bp_range=10):
    model = joblib.load(MODEL_FILE)
    ppg, fs, labels = load_data(TEST_FILE, n=n)

    # group segment indices by subject
    groups = defaultdict(list)
    for i, subj in enumerate(labels["subject"]):
        groups[subj].append(i)

    print(f"Loaded {n} segments across {len(groups)} subjects\n")

    raw_errors, cal_errors = [], []
    pred_deltas, actual_deltas = [], []
    subjects_used = 0

    for subj, idxs in groups.items():
        if len(idxs) < min_segments:
            continue

        sbps = labels["sbp"][idxs]
        # require meaningful BP variation within subject to test tracking
        if sbps.max() - sbps.min() < min_bp_range:
            continue

        # use lowest-SBP segment as calibration anchor
        anchor_local = int(np.argmin(sbps))
        anchor_i = idxs[anchor_local]
        cal_sbp = labels["sbp"][anchor_i]
        cal_dbp = labels["dbp"][anchor_i]

        offsets = calibrate(model, ppg[anchor_i], fs, cal_sbp, cal_dbp)
        if offsets is None:
            continue

        subjects_used += 1
        for i in idxs:
            if i == anchor_i:
                continue
            raw = predict_bp_window(model, ppg[i], fs)
            cal = predict_calibrated(model, ppg[i], fs, offsets)
            if raw is None or cal is None:
                continue

            true_sbp = labels["sbp"][i]
            true_dbp = labels["dbp"][i]

            raw_errors.append((raw[0] - true_sbp, raw[1] - true_dbp))
            cal_errors.append((cal[0] - true_sbp, cal[1] - true_dbp))

            pred_deltas.append(cal[0] - cal_sbp)
            actual_deltas.append(true_sbp - cal_sbp)

    raw_errors = np.array(raw_errors)
    cal_errors = np.array(cal_errors)
    pred_deltas = np.array(pred_deltas)
    actual_deltas = np.array(actual_deltas)

    print(f"Subjects evaluated: {subjects_used}")
    print(f"Test segments: {len(raw_errors)}\n")

    print("--- Raw (no calibration) ---")
    print(f"SBP MAE: {np.mean(np.abs(raw_errors[:, 0])):.2f}  DBP MAE: {np.mean(np.abs(raw_errors[:, 1])):.2f}")

    print("\n--- Calibrated (anchor = lowest-BP segment per subject) ---")
    print(f"SBP MAE: {np.mean(np.abs(cal_errors[:, 0])):.2f}  DBP MAE: {np.mean(np.abs(cal_errors[:, 1])):.2f}")

    print("\n--- SBP trend tracking (delta from anchor) ---")
    r = np.corrcoef(pred_deltas, actual_deltas)[0, 1]
    print(f"Pearson r (predicted Delta vs actual Delta): {r:.3f}")
    print(f"Actual Delta range: {actual_deltas.min():+.1f} to {actual_deltas.max():+.1f} mmHg")
    print(f"Predicted Delta range: {pred_deltas.min():+.1f} to {pred_deltas.max():+.1f} mmHg")


if __name__ == "__main__":
    main()
