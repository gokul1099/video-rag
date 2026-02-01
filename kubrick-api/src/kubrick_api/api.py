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
from  kubrick_api.models import UploadVideoResponse, ProcessVideoRequest, ProcessVideoResponse, AssitantMessageResponse, UserMessageRequest
import shutil
from kubrick_api.config import get_settings
from kubrick_api.agent import GroqAgent

settings = get_settings()
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = GroqAgent(
        name="kubrick",
        mcp_server=settings.MCP_SERVER,
        disable_tools=["process_video"],
    )

    app.state.bg_task_states = {}
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
    allow_methods=["*"],
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


@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, bg_tasks: BackgroundTasks, fastapi_request: Request):
    """
    Process a video and return the results
    """
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
            mcp_client = Client(settings.MCP_SERVER)
            async with mcp_client:
                _ = await mcp_client.call_tool("process_video", {"video_path": request.video_path})
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=500, detail=str(e))
    
    bg_tasks.add_task(background_process_video, request.video_path, task_id)
    return ProcessVideoResponse(message="Task enqued for processing", task_id=task_id)

@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)
    return {"task_id": task_id, "status": status}

@app.post("/chat", response_model=AssitantMessageResponse)
async def chat(request: UserMessageRequest, fastapi_request: Request):
    """
    CHat with the AI assistant
    """
    agent = fastapi_request.app.state.agent
    await agent.setup()

    try:
        response = await agent.chat(request.message, request.video_path, request.image_base64)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/media/{file_path:path}")
async def serve_media(file_path: str):
    """
    serve media files from the shared_media directory
    """
    try:
        clean_path = Path(file_path).name
        media_file = Path("shared_media") / clean_path

        if not media_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(str(media_file))
    except Exception as e:
        logger.error(f"Error serving media file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@click.command()
@click.option("--port", default=8080, help="FastAPI server port")
@click.option("--host", default="0.0.0.0", help="FastAPI server host")
def run_api(port, host):
    import uvicorn

    uvicorn.run("api:app", host=host, port=port, loop="asyncio")

if __name__ == "__main__":
    run_api()