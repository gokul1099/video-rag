import { Message } from "@/context/message-context";
import { ImagePreview } from "./image_preview";
import { buildApiUrl } from "@/lib/api-client";

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
    console.log(messages)
  return (
    <div className="max-w-5xl mx-auto space-y-4">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
          <div className={`max-w-[70%] rounded-lg px-4 py-2 ${msg.role === "user"
            ? "bg-sky-600 text-white"
            : "bg-neutral-secondary-medium text-white border border-default-medium"
            }`}>
            <p className="text-sm mb-1 opacity-70">{msg.role === "user" ? "You" : "Agent"}</p>
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.clip_path && (
              <div className="mt-3 bg-red-400">

                {
                    msg?.clip_path?.endsWith("mp4") ? 
                    <video
                  controls
                  className="w-full rounded-md"
                  src={buildApiUrl(`/media/${msg.clip_path}`)}/>
                 : 
                <ImagePreview uri={buildApiUrl(`/media/${msg.clip_path}`)}/>
                }
                
                  Your browser does not support the video tag.
              </div>
            )}
            {msg.image_base64 && (!msg.clip_path || !msg.clip_path) && (
              <div className="mt-3">
                <img
                  src={msg.image_base64}
                  alt="User image"
                  className="max-w-xs rounded-md"
                />
              </div>
            )}
            
          </div>
        </div>
      ))}
    </div>
  );
}

