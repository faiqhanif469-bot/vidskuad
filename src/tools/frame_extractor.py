"""
Enterprise-Grade Frame Extractor
Extract video frames at specific timestamps without full download
"""

import subprocess
import os
import yt_dlp
from typing import List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extract frames from videos at specific timestamps"""
    
    def __init__(self, cache_dir: str = "cache/frames"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_stream_url(self, video_url: str) -> Optional[str]:
        """
        Get direct stream URL without downloading
        
        Args:
            video_url: YouTube video URL
        
        Returns:
            Direct stream URL or None
        """
        try:
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit to 720p for speed
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return info.get('url')
                
        except Exception as e:
            logger.error(f"Error getting stream URL: {e}")
            return None
    
    def extract_frame_at_timestamp(
        self,
        video_url: str,
        timestamp: float,
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Extract single frame at timestamp
        
        Args:
            video_url: YouTube video URL
            timestamp: Timestamp in seconds
            output_path: Output file path (optional)
        
        Returns:
            Path to extracted frame or None
        """
        try:
            # Get stream URL
            stream_url = self.get_stream_url(video_url)
            if not stream_url:
                return None
            
            # Generate output path
            if not output_path:
                video_id = self._extract_video_id(video_url)
                output_path = self.cache_dir / f"{video_id}_{int(timestamp)}.jpg"
            
            # Check cache
            if os.path.exists(output_path):
                logger.info(f"Using cached frame: {output_path}")
                return str(output_path)
            
            # Extract frame using FFmpeg
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),  # Seek to timestamp
                '-i', stream_url,        # Input stream
                '-frames:v', '1',        # Extract 1 frame
                '-q:v', '2',             # Quality (2 = high)
                '-y',                    # Overwrite
                str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Extracted frame at {timestamp}s: {output_path}")
                return str(output_path)
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
            return None
    
    def extract_frames_at_timestamps(
        self,
        video_url: str,
        timestamps: List[float]
    ) -> List[str]:
        """
        Extract multiple frames from same video
        
        Args:
            video_url: YouTube video URL
            timestamps: List of timestamps in seconds
        
        Returns:
            List of frame paths
        """
        frames = []
        
        # Get stream URL once
        stream_url = self.get_stream_url(video_url)
        if not stream_url:
            return []
        
        video_id = self._extract_video_id(video_url)
        
        for timestamp in timestamps:
            output_path = self.cache_dir / f"{video_id}_{int(timestamp)}.jpg"
            
            # Check cache
            if os.path.exists(output_path):
                frames.append(str(output_path))
                continue
            
            # Extract frame
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', stream_url,
                '-frames:v', '1',
                '-q:v', '2',
                '-y',
                str(output_path)
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0 and os.path.exists(output_path):
                    frames.append(str(output_path))
                    logger.info(f"Extracted frame at {timestamp}s")
                    
            except Exception as e:
                logger.error(f"Error extracting frame at {timestamp}s: {e}")
        
        return frames
    
    def extract_sample_frames(
        self,
        video_url: str,
        num_frames: int = 5,
        duration: Optional[float] = None
    ) -> List[str]:
        """
        Extract evenly spaced sample frames
        
        Args:
            video_url: YouTube video URL
            num_frames: Number of frames to extract
            duration: Video duration (will fetch if not provided)
        
        Returns:
            List of frame paths
        """
        try:
            # Get duration if not provided
            if duration is None:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    duration = info.get('duration', 0)
            
            if duration <= 0:
                return []
            
            # Calculate timestamps
            interval = duration / (num_frames + 1)
            timestamps = [interval * (i + 1) for i in range(num_frames)]
            
            # Extract frames
            return self.extract_frames_at_timestamps(video_url, timestamps)
            
        except Exception as e:
            logger.error(f"Error extracting sample frames: {e}")
            return []
    
    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from URL"""
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            if 'v=' in video_url:
                return video_url.split('v=')[1].split('&')[0]
            elif 'youtu.be/' in video_url:
                return video_url.split('youtu.be/')[1].split('?')[0]
        return video_url
    
    def clear_cache(self):
        """Clear frame cache"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Cleared frame cache")


if __name__ == '__main__':
    extractor = FrameExtractor()
    
    video_url = "https://www.youtube.com/watch?v=gm3IIIVCKR8"
    
    # Extract frame at 155 seconds
    frame = extractor.extract_frame_at_timestamp(video_url, 155)
    
    if frame:
        print(f"Extracted frame: {frame}")
    
    # Extract multiple frames
    frames = extractor.extract_frames_at_timestamps(video_url, [100, 155, 200])
    print(f"Extracted {len(frames)} frames")
