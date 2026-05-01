from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from enum import Enum
import click
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastmcp.client import Client
from loguru import logger
from  kubrick_api.models import UploadVideoResponse, ProcessVideoRequest, ProcessVideoResponse, AssitantMessageResponse, UserMessageRequest
import shutil
from kubrick_api.config import get_settings
from kubrick_api.agent import GroqAgent
from kubrick_api.db.db import get_db_manager, get_db
from fastapi import HTTPException
from kubrick_api.routes import AuthRouter, ChatRouter, VideoRouter

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
    db=get_db_manager()
    db.init_db()
    logger.info("Database initialized")

    app.state.bg_task_states = {}
    yield
    app.state.agent.reset_memory()
    db = get_db_manager()
    db.shutdown()


app = FastAPI(
    title="Kubric API",
    description="An AI-powered sports assitant API using OpenAI",
    docs_url="/docs",
    lifespan=lifespan
)

app.include_router(AuthRouter, prefix="")
app.include_router(ChatRouter, prefix="")
app.include_router(VideoRouter, prefix="")


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


@click.command()
@click.option("--port", default=8080, help="FastAPI server port")
@click.option("--host", default="0.0.0.0", help="FastAPI server host")
def run_api(port, host):
    import uvicorn

    uvicorn.run("api:app", host=host, port=port, loop="asyncio")

if __name__ == "__main__":
    run_api()