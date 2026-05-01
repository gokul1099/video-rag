from fastapi import APIRouter, Request, HTTPException

from kubrick_api.models import AssitantMessageResponse, UserMessageRequest
from kubrick_api.agent import GroqAgent
from kubrick_api.config import get_settings
from loguru import logger

settings = get_settings()
router = APIRouter(prefix="/chat", tags=["video"])

@router.post("/{user_id}",response_model=AssitantMessageResponse)
async def chat(request: UserMessageRequest, fastapi_request: Request):
    agent = fastapi_request.app.state.agent
    await agent.setup()
    try:
        response = await agent.chat(request.message, request.video_path,request.image_base64)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))