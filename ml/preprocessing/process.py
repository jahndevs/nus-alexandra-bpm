from scipy.signal import butter, filtfilt
import numpy as np

# normalize the PPG signal using z-score normalization
def normalize(ppg):
    return (ppg -  np.mean(ppg)) / np.std(ppg)

# apply low-pass butterworth filter to PPG signal
def lowpass(ppg, fs):
    b, a = butter(6, 25, btype="low", fs=fs)
    return filtfilt(b, a, ppg)

# remove baseline wander from PPG signal using polynomial fitting
def baseline_correction(ppg, degree=3):
    x = np.arange(len(ppg))
    trend = np.polyval(np.polyfit(x, ppg, degree), x)
    
    return ppg - trend

# preprocessing pipeline function for PPG signal
def preprocess(ppg, fs):
    ppg = normalize(ppg)
    ppg = lowpass(ppg, fs)
    ppg = baseline_correction(ppg)

    return ppg