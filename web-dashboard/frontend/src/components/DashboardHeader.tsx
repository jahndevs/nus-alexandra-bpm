import React from "react";
import { AppBar, Toolbar, Typography, IconButton, Box, Avatar, Chip } from "@mui/material";
import MonitorHeartIcon from "@mui/icons-material/MonitorHeart";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import { MONO } from "../theme";

const DashboardHeader: React.FC = () => (
    <AppBar position="sticky">
        <Toolbar sx={{ gap: 1 }}>
            <IconButton size="large" edge="start" sx={{ mr: 1, color: "primary.main" }}>
                <MonitorHeartIcon />
            </IconButton>
            <Box sx={{ flexGrow: 1, display: "flex", alignItems: "baseline", gap: 1.5 }}>
                <Typography
                    variant="h6"
                    component="div"
                    sx={{ fontWeight: 800, letterSpacing: "-0.02em" }}
                >
                    BPM
                </Typography>
                <Typography
                    variant="caption"
                    sx={{
                        fontFamily: MONO,
                        color: "text.secondary",
                        textTransform: "uppercase",
                    }}
                >
                    / monitoring · ward 7
                </Typography>
            </Box>
            <Chip
                icon={
                    <FiberManualRecordIcon
                        sx={{
                            fontSize: 10,
                            color: "#15803d !important",
                            animation: "livePulse 1.4s ease-in-out infinite",
                            borderRadius: "50%",
                            "@keyframes livePulse": {
                                "0%, 100%": {
                                    opacity: 1,
                                    filter: "drop-shadow(0 0 0 rgba(21,128,61,0.7))",
                                },
                                "50%": {
                                    opacity: 0.55,
                                    filter: "drop-shadow(0 0 6px rgba(21,128,61,0.9))",
                                },
                            },
                        }}
                    />
                }
                label="LIVE"
                size="small"
                sx={{ mr: 2, fontWeight: 700, bgcolor: "#fff" }}
            />
            <Avatar
                sx={{
                    bgcolor: "primary.main",
                    color: "#fff",
                    width: 36,
                    height: 36,
                    fontFamily: MONO,
                    fontSize: 13,
                    fontWeight: 700,
                }}
            >
                JR
            </Avatar>
        </Toolbar>
    </AppBar>
);

export default DashboardHeader;
