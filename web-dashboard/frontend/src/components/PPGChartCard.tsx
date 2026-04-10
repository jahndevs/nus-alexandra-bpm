import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Box, Card, CardContent } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import SectionHeader from "./SectionHeader";

const PPG_COLOR = "#e74c3c";
const POLL_INTERVAL = 100;
const MAX_POINTS = 200;

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
                        setValues(buf.slice(-MAX_POINTS));
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
                    title="Raw PPG Signal"
                />
                <Box>
                    {values.length > 1 ? (
                        <LineChart
                            height={280}
                            margin={{ left: 50, right: 20, top: 10, bottom: 30 }}
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
