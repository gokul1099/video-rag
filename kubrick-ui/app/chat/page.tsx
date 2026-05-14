"use client"
import { UploadProvider, useUploads } from "@/context/upload_context";
import { MessageProvider, useMessages } from "@/context/message-context";
import MessageInput from "@/components/message_input";
import MessageList from "@/components/message_list";
import React, { useEffect, useState, useCallback } from "react";
import { apiFetch, apiRequest } from "@/lib/api-client";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";

interface ChatSession {
  id: number;
  title: string;
  updated_at: string;
}

function Main() {
  const router = useRouter();
  const { uploads, addUpload, updateUpload } = useUploads();
  const { addMessage, updateMessage, messages, loadMessages, clear } = useMessages();
  const [isProcessing, setIsProcessing] = useState(false);

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [activeSessionTitle, setActiveSessionTitle] = useState<string>("New Chat");

  // Check authentication and fetch sessions on mount
  useEffect(() => {
    const authToken = Cookies.get("authToken");
    if (!authToken) {
      router.push("/login");
      return;
    }

    const fetchSessions = async () => {
      try {
        const data = await apiFetch<ChatSession[]>("/chat/sessions");
        setSessions(data);
      } catch (e) {
        console.error("Failed to fetch sessions", e);
      }
    };
    fetchSessions();
  }, [router]);

  const handleNewChat = async () => {
    try {
      const data = await apiFetch<ChatSession>("/chat/sessions", {
        method: "POST",
        body: JSON.stringify({ title: "New Chat" }),
      });
      setSessions((prev) => [data, ...prev]);
      setActiveSessionId(data.id);
      setActiveSessionTitle(data.title);
      clear();
    } catch (e) {
      console.error("Failed to create new chat", e);
    }
  };

  const handleSessionClick = async (sessionId: number, title: string) => {
    setActiveSessionId(sessionId);
    setActiveSessionTitle(title);
    try {
      const data = await apiFetch<any[]>(`/chat/${sessionId}/messages`);
      loadMessages(
        data.map((m) => ({
          id: m.message_id || m.id || uuidv4(),
          role: m.role,
          content: m.content,
          timestamp: m.timestamp || m.created_at || new Date().toISOString(),
          clip_path: m.video_path || m.clip_path,
          image_base64: m.image_url || m.image_base64,
        }))
      );
    } catch (e) {
      console.error("Failed to fetch messages", e);
      clear();
    }
  };

  const handleSendMessage = async (message: string, image_base64: string | null) => {
    let currentSessionId = activeSessionId;

    // Create a new session if one is not active
    if (!currentSessionId) {
      try {
        const data = await apiFetch<ChatSession>("/chat/sessions", {
          method: "POST",
          body: JSON.stringify({ title: "New Chat" }),
        });
        setSessions((prev) => [data, ...prev]);
        setActiveSessionId(data.id);
        setActiveSessionTitle(data.title);
        currentSessionId = data.id;
      } catch (e) {
        console.error("Failed to create session", e);
        return;
      }
    }

    // add user message locally
    addMessage({ role: "user", content: message, ...(image_base64 && { image_base64 }) });

    // prepare request body
    const validUploads = uploads.filter(u => u.video_path);
    const video_path = validUploads.length > 0 ? validUploads[0].video_path : null;
    const body = { message, video_path, image_base64: image_base64 ? image_base64.split(",")[1] : null };

    try {
      const data = await apiFetch<{ message?: string; clip_path?: string }>(`/chat/${currentSessionId}`, {
        method: "POST",
        body: JSON.stringify(body),
      });

      const assistantText = data?.message ?? JSON.stringify(data);
      const clipPath = data?.clip_path;
      addMessage({
        role: "assistant",
        content: assistantText,
        ...(clipPath && { clip_path: clipPath })
      });
    } catch (e: any) {
      addMessage({ role: "assistant", content: `Request failed: ${String(e)}` });
    }
  };

  const pollTaskStatus = useCallback(async (taskId: string, msgId: string, fileName: string, videoPath?: string) => {
    try {
      const response = await apiRequest(`/video/task-status/${taskId}`);
      const data = await response.json();

      if (data.status === 'completed') {
        updateMessage(msgId, { content: `✅ Video ready: ${fileName}`, clip_path: videoPath });
        setIsProcessing(false);
      } else if (data.status === 'failed') {
        updateMessage(msgId, { content: `❌ Processing failed: ${fileName}` });
        setIsProcessing(false);
      } else if (data.status === 'not_found') {
        updateMessage(msgId, { content: `❌ Task not found: ${fileName}` });
        setIsProcessing(false);
      } else {
        setTimeout(() => pollTaskStatus(taskId, msgId, fileName, videoPath), 2000);
      }
    } catch (error) {
      console.error("Polling error", error);
      setTimeout(() => pollTaskStatus(taskId, msgId, fileName, videoPath), 2000);
    }
  }, [updateMessage]);

  const handleVideoUpload = async (file: File) => {
    if (!file.type.startsWith('video/')) {
      addMessage({ role: "system", content: `⚠️ Please select a valid video file.` });
      return;
    }

    setIsProcessing(true);
    const localId = Math.random().toString(36).substring(7);
    const msg = addMessage({ role: "system", content: `📤 Uploading ${file.name}...` });

    addUpload({
      id: localId,
      fileName: file.name,
      status: 'uploading'
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const uploadResponse = await apiRequest('/video/upload-video', { method: 'POST', body: formData });
      const uploadData: { message: string; video_path: string } = await uploadResponse.json();

      updateUpload(localId, { status: 'processing', video_path: uploadData.video_path });
      updateMessage(msg.id, { content: `⚙️ Processing ${file.name}...` });

      const processResponse = await apiRequest('/video/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_path: uploadData.video_path }),
      });
      const processData: { message: string; task_id: string } = await processResponse.json();

      updateUpload(localId, { task_id: processData.task_id });

      pollTaskStatus(processData.task_id, msg.id, file.name, uploadData.video_path);
    } catch (error: any) {
      console.error("Upload/Process failed:", error);
      updateUpload(localId, { status: 'error', error: String(error) });
      updateMessage(msg.id, { content: `❌ Upload failed: ${file.name}` });
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-white overflow-hidden">
      <button data-drawer-target="default-sidebar" data-drawer-toggle="default-sidebar" aria-controls="default-sidebar" type="button" className="inline-flex items-center p-2 mt-2 ms-3 text-sm text-gray-400 rounded-lg sm:hidden hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-gray-600">
        <span className="sr-only">Open sidebar</span>
        <svg className="w-6 h-6" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
          <path stroke="currentColor" strokeLinecap="round" strokeWidth="2" d="M5 7h14M5 12h14M5 17h10" />
        </svg>
      </button>

      <aside id="default-sidebar" className="fixed top-0 left-0 z-40 w-80 h-screen transition-transform -translate-x-full sm:translate-x-0" aria-label="Sidebar">
        <div className="h-full px-4 py-6 overflow-y-auto bg-white/5 backdrop-blur-md border-r border-white/10 flex flex-col shadow-xl">
          <div className="flex items-center mb-6 px-2">
            <img
              alt="Kubrick AI"
              src="https://tailwindcss.com/plus-assets/img/logos/mark.svg?color=indigo&shade=500"
              className="h-8 w-auto mr-3"
            />
            <h2 className="text-lg font-bold tracking-tight text-white">
              Kubrick AI
            </h2>
          </div>

          <div className="w-full mb-6">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
              </svg>
              New Chat
            </button>
          </div>

          <div className="mt-6 flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-1">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-2">Recent Chats</h3>
            {sessions.map(s => (
              <button
                key={s.id}
                onClick={() => handleSessionClick(s.id, s.title)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-colors ${activeSessionId === s.id ? 'bg-white/10 text-white' : 'text-gray-400 hover:bg-white/5 hover:text-white'}`}
              >
                {s.title}
              </button>
            ))}
          </div>

        </div>
      </aside>

      <div className="flex-1 flex flex-col sm:ml-80 h-screen relative">
        <div className="h-14 border-b border-white/10 flex items-center px-6 bg-white/5 backdrop-blur-sm sticky top-0 z-10">
          <h1 className="text-lg font-medium">{activeSessionTitle}</h1>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 mb-20">
          <MessageList messages={messages} />
        </div>

        <div className="absolute bottom-0 w-full bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/90 to-transparent pt-10 pb-6 px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <MessageInput onSend={handleSendMessage} onVideoUpload={handleVideoUpload} disabled={isProcessing} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <UploadProvider>
      <MessageProvider>
        <Main />
      </MessageProvider>
    </UploadProvider>
  );
}
