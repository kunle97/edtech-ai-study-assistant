import { useState, type FormEvent } from "react";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import MenuBookRoundedIcon from "@mui/icons-material/MenuBookRounded";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Navigate, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { user, isAuthenticated, login } = useAuth();

  const [email, setEmail] = useState("student@example.com");
  const [password, setPassword] = useState("StudyPass123!");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (isAuthenticated && user) {
    return (
      <Navigate
        to={user.role === "admin" ? "/admin" : "/study"}
        replace
      />
    );
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const authenticatedUser = await login(email, password);

      navigate(
        authenticatedUser.role === "admin" ? "/admin" : "/study",
        { replace: true },
      );
    } catch {
      setError("We could not sign you in. Check your email and password.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        gridTemplateColumns: { xs: "1fr", md: "1.1fr 0.9fr" },
        background:
          "linear-gradient(145deg, #F7F4FF 0%, #F8FAFF 55%, #EEF8F7 100%)",
      }}
    >
      <Box
        sx={{
          display: { xs: "none", md: "flex" },
          position: "relative",
          overflow: "hidden",
          alignItems: "center",
          px: { md: 8, lg: 12 },
          background:
            "linear-gradient(145deg, #4F378B 0%, #6750A4 50%, #006A6A 140%)",
          color: "white",
        }}
      >
        <Box
          sx={{
            position: "absolute",
            width: 420,
            height: 420,
            borderRadius: "50%",
            background: "rgba(255,255,255,0.08)",
            top: -130,
            right: -100,
          }}
        />

        <Stack spacing={4} sx={{ maxWidth: 600, zIndex: 1 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box
              sx={{
                width: 48,
                height: 48,
                display: "grid",
                placeItems: "center",
                borderRadius: 3,
                background: "rgba(255,255,255,0.16)",
                backdropFilter: "blur(12px)",
              }}
            >
              <MenuBookRoundedIcon />
            </Box>
            <Typography variant="h5">LearnPath</Typography>
          </Stack>

          <Typography variant="h3">
            Learn with an AI tutor grounded in your curriculum.
          </Typography>

          <Typography
            variant="h6"
            sx={{
              maxWidth: 530,
              color: "rgba(255,255,255,0.78)",
              fontWeight: 400,
              lineHeight: 1.7,
            }}
          >
            Ask questions, explore concepts, and receive reliable answers
            backed by approved learning content.
          </Typography>

          <Stack direction="row" spacing={1.5} alignItems="center">
            <AutoAwesomeRoundedIcon />
            <Typography>Personalized, curriculum-aware guidance</Typography>
          </Stack>
        </Stack>
      </Box>

      <Container
        maxWidth="sm"
        sx={{
          display: "flex",
          alignItems: "center",
          py: 6,
        }}
      >
        <Paper
          elevation={0}
          sx={{
            width: "100%",
            p: { xs: 3, sm: 5 },
            border: "1px solid",
            borderColor: "divider",
            boxShadow: "0 24px 80px rgba(36, 24, 66, 0.10)",
          }}
        >
          <Stack spacing={1} mb={4}>
            <Typography variant="h4">Welcome back</Typography>
            <Typography color="text.secondary">
              Sign in to continue to your study workspace.
            </Typography>
          </Stack>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              <TextField
                label="Email address"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
                required
                fullWidth
              />

              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
                fullWidth
              />

              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={isSubmitting}
                startIcon={
                  isSubmitting ? (
                    <CircularProgress color="inherit" size={18} />
                  ) : undefined
                }
              >
                {isSubmitting ? "Signing in…" : "Sign in"}
              </Button>
            </Stack>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
