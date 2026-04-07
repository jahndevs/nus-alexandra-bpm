import React, { useEffect, useState } from "react";
import axios from "axios";
import { Container, Typography, Button } from "@mui/material";

const App: React.FC = () => {
    const [message, setMessage] = useState<string>("");

    useEffect(() => {
        axios.get("/api/")
            .then(response => setMessage(response.data.message))
            .catch(error => console.error("Error fetching data", error));
    }, []);

    return (
        <Container>
            <Typography variant="h3" gutterBottom>
                Cuffless Blood Pressure Monitor Dashboard
            </Typography>
            <Typography variant="body1">
                {message || "Loading..."}
            </Typography>
            <Button variant="contained" color="primary" style={{ marginTop: '20px' }}>
                Click Me
            </Button>
        </Container>
    );
};

export default App;