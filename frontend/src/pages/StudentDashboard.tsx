import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import MenuBookRoundedIcon from "@mui/icons-material/MenuBookRounded";
import {
  AppBar,
  Box,
  Button,
  Container,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";

import { useAuth } from "../auth/AuthContext";

export function StudentDashboard() {
  const { user, logout } = useAuth();

  return (
    <Box minHeight="100vh" bgcolor="background.default">
      <AppBar position="static" color="inherit" elevation={0}>
        <Toolbar sx={{ borderBottom: "1px solid", borderColor: "divider" }}>
          <MenuBookRoundedIcon color="primary" />
          <Typography variant="h6" sx={{ ml: 1.5, flexGrow: 1 }}>
            LearnPath
          </Typography>
          <Button startIcon={<LogoutRoundedIcon />} onClick={logout}>
            Sign out
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        <Stack spacing={1}>
          <Typography variant="h4">Study workspace</Typography>
          <Typography color="text.secondary">
            Signed in as {user?.email}
          </Typography>
        </Stack>
      </Container>
    </Box>
  );
}
