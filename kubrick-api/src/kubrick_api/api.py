from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from enum import Enum
import click
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastmcp.client import Client
from loguru import logger
from kubrick_api.models import UploadVideoResponse
import shutil

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = ""
    app.state.bg_task_status = {}
    yield
    app.state.agent.reset_memory()


app = FastAPI(
    title="Kubric API",
    description="An AI-powered sports assitant API using OpenAI",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_method=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation
    """
    return {"message" : "Welcom to kubrick API. visit /docs for documentation"}


@app.post("/upload-video", response_model=UploadVideoResponse)
async def upload_video(file: UploadFile= File(...)):
    """
    Upload video and return the path
    """
    if not file.filename:
        raise HTTPException(status_code=400, details="No file uploaded")
    
    try:
        shared_media = Path(shared_media / file.filename)
        shared_media.mkdir(exist_ok=True)

        video_path = Path(shared_media / file.filename)
        if not video_path.exists():
            with open(video_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        return UploadVideoResponse(message="Video Uploaded Successfully", video_path=str(video_path))
    
    except Exception as e:
        logger.error(f"Error uploading video : {e}")
        raise HTTPException(status_code=500, detail=str(e))

