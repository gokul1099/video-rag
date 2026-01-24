from pathlib import Path
import os
def func(video_path):
    video_path_obj = Path(video_path)
    video_path_obj = Path(Path.cwd()/ video_path_obj)
    print(video_path_obj)
   
        
        
func("/shared_media/video.mp4")