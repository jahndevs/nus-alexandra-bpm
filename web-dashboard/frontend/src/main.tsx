import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import './index.css'
import App from './App.tsx'

const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: { main: '#5b8def' },
        secondary: { main: '#22d3ee' },
        background: {
            default: '#0b1020',
            paper: '#141a2e',
        },
        success: { main: '#22c55e' },
        warning: { main: '#f59e0b' },
        error: { main: '#ef4444' },
    },
    shape: { borderRadius: 14 },
    typography: {
        fontFamily: '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
        h2: { fontWeight: 700, letterSpacing: '-0.02em' },
        h5: { fontWeight: 600 },
        overline: { letterSpacing: '0.12em', fontWeight: 600 },
    },
    components: {
        MuiCard: {
            styleOverrides: {
                root: {
                    backgroundImage:
                        'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0) 100%)',
                    border: '1px solid rgba(255,255,255,0.06)',
                    boxShadow:
                        '0 10px 30px -12px rgba(0,0,0,0.6), 0 2px 6px rgba(0,0,0,0.25)',
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                    backgroundColor: 'rgba(11,16,32,0.85)',
                    backdropFilter: 'blur(12px)',
                    borderBottom: '1px solid rgba(255,255,255,0.06)',
                    boxShadow: 'none',
                },
            },
        },
    },
})

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <App />
        </ThemeProvider>
    </StrictMode>,
)
