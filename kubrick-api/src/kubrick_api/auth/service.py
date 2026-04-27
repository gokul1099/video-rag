from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timezone

from kubrick_api.db.models import User
from kubrick_api.auth.schema import UserLogin, UserCreate, UserResponse, TokenPayload, Token
from kubrick_api.auth.security import hash_password, verify_password,create_access_token,create_refresh_token
import logging

logger = logging.getLogger(__name__)
class AuthService:
    """Authentication Service handling business logic"""

    def __init__(self, db: Session ):
        self.db = db
    
    def register_user(self, request: UserCreate) -> User:
        """Register a new user Account"""
        existing_user = self.db.query(User).filter(
            User.email == request.email
        ).first()

        if existing_user:
            raise ValueError(f"Email {request.email} already exists")
        hashed_password =hash_password(request.password)
        new_user = User(
            email=request.email,
            full_name=request.full_name,
            hashed_password=hashed_password,
            is_active=True
        )
        try:
            self.db.add(new_user)
            logger.info("added to db")
            self.db.flush()
            logger.info("flushed db")
            self.db.refresh(new_user)
            logger.info("db refresh done")
            self.db.commit()
            return new_user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to register user: {str(e)}")
    
    def authenticate_user(self,request: UserLogin) -> Token:
        """Authenticate user and return JWT token"""
        user = self.db.query(User).filter(
            User.email == request.email
        ).first()
        # print(request.password,"password")
        # # Debug logging
        # print(f"Password from request: {request.password[:10]}...")
        # print(f"Stored hash length: {len(user.hashed_password)}")
        # print(f"Stored hash: {user.hashed_password}")
        if not user:
            raise ValueError("Invalid email or password")
        result = verify_password(request.password, user.hashed_password)
        print(f"Password verification result: {result}")
        if not result:
            raise ValueError("Invalid email or password")
           
        access_token, expires_at = create_access_token(user_id=user.id, email=user.email)
        refresh_token_tuple = create_refresh_token(user_id=user.id, email=user.email)
        refresh_token = refresh_token_tuple[0]  # Extract token string from tuple
        
        # Calculate expires_in as seconds from now
        expires_in = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        
        return Token(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )


    