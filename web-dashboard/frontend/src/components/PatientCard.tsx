import React from "react";
import { Avatar, Box, Card, CardContent, Divider, Stack, Typography } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import SectionHeader from "./SectionHeader";
import { MONO } from "../theme";

type Patient = {
    name: string;
    age: number;
    sex: string;
    id: string;
    height: string;
    weight: string;
};

const initials = (name: string) => name.split(" ").map(n => n[0]).join("");

const PatientCard: React.FC<{ patient: Patient }> = ({ patient }) => (
    <Card sx={{ height: "100%" }}>
        <CardContent sx={{ p: 3 }}>
            <SectionHeader index="01" icon={<PersonIcon fontSize="small" />} title="Patient" />
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 2.5 }}>
                <Avatar
                    sx={{
                        bgcolor: "background.default",
                        color: "text.primary",
                        width: 56,
                        height: 56,
                        fontSize: 18,
                        fontWeight: 800,
                        fontFamily: MONO,
                    }}
                >
                    {initials(patient.name)}
                </Avatar>
                <Box>
                    <Typography variant="h5">{patient.name}</Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ fontFamily: MONO }}>
                        ID · {patient.id}
                    </Typography>
                </Box>
            </Box>
            <Divider sx={{ my: 2.5, borderStyle: "dashed" }} />
            <Stack spacing={1.25}>
                <Row label="Age" value={`${patient.age}`} />
                <Row label="Sex" value={patient.sex} />
                <Row label="Height" value={patient.height} />
                <Row label="Weight" value={patient.weight} />
            </Stack>
        </CardContent>
    </Card>
);

const Row: React.FC<{ label: string; value: string }> = ({ label, value }) => (
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 1 }}>
        <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontFamily: MONO, textTransform: "uppercase" }}
        >
            {label}
        </Typography>
        <Box
            sx={{
                flexGrow: 1,
                borderBottom: "1px dotted",
                borderColor: "text.secondary",
                mx: 1,
                mb: 0.4,
            }}
        />
        <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: MONO }}>
            {value}
        </Typography>
    </Box>
);

export default PatientCard;
