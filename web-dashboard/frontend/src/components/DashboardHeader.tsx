import React from "react";
import { AppBar, Toolbar, Typography, Box, Avatar } from "@mui/material";

const DashboardHeader: React.FC = () => (
    <AppBar position="sticky">
        <Toolbar variant="dense" sx={{ minHeight: 44 }}>
            <Typography
                variant="h6"
                component="div"
                sx={{ fontWeight: 500, fontSize: 16, mr: 3, lineHeight: 1 }}
            >
                Alexandra Hospital
            </Typography>
            <Box sx={{ flexGrow: 1, display: "flex", alignItems: "center", gap: 3 }}>
                <Typography variant="body2" sx={{ color: "#bdc3c7", fontSize: 13, lineHeight: 1 }}>
                    Ward Level 1
                </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
                <Box
                    sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        bgcolor: "#5cb85c",
                        animation: "pulse 1.5s ease-in-out infinite",
                        "@keyframes pulse": {
                            "0%, 100%": {
                                opacity: 1,
                                boxShadow: "0 0 0 0 rgba(92, 184, 92, 0.7)",
                            },
                            "50%": {
                                opacity: 0.6,
                                boxShadow: "0 0 0 6px rgba(92, 184, 92, 0)",
                            },
                        },
                    }}
                />
                <Typography variant="body2" sx={{ color: "#ecf0f1", fontSize: 12, mr: 2 }}>
                    Live
                </Typography>
                <Avatar
                    sx={{
                        bgcolor: "#34495e",
                        color: "#ffffff",
                        width: 28,
                        height: 28,
                        fontSize: 12,
                        fontWeight: 400,
                    }}
                >
                    JR
                </Avatar>
            </Box>
        </Toolbar>
    </AppBar>
);

export default DashboardHeader;
