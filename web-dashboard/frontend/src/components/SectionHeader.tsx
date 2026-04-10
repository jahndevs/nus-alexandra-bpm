import React from "react";
import { Box, Typography } from "@mui/material";

type Props = { index?: string; icon?: React.ReactNode; title: string };

const SectionHeader: React.FC<Props> = ({ icon, title }) => (
    <Box
        sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            color: "#555555",
            pb: 1,
            borderBottom: "1px solid #eeeeee",
            mb: 1.5,
        }}
    >
        {icon}
        <Typography
            sx={{
                fontSize: 13,
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.02em",
                color: "#555555",
            }}
        >
            {title}
        </Typography>
    </Box>
);

export default SectionHeader;
