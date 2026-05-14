from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from kubrick_api.db.models import ChatSession
from typing import List, Optional
from kubrick_api.agent.memory import Memory, MemoryRecord

import logging

logger = logging.getLogger(__name__)

class ChatService:
    """Chat service"""

    def __init__(self, db: Session, memory: Memory = None ):
        self.db = db
        self.agent_memory = memory

    def format_conversaion(self, messages: List[MemoryRecord]):
        """Format the messages form database into the chat_history format expected by agent"""
        history= []
        for msg in messages:
            history.append(
                {
                    "role": msg.role,
                    "content": msg.content
                }
            )
        return history

    def get_sessions(self, user_id:str):
        sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).all()
        return sessions

    def get_session_messages(self, session_id: int) -> List[MemoryRecord]:
        """Fetches chronological messages from a specific session from Pixeltable"""
        if not session_id:
            raise ValueError("Session ID not provided")
        if not self.agent_memory:
            raise ValueError("Pixeltable memory instance was not provided")
        return self.agent_memory.get_by_session_id(str(session_id))

    def create_session(self, user_id: int, title: str = "New Chat") -> ChatSession:
        """Create a new chat session for the user"""
        try:
            session = ChatSession(user_id=user_id, title=title)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {e}")
            raise ValueError(e)
