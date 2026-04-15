import os
import joblib
import numpy as np
from loaders.pulsedb import load_data
from ml_pipeline import predict_bp_window

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "pulsedb")
TEST_FILE = os.path.join(DATA_DIR, "VitalDB_CalFree_Test_Subset.mat")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "models", "rfg.joblib")


def main(n=500):
    model = joblib.load(MODEL_FILE)
    ppg, fs, labels = load_data(TEST_FILE, n=n)

    errors_sbp, errors_dbp = [], []
    skipped = 0

    for i in range(len(ppg)):
        result = predict_bp_window(model, ppg[i], fs)
        if result is None:
            skipped += 1
            continue
        sbp_pred, dbp_pred = result
        errors_sbp.append(sbp_pred - labels["sbp"][i])
        errors_dbp.append(dbp_pred - labels["dbp"][i])

    errors_sbp = np.array(errors_sbp)
    errors_dbp = np.array(errors_dbp)

    print(f"Evaluated {len(errors_sbp)} windows ({skipped} skipped)")
    print(f"SBP  MAE: {np.mean(np.abs(errors_sbp)):.2f}  ME: {np.mean(errors_sbp):+.2f}  SD: {np.std(errors_sbp):.2f}")
    print(f"DBP  MAE: {np.mean(np.abs(errors_dbp)):.2f}  ME: {np.mean(errors_dbp):+.2f}  SD: {np.std(errors_dbp):.2f}")


if __name__ == "__main__":
    main()
