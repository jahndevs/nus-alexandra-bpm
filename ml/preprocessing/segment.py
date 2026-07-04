import numpy as np
from scipy.signal import find_peaks
# python3 ml_pipeline.py --anchor --calibrate 1

# split preprocessed PPG signal into individual beats (foot-to-foot)
def split_beats(ppg, fs, min_bpm=40, max_bpm=200):
    min_distance = int(fs * 60 / max_bpm)
    prom = 0.3 * np.std(ppg)

    peaks, _ = find_peaks(ppg, distance=min_distance, prominence=prom)
    feet, _ = find_peaks(-ppg, distance=min_distance, prominence=prom)

    result = []
    max_len = int(fs * 60 / min_bpm)
    min_len = int(fs * 60 / max_bpm)

    for start, end in zip(feet[:-1], feet[1:]):
        if not (min_len <= end - start <= max_len):
            continue
        # require exactly one systolic peak between the two feet
        between = peaks[(peaks > start) & (peaks < end)]
        if len(between) != 1:
            continue
        result.append(ppg[start:end])

    return result