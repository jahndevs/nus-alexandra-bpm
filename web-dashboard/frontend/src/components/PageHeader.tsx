import React from "react";
import { Box, Typography } from "@mui/material";

type Props = { timestamp: string };

const PageHeader: React.FC<Props> = ({ timestamp }) => (
    <Box
        sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            mb: 2.5,
            pb: 1.5,
            borderBottom: "1px solid #dddddd",
        }}
    >
        <Typography variant="h4" sx={{ fontWeight: 400, fontSize: 22, color: "#333333" }}>
            Patient Details
        </Typography>
        <Typography
            variant="caption"
            sx={{
                color: "#777777",
                fontSize: 12,
                display: { xs: "none", sm: "block" },
            }}
        >
            Last updated: 17/04/2026 14:35:22
        </Typography>
    </Box>
);

export default PageHeader;
