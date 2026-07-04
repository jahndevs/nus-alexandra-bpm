import csv
import numpy as np


# load a long PPG capture (sample,t_seconds,ppg_raw) and a sparse BP record
# (t_seconds,wall_clock,systolic,diastolic). Returns:
#   ppg:    (N,) float ADC samples
#   t_ppg:  (N,) sample timestamps in seconds
#   bp:     list of (t_seconds, sbp, dbp) tuples
def load_long_capture(ppg_path, bp_path):
    samples = []
    times = []
    with open(ppg_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append(float(row["ppg_raw"]))
            times.append(float(row["t_seconds"]))
    ppg = np.array(samples, dtype=np.float64)
    t_ppg = np.array(times, dtype=np.float64)

    bp = []
    with open(bp_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            bp.append((
                float(row["t_seconds"]),
                float(row["systolic"]),
                float(row["diastolic"]),
            ))
    return ppg, t_ppg, bp


# extract the 10s PPG window ending at each BP timestamp. If a reading is
# closer to the start than window_s, pad by taking the first window_s
# instead. Returns:
#   windows: (k, fs*window_s) raw PPG segments
#   bp:      (k, 2) [SBP, DBP] truths
#   t:       (k,) timestamps of the BP readings (kept windows only)
def extract_windows_at_bp(ppg, t_ppg, bp_records, fs=125, window_s=10):
    n = int(fs * window_s)
    windows, bps, ts = [], [], []
    for t, sbp, dbp in bp_records:
        end_idx = int(np.searchsorted(t_ppg, t, side="right"))
        start_idx = end_idx - n
        if start_idx < 0:
            # not enough history before the reading — slide forward
            start_idx = 0
            end_idx = n
        if end_idx > len(ppg):
            # PPG capture ended before this reading; skip
            continue
        windows.append(ppg[start_idx:end_idx])
        bps.append([sbp, dbp])
        ts.append(t)
    return np.array(windows), np.array(bps, dtype=np.float64), np.array(ts)
