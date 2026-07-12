import {
  useMemo,
  useState,
  type ReactNode,
} from "react";
import AdminPanelSettingsRoundedIcon from "@mui/icons-material/AdminPanelSettingsRounded";
import ChatBubbleOutlineRoundedIcon from "@mui/icons-material/ChatBubbleOutlineRounded";
import CheckCircleRoundedIcon from "@mui/icons-material/CheckCircleRounded";
import CloudUploadRoundedIcon from "@mui/icons-material/CloudUploadRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import PauseCircleRoundedIcon from "@mui/icons-material/PauseCircleRounded";
import RefreshRoundedIcon from "@mui/icons-material/RefreshRounded";
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  LinearProgress,
  Paper,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  listAdminChatSessions,
  listImportErrors,
  listImports,
  listUsers,
  reinstateUser,
  suspendUser,
  uploadCurriculum,
  type ImportJob,
} from "../api/admin";
import { useAuth } from "../auth/AuthContext";

function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function importColor(
  status: ImportJob["status"],
): "default" | "info" | "success" | "error" | "warning" {
  switch (status) {
    case "running":
      return "info";
    case "complete":
      return "success";
    case "failed":
      return "error";
    case "pending":
      return "warning";
    default:
      return "default";
  }
}

export function AdminDashboard() {
  const { logout } = useAuth();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedImport, setSelectedImport] =
    useState<ImportJob | null>(null);

  const usersQuery = useQuery({
    queryKey: ["admin-users"],
    queryFn: listUsers,
  });

  const importsQuery = useQuery({
    queryKey: ["admin-imports"],
    queryFn: listImports,
    refetchInterval: (query) => {
      const imports = query.state.data;

      return imports?.some(
        (job) => job.status === "pending" || job.status === "running",
      )
        ? 2_000
        : false;
    },
  });

  const chatSessionsQuery = useQuery({
    queryKey: ["admin-chat-sessions"],
    queryFn: listAdminChatSessions,
  });

  const importErrorsQuery = useQuery({
    queryKey: ["admin-import-errors", selectedImport?.id],
    queryFn: () => listImportErrors(selectedImport!.id),
    enabled: Boolean(selectedImport),
  });

  const suspendMutation = useMutation({
    mutationFn: suspendUser,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["admin-users"],
      }),
  });

  const reinstateMutation = useMutation({
    mutationFn: reinstateUser,
    onSuccess: () =>
      queryClient.invalidateQueries({
        queryKey: ["admin-users"],
      }),
  });

  const uploadMutation = useMutation({
    mutationFn: uploadCurriculum,
    onSuccess: async () => {
      setSelectedFile(null);

      await queryClient.invalidateQueries({
        queryKey: ["admin-imports"],
      });
    },
  });

  const studentCount = useMemo(
    () =>
      usersQuery.data?.users.filter(
        (currentUser) => currentUser.role === "student",
      ).length ?? 0,
    [usersQuery.data],
  );

  const suspendedCount = useMemo(
    () =>
      usersQuery.data?.users.filter(
        (currentUser) => currentUser.is_suspended,
      ).length ?? 0,
    [usersQuery.data],
  );

  const completedImports =
    importsQuery.data?.filter(
      (job) => job.status === "complete",
    ).length ?? 0;

  const refreshAll = async () => {
    await Promise.all([
      usersQuery.refetch(),
      importsQuery.refetch(),
      chatSessionsQuery.refetch(),
    ]);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <AppBar
        position="sticky"
        color="inherit"
        elevation={0}
        sx={{
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Toolbar sx={{ minHeight: 72 }}>
          <Avatar
            sx={{
              bgcolor: "primary.main",
              mr: 1.5,
            }}
          >
            <AdminPanelSettingsRoundedIcon />
          </Avatar>

          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" sx={{ fontWeight: 750 }}>
              LearnPath Administration
            </Typography>

            <Typography variant="body2" color="text.secondary">
              Platform operations and curriculum management
            </Typography>
          </Box>

          <Tooltip title="Refresh dashboard">
            <IconButton onClick={refreshAll}>
              <RefreshRoundedIcon />
            </IconButton>
          </Tooltip>

          <Button
            sx={{ ml: 1 }}
            startIcon={<LogoutRoundedIcon />}
            onClick={logout}
          >
            Sign out
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          sx={{ mb: 4 }}
        >
          <MetricCard
            title="Students"
            value={studentCount}
            icon={<GroupsRoundedIcon />}
          />

          <MetricCard
            title="Suspended"
            value={suspendedCount}
            icon={<PauseCircleRoundedIcon />}
          />

          <MetricCard
            title="Chat sessions"
            value={chatSessionsQuery.data?.length ?? 0}
            icon={<ChatBubbleOutlineRoundedIcon />}
          />

          <MetricCard
            title="Completed imports"
            value={completedImports}
            icon={<CheckCircleRoundedIcon />}
          />
        </Stack>

        <Paper
          elevation={0}
          sx={{
            border: "1px solid",
            borderColor: "divider",
            overflow: "hidden",
          }}
        >
          <Tabs
            value={activeTab}
            onChange={(_, value: number) => setActiveTab(value)}
            sx={{
              px: 2,
              borderBottom: "1px solid",
              borderColor: "divider",
            }}
          >
            <Tab label="Users" />
            <Tab label="Curriculum imports" />
            <Tab label="Chat sessions" />
          </Tabs>

          {activeTab === 0 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 0.5 }}>
                User management
              </Typography>

              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Suspend or reinstate student access immediately.
              </Typography>

              {usersQuery.isLoading ? (
                <LoadingState />
              ) : usersQuery.isError ? (
                <Alert severity="error">
                  Users could not be loaded.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>User</TableCell>
                        <TableCell>Role</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell align="right">Action</TableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {usersQuery.data?.users.map((currentUser) => (
                        <TableRow key={currentUser.id} hover>
                          <TableCell>
                            <Typography sx={{ fontWeight: 650 }}>
                              {currentUser.email}
                            </Typography>
                          </TableCell>

                          <TableCell>
                            <Chip
                              size="small"
                              label={currentUser.role}
                              variant="outlined"
                            />
                          </TableCell>

                          <TableCell>
                            <Chip
                              size="small"
                              color={
                                currentUser.is_suspended
                                  ? "error"
                                  : "success"
                              }
                              label={
                                currentUser.is_suspended
                                  ? "Suspended"
                                  : "Active"
                              }
                            />
                          </TableCell>

                          <TableCell>
                            {formatDate(currentUser.created_at)}
                          </TableCell>

                          <TableCell align="right">
                            {currentUser.role === "student" && (
                              <Button
                                size="small"
                                color={
                                  currentUser.is_suspended
                                    ? "success"
                                    : "error"
                                }
                                variant="outlined"
                                disabled={
                                  suspendMutation.isPending ||
                                  reinstateMutation.isPending
                                }
                                onClick={() => {
                                  if (currentUser.is_suspended) {
                                    reinstateMutation.mutate(
                                      currentUser.id,
                                    );
                                  } else {
                                    suspendMutation.mutate(
                                      currentUser.id,
                                    );
                                  }
                                }}
                              >
                                {currentUser.is_suspended
                                  ? "Reinstate"
                                  : "Suspend"}
                              </Button>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {activeTab === 1 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 0.5 }}>
                Curriculum imports
              </Typography>

              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Upload JSONL curriculum content and monitor processing.
              </Typography>

              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  mb: 3,
                  border: "1px dashed",
                  borderColor: "primary.main",
                  bgcolor: "primary.light",
                }}
              >
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={2}
                  sx={{ alignItems: { sm: "center" } }}
                >
                  <Button
                    component="label"
                    variant="outlined"
                    startIcon={<CloudUploadRoundedIcon />}
                  >
                    Choose JSONL file
                    <input
                      hidden
                      type="file"
                      accept=".jsonl"
                      onChange={(event) => {
                        setSelectedFile(
                          event.target.files?.[0] ?? null,
                        );
                      }}
                    />
                  </Button>

                  <Typography sx={{ flexGrow: 1 }}>
                    {selectedFile?.name ?? "No file selected"}
                  </Typography>

                  <Button
                    variant="contained"
                    disabled={
                      !selectedFile || uploadMutation.isPending
                    }
                    onClick={() => {
                      if (selectedFile) {
                        uploadMutation.mutate(selectedFile);
                      }
                    }}
                  >
                    {uploadMutation.isPending
                      ? "Uploading…"
                      : "Start import"}
                  </Button>
                </Stack>
              </Paper>

              {uploadMutation.isError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  The curriculum file could not be uploaded.
                </Alert>
              )}

              {importsQuery.isLoading ? (
                <LoadingState />
              ) : importsQuery.isError ? (
                <Alert severity="error">
                  Import history could not be loaded.
                </Alert>
              ) : (
                <Stack spacing={2}>
                  {importsQuery.data?.map((job) => {
                    const progress =
                      job.total_records > 0
                        ? Math.round(
                            ((job.processed_records +
                              job.failed_records) /
                              job.total_records) *
                              100,
                          )
                        : 0;

                    return (
                      <Paper
                        key={job.id}
                        elevation={0}
                        sx={{
                          p: 2.5,
                          border: "1px solid",
                          borderColor: "divider",
                        }}
                      >
                        <Stack
                          direction={{ xs: "column", md: "row" }}
                          spacing={2}
                          sx={{ alignItems: { md: "center" } }}
                        >
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography sx={{ fontWeight: 700 }}>
                              {job.filename}
                            </Typography>

                            <Typography
                              variant="body2"
                              color="text.secondary"
                            >
                              {formatDate(job.created_at)}
                            </Typography>
                          </Box>

                          <Chip
                            label={job.status}
                            color={importColor(job.status)}
                            size="small"
                          />

                          <Typography variant="body2">
                            {job.processed_records} processed
                          </Typography>

                          <Typography variant="body2">
                            {job.failed_records} failed
                          </Typography>

                          <Button
                            size="small"
                            disabled={job.failed_records === 0}
                            onClick={() => setSelectedImport(job)}
                          >
                            View errors
                          </Button>
                        </Stack>

                        {(job.status === "running" ||
                          job.status === "pending") && (
                          <LinearProgress
                            variant={
                              job.total_records > 0
                                ? "determinate"
                                : "indeterminate"
                            }
                            value={progress}
                            sx={{ mt: 2 }}
                          />
                        )}

                        {job.error_message && (
                          <Alert severity="error" sx={{ mt: 2 }}>
                            {job.error_message}
                          </Alert>
                        )}
                      </Paper>
                    );
                  })}
                </Stack>
              )}
            </Box>
          )}

          {activeTab === 2 && (
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ mb: 0.5 }}>
                Chat sessions
              </Typography>

              <Typography color="text.secondary" sx={{ mb: 3 }}>
                Review platform chat activity and message counts.
              </Typography>

              {chatSessionsQuery.isLoading ? (
                <LoadingState />
              ) : chatSessionsQuery.isError ? (
                <Alert severity="error">
                  Chat sessions could not be loaded.
                </Alert>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Session</TableCell>
                        <TableCell>Student</TableCell>
                        <TableCell>Started</TableCell>
                        <TableCell align="right">Messages</TableCell>
                      </TableRow>
                    </TableHead>

                    <TableBody>
                      {chatSessionsQuery.data?.map((session) => (
                        <TableRow key={session.id} hover>
                          <TableCell>
                            <Typography sx={{ fontWeight: 650 }}>
                              {session.title || "Untitled session"}
                            </Typography>
                          </TableCell>

                          <TableCell>{session.user_email}</TableCell>

                          <TableCell>
                            {formatDate(session.start_time)}
                          </TableCell>

                          <TableCell align="right">
                            <Chip
                              size="small"
                              label={session.message_count}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </Paper>
      </Container>

      <Dialog
        open={Boolean(selectedImport)}
        onClose={() => setSelectedImport(null)}
        fullWidth
        maxWidth="md"
      >
        <DialogTitle>Quarantined import records</DialogTitle>

        <DialogContent dividers>
          {importErrorsQuery.isLoading ? (
            <LoadingState />
          ) : importErrorsQuery.data?.length === 0 ? (
            <Alert severity="success">
              This import has no quarantined records.
            </Alert>
          ) : (
            <Stack spacing={2}>
              {importErrorsQuery.data?.map((error) => (
                <Paper
                  key={error.id}
                  elevation={0}
                  sx={{
                    p: 2,
                    border: "1px solid",
                    borderColor: "divider",
                  }}
                >
                  <Typography sx={{ fontWeight: 700 }}>
                    Line {error.line_number}
                  </Typography>

                  <Typography
                    variant="body2"
                    color="error"
                    sx={{
                      mt: 1,
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {error.error_message}
                  </Typography>
                </Paper>
              ))}
            </Stack>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={() => setSelectedImport(null)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

interface MetricCardProps {
  title: string;
  value: number;
  icon: ReactNode;
}

function MetricCard({
  title,
  value,
  icon,
}: MetricCardProps) {
  return (
    <Paper
      elevation={0}
      sx={{
        flex: 1,
        p: 2.5,
        border: "1px solid",
        borderColor: "divider",
      }}
    >
      <Stack
        direction="row"
        spacing={2}
        sx={{ alignItems: "center" }}
      >
        <Avatar
          sx={{
            bgcolor: "primary.light",
            color: "primary.dark",
          }}
        >
          {icon}
        </Avatar>

        <Box>
          <Typography variant="h4">{value}</Typography>
          <Typography color="text.secondary">{title}</Typography>
        </Box>
      </Stack>
    </Paper>
  );
}

function LoadingState() {
  return (
    <Box
      sx={{
        minHeight: 180,
        display: "grid",
        placeItems: "center",
      }}
    >
      <CircularProgress />
    </Box>
  );
}
