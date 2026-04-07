import React, { useEffect, useState } from "react";
import axios from "axios";
import {
    AppBar,
    Toolbar,
    Typography,
    IconButton,
    Box,
    Avatar,
    Grid,
    Card,
    CardContent,
    Divider,
    Stack,
    Chip,
    useTheme,
} from "@mui/material";
import MonitorHeartIcon from "@mui/icons-material/MonitorHeart";
import FavoriteIcon from "@mui/icons-material/Favorite";
import PersonIcon from "@mui/icons-material/Person";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import { LineChart } from "@mui/x-charts/LineChart";

const patient = {
    name: "Jane Doe",
    age: 54,
    sex: "F",
    id: "P-00421",
    height: "165 cm",
    weight: "68 kg",
};

const currentBP = {
    systolic: 122,
    diastolic: 78,
    hr: 74,
    timestamp: "12:04:31",
};

const history = {
    times: ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00"],
    systolic: [118, 121, 125, 119, 122, 124, 120],
    diastolic: [76, 78, 80, 77, 78, 81, 79],
};

const classifyBP = (sys: number, dia: number) => {
    if (sys >= 140 || dia >= 90) return { label: "Hypertension", color: "error" as const };
    if (sys >= 130 || dia >= 80) return { label: "Elevated", color: "warning" as const };
    return { label: "Normal", color: "success" as const };
};

const initials = (name: string) => name.split(" ").map(n => n[0]).join("");

