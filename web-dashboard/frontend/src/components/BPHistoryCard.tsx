import React from "react";
import { Box, Card, CardContent, Typography } from "@mui/material";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import { LineChart } from "@mui/x-charts/LineChart";
import SectionHeader from "./SectionHeader";

type History = {
    times: string[];
    systolic: number[];
    diastolic: number[];
};

const SYS_COLOR = "#337ab7";
const DIA_COLOR = "#f0ad4e";

const BPHistoryCard: React.FC<{ history: History }> = ({ history }) => {
    return (
        <Card sx={{ height: "100%" }}>
            <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Box sx={{ flexGrow: 1 }}>
                        <SectionHeader
                            icon={<ShowChartIcon sx={{ fontSize: 16 }} />}
                            title="Blood Pressure History"
                        />
                    </Box>
                </Box>
                <Box sx={{ display: "flex", gap: 2, mb: 1, ml: 0.5 }}>
                    <LegendDot color={SYS_COLOR} label="Systolic" />
                    <LegendDot color={DIA_COLOR} label="Diastolic" />
                </Box>
                <Box>
                    <LineChart
                        height={240}
                        margin={{ left: 50, right: 20, top: 10, bottom: 30 }}
                        xAxis={[{ scaleType: "point", data: history.times }]}
                        series={[
                            {
                                data: history.systolic,
                                label: "Systolic",
                                color: SYS_COLOR,
                                showMark: true,
                            },
                            {
                                data: history.diastolic,
                                label: "Diastolic",
                                color: DIA_COLOR,
                                showMark: true,
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
                </Box>
            </CardContent>
        </Card>
    );
};

const LegendDot: React.FC<{ color: string; label: string }> = ({ color, label }) => (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.75 }}>
        <Box sx={{ width: 10, height: 10, bgcolor: color, borderRadius: "50%" }} />
        <Typography sx={{ fontSize: 11, color: "#555555" }}>{label}</Typography>
    </Box>
);

export default BPHistoryCard;
