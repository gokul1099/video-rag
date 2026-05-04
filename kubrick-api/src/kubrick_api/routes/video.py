from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, Request
from fastapi.responses import FileResponse
from pathlib import Path
from uuid import uuid4
import shutil
import asyncio

from kubrick_api.models import UploadVideoResponse, ProcessVideoResponse, ProcessVideoRequest, TaskStatus
from kubrick_api.config import get_settings
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

        # Generate a unique filename to prevent collisions or reusing old corrupted files
        unique_filename = f"{uuid4().hex}_{file.filename}"
        video_path = Path(shared_media / unique_filename)
        
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
    bg_task_states[task_id] = TaskStatus.IN_PROGRESS

    async def background_process_video(video_path: str, task_id: str):
        """
        Background task to process the video
        """
        if not Path(video_path).exists():
            bg_task_states[task_id] = TaskStatus.FAILED
            logger.error(f"Video file not found: {video_path}")
            return

        try:
            _ = await mcp_client.call_tool("process_video", {"video_path": video_path})
            bg_task_states[task_id] = TaskStatus.COMPLETED
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            bg_task_states[task_id] = TaskStatus.FAILED
    
    bg_tasks.add_task(background_process_video, request.video_path, task_id)
    return ProcessVideoResponse(message="Task enqued for processing", task_id=task_id)

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    timeout = 30 
    poll_interval = 1
    
    for _ in range(int(timeout / poll_interval)):
        status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)

        if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return {"task_id" : task_id, "status": status}
            
        if status == TaskStatus.NOT_FOUND:
            return {"task_id" : task_id, "status": status}

        await asyncio.sleep(poll_interval)

    return {"task_id": task_id, "status": TaskStatus.IN_PROGRESS}


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