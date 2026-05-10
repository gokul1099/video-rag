from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from pwdlib import PasswordHash
from kubrick_api.config import get_settings
from kubrick_api.auth.schema import TokenPayload
import logging
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException

logger = logging.getLogger(__name__)
settings = get_settings()
hash_gen = PasswordHash.recommended()
security = HTTPBearer()

def hash_password(password: str) -> str:
    hashed = hash_gen.hash(password)
    print(f"[HASH] Original: {hashed}")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        print(plain_password,"plainpassword ---- ")
        result = hash_gen.verify(plain_password, hashed_password)
        logger.info(f"[VERIFY] Result: {result}")
        return result
    except Exception as e:
        logger.error(f"[VERIFY] Exception: {str(e)}")
        return False

def create_access_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode= {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    logger.info(f"Create access token for user {user_id}")

    return encoded_jwt, expire


def create_refresh_token(user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type":"refresh"
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt, expire

def verify_token(token: str, token_type: str = "access") -> Optional[TokenPayload]:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id_str = payload.get("sub")
        user_id: int | None = int(user_id_str) if user_id_str else None
        email: str = payload.get("email")
        exp: int = payload.get("exp")
        iat: int = payload.get("iat")
        token_type_claim: str = payload.get('type',"access")

        if user_id is None or email is None:
            logger.warning("Token missing required claims (sub or email)")
            return None

        if token_type_claim != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {token_type_claim}")
            return None
        
        return TokenPayload(
            sub=user_id,
            email=email,
            exp=exp,
            iat=iat,
            type=token_type_claim
        )
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")


def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    payload = verify_token(token)
    if payload is not None:
        return payload.sub
    
    logger.error("Could not extract user_id, Token is invalid or expired")
    raise HTTPException(status_code=401, detail="User is not authorised")

