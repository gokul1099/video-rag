"use client"
import VideoUploader from "@/components/upload_video";
import { UploadProvider, useUploads } from "@/context/upload_context";
import UploadList from "@/components/upload_list";
import { MessageProvider, useMessages } from "@/context/message-context";
import MessageInput from "@/components/message_input";
import MessageList from "@/components/message_list";
import React, { useEffect } from "react";
import { apiFetch } from "@/lib/api-client";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";

function Main() {
  const router = useRouter();
  const { uploads } = useUploads();
  const { addMessage, messages } = useMessages();

  // Check authentication on mount
  useEffect(() => {
    const authToken = Cookies.get("authToken");
    if (!authToken) {
      router.push("/login");
    }
  }, [router]);

  const handleSendMessage = async (message: string, image_base64: string | null) => {
    // add user message locally
    addMessage({ role: "user", content: message, ...(image_base64 && { image_base64 }) });

    // prepare request body (using the most recent completed/processing video as main focus if needed)
    const validUploads = uploads.filter(u => u.video_path);
    const video_path = validUploads.length > 0 ? validUploads[0].video_path : null;
    const body = { message, video_path, image_base64: image_base64 ? image_base64.split(",")[1] : null };

    try {
      const data = await apiFetch<{ message?: string; clip_path?: string }>("/chat", {
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
          
          <VideoUploader />
          
          <div className="flex-1 mt-4 overflow-y-auto pr-2 custom-scrollbar">
            <UploadList />
          </div>
        </div>
      </aside>

      <div className="flex-1 flex flex-col sm:ml-80 h-screen relative">
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-32">
          <MessageList messages={messages} />
        </div>
        
        <div className="absolute bottom-0 w-full bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a]/90 to-transparent pt-10 pb-6 px-4 sm:px-6">
          <div className="max-w-4xl mx-auto">
            <MessageInput onSend={handleSendMessage} />
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
