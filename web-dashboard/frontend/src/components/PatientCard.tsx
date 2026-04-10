import React from "react";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import SectionHeader from "./SectionHeader";

type Patient = {
    name: string;
    age: number;
    sex: string;
    id: string;
    height: string;
    weight: string;
};

const PatientCard: React.FC<{ patient: Patient }> = ({ patient }) => (
    <Card sx={{ height: "100%" }}>
        <CardContent sx={{ p: 2 }}>
            <SectionHeader icon={<PersonIcon sx={{ fontSize: 16 }} />} title="Patient Info" />
            <Box sx={{ mb: 1.5 }}>
                <Typography sx={{ fontSize: 16, fontWeight: 500, color: "#333333" }}>
                    {patient.name}
                </Typography>
                <Typography sx={{ fontSize: 12, color: "#777777" }}>
                    Patient ID: {patient.id}
                </Typography>
            </Box>
            <Stack spacing={0}>
                <Row label="Age" value={`${patient.age}`} />
                <Row label="Sex" value={patient.sex} />
                <Row label="Height" value={patient.height} />
                <Row label="Weight" value={patient.weight} />
            </Stack>
        </CardContent>
    </Card>
);

const Row: React.FC<{ label: string; value: string }> = ({ label, value }) => (
    <Box
        sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            py: 0.75,
            borderBottom: "1px solid #f0f0f0",
            "&:last-child": { borderBottom: "none" },
        }}
    >
        <Typography sx={{ fontSize: 12, color: "#777777" }}>{label}</Typography>
        <Typography sx={{ fontSize: 13, color: "#333333" }}>{value}</Typography>
    </Box>
);

export default PatientCard;
