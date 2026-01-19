from pydantic import BaseModel, Field



class UploadVideoResponse(BaseModel):
    message: str
    video_path: str | None = None
    task_id: str | None = None

    