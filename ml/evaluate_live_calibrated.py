import os
import joblib
import numpy as np
from loaders.esp32 import load_sessions
from ml_pipeline import predict_bp_window, calibrate, predict_calibrated

DATA_FILE = os.path.join(os.path.dirname(__file__), "data_collection", "data", "ppg_dataset.xlsx")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "models", "rfg.joblib")


def main():
    model = joblib.load(MODEL_FILE)
    sessions = load_sessions(DATA_FILE)
    print(f"Loaded {len(sessions)} sessions\n")

    raw_errors = []
    cal_errors = []

    for s in sessions:
        ppg = s["ppg"]
        fs = s["fs"]
        sbp_true = s["metadata"]["sbp"]
        dbp_true = s["metadata"]["dbp"]

        # split session in half for calibration and testing
        half = len(ppg) // 2
        cal_ppg, test_ppg = ppg[:half], ppg[half:]

        offsets = calibrate(model, cal_ppg, fs, sbp_true, dbp_true)
        if offsets is None:
            print(f"Session {s['session_id']}: calibration failed")
            continue

        raw = predict_bp_window(model, test_ppg, fs)
        cal = predict_calibrated(model, test_ppg, fs, offsets)
        if raw is None or cal is None:
            print(f"Session {s['session_id']}: test prediction failed")
            continue

        raw_sbp, raw_dbp = raw
        cal_sbp, cal_dbp = cal

        raw_errors.append((raw_sbp - sbp_true, raw_dbp - dbp_true))
        cal_errors.append((cal_sbp - sbp_true, cal_dbp - dbp_true))

        print(f"Session {s['session_id']}: actual {sbp_true}/{dbp_true}")
        print(f"  raw pred: {raw_sbp:.0f}/{raw_dbp:.0f}  offsets: {offsets[0]:+.1f}/{offsets[1]:+.1f}")
        print(f"  cal pred: {cal_sbp:.0f}/{cal_dbp:.0f}")

    if raw_errors:
        raw_errors = np.array(raw_errors)
        cal_errors = np.array(cal_errors)
        print(f"\n--- Raw (no calibration) ---")
        print(f"SBP MAE: {np.mean(np.abs(raw_errors[:, 0])):.2f}  DBP MAE: {np.mean(np.abs(raw_errors[:, 1])):.2f}")
        print(f"\n--- Calibrated ---")
        print(f"SBP MAE: {np.mean(np.abs(cal_errors[:, 0])):.2f}  DBP MAE: {np.mean(np.abs(cal_errors[:, 1])):.2f}")

if __name__ == "__main__":
    main()
