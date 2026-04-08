import React, { useEffect, useState } from "react";
import axios from "axios";
import { Box, Grid, Typography } from "@mui/material";
import DashboardHeader from "./components/DashboardHeader";
import PageHeader from "./components/PageHeader";
import PatientCard from "./components/PatientCard";
import BloodPressureCard from "./components/BloodPressureCard";
import BPHistoryCard from "./components/BPHistoryCard";
import { patient, currentBP, history } from "./mockData";
import { MONO } from "./theme";

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
            }}
        >
            <DashboardHeader />

            <Box sx={{ flexGrow: 1, p: { xs: 2, md: 4 }, maxWidth: 1400, width: "100%", mx: "auto" }}>
                <PageHeader timestamp={currentBP.timestamp} />

                {message && (
                    <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ mb: 2, display: "block", fontFamily: MONO }}
                    >
                        ↳ {message}
                    </Typography>
                )}

                <Grid container spacing={4}>
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
