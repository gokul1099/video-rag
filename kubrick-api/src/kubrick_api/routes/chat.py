from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from kubrick_api.models import AssitantMessageResponse, UserMessageRequest
from kubrick_api.agent import GroqAgent
from kubrick_api.config import get_settings
from loguru import logger
from kubrick_api.auth.security import get_user_id
from kubrick_api.chat.service import ChatService
from kubrick_api.db.db import get_db


settings = get_settings()
router = APIRouter(prefix="/chat", tags=["video"])


@router.get("/sessions")
async def get_sessions(
    fastapi_request: Request,
    db: Session = Depends(get_db), 
    user_id: int = Depends(get_user_id)
):
    if not user_id:
        raise HTTPException(
            status_code=401, detail="User not authorized or session expired"
        )
    try:
        agent = fastapi_request.app.state.agent
        chat_service = ChatService(db,  memory=agent.memory)
        sessions = chat_service.get_sessions(user_id=user_id)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_sessions(
    fastapi_request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    agent = fastapi_request.app.state.agent
    try:
        chat_service = ChatService(db=db, memory=agent.memory)
        session = chat_service.create_session(user_id=user_id, title=f"new_chat")
        return session
    except Exception as e:
        logger.error(f"Error in creating session ${e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/messages")
async def get_chat_history(
    session_id: int, 
    fastapi_request: Request,
    db: Session = Depends(get_db)
):
    agent = fastapi_request.app.state.agent
    chat_service = ChatService(db=db, memory=agent.memory)
    messages = chat_service.get_session_messages(session_id)
    return messages


@router.post("/{session_id}", response_model=AssitantMessageResponse)
async def chat(
    session_id: int,
    request: UserMessageRequest,
    fastapi_request: Request,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db),
):
    agent = fastapi_request.app.state.agent
    await agent.setup()
    chat_service = ChatService(db=db, memory=agent.memory)
    try:
        
        response = await agent.chat(
            message=request.message,
            session_id=session_id,
            user_id=user_id,
            video_path=request.video_path,
            image_base64=request.image_base64,
        )

        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
