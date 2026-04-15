import os
import joblib
import numpy as np
from loaders.esp32 import load_sessions
from ml_pipeline import predict_bp_window

DATA_FILE = os.path.join(os.path.dirname(__file__), "data_collection", "data", "ppg_dataset.xlsx")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "models", "rfg.joblib")


def main():
    model = joblib.load(MODEL_FILE)
    sessions = load_sessions(DATA_FILE)
    print(f"Loaded {len(sessions)} sessions\n")

    errors_sbp, errors_dbp = [], []

    for s in sessions:
        result = predict_bp_window(model, s["ppg"], s["fs"])
        if result is None:
            print(f"Session {s['session_id']}: no valid beats")
            continue
        sbp_pred, dbp_pred = result
        sbp_true = s["metadata"]["sbp"]
        dbp_true = s["metadata"]["dbp"]
        errors_sbp.append(sbp_pred - sbp_true)
        errors_dbp.append(dbp_pred - dbp_true)
        print(f"Session {s['session_id']}: pred {sbp_pred:.0f}/{dbp_pred:.0f}  actual {sbp_true}/{dbp_true}")

    if errors_sbp:
        errors_sbp = np.array(errors_sbp)
        errors_dbp = np.array(errors_dbp)
        print(f"\nSBP  MAE: {np.mean(np.abs(errors_sbp)):.2f}  ME: {np.mean(errors_sbp):+.2f}")
        print(f"DBP  MAE: {np.mean(np.abs(errors_dbp)):.2f}  ME: {np.mean(errors_dbp):+.2f}")


if __name__ == "__main__":
    main()
