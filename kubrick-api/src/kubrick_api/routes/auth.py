from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from kubrick_api.auth.service import AuthService
from kubrick_api.auth.schema import (UserLogin, UserCreate, Token, UserResponse, TokenRefresh)
from kubrick_api.auth.dependencies import get_curret_user
from kubrick_api.db.models import User
from kubrick_api.db.db import get_db

# TODO: Need to implement token rotation and revocation by storing the token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"}
    }
)

@router.post("/register", 
             response_model=Token, 
             status_code=status.HTTP_201_CREATED,
             summary="Ragister a new user",
             description="Create a new user account with email and password"
             )
async def resigter(request: UserCreate, db:Session = Depends(get_db)) -> Token:
    auth_service = AuthService(db=db)
    try:
        token = auth_service.register_user(request=request)

        return token
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register user")


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK, summary="Login User", description="Authenticate with email and passwordm receieve JWT tokens")
async def login(request: UserLogin, db: Session = Depends(get_db)) -> Token:
    auth_service = AuthService(db=db)
    try:
        token_response = auth_service.authenticate_user(request)
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Failed to authenticate {e}')
    
@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK, summary="Refresh access token", description="Get a new access token using a refresh token")
async def refresh(request: TokenRefresh, db:Session = Depends(get_db)):
    refresh_token = request.refresh_token
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="refresh_token required in request body")
    auth_service = AuthService(db=db)
    try:
        token_response = auth_service.refresh_token(refresh_token=refresh_token)
        return token_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Failed to refresh token {e}')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to refresh token {e}")