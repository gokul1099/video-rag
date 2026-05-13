import { Message } from "@/context/message-context";
import { ImagePreview } from "./image_preview";
import { buildApiUrl } from "@/lib/api-client";

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 mt-20">
          <svg className="w-16 h-16 mb-4 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-lg font-medium text-gray-400">No messages yet</p>
          <p className="text-sm">Upload a video and start asking questions.</p>
        </div>
      )}
      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={`max-w-[85%] sm:max-w-[75%] px-5 py-3.5 shadow-sm ${msg.role === "user"
            ? "bg-indigo-600 text-white rounded-2xl rounded-tr-sm"
            : "bg-white/10 text-gray-100 border border-white/5 rounded-2xl rounded-tl-sm backdrop-blur-sm"
            }`}>
            <div className="flex items-center mb-1.5 space-x-2">
              <span className="text-xs font-semibold opacity-70 tracking-wide uppercase">
                {msg.role === "user" ? "You" : "Kubrick AI"}
              </span>
            </div>
            <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>
            
            {msg.clip_path && (
              <div className="mt-4 rounded-lg overflow-hidden border border-white/10 bg-black/40">
                {msg.clip_path.endsWith("mp4") ? (
                  <video
                    controls
                    className="w-full max-h-64 object-contain bg-black"
                    src={buildApiUrl(`/video/media/${msg.clip_path.split('/').pop()}`)} 
                  />
                ) : (
                  <ImagePreview uri={buildApiUrl(`/video/media/${msg.clip_path.split('/').pop()}`)}/>
                )}
              </div>
            )}

            {msg.image_base64 && !msg.clip_path && (
              <div className="mt-3">
                <img
                  src={msg.image_base64}
                  alt="Attached image"
                  className="max-w-[240px] rounded-lg border border-white/10 shadow-sm"
                />
              </div>
            )}
            
          </div>
        </div>
      ))}
    </div>
  );
}
