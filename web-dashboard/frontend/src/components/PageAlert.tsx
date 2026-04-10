import React, { useState } from "react";
import { Alert, AlertTitle, Collapse, IconButton, Box } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";

type Severity = "error" | "warning" | "info" | "success";

interface PageAlertProps {
    severity?: Severity;
    title: string;
    message: string;
    details?: string;
}

const PageAlert: React.FC<PageAlertProps> = ({
    severity = "warning",
    title,
    message,
    details,
}) => {
    const [open, setOpen] = useState(true);
    const [expanded, setExpanded] = useState(false);

    return (
        <Collapse in={open}>
            <Alert
                severity={severity}
                variant="filled"
                sx={{ mb: 2, alignItems: "flex-start" }}
                action={
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                        {details && (
                            <IconButton
                                size="small"
                                color="inherit"
                                onClick={() => setExpanded((v) => !v)}
                                aria-label={expanded ? "collapse details" : "expand details"}
                            >
                                {expanded ? (
                                    <ExpandLessIcon fontSize="small" />
                                ) : (
                                    <ExpandMoreIcon fontSize="small" />
                                )}
                            </IconButton>
                        )}
                        <IconButton
                            size="small"
                            color="inherit"
                            onClick={() => setOpen(false)}
                            aria-label="dismiss alert"
                        >
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </Box>
                }
            >
                <AlertTitle sx={{ fontSize: 14, fontWeight: 600, mb: 0.25 }}>
                    {title}
                </AlertTitle>
                <Box sx={{ fontSize: 13 }}>{message}</Box>
                <Collapse in={expanded}>
                    {details && (
                        <Box sx={{ fontSize: 12, mt: 1, opacity: 0.9 }}>{details}</Box>
                    )}
                </Collapse>
            </Alert>
        </Collapse>
    );
};

export default PageAlert;
