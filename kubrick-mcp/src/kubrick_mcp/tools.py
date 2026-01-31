from typing import Dict
from uuid import uuid4
from loguru import logger

from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.tools import extract_video_clip
from kubrick_mcp.video.ingestion.video_processor import VideoProcessor

logger = logger.bind(name="MCPVideoTools")
video_processor = VideoProcessor()

settings = get_settings()

def process_video(video_path: str) -> str | bool:
    """
    Process a video file and prepare it for searching
    """

    exists = video_processor._check_if_exists(video_path=video_path)
    if exists:
        logger.info(f"Video index for {video_path} is alreadt exists and ready for use")
        return False
    video_processor.setup_table(video_name=video_path)
    is_done = video_processor.add_video(video_path=video_path)
    logger.info(f"Done processing returning response {is_done}")
    return is_done