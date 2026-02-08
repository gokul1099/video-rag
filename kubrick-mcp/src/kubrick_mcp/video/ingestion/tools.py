import base64
import subprocess
from io import BytesIO
from pathlib import Path

import av
import loguru
from moviepy import VideoFileClip
from PIL import Image
import os

logger = loguru.logger.bind(name="VideoTools")

def extract_video_clip(video_path:str, start_time: float, end_time: float, output_path: str = None) -> VideoFileClip:
    if start_time >= end_time:
        return ValueError("start_time must be less than end_time")
    if not Path(video_path).exists():
        logger.error(f"Input video file not found: {video_path} (Absolute: {Path(video_path).resolve()})")
        raise FileNotFoundError(f"Input video file not found: {video_path}")

    logger.info(f"Extracting video clip from {video_path} ({start_time}-{end_time}) to {output_path}")
    
    ## Anatomy of FFMPEG command
    # -i = input file
    # -ss/-to = start and end time of the clip, formatted as seconds or hh:mm:ss
    # -c (:v, :a) = sets the codec for the audio, and video channels
    # -preset = encoding speed/quality split
    # last argument is the output video path (if using libx264, it must end with .mp4)

    command = [
        "ffmpeg",
        "-ss",
        str(start_time),
        "-to",
        str(end_time),
        "-i",
        str(video_path),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-c:a",
        "copy",
        "-y",
        str(output_path)
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors="ignore")
            logger.error(f"FFmpeg failed with return code {process.returncode}")
            logger.error(f"FFmpeg stderr: {error_msg}")
            raise IOError(f"FFmpeg failed: {error_msg}")

        logger.debug(f"FFmpeg output: {stdout.decode('utf-8', errors='ignore')}")
        
        if not Path(output_path).exists():
             raise FileNotFoundError(f"FFmpeg completed but output file not found at {output_path}")

        return VideoFileClip(str(output_path))
    except Exception as e:
        logger.error(f"Failed to extract video clip: {str(e)}")
        raise
    

def encode_image(image:str | Image.Image) -> str:
    """
    Encode an image to base64 string
    """
    try:
        if isinstance(image,str):
            with open(image, "rb") as image_file:
                image_str = image_file.read()
        else:
            if not image.format:
                image_format = "JPEG"
            else:
                image_format=image.format
            buffered = BytesIO()
            image.save(buffered, format=image_format)
            image_str = buffered.getvalue()
        return base64.b64encode(image_str).decode("utf-8")
    except (FileNotFoundError, IOError) as e:
        raise IOError(f"Failed to process image: {str(e)}")
    
def decode_image(base64_string: str) -> Image.Image:
    """
    Decode a base64 image to PIL image object
    """
    try:
        image_bytes = base64.b64decode(base64_string)
        image_buffer = BytesIO(image_bytes)
        return Image.open(image_buffer)
    except (ValueError, IOError) as e:
        raise IOError(f"Failed to decode image {str(e)}")

def re_encode_video(video_path: str) -> str | bool:
    """
    re-encode a video file to ensure compatibility with PyAV.
    Note: Incase a video was downloaded from the web, it may not be compatible with PyAV.
    This function attempt to re-encode the video using FFmpeg and return the path to the re-encoded video
    """
    if not Path(video_path).exists():
        logger.error(f"Error: Video file not found at {video_path}")
        return False

    try:
        with av.open(video_path) as _:
            logger.info(f"Video {video_path} successfully opened by PyAV")
            return str(video_path)
    except Exception as e:
        logger.warning(f"PyAV couldn't open video {video_path}: {e}. Attempting re-encode...")
        
        # Re-encode the video
        o_dir, o_fname = Path(video_path).parent, Path(video_path).stem
        o_ext = Path(video_path).suffix
        reencoded_file_name = f're_{o_fname}{o_ext}'
        reencoded_video_path = Path(o_dir) / reencoded_file_name
        
        # Re-encode to H.264 + AAC for maximum compatibility
        command = [
            "ffmpeg",
            "-i", str(video_path),
            "-c:v", "libx264",           # Re-encode video to H.264
            "-preset", "fast",           # Encoding speed preset
            "-crf", "23",                # Quality (lower = better, 18-28 is good range)
            "-c:a", "aac",               # Re-encode audio to AAC
            "-b:a", "128k",              # Audio bitrate
            "-movflags", "+faststart",   # Enable streaming
            "-y",                        # Overwrite output file if exists
            str(reencoded_video_path)
        ]
        
        logger.info(f"Attempting to re-encode video using FFmpeg: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=300  # 5 minute timeout for long videos
            )
            logger.info(f"FFmpeg re-encoding successful for {video_path} to {reencoded_file_name}")
            logger.debug(f"FFmpeg stderr: {result.stderr}")

            try:
                with av.open(str(reencoded_video_path)):
                    logger.info(f"Re-encoded video {reencoded_video_path} successfully opened by PyAV")
                    return str(reencoded_video_path)
            except Exception as e:
                logger.error(
                    f"Re-encoded video {reencoded_video_path} still can't be opened by PyAV: {e}"
                )
                return None
                
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg re-encoding failed with exit code {e.returncode}")
            logger.error(f"FFmpeg stderr: {e.stderr}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg re-encoding timed out after 5 minutes")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during FFmpeg re-encoding: {e}")
            return None