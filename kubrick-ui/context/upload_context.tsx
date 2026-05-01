"use client"
import React, { createContext, useContext, useState } from "react";

export type UploadStatus = 'uploading' | 'processing' | 'completed' | 'error';

export type UploadItem = {
  id: string; // local unique id
  fileName: string;
  status: UploadStatus;
  message?: string;
  video_path?: string;
  task_id?: string;
  error?: string;
};

type UploadContextType = {
  uploads: UploadItem[];
  addUpload: (u: UploadItem) => void;
  updateUpload: (id: string, updates: Partial<UploadItem>) => void;
};

const UploadContext = createContext<UploadContextType | null>(null);

export const UploadProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [uploads, setUploads] = useState<UploadItem[]>([]);

  const addUpload = (u: UploadItem) => setUploads((s) => [u, ...s]);
  
  const updateUpload = (id: string, updates: Partial<UploadItem>) => {
    setUploads((s) => s.map(u => u.id === id ? { ...u, ...updates } : u));
  };

  return <UploadContext.Provider value={{ uploads, addUpload, updateUpload }}>{children}</UploadContext.Provider>;
};

export const useUploads = () => {
  const ctx = useContext(UploadContext);
  if (!ctx) throw new Error("useUploads must be used within an UploadProvider");
  return ctx;
};

export default UploadProvider;
