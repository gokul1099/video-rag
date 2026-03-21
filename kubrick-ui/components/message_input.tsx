"use client"
import React, { useState } from "react";

interface MessageInputProps {
    onSend: (message: string, image_base64: string | null) => void;
}

export default function MessageInput({ onSend }: MessageInputProps) {
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
        fileInput.accept = "image/*";
        fileInput.onchange = async (e) => {
            const file = (e.target as HTMLInputElement).files?.[0];
            if (file) {
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
        <div className="fixed bottom-0 left-0 right-0 sm:left-64 bg-transparent border-t px-4 py-3 max-width:700px; margin: 100px auto;">
            {imagePreview && (
                <div className="mb-3 relative inline-block">
                    <img src={imagePreview} alt="Preview" className="max-h-32 rounded-lg" />
                    <button
                        onClick={handleRemoveImage}
                        type="button"
                        className="absolute top-1 right-1 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold"
                    >
                        ×
                    </button>
                </div>
            )}
            <form className="flex items-center">
                <label htmlFor="voice-search" className="sr-only">Search</label>
                <div className="relative w-full">
                    <input type="text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        id="voice-search"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5  dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        placeholder="Enter your query here"
                        required={true} />
                    <button onClick={onClickAttach} type="button" className="flex absolute inset-y-0 right-0 items-center pr-3">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                        </svg>
                    </button>
                </div>
                <button onClick={handleSend} type="button" className="inline-flex items-center py-2.5 px-3 ml-2 text-sm font-medium text-white bg-blue-700 border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="22" y1="2" x2="11" y2="13" />
                        <polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                </button>
            </form>

        </div>
    );
}
