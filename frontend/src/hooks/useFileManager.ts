import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { AlertItem, FileItem } from "@/types";

export function useFileManager() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([api.listFiles(), api.listAlerts()]);
      setFiles(filesData);
      setAlerts(alertsData);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const uploadFile = useCallback(
    async (title: string, file: File) => {
      setIsUploading(true);
      setErrorMessage(null);

      try {
        await api.uploadFile(title, file);
        await loadData();
        return true;
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Не удалось загрузить файл");
        return false;
      } finally {
        setIsUploading(false);
      }
    },
    [loadData],
  );

  return { files, alerts, isLoading, isUploading, errorMessage, loadData, uploadFile };
}
