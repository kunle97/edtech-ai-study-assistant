import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import AutoAwesomeRoundedIcon from "@mui/icons-material/AutoAwesomeRounded";
import ChatBubbleOutlineRoundedIcon from "@mui/icons-material/ChatBubbleOutlineRounded";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import MenuBookRoundedIcon from "@mui/icons-material/MenuBookRounded";
import SendRoundedIcon from "@mui/icons-material/SendRounded";
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  TextField,
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
  createChatSession,
  getChatSession,
  listChatSessions,
  sendChatMessage,
  type ChatMessage,
  type MessageStatus,
} from "../api/chat";
import { useAuth } from "../auth/AuthContext";

const drawerWidth = 300;

function formatSessionDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

function statusLabel(status: MessageStatus): string {
  switch (status) {
    case "queued":
      return "Queued";
    case "processing":
      return "Thinking";
    case "retrying":
      return "Retrying";
    case "failed":
      return "Failed";
    case "blocked":
      return "Blocked";
    default:
      return "Complete";
  }
}

function isPendingMessage(message: ChatMessage): boolean {
  return ["queued", "processing", "retrying"].includes(message.status);
}

export function StudentDashboard() {
  const { user, logout } = useAuth();
  const queryClient = useQueryClient();
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(
    null,
  );
  const [message, setMessage] = useState("");
  const [newSessionTitle, setNewSessionTitle] = useState("");

  const sessionsQuery = useQuery({
    queryKey: ["chat-sessions"],
    queryFn: listChatSessions,
  });

  useEffect(() => {
    if (
      !selectedSessionId &&
      sessionsQuery.data &&
      sessionsQuery.data.length > 0
    ) {
      setSelectedSessionId(sessionsQuery.data[0].id);
    }
  }, [selectedSessionId, sessionsQuery.data]);

  const sessionQuery = useQuery({
    queryKey: ["chat-session", selectedSessionId],
    queryFn: () => getChatSession(selectedSessionId!),
    enabled: Boolean(selectedSessionId),
    refetchInterval: (query) => {
      const session = query.state.data;

      if (!session) {
        return 2_000;
      }

      const hasPendingMessage = session.messages.some(isPendingMessage);
      return hasPendingMessage ? 1_500 : false;
    },
  });

  const createSessionMutation = useMutation({
    mutationFn: () => createChatSession(newSessionTitle),
    onSuccess: async (session) => {
      setNewSessionTitle("");
      setSelectedSessionId(session.id);

      await queryClient.invalidateQueries({
        queryKey: ["chat-sessions"],
      });
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: (content: string) =>
      sendChatMessage(selectedSessionId!, content),
    onSuccess: async () => {
      setMessage("");

      await queryClient.invalidateQueries({
        queryKey: ["chat-session", selectedSessionId],
      });

      await queryClient.invalidateQueries({
        queryKey: ["chat-sessions"],
      });
    },
  });

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [sessionQuery.data?.messages]);

  const selectedSession = useMemo(
    () =>
      sessionsQuery.data?.find(
        (session) => session.id === selectedSessionId,
      ),
    [selectedSessionId, sessionsQuery.data],
  );

  const handleSendMessage = (event: FormEvent) => {
    event.preventDefault();

    const trimmedMessage = message.trim();

    if (!selectedSessionId || !trimmedMessage) {
      return;
    }

    sendMessageMutation.mutate(trimmedMessage);
  };

  const hasActiveSession = Boolean(selectedSessionId);

  return (
    <Box
      sx={{
        display: "flex",
        minHeight: "100vh",
        bgcolor: "background.default",
      }}
    >
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            width: drawerWidth,
            boxSizing: "border-box",
            borderRight: "1px solid",
            borderColor: "divider",
            bgcolor: "#FCFBFF",
          },
        }}
      >
        <Toolbar sx={{ px: 2.5 }}>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2.5,
                bgcolor: "primary.main",
                color: "white",
                display: "grid",
                placeItems: "center",
              }}
            >
              <MenuBookRoundedIcon />
            </Box>

            <Box>
              <Typography fontWeight={750}>LearnPath</Typography>
              <Typography variant="caption" color="text.secondary">
                AI Study Assistant
              </Typography>
            </Box>
          </Stack>
        </Toolbar>

        <Divider />

        <Box sx={{ p: 2 }}>
          <TextField
            size="small"
            fullWidth
            placeholder="Session title"
            value={newSessionTitle}
            onChange={(event) => setNewSessionTitle(event.target.value)}
            sx={{ mb: 1.5 }}
          />

          <Button
            fullWidth
            variant="contained"
            startIcon={
              createSessionMutation.isPending ? (
                <CircularProgress size={17} color="inherit" />
              ) : (
                <AddRoundedIcon />
              )
            }
            disabled={createSessionMutation.isPending}
            onClick={() => createSessionMutation.mutate()}
          >
            New study session
          </Button>
        </Box>

        <Typography
          variant="overline"
          color="text.secondary"
          sx={{ px: 2.5, mt: 1 }}
        >
          Recent sessions
        </Typography>

        <List sx={{ px: 1.5, overflowY: "auto", flexGrow: 1 }}>
          {sessionsQuery.isLoading && (
            <Box sx={{ display: "grid", placeItems: "center", py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          )}

          {sessionsQuery.data?.map((session) => (
            <ListItemButton
              key={session.id}
              selected={session.id === selectedSessionId}
              onClick={() => setSelectedSessionId(session.id)}
              sx={{
                mb: 0.5,
                borderRadius: 2.5,
                alignItems: "flex-start",
                "&.Mui-selected": {
                  bgcolor: "primary.light",
                },
              }}
            >
              <ChatBubbleOutlineRoundedIcon
                fontSize="small"
                sx={{ mt: 0.6, mr: 1.5 }}
              />

              <ListItemText
                primary={session.title || "Untitled study session"}
                secondary={formatSessionDate(session.created_at)}
                primaryTypographyProps={{
                  fontWeight: 650,
                  noWrap: true,
                }}
              />
            </ListItemButton>
          ))}
        </List>

        <Divider />

        <Stack
          direction="row"
          alignItems="center"
          spacing={1.5}
          sx={{ p: 2 }}
        >
          <Avatar sx={{ bgcolor: "secondary.main" }}>
            {user?.email.charAt(0).toUpperCase()}
          </Avatar>

          <Box sx={{ minWidth: 0, flexGrow: 1 }}>
            <Typography variant="body2" fontWeight={650} noWrap>
              {user?.email}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Student
            </Typography>
          </Box>

          <Tooltip title="Sign out">
            <IconButton onClick={logout}>
              <LogoutRoundedIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          height: "100vh",
        }}
      >
        <AppBar
          position="static"
          color="inherit"
          elevation={0}
          sx={{
            borderBottom: "1px solid",
            borderColor: "divider",
          }}
        >
          <Toolbar sx={{ minHeight: 72 }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" fontWeight={750}>
                {selectedSession?.title || "Study assistant"}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Responses are grounded in approved curriculum content.
              </Typography>
            </Box>

            <Chip
              icon={<AutoAwesomeRoundedIcon />}
              label="Curriculum grounded"
              variant="outlined"
              color="primary"
            />
          </Toolbar>
        </AppBar>

        {!hasActiveSession ? (
          <Container
            maxWidth="md"
            sx={{
              flexGrow: 1,
              display: "grid",
              placeItems: "center",
              py: 6,
            }}
          >
            <Paper
              elevation={0}
              sx={{
                width: "100%",
                maxWidth: 620,
                p: 5,
                textAlign: "center",
                border: "1px solid",
                borderColor: "divider",
                boxShadow: "0 20px 70px rgba(36, 24, 66, 0.08)",
              }}
            >
              <Box
                sx={{
                  width: 72,
                  height: 72,
                  mx: "auto",
                  mb: 3,
                  borderRadius: 4,
                  bgcolor: "primary.light",
                  color: "primary.dark",
                  display: "grid",
                  placeItems: "center",
                }}
              >
                <AutoAwesomeRoundedIcon fontSize="large" />
              </Box>

              <Typography variant="h4" gutterBottom>
                Start learning
              </Typography>

              <Typography color="text.secondary" mb={3}>
                Create a study session and ask a question about your
                curriculum.
              </Typography>

              <Button
                variant="contained"
                startIcon={<AddRoundedIcon />}
                onClick={() => createSessionMutation.mutate()}
              >
                Create your first session
              </Button>
            </Paper>
          </Container>
        ) : (
          <>
            <Box
              sx={{
                flexGrow: 1,
                overflowY: "auto",
                px: { xs: 2, md: 5 },
                py: 4,
              }}
            >
              <Container maxWidth="md">
                {sessionQuery.isLoading && (
                  <Box sx={{ display: "grid", placeItems: "center", py: 8 }}>
                    <CircularProgress />
                  </Box>
                )}

                {sessionQuery.isError && (
                  <Alert severity="error">
                    The conversation could not be loaded.
                  </Alert>
                )}

                {sessionQuery.data?.messages.length === 0 && (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 4,
                      textAlign: "center",
                      border: "1px dashed",
                      borderColor: "divider",
                    }}
                  >
                    <Typography variant="h6" gutterBottom>
                      What would you like to study?
                    </Typography>

                    <Typography color="text.secondary">
                      Try asking: “What is photosynthesis?”
                    </Typography>
                  </Paper>
                )}

                <Stack spacing={3}>
                  {sessionQuery.data?.messages.map((chatMessage) => {
                    const isAssistant = chatMessage.role === "assistant";
                    const pending = isPendingMessage(chatMessage);

                    return (
                      <Stack
                        key={chatMessage.id}
                        direction="row"
                        spacing={1.5}
                        justifyContent={
                          isAssistant ? "flex-start" : "flex-end"
                        }
                        alignItems="flex-start"
                      >
                        {isAssistant && (
                          <Avatar
                            sx={{
                              bgcolor: "primary.main",
                              width: 36,
                              height: 36,
                            }}
                          >
                            <AutoAwesomeRoundedIcon fontSize="small" />
                          </Avatar>
                        )}

                        <Paper
                          elevation={0}
                          sx={{
                            maxWidth: "78%",
                            px: 2.5,
                            py: 2,
                            bgcolor: isAssistant
                              ? "background.paper"
                              : "primary.main",
                            color: isAssistant
                              ? "text.primary"
                              : "primary.contrastText",
                            border: isAssistant ? "1px solid" : "none",
                            borderColor: "divider",
                            borderRadius: isAssistant
                              ? "6px 18px 18px 18px"
                              : "18px 6px 18px 18px",
                            boxShadow: isAssistant
                              ? "0 8px 30px rgba(36, 24, 66, 0.06)"
                              : "none",
                          }}
                        >
                          <Typography
                            sx={{
                              whiteSpace: "pre-wrap",
                              lineHeight: 1.7,
                            }}
                          >
                            {chatMessage.content}
                          </Typography>

                          {(pending ||
                            chatMessage.status === "failed" ||
                            chatMessage.status === "blocked") && (
                            <Stack
                              direction="row"
                              spacing={1}
                              alignItems="center"
                              mt={1.5}
                            >
                              {pending && (
                                <CircularProgress
                                  size={14}
                                  color="inherit"
                                />
                              )}

                              <Typography
                                variant="caption"
                                color={
                                  isAssistant
                                    ? "text.secondary"
                                    : "inherit"
                                }
                              >
                                {statusLabel(chatMessage.status)}
                              </Typography>
                            </Stack>
                          )}

                          {chatMessage.error_message && (
                            <Typography
                              variant="caption"
                              display="block"
                              mt={1}
                            >
                              {chatMessage.error_message}
                            </Typography>
                          )}
                        </Paper>
                      </Stack>
                    );
                  })}
                </Stack>

                <div ref={messagesEndRef} />
              </Container>
            </Box>

            <Box
              sx={{
                borderTop: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper",
                p: 2.5,
              }}
            >
              <Container maxWidth="md">
                {sendMessageMutation.isError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    Your message could not be sent. Please try again.
                  </Alert>
                )}

                <Box
                  component="form"
                  onSubmit={handleSendMessage}
                  sx={{
                    display: "flex",
                    gap: 1.5,
                    alignItems: "flex-end",
                  }}
                >
                  <TextField
                    fullWidth
                    multiline
                    maxRows={5}
                    placeholder="Ask a question about your curriculum…"
                    value={message}
                    onChange={(event) => setMessage(event.target.value)}
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter" &&
                        !event.shiftKey &&
                        !event.nativeEvent.isComposing
                      ) {
                        event.preventDefault();
                        handleSendMessage(event);
                      }
                    }}
                  />

                  <IconButton
                    type="submit"
                    disabled={
                      !message.trim() ||
                      sendMessageMutation.isPending
                    }
                    sx={{
                      width: 50,
                      height: 50,
                      bgcolor: "primary.main",
                      color: "white",
                      "&:hover": {
                        bgcolor: "primary.dark",
                      },
                      "&.Mui-disabled": {
                        bgcolor: "action.disabledBackground",
                      },
                    }}
                  >
                    {sendMessageMutation.isPending ? (
                      <CircularProgress size={20} color="inherit" />
                    ) : (
                      <SendRoundedIcon />
                    )}
                  </IconButton>
                </Box>

                <Typography
                  variant="caption"
                  color="text.secondary"
                  display="block"
                  textAlign="center"
                  mt={1.5}
                >
                  Answers are generated from imported curriculum and may
                  require instructor verification.
                </Typography>
              </Container>
            </Box>
          </>
        )}
      </Box>
    </Box>
  );
}
