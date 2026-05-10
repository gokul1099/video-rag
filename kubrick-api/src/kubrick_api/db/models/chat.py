from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Index,
    ForeignKey,
    UUID,
    Enum as SQLEnum
)
from enum import Enum
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from kubrick_api.db.db import get_db_manager
import uuid 

Base = get_db_manager().Base

class ChatRole(str, Enum):
    """Chat message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
class ChatSession(Base):
    """
    Chat Model representing conversation history
    
    """

    __tablename__ = "ChatSession"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer ,ForeignKey('users.id'), nullable=False)
    title: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        """String representation for debugging"""
        return f"<ChatSession(id={self.id}, user_id={self.user_id} title={self.title})"

class ChatMessage(Base):
    """Message model for event individual messages"""
    
    __tablename__ = "ChatMessage"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    session_id: int = Column(Integer, ForeignKey('ChatSession.id'), index=True, nullable=False)
    role = Column(SQLEnum(ChatRole), nullable=False, default=ChatRole.USER)
    content: str = Column(String, nullable=False)
    video_path: str = Column(String)
    image_url: str = Column(String)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
