import { createTheme } from "@mui/material";

export const MONO = '"JetBrains Mono", ui-monospace, Consolas, monospace';

export const theme = createTheme({
    palette: {
        mode: "light",
        primary: { main: "#1d4ed8", light: "#3b82f6", dark: "#1e3a8a" },   // blue (systolic)
        secondary: { main: "#ea580c", light: "#fb923c", dark: "#9a3412" }, // orange (diastolic)
        background: {
            default: "#f4f4f1", // warm paper gray
            paper: "#ffffff",
        },
        text: {
            primary: "#1a1a1a",
            secondary: "#6b6b6b",
        },
        divider: "#1a1a1a",
        success: { main: "#15803d" },
        warning: { main: "#c2410c" },
        error: { main: "#b91c1c" },
    },
    shape: { borderRadius: 0 },
    typography: {
        fontFamily: '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
        h2: { fontWeight: 800, letterSpacing: "-0.04em", fontFeatureSettings: '"tnum"' },
        h4: { fontWeight: 700, letterSpacing: "-0.02em" },
        h5: { fontWeight: 700, letterSpacing: "-0.01em" },
        overline: {
            letterSpacing: "0.18em",
            fontWeight: 700,
            fontSize: 11,
            fontFamily: MONO,
        },
        caption: {
            fontFamily: MONO,
            letterSpacing: "0.06em",
        },
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    backgroundColor: "#f4f4f1",
                    backgroundImage:
                        "linear-gradient(#e8e8e3 1px, transparent 1px), linear-gradient(90deg, #e8e8e3 1px, transparent 1px)",
                    backgroundSize: "32px 32px",
                    backgroundPosition: "-1px -1px",
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundColor: "#ffffff",
                    border: "1.5px solid #1a1a1a",
                    boxShadow: "6px 6px 0 0 #1a1a1a",
                    borderRadius: 0,
                    backgroundImage: "none",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: "#ffffff",
                    color: "#1a1a1a",
                    borderBottom: "1.5px solid #1a1a1a",
                    boxShadow: "none",
                    backgroundImage: "none",
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 0,
                    border: "1.5px solid #1a1a1a",
                    fontFamily: MONO,
                    letterSpacing: "0.08em",
                    textTransform: "uppercase",
                },
                outlined: {
                    backgroundColor: "#fff",
                },
            },
        },
        MuiAvatar: {
            styleOverrides: {
                root: {
                    border: "1.5px solid #1a1a1a",
                    borderRadius: 0,
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: "#1a1a1a",
                },
            },
        },
    },
});
