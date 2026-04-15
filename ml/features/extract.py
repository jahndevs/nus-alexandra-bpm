import numpy as np
from scipy.signal import find_peaks


# find a,b,c,d,e fiducial points on the APG (first 5 alternating extrema)
def apg_points(apg):
    pos, _ = find_peaks(apg)
    neg, _ = find_peaks(-apg)
    points = sorted(list(pos) + list(neg))
    return points[:5]


# extract the 10 BP-correlated features from a single PPG beat
def extract(ppg, fs):
    vpg = np.gradient(ppg)
    apg = np.gradient(vpg)

    # APG fiducials
    a_i, b_i, c_i, d_i, e_i = apg_points(apg)
    a, b, c, d, e = apg[a_i], apg[b_i], apg[c_i], apg[d_i], apg[e_i]

    # PPG fiducials
    S_i = int(np.argmax(ppg))
    O_i, Op_i = 0, len(ppg) - 1
    S = ppg[S_i]
    w = len(ppg) / fs

    # APG values at PPG fiducial times
    Sc_2 = apg[S_i]
    c_2 = apg[c_i]

    # VPG values at fiducial times
    S1 = vpg[S_i]
    c_1 = vpg[c_i]
    O1 = vpg[O_i]
    Op1 = vpg[Op_i]

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
    }