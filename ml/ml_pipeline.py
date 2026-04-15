import numpy as np
from preprocessing.process import preprocess 
from preprocessing.segment import split_beats
from features.extract import extract

# build per beat feature matrix and target matrix from loader
def build_matrices(ppg_segments, fs, labels):
    feature_matrix, target_matrix = [], []

    for i, raw in enumerate(ppg_segments):
        # preprocess raw PPG signal
        clean = preprocess(raw, fs)
        # split into beats
        beats = split_beats(clean, fs)

        for beat in beats:
            try:
                feats = extract(beat, fs)
            except Exception:
                # skip beats where feature extraction fails
                continue
            feature_matrix.append(list(feats.values()))
            target_matrix.append([labels["sbp"][i], labels["dbp"][i]])

    return np.array(feature_matrix), np.array(target_matrix)

# predict sbp and dbp for PPG window
def predict_bp_window(model, ppg, fs):
    if len(ppg) < fs * 2:  # need at least 2 seconds of signal
        return None
    clean = preprocess(ppg, fs)
    beats = split_beats(clean, fs)

    feats_list = []
    for beat in beats:
        try:
            feats = extract(beat, fs)
        except Exception:
            continue
        feats_list.append(list(feats.values()))

    if not feats_list:
        return None

    # batched predict avoids per-beat parallel dispatch overhead
    preds = model.predict(np.array(feats_list))
    sbp = np.median(preds[:, 0])
    dbp = np.median(preds[:, 1])

    return sbp, dbp


# compute per-subject offsets from a calibration window with a known cuff reading
def calibrate(model, ppg_cal, fs, true_sbp, true_dbp):
    result = predict_bp_window(model, ppg_cal, fs)
    if result is None:
        return None
    pred_sbp, pred_dbp = result
    return (true_sbp - pred_sbp, true_dbp - pred_dbp)


# predict with a subject's calibration offsets applied
def predict_calibrated(model, ppg, fs, offsets):
    result = predict_bp_window(model, ppg, fs)
    if result is None:
        return None
    sbp, dbp = result
    off_sbp, off_dbp = offsets
    return sbp + off_sbp, dbp + off_dbp
