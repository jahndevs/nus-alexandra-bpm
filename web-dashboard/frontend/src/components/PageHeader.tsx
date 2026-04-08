import React from "react";
import { Box, Typography } from "@mui/material";
import { MONO } from "../theme";

type Props = { timestamp: string };

const PageHeader: React.FC<Props> = ({ timestamp }) => (
    <Box
        sx={{
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
            mb: 3,
            pb: 2,
            borderBottom: "1.5px solid",
            borderColor: "divider",
        }}
    >
        <Box>
            <Typography
                variant="caption"
                sx={{ fontFamily: MONO, color: "text.secondary", display: "block" }}
            >
                № 001 — REAL-TIME PATIENT VITALS
            </Typography>
            <Typography variant="h4" sx={{ mt: 0.5, fontWeight: 800, letterSpacing: "-0.03em" }}>
                Dashboard
                <Box component="span" sx={{ color: "secondary.main" }}>
                    .
                </Box>
            </Typography>
        </Box>
        <Typography
            variant="caption"
            sx={{
                fontFamily: MONO,
                color: "text.secondary",
                display: { xs: "none", sm: "block" },
            }}
        >
            {new Date().toISOString().slice(0, 10)} · {timestamp}
        </Typography>
    </Box>
);

export default PageHeader;
