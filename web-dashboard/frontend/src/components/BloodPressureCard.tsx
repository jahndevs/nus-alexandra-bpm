import React from "react";
import { Box, Card, CardContent, Chip, Divider, Typography } from "@mui/material";
import FavoriteIcon from "@mui/icons-material/Favorite";
import SectionHeader from "./SectionHeader";
import { MONO } from "../theme";

type BPReading = {
    systolic: number;
    diastolic: number;
    hr: number;
    timestamp: string;
};

const classifyBP = (sys: number, dia: number) => {
    if (sys >= 140 || dia >= 90) return { label: "Hypertension", tone: "error" as const };
    if (sys >= 130 || dia >= 80) return { label: "Elevated", tone: "warning" as const };
    return { label: "Normal", tone: "success" as const };
};

const TONE_BG = { success: "#dcfce7", warning: "#ffedd5", error: "#fee2e2" };
const TONE_FG = { success: "#15803d", warning: "#c2410c", error: "#b91c1c" };

const BloodPressureCard: React.FC<{ reading: BPReading }> = ({ reading }) => {
    const status = classifyBP(reading.systolic, reading.diastolic);
    return (
        <Card
            sx={{
                height: "100%",
                position: "relative",
                overflow: "hidden",
                "&::before": {
                    content: '""',
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 6,
                    background:
                        "linear-gradient(90deg, #1d4ed8 0%, #3b82f6 50%, #fb923c 75%, #ea580c 100%)",
                },
            }}
        >
            <CardContent sx={{ p: 3, pt: 3.5 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <SectionHeader
                        index="02"
                        icon={<FavoriteIcon fontSize="small" />}
                        title="Blood Pressure"
                    />
                    <Chip
                        label={status.label}
                        size="small"
                        sx={{
                            fontWeight: 700,
                            bgcolor: TONE_BG[status.tone],
                            color: TONE_FG[status.tone],
                        }}
                    />
                </Box>
                <Box
                    sx={{
                        display: "flex",
                        alignItems: "baseline",
                        justifyContent: "center",
                        gap: 1,
                        mt: 3.5,
                        mb: 1,
                    }}
                >
                    <Typography
                        variant="h2"
                        component="span"
                        sx={{ color: "primary.main", fontSize: { xs: 64, md: 80 } }}
                    >
                        {reading.systolic}
                    </Typography>
                    <Typography
                        variant="h4"
                        component="span"
                        sx={{ color: "text.secondary", fontWeight: 300 }}
                    >
                        /
                    </Typography>
                    <Typography
                        variant="h2"
                        component="span"
                        sx={{ color: "secondary.main", fontSize: { xs: 64, md: 80 } }}
                    >
                        {reading.diastolic}
                    </Typography>
                </Box>
                <Typography
                    variant="caption"
                    sx={{
                        display: "block",
                        textAlign: "center",
                        fontFamily: MONO,
                        color: "text.secondary",
                        mb: 1,
                    }}
                >
                    mmHg · sys / dia
                </Typography>
                <Divider sx={{ my: 2, borderStyle: "dashed" }} />
                <Box sx={{ display: "flex", justifyContent: "space-around" }}>
                    <Stat label="Heart rate" value={`${reading.hr}`} unit="bpm" />
                    <Stat label="Updated" value={reading.timestamp} />
                </Box>
            </CardContent>
        </Card>
    );
};

const Stat: React.FC<{ label: string; value: string; unit?: string }> = ({ label, value, unit }) => (
    <Box sx={{ textAlign: "center" }}>
        <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: "block", fontFamily: MONO, textTransform: "uppercase" }}
        >
            {label}
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: 700, fontFamily: MONO, mt: 0.5 }}>
            {value}
            {unit && (
                <Box component="span" sx={{ ml: 0.5, fontSize: 11, color: "text.secondary" }}>
                    {unit}
                </Box>
            )}
        </Typography>
    </Box>
);

export default BloodPressureCard;
