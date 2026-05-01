from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from datetime import datetime, timezone

from kubrick_api.db.models import User
from kubrick_api.auth.schema import UserLogin, UserCreate, UserResponse, TokenPayload, Token
from kubrick_api.auth.security import hash_password, verify_password,create_access_token,create_refresh_token, verify_token
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
            self.db.flush()
            self.db.refresh(new_user)
            self.db.commit()
            
            access_token,acess_expires_in = create_access_token(user_id=new_user.id, email=new_user.email)
            refresh_token,refresh_expires_in = create_refresh_token(user_id=new_user.id, email=new_user.email)

            ### TODO : can implement a separate DB for handling token rotation

            expires_in = int((acess_expires_in - datetime.now(timezone.utc)).total_seconds())
            return Token(
                access_token=access_token, 
                refresh_token=refresh_token,
                expires_in=expires_in,
        )
        
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to register user: {str(e)}")
    
    def authenticate_user(self,request: UserLogin) -> Token:
        """Authenticate user and return JWT token"""
        user = self.db.query(User).filter(
            User.email == request.email
        ).first()
        if not user:
            raise ValueError("Invalid email or password")
        result = verify_password(request.password, user.hashed_password)

        if not result:
            raise ValueError("Invalid email or password")
           
        access_token, expires_at = create_access_token(user_id=user.id, email=user.email)
        refresh_token_tuple = create_refresh_token(user_id=user.id, email=user.email)
        refresh_token = refresh_token_tuple[0]  # Extract token string from tuple
        
        expires_in = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        
        return Token(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
        )

    def refresh_token(self,refresh_token: str) -> Token:
        payload = verify_token(token=refresh_token, token_type="refresh")
        if not payload:
            raise ValueError("Invalid or expired refresh token")

        user = self.db.query(User).filter(User.id == payload.sub).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token,expires_at = create_access_token(user_id=user.id, email=user.email)
        new_refresh_token,_ = create_refresh_token(user_id=user.id, email=user.email)

        expires_in = int((expires_at - datetime.now(timezone.utc)).total_seconds())

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=expires_in
        )

            

    