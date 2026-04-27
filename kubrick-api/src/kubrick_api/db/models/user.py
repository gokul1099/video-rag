from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Integer,
    Index,
    func
)
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from kubrick_api.db.db import get_db_manager

Base = get_db_manager().Base

class User(Base):
    """
    User model rephoneresenting a user account in the system

    Attributes:
        id: Primary key, Unique identifier for user
        email: Unique email address, used as login username
        full_name: Display name for user
        hashed_password: bcrypt-hashed password (never store plaintext!)
        is_active: Soft delete flag; False means user account is disabled
        created_at: Timestamp of account creation
        updated_at: Timestamp of last profile update
    """

    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email: str = Column(String(255), unique=True, nullable=False,
                         index=True)
    full_name: str = Column(String(255), nullable=False, index=False )
    hashed_password: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False, index=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_email_is_active", "email", "is_active"),
    )

    def __repr__(self):
        """String representation for debugging"""
        return f"<User(id={self.id}, email={self.email}, username={self.username})"