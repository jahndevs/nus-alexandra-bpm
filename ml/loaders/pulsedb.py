import h5py
import numpy as np

# sampling rate
fs = 125
ppg_channel = 1

# load n 10 second PPG segments + BP labels + demographics from database
def load_data(path, n=1000):
    with h5py.File(path, "r") as f:
        s = f["Subset"]
        n = min(n, s["SBP"].shape[1])

        # (n, 1250) one ten second segment per row
        ppg = s["Signals"][:, ppg_channel, :n].T

        labels = {
            "sbp": np.array(s["SBP"])[0, :n],
            "dbp": np.array(s["DBP"])[0, :n],
            "age": np.array(s["Age"])[0, :n],
            "height": np.array(s["Height"])[0, :n],
            "weight": np.array(s["Weight"])[0, :n],
            "bmi": np.array(s["BMI"])[0, :n],
        }

        # dereference subject ID strings
        subjects = []
        for i in range(n):
            ref = s["Subject"][0, i]
            subjects.append("".join(chr(c[0]) for c in f[ref][:]))
        labels["subject"] = np.array(subjects)

    return ppg, fs, labels

