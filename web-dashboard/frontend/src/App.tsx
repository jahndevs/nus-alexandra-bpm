import React, { useEffect, useState } from "react";
import axios from "axios";
import { Box, Grid, Typography } from "@mui/material";
import DashboardHeader from "./components/DashboardHeader";
import PageHeader from "./components/PageHeader";
import PatientCard from "./components/PatientCard";
import BloodPressureCard from "./components/BloodPressureCard";
import BPHistoryCard from "./components/BPHistoryCard";
import PPGChartCard from "./components/PPGChartCard";
import PageAlert from "./components/PageAlert";
import { patient, currentBP, history } from "./mockData";

const App: React.FC = () => {
    const [message, setMessage] = useState<string>("");

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
                bgcolor: "#f5f5f5",
            }}
        >
            <DashboardHeader />

            <Box sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, maxWidth: 1280, width: "100%", mx: "auto" }}>
                <PageHeader timestamp={currentBP.timestamp} />

                <PageAlert
                    severity="warning"
                    title="High Blood Pressure Alert"
                    message="182/110 mmHg recorded 2 minutes ago. Attention required!"
                    details=""
                />

                {message && (
                    <Typography
                        variant="caption"
                        sx={{ mb: 2, display: "block", color: "#777777", fontSize: 11 }}
                    >
                        {message}
                    </Typography>
                )}

                <Grid container spacing={2}>
                    <Grid size={{ xs: 12 }}>
                        <PPGChartCard />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <PatientCard patient={patient} />
                    </Grid>
                    <Grid size={{ xs: 12, md: 6, lg: 4 }}>
                        <BloodPressureCard reading={currentBP} />
                    </Grid>
                    <Grid size={{ xs: 12, lg: 4 }}>
                        <BPHistoryCard history={history} />
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
};

export default App;
