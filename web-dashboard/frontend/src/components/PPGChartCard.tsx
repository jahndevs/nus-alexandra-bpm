import React, { useEffect, useState, useRef } from "react";
import { Box, Card, CardContent, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import SectionHeader from "./SectionHeader";

const PPG_COLOR = "#e74c3c";
const WS_URL = "ws://localhost:8765";
const RECONNECT_DELAY = 2000;

const PPGChartCard: React.FC = () => {
    const [values, setValues] = useState<number[]>([]);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectRef = useRef<number | null>(null);
    const closedRef = useRef(false);

    useEffect(() => {
        closedRef.current = false;
        const connect = () => {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            ws.onmessage = (event) => {
                try {
                    const msg = JSON.parse(event.data);
                    if (Array.isArray(msg.buffer)) {
                        setValues(msg.buffer);
                    }
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

    const xLabels = values.map((_, i) => i);

    return (
        <Card sx={{ height: "100%" }}>
            <CardContent sx={{ p: 2 }}>
                <SectionHeader
                    title="Live PPG Signal"
                />
                {values.length > 0 && (
                    <Typography
                        variant="h4"
                        sx={{ fontWeight: 700, color: PPG_COLOR, mb: 1 }}
                    >
                        {values[values.length - 1]}
                    </Typography>
                )}
                <Box>
                    {values.length > 1 ? (
                        <LineChart
                            height={280}
                            margin={{ left: 50, right: 20, top: 10, bottom: 30 }}
                            skipAnimation
                            xAxis={[
                                {
                                    scaleType: "point",
                                    data: xLabels,
                                    tickLabelStyle: { display: "none" },
                                },
                            ]}
                            series={[
                                {
                                    data: values,
                                    label: "Raw PPG",
                                    color: PPG_COLOR,
                                    showMark: false,
                                },
                            ]}
                            slotProps={{ legend: { hidden: true } as never }}
                            sx={{
                                "& .MuiChartsAxis-line, & .MuiChartsAxis-tick": {
                                    stroke: "#cccccc",
                                },
                                "& .MuiChartsAxis-tickLabel": {
                                    fill: "#777777",
                                    fontSize: 11,
                                },
                                "& .MuiLineElement-root": {
                                    strokeWidth: 1.5,
                                },
                            }}
                        />
                    ) : (
                        <Box
                            sx={{
                                height: 280,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                color: "#999",
                                fontSize: 13,
                            }}
                        >
                            Waiting for PPG data...
                        </Box>
                    )}
                </Box>
            </CardContent>
        </Card>
    );
};

export default PPGChartCard;
