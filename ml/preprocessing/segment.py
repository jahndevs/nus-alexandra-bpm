import numpy as np
from scipy.signal import find_peaks

# split preprocessed PPG signal into individual beats
def split_beats(ppg, fs, min_bpm=40, max_bpm=200):
    # systolic peaks
    min_distance = int(fs * 60 / max_bpm)
    peaks, _ = find_peaks(ppg, distance=min_distance)

    # troughs of the signal 
    feet, _ = find_peaks(-ppg, distance=min_distance)

    result = []
    max_len = int(fs * 60 / min_bpm)
    min_len = int(fs * 60 / max_bpm)

    for start, end in zip(feet[:-1], feet[1:]):
        if not (min_len <= end - start <= max_len):
            continue
        if not np.any((peaks > start) & (peaks < end)):
            continue
        result.append(ppg[start:end])
    
    return result