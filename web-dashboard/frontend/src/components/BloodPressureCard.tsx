import React from "react";
import { Box, Card, CardContent, Typography } from "@mui/material";
import SectionHeader from "./SectionHeader";

type BPReading = {
    systolic: number;
    diastolic: number;
    hr: number;
    timestamp: string;
};

const classifyBP = (sys: number, dia: number) => {
    if (sys >= 140 || dia >= 90) return { label: "High", tone: "error" as const };
    if (sys >= 130 || dia >= 80) return { label: "Elevated", tone: "warning" as const };
    return { label: "Normal", tone: "success" as const };
};

const TONE_BG = { success: "#dff0d8", warning: "#fcf8e3", error: "#f2dede" };
const TONE_FG = { success: "#3c763d", warning: "#8a6d3b", error: "#a94442" };
const TONE_BORDER = { success: "#d6e9c6", warning: "#faebcc", error: "#ebccd1" };

const BloodPressureCard: React.FC<{ reading: BPReading }> = ({ reading }) => {
    const status = classifyBP(reading.systolic, reading.diastolic);
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
                        {reading.systolic}
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
                        {reading.diastolic}
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
                            {reading.hr}
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
