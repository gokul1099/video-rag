from typing import Annotated
from uuid import uuid4
from loguru import logger
from pathlib import Path
from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.tools import extract_video_clip
from kubrick_mcp.video.ingestion.video_processor import VideoProcessor
from kubrick_mcp.video.video_search_engine import VideoSearchEngine

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


def get_video_clip_from_user_query(
        video_path: Annotated[str, "The path to the video file"] = "", 
        user_query: Annotated[str, "he user query to search for"] = "") -> Annotated[str,"Path to the extracted video clip"]:
    
    """Get a video clip based on similarity to a provided image.

    Returns:
        str: Path to the extracted video clip.
    """

    search_engine = VideoSearchEngine(video_path)
    logger.info(f"userquery: ---------------------- {user_query}")
    speech_clips = search_engine.search_by_speech(user_query, settings.VIDEO_CLIP_SPEECH_SEARCH_TOP_K)
    caption_clips = search_engine.search_by_caption(user_query, settings.VIDEO_CLIP_CAPTION_SEARCH_TOP_K)

    if not speech_clips and not caption_clips:
        logger.warning(f"No video clips found for query: {user_query}")
        return "No relevant video clips found for your query."

    speech_sim = speech_clips[0]["similarity"] if speech_clips else -1
    caption_sim = caption_clips[0]["similarity"] if caption_clips else -1
    
    logger.info(f"speech clips : {speech_clips}")
    logger.info(f"caption clips : {caption_clips}")
    logger.info(f"speech sim {speech_sim}")
    logger.info(f"caption sim {caption_sim}")
    
    if speech_sim > caption_sim:
        video_clip_info = speech_clips[0]
    else:
        video_clip_info = caption_clips[0]
    shared_media = Path("shared_media")
    shared_media.mkdir(exist_ok=True)
    file_name = f"{str(uuid4())}.mp4"
    output_path= Path(shared_media / file_name )

    video_clip = extract_video_clip(
        video_path=video_path,
        start_time= video_clip_info["start_time"],
        end_time = video_clip_info["end_time"],
        output_path=output_path
    )

    return video_clip.filename

