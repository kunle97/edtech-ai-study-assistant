import { useState, type FormEvent } from "react";
import MenuBookRoundedIcon from "@mui/icons-material/MenuBookRounded";
import PersonAddRoundedIcon from "@mui/icons-material/PersonAddRounded";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Link,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink, Navigate, useNavigate } from "react-router-dom";

import { apiClient } from "../api/client";
import { useAuth } from "../auth/AuthContext";

interface RegisterResponse {
  id: string;
  email: string;
  role: "student";
  is_suspended: boolean;
  created_at: string;
}

export function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
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

    if (password !== confirmation) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    setIsSubmitting(true);

    try {
      await apiClient.post<RegisterResponse>(
        "/api/v1/auth/register",
        {
          email: email.trim(),
          password,
        },
      );

      navigate("/login", {
        replace: true,
        state: {
          registrationSuccess: true,
          registeredEmail: email.trim(),
        },
      });
    } catch (requestError: any) {
      const detail = requestError.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "We could not create your account. Please try again.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        px: 2,
        py: 6,
        background:
          "linear-gradient(145deg, #F7F4FF 0%, #F8FAFF 55%, #EEF8F7 100%)",
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, sm: 5 },
            border: "1px solid",
            borderColor: "divider",
            boxShadow: "0 24px 80px rgba(36, 24, 66, 0.10)",
          }}
        >
          <Stack spacing={2} alignItems="center" sx={{ mb: 4 }}>
            <Box
              sx={{
                width: 56,
                height: 56,
                display: "grid",
                placeItems: "center",
                borderRadius: 3,
                bgcolor: "primary.main",
                color: "white",
              }}
            >
              <MenuBookRoundedIcon />
            </Box>

            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4">Create your account</Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }}>
                Join LearnPath and start a curriculum-grounded study session.
              </Typography>
            </Box>
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
                autoComplete="new-password"
                helperText="Use at least 8 characters."
                required
                fullWidth
              />

              <TextField
                label="Confirm password"
                type="password"
                value={confirmation}
                onChange={(event) => setConfirmation(event.target.value)}
                autoComplete="new-password"
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
                  ) : (
                    <PersonAddRoundedIcon />
                  )
                }
              >
                {isSubmitting ? "Creating account…" : "Create account"}
              </Button>
            </Stack>
          </Box>

          <Typography
            color="text.secondary"
            sx={{ mt: 3, textAlign: "center" }}
          >
            Already have an account?{" "}
            <Link component={RouterLink} to="/login" underline="hover">
              Sign in
            </Link>
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
}
