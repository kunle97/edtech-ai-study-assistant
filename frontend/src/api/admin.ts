import { apiClient } from "./client";

export type UserRole = "student" | "admin";
export type ImportStatus =
  | "pending"
  | "running"
  | "complete"
  | "failed";

export interface AdminUser {
  id: string;
  email: string;
  role: UserRole;
  is_suspended: boolean;
  suspended_at: string | null;
  created_at: string;
}

export interface UserListResponse {
  users: AdminUser[];
  total: number;
}

export interface AdminChatSession {
  id: string;
  user_id: string;
  user_email: string;
  title: string | null;
  start_time: string;
  message_count: number;
}

export interface ImportJob {
  id: string;
  filename: string;
  status: ImportStatus;
  total_records: number;
  processed_records: number;
  failed_records: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ImportErrorRecord {
  id: string;
  line_number: number;
  raw_record: Record<string, unknown> | null;
  error_message: string;
  created_at: string;
}

export async function listUsers(): Promise<UserListResponse> {
  const response = await apiClient.get<UserListResponse>(
    "/api/v1/admin/users",
  );

  return response.data;
}

export async function suspendUser(
  userId: string,
): Promise<AdminUser> {
  const response = await apiClient.post<AdminUser>(
    `/api/v1/admin/users/${userId}/suspend`,
  );

  return response.data;
}

export async function reinstateUser(
  userId: string,
): Promise<AdminUser> {
  const response = await apiClient.post<AdminUser>(
    `/api/v1/admin/users/${userId}/reinstate`,
  );

  return response.data;
}

export async function listAdminChatSessions(): Promise<
  AdminChatSession[]
> {
  const response = await apiClient.get<AdminChatSession[]>(
    "/api/v1/admin/chat-sessions",
  );

  return response.data;
}

export async function listImports(): Promise<ImportJob[]> {
  const response = await apiClient.get<ImportJob[]>(
    "/api/v1/admin/imports",
  );

  return response.data;
}

export async function uploadCurriculum(
  file: File,
): Promise<ImportJob> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<ImportJob>(
    "/api/v1/admin/imports",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    },
  );

  return response.data;
}

export async function listImportErrors(
  jobId: string,
): Promise<ImportErrorRecord[]> {
  const response = await apiClient.get<ImportErrorRecord[]>(
    `/api/v1/admin/imports/${jobId}/errors`,
  );

  return response.data;
}
