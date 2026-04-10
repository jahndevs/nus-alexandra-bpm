import time
import numpy as np
import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import butter, lfilter, lfilter_zi, savgol_filter
from scipy.ndimage import median_filter

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200
FS = 100            # match the MCU sample rate
WINDOW_SEC = 5

# Filter params
LOWPASS_CUTOFF = 2.5
LOWPASS_ORDER = 4
MEDIAN_KERNEL = 9      
SAVGOL_WINDOW = 61          # ~XXX ms
SAVGOL_POLY = 2

# low-pass butterworth filter
b, a = butter(LOWPASS_ORDER, LOWPASS_CUTOFF / (FS / 2.0), btype='low')
_zi_template = lfilter_zi(b, a)

ser = serial.Serial(PORT, BAUD)
times: list[float] = []
vals: list[int] = []
lp_vals: list[float] = []
zi = _zi_template.copy()
t0 = None

fig, ax = plt.subplots(figsize=(11, 5))
(line_raw,)    = ax.plot([], [], "b-", linewidth=0.6, alpha=0.25, label="Raw")
(line_smooth,) = ax.plot([], [], color="#22c55e", linewidth=2.0, alpha=0.95,
                         label="Smoothed")
ax.legend(loc="upper right", fontsize=9)
ax.set_ylim(0, 4095)
ax.set_xlim(0, WINDOW_SEC)
ax.set_xlabel("Time (s)")
ax.set_ylabel("PPG Value")
ax.set_title("PPG Waveform")
ax.grid(True, alpha=0.15)


def update(frame):
    global t0, zi

    new_chunk: list[int] = []
    while ser.in_waiting:
        try:
            val = int(ser.readline().decode().strip())
        except ValueError:
            continue
        now = time.monotonic()
        if t0 is None:
            t0 = now
            zi = _zi_template * val
        times.append(now - t0)
        vals.append(val)
        new_chunk.append(val)

    # low-pass on new samples, zi carries across frames
    if new_chunk:
        out, zi = lfilter(b, a, np.array(new_chunk, dtype=float), zi=zi)
        lp_vals.extend(out.tolist())

    # drop the old samples outside the window
    if times:
        cutoff = times[-1] - WINDOW_SEC
        drop = 0
        while drop < len(times) and times[drop] < cutoff:
            drop += 1
        if drop:
            del times[:drop]
            del vals[:drop]
            del lp_vals[:drop]

    if vals:
        v_arr = np.array(vals, dtype=float)
        lp_arr = np.array(lp_vals, dtype=float)

        # low-pass --> median --> savitzky-golay 2x
        t_arr = np.array(times)
        smooth = median_filter(lp_arr, size=MEDIAN_KERNEL)
        if len(smooth) >= SAVGOL_WINDOW:
            smooth = savgol_filter(smooth, SAVGOL_WINDOW, SAVGOL_POLY)
            smooth = savgol_filter(smooth, SAVGOL_WINDOW, SAVGOL_POLY)

        line_raw.set_data(t_arr, v_arr)
        line_smooth.set_data(t_arr, smooth)

        right = max(times[-1], WINDOW_SEC)
        ax.set_xlim(right - WINDOW_SEC, right)

        ymin, ymax = v_arr.min(), v_arr.max()
        margin = (ymax - ymin) * 0.1 or 50
        ax.set_ylim(ymin - margin, ymax + margin)


ani = FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.show()
ser.close()
