import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Box, Card, CardContent, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import SectionHeader from "./SectionHeader";

const PPG_COLOR = "#e74c3c";
const POLL_INTERVAL = 100;

const PPGChartCard: React.FC = () => {
    const [values, setValues] = useState<number[]>([]);
    const intervalRef = useRef<number | null>(null);

    useEffect(() => {
        const fetchBuffer = () => {
            axios
                .get("/api/ppg/buffer")
                .then((res) => {
                    const buf: number[] = res.data.values;
                    if (buf.length > 0) {
                        setValues(buf);
                    }
                })
                .catch(() => {});
        };

        fetchBuffer();
        intervalRef.current = window.setInterval(fetchBuffer, POLL_INTERVAL);

        return () => {
            if (intervalRef.current !== null) window.clearInterval(intervalRef.current);
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
