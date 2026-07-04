import React, { useEffect, useRef, useState } from "react";
import { Box, Card, CardContent, Typography } from "@mui/material";
import SectionHeader from "./SectionHeader";
import { RoundaboutLeftSharp } from "@mui/icons-material";

type BPReading = {
    systolic: number;
    diastolic: number;
    hr: number;
    timestamp: string;
};

const WS_URL = "ws://localhost:8765";
const RECONNECT_DELAY = 2000;

const classifyBP = (sys: number, dia: number) => {
    if (sys >= 140 || dia >= 90) return { label: "High", tone: "error" as const };
    if (sys >= 130 || dia >= 80) return { label: "Elevated", tone: "warning" as const };
    return { label: "Normal", tone: "success" as const };
};

const TONE_BG = { success: "#dff0d8", warning: "#fcf8e3", error: "#f2dede" };
const TONE_FG = { success: "#3c763d", warning: "#8a6d3b", error: "#a94442" };
const TONE_BORDER = { success: "#d6e9c6", warning: "#faebcc", error: "#ebccd1" };

const PPG_LOW_THRESHOLD = 1000;
const OFF_WRIST_MS = 3000;

const BloodPressureCard: React.FC<{ reading: BPReading }> = ({ reading }) => {
    const [live, setLive] = useState<{ sbp?: number; dbp?: number; hr?: number }>({});
    const [detected, setDetected] = useState(true);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectRef = useRef<number | null>(null);
    const closedRef = useRef(false);
    const lowSinceRef = useRef<number | null>(null);

    useEffect(() => {
        closedRef.current = false;
        const connect = () => {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);

                    // off-wrist detection from raw PPG samples
                    if (msg.type === "ppg" && typeof msg.raw === "number") {
                        const now = Date.now();
                        if (msg.raw < PPG_LOW_THRESHOLD) {
                            if (lowSinceRef.current === null) lowSinceRef.current = now;
                            if (now - lowSinceRef.current >= OFF_WRIST_MS) setDetected(false);
                        } else {
                            lowSinceRef.current = null;
                            setDetected(true);
                        }
                    }

                    if (msg.type !== "bp") return;
                    setLive((prev) => ({
                        sbp: typeof msg.sbp === "number" ? msg.sbp : prev.sbp,
                        dbp: typeof msg.dbp === "number" ? msg.dbp : prev.dbp,
                        hr: typeof msg.hr === "number" ? msg.hr : prev.hr,
                    }));
                } catch {}
            };

            ws.onclose = () => {
                if (closedRef.current) return;
                reconnectRef.current = window.setTimeout(connect, RECONNECT_DELAY);
            };

            ws.onerror = () => {
                ws.close();
            };
        };

        connect();

        return () => {
            closedRef.current = true;
            if (reconnectRef.current !== null) window.clearTimeout(reconnectRef.current);
            wsRef.current?.close();
        };
    }, []);

    const systolic = live.sbp !== undefined ? Math.round(live.sbp) : reading.systolic;
    const diastolic = live.dbp !== undefined ? Math.round(live.dbp) : reading.diastolic;
    const hr = live.hr !== undefined ? Math.round(live.hr) : reading.hr;
    const status = classifyBP(systolic, diastolic);

    if (!detected) {
        return (
            <Card sx={{ height: "100%" }}>
                <CardContent sx={{ p: 2 }}>
                    <SectionHeader title="Blood Pressure" />
                    <Box
                        sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            justifyContent: "center",
                            py: 6,
                            color: "#999",
                        }}
                    >
                        <Typography sx={{ fontSize: 40, mb: 1 }}>--/--</Typography>
                        <Typography sx={{ fontSize: 13 }}>
                            No human detected
                        </Typography>
                    </Box>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card sx={{ height: "100%" }}>
            <CardContent sx={{ p: 2 }}>
                <SectionHeader title="Blood Pressure" />
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "baseline",
                        justifyContent: "center",
                        gap: 1,
                        mt: 2,
                        mb: 0.5,
                    }}
                >
                    <Typography
                        component="span"
                        sx={{ color: "#333333", fontSize: 56, fontWeight: 300, lineHeight: 1 }}
                    >
                        {systolic}
                    </Typography>
                    <Typography
                        component="span"
                        sx={{ color: "#999999", fontSize: 32, fontWeight: 300 }}
                    >
                        /
                    </Typography>
                    <Typography
                        component="span"
                        sx={{ color: "#333333", fontSize: 56, fontWeight: 300, lineHeight: 1 }}
                    >
                        {diastolic}
                    </Typography>
                </Box>
                <Typography
                    sx={{
                        display: "block",
                        textAlign: "center",
                        fontSize: 11,
                        color: "#777777",
                        mb: 1.5,
                    }}
                >
                    mmHg (systolic / diastolic)
                </Typography>
                <Box
                    sx={{
                        textAlign: "center",
                        py: 0.5,
                        mb: 1.5,
                        bgcolor: TONE_BG[status.tone],
                        color: TONE_FG[status.tone],
                        border: `1px solid ${TONE_BORDER[status.tone]}`,
                        borderRadius: "3px",
                        fontSize: 12,
                    }}
                >
                    Status: {status.label}
                </Box>
                <Box
                    sx={{
                        borderTop: "1px solid #eeeeee",
                        pt: 1,
                    }}
                >
                    <SectionHeader title="Heart Rate" />
                    <Box
                        sx={{
                            display: "flex",
                            alignItems: "baseline",
                            justifyContent: "center",
                            gap: 1,
                            mt: 2,
                            mb: 0.5,
                        }}
                    >
                        <Typography
                            component="span"
                            sx={{ color: "#333333", fontSize: 56, fontWeight: 300, lineHeight: 1 }}
                        >
                            {Math.round(hr / 2.3)}
                        </Typography>
                    </Box>
                    <Typography
                        sx={{
                            display: "block",
                            textAlign: "center",
                            fontSize: 11,
                            color: "#777777",
                        }}
                    >
                        bpm
                    </Typography>
                </Box>
            </CardContent>
        </Card>
    );
};

export default BloodPressureCard;
