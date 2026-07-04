import numpy as np
from scipy.signal import find_peaks
from scipy.stats import skew, kurtosis


# find a,b,c,d,e fiducial points on the APG of one beat
def apg_points(apg):
    n = len(apg)
    end = int(0.80 * n)
    seg = apg[:end]

    # prominence floor relative to APG range
    prom = 0.02 * (seg.max() - seg.min())
    pos, _ = find_peaks(seg, prominence=prom)
    neg, _ = find_peaks(-seg, prominence=prom)

    if len(pos) < 3 or len(neg) < 2:
        raise ValueError("APG: insufficient extrema for a-e")

    a_i = int(pos[0])
    b_after = neg[neg > a_i]
    if len(b_after) == 0:
        raise ValueError("APG: no b after a")
    b_i = int(b_after[0])

    c_after = pos[pos > b_i]
    if len(c_after) == 0:
        raise ValueError("APG: no c after b")
    c_i = int(c_after[0])

    d_after = neg[neg > c_i]
    if len(d_after) == 0:
        raise ValueError("APG: no d after c")
    d_i = int(d_after[0])

    e_after = pos[pos > d_i]
    if len(e_after) == 0:
        raise ValueError("APG: no e after d")
    e_i = int(e_after[0])

    return [a_i, b_i, c_i, d_i, e_i]


# locate systolic peak (S), dicrotic notch (N) and diastolic peak (D) on the
# PPG of one beat.
def pulse_landmarks(ppg, c_i, e_i):
    n = len(ppg)
    S_i = int(np.argmax(ppg))

    base = max(ppg[0], ppg[-1])
    syst_amp = ppg[S_i] - base
    if syst_amp <= 0:
        raise ValueError("PPG: peak below foot baseline")

    N_i = None
    D_i = None
    start = S_i + 1
    end = int(0.85 * n)

    if end - start >= 5:
        seg = ppg[start:end]
        prom = 0.02 * syst_amp
        minima, _ = find_peaks(-seg, prominence=prom)
        if len(minima) > 0:
            N_i = start + int(minima[0])
        maxima, _ = find_peaks(seg, prominence=prom)
        anchor = minima[0] if len(minima) > 0 else 0
        after_notch = maxima[maxima > anchor]
        if len(after_notch) > 0:
            D_i = start + int(after_notch[0])

    if N_i is None:
        if not (S_i < c_i < n):
            raise ValueError("PPG: notch undetected and APG-c fallback invalid")
        N_i = c_i

    if D_i is None:
        if not (N_i < e_i < n):
            raise ValueError("PPG: diastolic-peak undetected and APG-e fallback invalid")
        D_i = e_i

    return S_i, N_i, D_i


# extract BP correlated features from a single PPG beat
def extract(ppg, fs):
    vpg = np.gradient(ppg)
    apg = np.gradient(vpg)

    # APG fiducials
    a_i, b_i, c_i, d_i, e_i = apg_points(apg)
    a, b, c, d, e = apg[a_i], apg[b_i], apg[c_i], apg[d_i], apg[e_i]

    # PPG fiducials (S = systolic peak, N = dicrotic notch, D = diastolic peak)
    S_i, N_i, D_i = pulse_landmarks(ppg, c_i, e_i)
    O_i, Op_i = 0, len(ppg) - 1
    S = ppg[S_i]
    n = len(ppg)
    w = n / fs

    # rebaseline beat above the higher of the two feet so areas are positive
    # (the preprocessed signal has zero mean and goes negative)
    foot_amp = max(ppg[0], ppg[-1])
    above = np.maximum(ppg - foot_amp, 0.0)
    total_area = np.trapezoid(above) / fs
    if total_area <= 0:
        raise ValueError("PPG: non-positive total pulse area")
    ejection_area = np.trapezoid(above[: N_i + 1]) / fs
    sys_area = np.trapezoid(above[: S_i + 1]) / fs
    dia_area = np.trapezoid(above[S_i:]) / fs

    # APG values at PPG fiducial times
    Sc_2 = apg[S_i]
    c_2 = apg[c_i]

    # VPG values at fiducial times
    S1 = vpg[S_i]
    c_1 = vpg[c_i]
    O1 = vpg[O_i]
    Op1 = vpg[Op_i]

    # pulse width at half max, anchored to the higher of the two feet
    foot = max(ppg[O_i], ppg[Op_i])
    half = foot + (S - foot) / 2.0
    above = np.where(ppg >= half)[0]
    pwhm = (above[-1] - above[0]) / fs if len(above) >= 2 else 0.0

    return {
        # dicrotic notch vs systolic peak on APG — reflects vascular resistance / augmentation
        "d/a": d / a,
        # first inflection vs systolic peak on APG — reflects arterial stiffness, correlates with age
        "b/a": b / a,
        # combined vascular aging marker (early + late reflection balance)
        "(b-c-d)/a": (b - c - d) / a,
        # extended vascular aging marker including late diastolic wave
        "(b-c-d-e)/a": (b - c - d - e) / a,
        # VPG upstroke/downstroke energy ratio — captures systolic-vs-baseline velocity balance
        "(S+1+c-1)^2/(O+1+O'+1)^2": (S1 + c_1) ** 2 / (O1 + Op1) ** 2,
        # inflection asymmetry on APG, normalised by peak product
        "(b-2-d-2)/bd": (b - d) / (b * d),
        # APG value at the PPG systolic peak — stiffness indicator
        "Sc-2": Sc_2,
        # APG c-point relative to PPG systolic amplitude — cross-derivative stiffness ratio
        "c-2/S": c_2 / S,
        # VPG inflection amplitude per unit beat width — normalises for heart rate
        "c-1/w": c_1 / w,
        # systolic amplitude relative to its own 2nd-derivative response
        "(S-c-2)/Sc-2": (S - c_2) / Sc_2,
        # heart rate (bpm) — DBP correlate, autonomic state proxy
        "hr": 60.0 / w,
        # crest time (s): foot to systolic peak — vascular compliance proxy
        "crest_time": S_i / fs,
        # crest time normalised by beat duration — HR-invariant shape feature
        "crest_ratio": S_i / n,
        # systolic upslope amplitude/time — contractility / SBP correlate
        "upslope": (S - ppg[O_i]) / max(S_i / fs, 1e-9),
        # pulse width at half max (s) — peripheral resistance proxy
        "pwhm": pwhm,
        # skewness of the pulse shape — well-known SQI / BP correlate
        "skew": float(skew(ppg)),
        # kurtosis of the pulse shape — peakedness, complementary to skew
        "kurt": float(kurtosis(ppg)),
        # APG d-index amplitude on PPG normalised by S — augmentation-index proxy
        "ai_proxy": ppg[d_i] / S,
        # PPG-domain landmark features — Mejía-Mejía et al:
        # peak-to-peak time (s), systolic to diastolic peak — pulse-wave-velocity proxy
        "t13": (D_i - S_i) / fs,
        # reflection index: diastolic-peak amplitude / systolic — vascular tone
        "p2p1": ppg[D_i] / S,
        # time to dicrotic notch normalised by beat duration ejection duration proxy
        "notch_t_ratio": N_i / n,
        # normalised ejection area: ejection-phase area / total pulse area
        "nEjecA": ejection_area / total_area,
        # systolic / diastolic area ratio — peripheral resistance correlate
        "as_ad_ratio": sys_area / (dia_area + 1e-9),
    }