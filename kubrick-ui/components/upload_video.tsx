"use client"
import React, { useState, useRef } from 'react';
import { apiFetch, apiRequest } from '@/lib/api-client';
import { useUploads } from '@/context/upload_context';

type UploadResponse = {
  message: string;
  video_path: string;
  task_id: string;
};

const VideoUploader: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { addUpload, updateUpload } = useUploads();

  // Handle drag events
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  // Triggered by clicking the area
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (files: File[]) => {
    files.forEach(file => {
      uploadFile(file);
    });
    // clear input so same file can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  const uploadFile = async (file: File) => {
    // Basic validation
    if (!file.type.startsWith('video/')) {
      alert("Please upload a valid video file.");
      return;
    }

    const localId = Math.random().toString(36).substring(7);
    
    addUpload({
      id: localId,
      fileName: file.name,
      status: 'uploading'
    });

    // Prepare the form with the correct field name expected by the API
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await apiRequest('/video/upload', { method: 'POST', body: formData });
      const data: UploadResponse = await uploadResponse.json();

      updateUpload(localId, {
        status: 'processing',
        task_id: data.task_id,
        video_path: data.video_path
      });

      await apiFetch('/video/process-video', {
        method: 'POST',
        body: JSON.stringify({ video_path: data.video_path }),
      });

      updateUpload(localId, {
        status: 'completed'
      });
      
    } catch (error: any) {
      console.error("Upload failed:", error);
      updateUpload(localId, {
        status: 'error',
        error: String(error)
      });
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative group cursor-pointer border-2 border-dashed rounded-xl p-6 transition-all duration-200 flex flex-col items-center justify-center
          ${isDragging 
            ? 'border-indigo-500 bg-indigo-500/10' 
            : 'border-white/20 hover:border-white/40 bg-white/5'}`}
      >
        <input 
          type="file" 
          className="hidden" 
          accept="video/*" 
          multiple
          ref={fileInputRef}
          onChange={handleFileChange}
        />

        <div className="bg-indigo-500/20 p-3 rounded-full shadow-sm group-hover:scale-110 transition-transform">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <h1 className='text-gray-100 mt-2 font-medium'>Upload Media</h1>
        <p className="text-xs text-gray-400 mt-1">Drag and drop or click to browse</p>
      </div>
    </div>
  );
};

export default VideoUploader;