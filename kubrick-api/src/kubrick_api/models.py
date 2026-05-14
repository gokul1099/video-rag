from pydantic import BaseModel, Field
from enum import Enum
from typing import Dict, Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


class UploadVideoResponse(BaseModel):
    message: str
    video_path: str | None = None
    task_id: str | None = None


class ProcessVideoRequest(BaseModel):
    video_path: str


class ProcessVideoResponse(BaseModel):
    message: str
    task_id: str

class UserMessageRequest(BaseModel):
    message: str
    video_path: str | None = None
    image_base64: str | None = None

class AssitantMessageResponse(BaseModel):
    message: str
    clip_path: str | None =None

class ResetMemoryReponse(BaseModel):
    message: str


class RoutingResponseModel(BaseModel):
    tool_use: bool = Field(
        description="Whether the user's question requires a tool call."
    )

class GeneralResponseModel(BaseModel):
    message: str = Field(
        description="Your response to the user's question, that needs to follow kubric's style and personality"
    )

class VideoClipResponseModel(BaseModel):
    message: str = Field(
        description="A fun and engaging message to the user, asking them to watch the video clip, that need to follow kubrick's style and personality"
    )
    clip_path: str = Field(description="The path to the generated clip")

class ToolChoice(str, Enum):
    PROCESS_VIDEO = "process_video"
    GET_CLIP_FROM_QUERY = "get_video_clip_from_user_query"
    GET_CLIP_FROM_IMAGE = "get_video_clip_from_image"
    ASK_QUESTION = "ask_question_about_video"

class ToolSelectionResponse(BaseModel):
    """Structured response for tool selection"""
    tool_name: ToolChoice = Field(
        description="The specific tool to use based on user intent"
    )
    parameters: Dict[str, Any] = Field(
        description="Parameters to pass to the tool (e.g., {'user_query': '...'} or {'user_query': '...'})",
        default_factory=dict
    )
    reasoning: str = Field(
        description="Why this tool was selected for the user's request"
    )