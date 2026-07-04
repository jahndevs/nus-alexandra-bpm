"""BLE ingest from the XIAO sensor. """

import argparse
import asyncio
import csv
import os
import threading
import time
from collections import deque

import numpy as np
from bleak import BleakClient, BleakScanner

DEVICE_NAME = "XIAO Sensor"
CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
FS = 125
SAMPLE_BYTES = 2  # firmware sends uint16 little-endian samples


def _unpack_batch(data: bytes) -> list[int]:
    n = len(data) // SAMPLE_BYTES
    return [
        int.from_bytes(data[i * SAMPLE_BYTES : (i + 1) * SAMPLE_BYTES], "little")
        for i in range(n)
    ]


class BleStream:
    """Run BLE notifications in a background thread; expose a shared deque."""

    def __init__(self, device_name: str = DEVICE_NAME, maxlen: int = FS * 15):
        self.device_name = device_name
        self.buffer: deque[int] = deque(maxlen=maxlen)
        self.times: deque[float] = deque(maxlen=maxlen)
        self.t0: float | None = None
        self.total_samples = 0
        self.connected = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> "BleStream":
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _run(self):
        try:
            asyncio.run(self._loop())
        except Exception as e:
            print(f"[ble] fatal: {e}")

    async def _loop(self):
        dt = 1.0 / FS

        def on_notify(_sender, data: bytearray):
            now = time.monotonic()
            if self.t0 is None:
                self.t0 = now
            samples = _unpack_batch(data)
            if not samples:
                return
            # firmware sampled at fixed FS, so spread timestamps across the batch
            arrival = now - self.t0
            base = arrival - (len(samples) - 1) * dt
            for i, v in enumerate(samples):
                self.buffer.append(v)
                self.times.append(base + i * dt)
            self.total_samples += len(samples)

        while not self._stop.is_set():
            print(f"[ble] scanning for '{self.device_name}'...")
            device = await BleakScanner.find_device_by_name(self.device_name, timeout=10)
            if device is None:
                print("[ble] not found, retrying in 3s...")
                await asyncio.sleep(3)
                continue
            try:
                async with BleakClient(device) as client:
                    print(f"[ble] connected to {device.address}")
                    await client.start_notify(CHAR_UUID, on_notify)
                    self.connected.set()
                    while client.is_connected and not self._stop.is_set():
                        await asyncio.sleep(0.1)
                    await client.stop_notify(CHAR_UUID)
            except Exception as e:
                print(f"[ble] error: {e}, reconnecting in 3s...")
                await asyncio.sleep(3)
            finally:
                self.connected.clear()


async def _capture(duration_s: float, device_name: str) -> np.ndarray:
    samples: list[int] = []

    def on_notify(_sender, data: bytearray):
        samples.extend(_unpack_batch(data))

    print(f"Scanning for '{device_name}'...")
    device = await BleakScanner.find_device_by_name(device_name, timeout=10)
    if device is None:
        raise RuntimeError(f"BLE device '{device_name}' not found")

    async with BleakClient(device) as client:
        print(f"Connected to {device.address}. Capturing {duration_s:.1f}s...")
        await client.start_notify(CHAR_UUID, on_notify)
        await asyncio.sleep(duration_s)
        await client.stop_notify(CHAR_UUID)

    rate = len(samples) / duration_s if duration_s > 0 else 0
    print(f"Captured {len(samples)} samples (~{rate:.1f} Hz)")
    return np.asarray(samples, dtype=float)


def capture(duration_s: float, device_name: str = DEVICE_NAME) -> np.ndarray:
    return asyncio.run(_capture(duration_s, device_name))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seconds", type=float, default=15.0)
    p.add_argument("--device", default=DEVICE_NAME)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    sig = capture(args.seconds, args.device)

    out = args.out or os.path.join(
        os.path.dirname(__file__), "data", f"ble_raw_{int(time.time())}.csv"
    )
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample", "ppg_raw"])
        for i, v in enumerate(sig):
            w.writerow([i, int(v)])
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()
