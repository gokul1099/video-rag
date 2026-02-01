"use client"
import React, { createContext, useContext, useState } from "react";

type UploadItem = {
  message: string;
  video_path: string;
  task_id: string;
};

type UploadContextType = {
  uploads: UploadItem[];
  addUpload: (u: UploadItem) => void;
};

const UploadContext = createContext<UploadContextType | null>(null);

export const UploadProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [uploads, setUploads] = useState<UploadItem[]>([]);

  const addUpload = (u: UploadItem) => setUploads((s) => [u, ...s]);

  return <UploadContext.Provider value={{ uploads, addUpload }}>{children}</UploadContext.Provider>;
};

export const useUploads = () => {
  const ctx = useContext(UploadContext);
  if (!ctx) throw new Error("useUploads must be used within an UploadProvider");
  return ctx;
};

export default UploadProvider;
