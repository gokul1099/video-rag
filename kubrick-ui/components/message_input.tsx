"use client"
import React, { useState } from "react";

interface MessageInputProps {
    onSend: (message: string, image_base64: string | null) => void;
    onVideoUpload?: (file: File) => void;
    disabled?: boolean;
}

export default function MessageInput({ onSend, onVideoUpload, disabled }: MessageInputProps) {
    const [text, setText] = useState("");
    const [imagePreview, setImagePreview] = useState<string | null>(null);

    const handleSend = () => {
        const trimmed = text.trim();
        if (!trimmed) return;

        onSend(trimmed, imagePreview);
        setText("");
        setImagePreview(null);
    };

    const handleRemoveImage = () => {
        setImagePreview(null);
    };

    const onClickAttach = () => {
        const fileInput = document.createElement("input");
        fileInput.type = "file";
        fileInput.accept = "image/*,video/*";
        fileInput.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (!file) return;

            if (file.type.startsWith("video/")) {
                onVideoUpload?.(file);
            } else {
                const reader = new FileReader();
                reader.onload = () => {
                    setImagePreview(reader.result as string);
                };
                reader.readAsDataURL(file);
            }
        };
        fileInput.click();
    }
    return (
        <div className="w-full relative">
            {imagePreview && (
                <div className="mb-3 relative inline-block">
                    <img src={imagePreview} alt="Preview" className="max-h-32 rounded-lg border border-white/20 shadow-lg" />
                    <button
                        onClick={handleRemoveImage}
                        type="button"
                        className="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold shadow"
                    >
                        ×
                    </button>
                </div>
            )}
            <form className={`flex items-center space-x-2 transition-all duration-300 ${disabled ? "opacity-40 pointer-events-none blur-[1px]" : ""}`} onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
                <label htmlFor="voice-search" className="sr-only">Message</label>
                <div className="relative flex-1">
                    <input type="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        id="voice-search"
                        disabled={disabled}
                        className="bg-white/5 border border-white/10 text-white text-sm rounded-full focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-4 pr-12 py-3 placeholder-gray-400 backdrop-blur-sm transition-all shadow-sm disabled:cursor-not-allowed"
                        placeholder={disabled ? "Processing video, please wait..." : "Type a message..."}
                        required={true} />
                    <button onClick={onClickAttach} type="button" disabled={disabled} className="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 hover:text-white transition-colors disabled:text-gray-600">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                        </svg>
                    </button>
                </div>
                <button type="submit" disabled={disabled} className="inline-flex items-center justify-center w-12 h-12 text-sm font-medium text-white bg-indigo-500 rounded-full hover:bg-indigo-400 focus:ring-4 focus:outline-none focus:ring-indigo-500/50 transition-colors shadow-lg shadow-indigo-500/20 disabled:bg-indigo-500/50 disabled:cursor-not-allowed">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="ml-1">
                        <line x1="22" y1="2" x2="11" y2="13" />
                        <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                </button>
            </form>
            {disabled && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <span className="text-xs text-indigo-400 bg-black/60 px-3 py-1 rounded-full backdrop-blur-sm">Processing video...</span>
                </div>
            )}
        </div>
    );
}
