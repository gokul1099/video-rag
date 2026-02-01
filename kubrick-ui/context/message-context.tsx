"use client"
import React, { createContext, useContext, useState } from "react";
import { v4 as uuidv4 } from "uuid";

export type Message = {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: string;
};

type MessageContextType = {
	messages: Message[];
	addMessage: (m: Omit<Message, "id" | "timestamp">) => Message;
	clear: () => void;
};

const MessageContext = createContext<MessageContextType | null>(null);

export const MessageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
	const [messages, setMessages] = useState<Message[]>([]);

	const addMessage = (m: Omit<Message, "id" | "timestamp">) => {
		const msg: Message = {
			id: uuidv4(),
			timestamp: new Date().toISOString(),
			...m,
		};
		setMessages((s) => [...s, msg]);
		return msg;
	};

	const clear = () => setMessages([]);

	return <MessageContext.Provider value={{ messages, addMessage, clear }}>{children}</MessageContext.Provider>;
};

export const useMessages = () => {
	const ctx = useContext(MessageContext);
	if (!ctx) throw new Error("useMessages must be used within MessageProvider");
	return ctx;
};

export default MessageProvider;
