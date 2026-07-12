import { apiClient } from "./client";

export type MessageRole = "user" | "assistant";

export type MessageStatus =
  | "queued"
  | "processing"
  | "completed"
  | "retrying"
  | "failed"
  | "blocked";

export interface ChatMessage {
  id: string;
  session_id: string;
  role: MessageRole;
  status: MessageStatus;
  content: string;
  error_message: string | null;
  created_at: string;
}

export interface ChatSession {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

export async function listChatSessions(): Promise<ChatSession[]> {
  const response = await apiClient.get<ChatSession[]>(
    "/api/v1/chat/sessions",
  );

  return response.data;
}

export async function getChatSession(
  sessionId: string,
): Promise<ChatSessionDetail> {
  const response = await apiClient.get<ChatSessionDetail>(
    `/api/v1/chat/sessions/${sessionId}`,
  );

  return response.data;
}

export async function createChatSession(
  title?: string,
): Promise<ChatSession> {
  const response = await apiClient.post<ChatSession>(
    "/api/v1/chat/sessions",
    {
      title: title?.trim() || null,
    },
  );

  return response.data;
}

export async function sendChatMessage(
  sessionId: string,
  content: string,
): Promise<ChatMessage> {
  const response = await apiClient.post<ChatMessage>(
    `/api/v1/chat/sessions/${sessionId}/messages`,
    {
      content,
    },
  );

  return response.data;
}
