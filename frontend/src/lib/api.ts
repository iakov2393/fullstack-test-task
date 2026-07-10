import type { AlertItem, FileItem } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  listFiles: () => request<FileItem[]>("/files"),

  listAlerts: () => request<AlertItem[]>("/alerts"),

  uploadFile: (title: string, file: File) => {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    return request<FileItem>("/files", {
      method: "POST",
      body: formData,
    });
  },

  downloadUrl: (fileId: string) => `${API_BASE_URL}/files/${fileId}/download`,
};
