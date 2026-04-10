from collections import deque
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

PPG_BUFFER_SIZE = 200
latest_reading = {"raw": 0}
ppg_buffer: deque[int] = deque(maxlen=PPG_BUFFER_SIZE)


class PPGReading(BaseModel):
    raw: int


@app.get("/api/")
async def root():
    return {"message": "Hello Frontend!"}


@app.post("/api/ppg")
async def receive_ppg(reading: PPGReading):
    latest_reading["raw"] = reading.raw
    ppg_buffer.append(reading.raw)
    return {"status": "ok"}


@app.get("/api/ppg/latest")
async def get_ppg():
    return latest_reading


@app.get("/api/ppg/buffer")
async def get_ppg_buffer():
    return {"values": list(ppg_buffer)}
