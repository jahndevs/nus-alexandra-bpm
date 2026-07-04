import asyncio
import json
import os
import sys
from collections import deque

import numpy as np
import websockets
from bleak import BleakClient, BleakScanner

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ML_DIR = os.path.join(ROOT, "ml")
sys.path.insert(0, ML_DIR)

from heart_rate import compute_hr
from loaders.long_capture import extract_windows_at_bp, load_long_capture
from models.cnn_anchor import _AnchorWrapper
from preprocessing.process import preprocess

DEVICE_NAME = "XIAO Sensor"
CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
FS = 125
SAMPLE_BYTES = 2  # firmware sends uint16 little-endian samples
WINDOW_SECONDS = 10
PPG_BUFFER_SIZE = FS * WINDOW_SECONDS
PREDICT_INTERVAL = 2.0
MIN_PREDICT_SAMPLES = FS * 4

MODEL_FILE = os.path.join(ML_DIR, "models", "cnn_anchor.pt")
ANCHOR_PPG_CSV = os.path.join(ML_DIR, "long_capture", "ppg.csv")
ANCHOR_BP_CSV = os.path.join(ML_DIR, "long_capture", "bp.csv")
# index into the BP records in bp.csv to use as the calibration anchor
ANCHOR_INDEX = 0


def build_anchor():
    ppg, t_ppg, bp_records = load_long_capture(ANCHOR_PPG_CSV, ANCHOR_BP_CSV)
    windows, bps, _ = extract_windows_at_bp(ppg, t_ppg, bp_records, fs=FS, window_s=WINDOW_SECONDS)
    if len(windows) == 0:
        raise RuntimeError("no anchor windows extracted from long_capture")
    raw_window = windows[ANCHOR_INDEX]
    anchor_signal = preprocess(raw_window, FS).astype(np.float32)
    anchor_bp = bps[ANCHOR_INDEX].astype(np.float32)
    return anchor_signal, anchor_bp


print(f"Loading anchor CNN: {MODEL_FILE}")
model = _AnchorWrapper.load(MODEL_FILE)
print("Building calibration anchor from long_capture...")
ANCHOR_SIGNAL, ANCHOR_BP = build_anchor()
print(f"Anchor cuff BP: {ANCHOR_BP[0]:.0f}/{ANCHOR_BP[1]:.0f} mmHg")

ppg_buffer: deque[int] = deque(maxlen=PPG_BUFFER_SIZE)
connected_clients = set()


async def broadcast(msg: dict):
    if connected_clients:
        text = json.dumps(msg)
        await asyncio.gather(*[client.send(text) for client in connected_clients])


def handle_notification(_sender, data):
    n = len(data) // SAMPLE_BYTES
    samples = [
        int.from_bytes(data[i * SAMPLE_BYTES : (i + 1) * SAMPLE_BYTES], "little")
        for i in range(n)
    ]
    if not samples:
        return
    ppg_buffer.extend(samples)
    print(f"[ppg] raw={samples[-1]} buffer_size={len(ppg_buffer)}")
    asyncio.get_event_loop().create_task(
        broadcast({"type": "ppg", "raw": samples[-1], "buffer": list(ppg_buffer)})
    )


def predict_bp(signal):
    clean = preprocess(signal, FS).astype(np.float32)
    if len(clean) != len(ANCHOR_SIGNAL):
        # CNN expects a fixed window length; pad/trim to anchor length
        if len(clean) > len(ANCHOR_SIGNAL):
            clean = clean[-len(ANCHOR_SIGNAL):]
        else:
            pad = np.zeros(len(ANCHOR_SIGNAL) - len(clean), dtype=np.float32)
            clean = np.concatenate([pad, clean])
    return model.predict_one(clean, ANCHOR_SIGNAL, ANCHOR_BP)


async def predict_task():
    print("[predict] task started")
    while True:
        await asyncio.sleep(PREDICT_INTERVAL)
        n = len(ppg_buffer)
        if n < MIN_PREDICT_SAMPLES:
            print(f"[predict] buffer too small ({n}/{MIN_PREDICT_SAMPLES})")
            continue
        signal = np.asarray(ppg_buffer, dtype=float)
        try:
            sbp, dbp = await asyncio.to_thread(predict_bp, signal)
            hr = await asyncio.to_thread(compute_hr, signal, FS)
        except Exception as e:
            print(f"[predict] error: {e}")
            continue

        frame: dict = {"type": "bp", "sbp": float(sbp), "dbp": float(dbp)}
        if hr is not None:
            frame["hr"] = hr

        parts = [f"BP {frame['sbp']:.0f}/{frame['dbp']:.0f}"]
        if "hr" in frame:
            parts.append(f"HR {frame['hr']:.0f}")
        print(f"[predict] {' | '.join(parts)} -> {len(connected_clients)} clients")
        await broadcast(frame)


async def ble_task():
    while True:
        try:
            print("Scanning for XIAO...")
            device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10)
            if not device:
                print("Not found, retrying...")
                await asyncio.sleep(3)
                continue
            async with BleakClient(device) as client:
                print("BLE connected!")
                await client.start_notify(CHAR_UUID, handle_notification)
                while client.is_connected:
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"BLE error: {e}, retrying in 3s...")
            await asyncio.sleep(3)


async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"Dashboard connected ({len(connected_clients)} clients)")
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.discard(websocket)


async def main():
    print(f"Starting server | model={MODEL_FILE} | fs={FS} | buffer={PPG_BUFFER_SIZE}")
    tasks = [asyncio.create_task(ble_task()), asyncio.create_task(predict_task())]
    async with websockets.serve(ws_handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.gather(*tasks)


asyncio.run(main())
