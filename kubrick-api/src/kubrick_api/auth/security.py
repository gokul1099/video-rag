from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from kubrick_api.config import get_settings
from kubrick_api.auth.schema import TokenPayload
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__default_rounds=12
)


def hash_password(password: str) -> str:
    # Bcrypt has 72-byte limit (Blowfish algorithm)
    password_stripped = password.strip()
    password_bytes = password_stripped.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    hashed = pwd_context.hash(password_truncated)
    logger.info(f"[HASH] Original: {password_stripped[:20]}... | Bytes len: {len(password_bytes)} | Hash: {hashed}")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Bcrypt has 72-byte limit (Blowfish algorithm)
    password_stripped = plain_password.strip()
    password_bytes = password_stripped.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')

    logger.info(f"[VERIFY] Original: {password_stripped[:20]}... | Bytes len: {len(password_bytes)} | Truncated: {password_truncated[:20]}...")
    logger.info(f"[VERIFY] Stored hash: {hashed_password}")
    logger.info(f"[VERIFY] Hash type: {type(hashed_password)} | Pwd type: {type(password_truncated)}")

    try:
        result = pwd_context.verify(password_truncated, hashed_password)
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
        "sub": user_id,
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
        "sub": user_id,
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
        user_id: int = payload.get("sub")
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
