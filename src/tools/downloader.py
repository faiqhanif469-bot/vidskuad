"""
Video downloader - downloads videos from various platforms
"""

import os
from pathlib import Path
from typing import Optional
from src.core.models import VideoResult, Platform


class VideoDownloader:
    """Download videos from various platforms"""
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_youtube(self, video: VideoResult, output_name: Optional[str] = None) -> Optional[str]:
        """Download YouTube video using yt-dlp"""
        try:
            import yt_dlp
            
            if output_name is None:
                output_name = f"{video.id}.mp4"
            
            output_path = self.output_dir / output_name
            
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': str(output_path),
                'quiet': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video.url])
            
            return str(output_path)
        except Exception as e:
            print(f"Download error: {e}")
            return None
    
    def download(self, video: VideoResult, output_name: Optional[str] = None) -> Optional[str]:
        """Download video based on platform"""
        if video.source == Platform.YOUTUBE:
            return self.download_youtube(video, output_name)
        else:
            print(f"Download not implemented for {video.source.value}")
            return None
