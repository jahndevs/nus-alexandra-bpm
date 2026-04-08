import React from "react";
import { Box, Card, CardContent, Typography, useTheme } from "@mui/material";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import { LineChart } from "@mui/x-charts/LineChart";
import SectionHeader from "./SectionHeader";
import { MONO } from "../theme";

type History = {
    times: string[];
    systolic: number[];
    diastolic: number[];
};

const BPHistoryCard: React.FC<{ history: History }> = ({ history }) => {
    const theme = useTheme();
    return (
        <Card sx={{ height: "100%" }}>
            <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <SectionHeader
                        index="03"
                        icon={<ShowChartIcon fontSize="small" />}
                        title="BP History"
                    />
                    <Box sx={{ display: "flex", gap: 1.5 }}>
                        <LegendDot color={theme.palette.primary.main} label="SYS" />
                        <LegendDot color={theme.palette.secondary.main} label="DIA" />
                    </Box>
                </Box>
                <Box sx={{ mt: 1 }}>
                    <LineChart
                        height={260}
                        margin={{ left: 50, right: 20, top: 20, bottom: 30 }}
                        xAxis={[{ scaleType: "point", data: history.times }]}
                        series={[
                            {
                                data: history.systolic,
                                label: "Systolic",
                                color: theme.palette.primary.main,
                                curve: "monotoneX",
                                showMark: true,
                            },
                            {
                                data: history.diastolic,
                                label: "Diastolic",
                                color: theme.palette.secondary.main,
                                curve: "monotoneX",
                                showMark: true,
                            },
                        ]}
                        slotProps={{ legend: { hidden: true } as never }}
                        sx={{
                            "& .MuiChartsAxis-line, & .MuiChartsAxis-tick": {
                                stroke: "#1a1a1a",
                            },
                            "& .MuiChartsAxis-tickLabel": {
                                fill: "#6b6b6b",
                                fontFamily: MONO,
                                fontSize: 11,
                            },
                            "& .MuiLineElement-root": {
                                strokeWidth: 2,
                            },
                        }}
                    />
                </Box>
            </CardContent>
        </Card>
    );
};

const LegendDot: React.FC<{ color: string; label: string }> = ({ color, label }) => (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
        <Box sx={{ width: 10, height: 10, bgcolor: color, border: "1.5px solid #1a1a1a" }} />
        <Typography
            variant="caption"
            sx={{ fontFamily: MONO, fontSize: 10, fontWeight: 700, color: "text.primary" }}
        >
            {label}
        </Typography>
    </Box>
);

export default BPHistoryCard;
