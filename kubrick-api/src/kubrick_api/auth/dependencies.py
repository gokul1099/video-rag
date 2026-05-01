from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from kubrick_api.db.db import get_db
from kubrick_api.auth.schema import TokenPayload
from kubrick_api.db.models import User
from kubrick_api.auth.security import verify_password, verify_token
security_scheme = HTTPBearer(
    description="JWT access token",
    auto_error=False
)

def get_curret_user(credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
                          db: Session = Depends(get_db)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={'WWW-Authenticate': "Bearer"}
        )

    token = credentials.credentials
    try:
        payload = verify_token(token=token)

        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )
        user_id_str = payload.sub
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers = {"WWW-Authenticate":"Bearer"}
            )
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user id",
            headers = {"WWW-Authenticate":"Bearer"}
        )
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or user is not active",
                headers = {"WWW-Authenticate":"Bearer"}
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate":"Bearer"}
        )
