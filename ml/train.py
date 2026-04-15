import os
import joblib
from loaders.pulsedb import load_data
from ml_pipeline import build_matrices
from models.rfg import train 


DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), "data", "pulsedb")
TRAIN_FILE = os.path.join(DATA_DIRECTORY, "VitalDB_Train_Subset.mat")
MODEL_OUT = os.path.join(os.path.dirname(__file__), "models", "rfg.joblib")

def main(n=20000):
    print(f"Loading data from {TRAIN_FILE}...")
    ppg, fs, labels = load_data(TRAIN_FILE, n=n)

    print("Building Feature Matrix")
    X, y = build_matrices(ppg, fs, labels)
    print(f"Feature Matrix Shape: {X.shape}, Labels Shape: {y.shape}")

    print("Training Random Forest Regression Model...")
    model, metrics = train(X, y)
    print(metrics)

    joblib.dump(model, MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")

if __name__ == "__main__":
    main()