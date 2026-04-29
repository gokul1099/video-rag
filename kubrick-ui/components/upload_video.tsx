"use client"
import React, { useState, useRef } from 'react';
import { apiFetch, apiRequest } from '@/lib/api-client';

type UploadResponse = {
  message: string;
  video_path: string;
  task_id: string;
};

const VideoUploader: React.FC<{ onUploadSuccess: (resp: UploadResponse) => void }> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

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
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      uploadFile(files[0]);
    }
  };

  // Triggered by clicking the area
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    // Basic validation
    if (!file.type.startsWith('video/')) {
      alert("Please upload a valid video file.");
      return;
    }

    setIsLoading(true);

    // Prepare the form with the correct field name expected by the API
    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await apiRequest('/upload-video', { method: 'POST', body: formData });
      const data: UploadResponse = await uploadResponse.json();

      await apiFetch('/process-video', {
        method: 'POST',
        body: JSON.stringify({ video_path: data.video_path }),
      })

      onUploadSuccess(data);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed. See console for details.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative group cursor-pointer border-2 border-dashed rounded-xl p-2 transition-all duration-200 flex flex-col items-center justify-center
          ${isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-slate-300 hover:border-slate-400 bg-slate-50'}`}
      >
        <input 
          type="file" 
          className="hidden" 
          accept="video/*" 
          ref={fileInputRef}
          onChange={handleFileChange}
        />

        {isLoading ? (
          <div className="flex flex-col items-center">
            {/* Simple Spinner */}
            <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
            <p className="text-slate-600 font-medium">Uploading video...</p>
          </div>
        ) : (
          <>
            <div className="bg-white p-2 rounded-full shadow-sm group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
            <h1 className='text-black'>Upload Video</h1>
          </>
        )}
      </div>
    </div>
  );
};

export default VideoUploader;