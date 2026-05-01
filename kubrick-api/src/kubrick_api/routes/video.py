from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
from pathlib import Path
from uuid import uuid4
import shutil

from kubrick_api.models import UploadVideoResponse, ProcessVideoResponse, ProcessVideoRequest
from kubrick_api.config import get_settings
from kubrick_api.api import TaskStatus
from kubrick_api.mcp_client import mcp_client
from loguru import logger

settings = get_settings()
router = APIRouter(prefix="/video", tags=["video"])

@router.post("/upload-video", response_model=UploadVideoResponse)
async def upload_video(file: UploadFile= File(...)):
    """
    Upload video and return the path
    """
    if not file.filename:
        raise HTTPException(status_code=400, details="No file uploaded")
    
    try:
        shared_media = Path("shared_media")
        shared_media.mkdir(exist_ok=True)

        video_path = Path(shared_media / file.filename)
        if not video_path.exists():
            with open(video_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        return UploadVideoResponse(message="Video Uploaded Successfully", video_path=str(video_path))
    
    except Exception as e:
        logger.error(f"Error uploading video : {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/process", response_model=ProcessVideoResponse)
async def process_video(
    request: ProcessVideoRequest,
    bg_tasks: BackgroundTasks,
    fastapi_request: Request
):
    task_id = str(uuid4())
    bg_task_states = fastapi_request.app.state.bg_task_states

    async def background_process_video(video_path: str, task_id: str):
        """
        Background task to process the video
        """
        bg_task_states[task_id] = TaskStatus.IN_PROGRESS
        if not Path(video_path).exists():
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=404, detail="Video file not found")

        try:
            async with mcp_client:
                _ = await mcp_client.call_tool("process_video", {"video_path": request.video_path})
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=500, detail=str(e))
    
    bg_tasks.add_task(background_process_video, request.video_path, task_id)
    return ProcessVideoResponse(message="Task enqued for processing", task_id=task_id)

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)
    return {"task_id": task_id, "status": status}


@router.get("/media/{file_path:path}")
async def serve_media(file_path: str):
    try:
        clean_path = Path(file_path).name
        media_file = Path("shared_media") / clean_path

        if not media_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(str(media_file))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))