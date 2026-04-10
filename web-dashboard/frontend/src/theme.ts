import { createTheme } from "@mui/material";

// Kept as a no-op alias so existing imports keep working.
// In the flat 2015-era look we just use the regular sans-serif everywhere.
export const MONO = '"Helvetica Neue", Helvetica, Arial, sans-serif';

export const theme = createTheme({
    palette: {
        mode: "light",
        primary: { main: "#337ab7", light: "#5bc0de", dark: "#286090" },   // bootstrap 3 blue
        secondary: { main: "#f0ad4e", light: "#f7c171", dark: "#ec971f" }, // bootstrap 3 warning
        background: {
            default: "#f5f5f5",
            paper: "#ffffff",
        },
        text: {
            primary: "#333333",
            secondary: "#777777",
        },
        divider: "#dddddd",
        success: { main: "#5cb85c" },
        warning: { main: "#f0ad4e" },
        error: { main: "#d9534f" },
    },
    shape: { borderRadius: 3 },
    typography: {
        fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
        fontSize: 13,
        h2: { fontWeight: 400, letterSpacing: 0 },
        h4: { fontWeight: 400, letterSpacing: 0 },
        h5: { fontWeight: 500, letterSpacing: 0, fontSize: 16 },
        h6: { fontWeight: 500, letterSpacing: 0, fontSize: 15 },
        overline: {
            letterSpacing: "0.04em",
            fontWeight: 700,
            fontSize: 12,
            textTransform: "uppercase",
        },
        caption: {
            fontSize: 12,
            letterSpacing: 0,
        },
        button: {
            textTransform: "none",
            fontWeight: 400,
        },
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: {
                body: {
                    backgroundColor: "#f5f5f5",
                    backgroundImage: "none",
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundColor: "#ffffff",
                    border: "1px solid #dddddd",
                    boxShadow: "none",
                    borderRadius: 3,
                    backgroundImage: "none",
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundColor: "#2c3e50",
                    color: "#ffffff",
                    borderBottom: "1px solid #1f2d3d",
                    boxShadow: "none",
                    backgroundImage: "none",
                },
            },
        },
        MuiChip: {
            styleOverrides: {
                root: {
                    borderRadius: 3,
                    border: "1px solid #cccccc",
                    fontWeight: 400,
                    letterSpacing: 0,
                    textTransform: "none",
                    height: 22,
                    fontSize: 11,
                },
                outlined: {
                    backgroundColor: "#ffffff",
                },
            },
        },
        MuiAvatar: {
            styleOverrides: {
                root: {
                    border: "none",
                    borderRadius: "50%",
                },
            },
        },
        MuiDivider: {
            styleOverrides: {
                root: {
                    borderColor: "#eeeeee",
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: "none",
                },
            },
        },
    },
});
