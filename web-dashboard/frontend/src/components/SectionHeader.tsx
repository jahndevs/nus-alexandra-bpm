import React from "react";
import { Box, Typography } from "@mui/material";
import { MONO } from "../theme";

type Props = { index?: string; icon: React.ReactNode; title: string };

const SectionHeader: React.FC<Props> = ({ index, icon, title }) => (
    <Box sx={{ display: "flex", alignItems: "center", gap: 1, color: "text.secondary" }}>
        {index && (
            <Box
                sx={{
                    fontFamily: MONO,
                    fontSize: 11,
                    fontWeight: 700,
                    color: "text.primary",
                    border: "1.5px solid",
                    borderColor: "text.primary",
                    px: 0.75,
                    py: 0.1,
                }}
            >
                {index}
            </Box>
        )}
        {icon}
        <Typography variant="overline">{title}</Typography>
    </Box>
);

export default SectionHeader;
