import serial
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

PORT = "/dev/cu.usbserial-0001"
BAUD = 115200
SAMPLE_RATE = 100
WINDOW_SEC = 10
WINDOW = SAMPLE_RATE * WINDOW_SEC


# Plots PPG waveforms from microcontroller port in real-time
ser = serial.Serial(PORT, BAUD)
buf = []

fig, ax = plt.subplots()
(line,) = ax.plot([], [], "b-", linewidth=1.5)
ax.set_ylim(0, 4095)
ax.set_xlim(0, WINDOW_SEC)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Raw ADC Value")
ax.set_title("PPG Waveform")


def update(frame):
    while ser.in_waiting:
        try:
            val = int(ser.readline().decode().strip())
            buf.append(val)
        except ValueError:
            pass

    if len(buf) > WINDOW:
        del buf[: len(buf) - WINDOW]

    if buf:
        times = [i / SAMPLE_RATE for i in range(len(buf))]
        line.set_data(times, buf)
        ax.set_xlim(0, WINDOW_SEC)

        ymin, ymax = min(buf), max(buf)
        margin = (ymax - ymin) * 0.1 or 50
        ax.set_ylim(ymin - margin, ymax + margin)

    return (line,)


ani = FuncAnimation(fig, update, interval=50, blit=True)
plt.show()
ser.close()