const App: React.FC = () => {
    const [message, setMessage] = useState<string>("");
    const theme = useTheme();
    const status = classifyBP(currentBP.systolic, currentBP.diastolic);

    useEffect(() => {
        axios.get("/api/")
            .then(response => setMessage(response.data.message))
            .catch(error => console.error("Error fetching data", error));
    }, []);

    return (
        <Box
            sx={{
                flexGrow: 1,
                display: "flex",
                flexDirection: "column",
                minHeight: "100svh",
                background:
                    "radial-gradient(1200px 600px at 10% -10%, rgba(91,141,239,0.18), transparent 60%), radial-gradient(900px 500px at 100% 0%, rgba(34,211,238,0.12), transparent 60%)",
            }}
        >
            <AppBar position="sticky">
                <Toolbar>
                    <IconButton size="large" edge="start" color="inherit" sx={{ mr: 1 }}>
                        <MonitorHeartIcon color="primary" />
                    </IconButton>
                    <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                        Monitoring Dashboard
                    </Typography>
                    <Chip
                        icon={<FiberManualRecordIcon sx={{ fontSize: 12 }} />}
                        label="LIVE"
                        size="small"
                        color="success"
                        variant="outlined"
                        sx={{ mr: 2, fontWeight: 600, letterSpacing: 0.5 }}
                    />
                    <Avatar sx={{ bgcolor: "primary.main", width: 36, height: 36 }} />
                </Toolbar>
            </AppBar>

            <Box sx={{ flexGrow: 1, p: { xs: 2, md: 4 } }}>
                {message && (
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ mb: 2, display: "block" }}
                    >
                        {message}
                    </Typography>
                )}

                <Grid container spacing={3}>
                    {/* Patient Info */}
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <Card sx={{ height: "100%" }}>
                            <CardContent sx={{ p: 3 }}>
                                <SectionHeader icon={<PersonIcon fontSize="small" />} title="Patient" />
                                <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 2 }}>
                                    <Avatar
                                        sx={{
                                            bgcolor: "primary.main",
                                            width: 56,
                                            height: 56,
                                            fontSize: 20,
                                            fontWeight: 600,
                                        }}
                                    >
                                        {initials(patient.name)}
                                    </Avatar>
                                    <Box>
                                        <Typography variant="h5">{patient.name}</Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            ID {patient.id}
                                        </Typography>
                                    </Box>
                                </Box>
                                <Divider sx={{ my: 2.5, borderColor: "rgba(255,255,255,0.06)" }} />
                                <Stack spacing={1.25}>
                                    <Row label="Age" value={`${patient.age}`} />
                                    <Row label="Sex" value={patient.sex} />
                                    <Row label="Height" value={patient.height} />
                                    <Row label="Weight" value={patient.weight} />
                                </Stack>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* Current Blood Pressure */}
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <Card sx={{ height: "100%" }}>
                            <CardContent sx={{ p: 3 }}>
                                <Box
                                    sx={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                    }}
                                >
                                    <SectionHeader
                                        icon={<FavoriteIcon fontSize="small" />}
                                        title="Blood Pressure"
                                    />
                                    <Chip
                                        label={status.label}
                                        color={status.color}
                                        size="small"
                                        sx={{ fontWeight: 600 }}
                                    />
                                </Box>
                                <Box
                                    sx={{
                                        display: "flex",
                                        alignItems: "baseline",
                                        justifyContent: "center",
                                        gap: 1,
                                        mt: 3,
                                    }}
                                >
                                    <Typography
                                        variant="h2"
                                        component="span"
                                        sx={{
                                            background: `linear-gradient(180deg, ${theme.palette.primary.light}, ${theme.palette.primary.main})`,
                                            WebkitBackgroundClip: "text",
                                            WebkitTextFillColor: "transparent",
                                        }}
                                    >
                                        {currentBP.systolic}
                                    </Typography>
                                    <Typography variant="h4" component="span" color="text.secondary">
                                        /
                                    </Typography>
                                    <Typography
                                        variant="h2"
                                        component="span"
                                        sx={{
                                            background: `linear-gradient(180deg, ${theme.palette.secondary.light}, ${theme.palette.secondary.main})`,
                                            WebkitBackgroundClip: "text",
                                            WebkitTextFillColor: "transparent",
                                        }}
                                    >
                                        {currentBP.diastolic}
                                    </Typography>
                                    <Typography variant="body1" color="text.secondary" sx={{ ml: 1 }}>
                                        mmHg
                                    </Typography>
                                </Box>
                                <Divider sx={{ my: 2, borderColor: "rgba(255,255,255,0.06)" }} />
                                <Box sx={{ display: "flex", justifyContent: "space-around" }}>
                                    <Stat label="Heart rate" value={`${currentBP.hr} bpm`} />
                                    <Stat label="Updated" value={currentBP.timestamp} />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>

                    {/* History */}
                    <Grid size={{ xs: 12, lg: 4 }}>
                        <Card sx={{ height: "100%" }}>
                            <CardContent sx={{ p: 3 }}>
                                <SectionHeader
                                    icon={<ShowChartIcon fontSize="small" />}
                                    title="BP History"
                                />
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
                                                showMark: false,
                                            },
                                            {
                                                data: history.diastolic,
                                                label: "Diastolic",
                                                color: theme.palette.secondary.main,
                                                curve: "monotoneX",
                                                showMark: false,
                                            },
                                        ]}
                                        sx={{
                                            "& .MuiChartsAxis-line, & .MuiChartsAxis-tick": {
                                                stroke: "rgba(255,255,255,0.2)",
                                            },
                                            "& .MuiChartsAxis-tickLabel": {
                                                fill: "rgba(255,255,255,0.6)",
                                            },
                                        }}
                                    />
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
};

const SectionHeader: React.FC<{ icon: React.ReactNode; title: string }> = ({ icon, title }) => (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1, color: "text.secondary" }}>
        {icon}
        <Typography variant="overline">{title}</Typography>
    </Box>
);

const Row: React.FC<{ label: string; value: string }> = ({ label, value }) => (
    <Box sx={{ display: "flex", justifyContent: "space-between" }}>
        <Typography variant="body2" color="text.secondary">
            {label}
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {value}
        </Typography>
    </Box>
);

const Stat: React.FC<{ label: string; value: string }> = ({ label, value }) => (
    <Box sx={{ textAlign: "center" }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: "block" }}>
            {label}
        </Typography>
        <Typography variant="body1" sx={{ fontWeight: 600 }}>
            {value}
        </Typography>
    </Box>
);

export default App;
