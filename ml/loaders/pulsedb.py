import h5py
import numpy as np

# sampling rate
fs = 125
ppg_channel = 1


# resolve PulseDB Subject column to a 1D array of subject IDs (one per segment)
def _load_subject(f, s, idx):
    raw = s["Subject"]
    if h5py.check_dtype(ref=raw.dtype):
        refs = np.array(raw)[0, idx]
        out = []
        for r in refs:
            val = np.array(f[r]).flatten()
            # numeric subject ids are stored as a single number; strings as
            # uint16 char codes — collapse either to a hashable scalar
            if val.dtype.kind in ("u", "i", "f"):
                if val.size == 1:
                    out.append(val.item())
                else:
                    out.append("".join(chr(int(c)) for c in val))
            else:
                out.append(val.tobytes().decode(errors="ignore"))
        return np.array(out)
    return np.array(raw)[0, idx]

def load_data(path, n=1000, random_state=None):
    with h5py.File(path, "r") as f:
        s = f["Subset"]
        total = s["SBP"].shape[1]
        n = min(n, total)

        if random_state is None:
            idx = np.arange(n)
        else:
            rng = np.random.default_rng(random_state)
            idx = np.sort(rng.choice(total, size=n, replace=False))

        # (n, 1250) one ten second segment per row
        ppg = s["Signals"][:, ppg_channel, idx].T

        labels = {
            "sbp": np.array(s["SBP"])[0, idx],
            "dbp": np.array(s["DBP"])[0, idx],
            "age": np.array(s["Age"])[0, idx],
            "height": np.array(s["Height"])[0, idx],
            "weight": np.array(s["Weight"])[0, idx],
            "bmi": np.array(s["BMI"])[0, idx],
            "subject": _load_subject(f, s, idx),
        }

    return ppg, fs, labels

