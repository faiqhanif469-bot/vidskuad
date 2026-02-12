"""
Video search engine - searches across multiple platforms
"""

import requests
from typing import List, Optional
from src.core.models import VideoResult, Platform
from src.core.config import Config


class VideoSearchEngine:
    """Search for videos across multiple platforms"""
    
    def __init__(self, config: Config):
        self.config = config
        self.pexels_key = config.api.pexels_api_key
        self.pixabay_key = config.api.pixabay_api_key
    
    def search_pexels(self, query: str, max_results: int = 10) -> List[VideoResult]:
        """Search Pexels for videos"""
        if not self.pexels_key:
            return []
        
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": max_results}
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                timeout=self.config.search.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get('videos', []):
                results.append(VideoResult(
                    id=str(video['id']),
                    title=query,
                    url=video['url'],
                    thumbnail=video['image'],
                    duration=video['duration'],
                    source=Platform.PEXELS,
                    description=f"By {video['user']['name']}"
                ))
            
            return results
        except Exception as e:
            print(f"Pexels search error: {e}")
            return []
    
    def search_pixabay(self, query: str, max_results: int = 10) -> List[VideoResult]:
        """Search Pixabay for videos"""
        if not self.pixabay_key:
            return []
        
        url = "https://pixabay.com/api/videos/"
        params = {
            "key": self.pixabay_key,
            "q": query,
            "per_page": max_results
        }
        
        try:
            response = requests.get(
                url, 
                params=params, 
                timeout=self.config.search.timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for video in data.get('hits', []):
                results.append(VideoResult(
                    id=str(video['id']),
                    title=video.get('tags', query),
                    url=video['pageURL'],
                    thumbnail=video.get('userImageURL', ''),
                    duration=video['duration'],
                    source=Platform.PIXABAY,
                    description=f"By {video['user']}"
                ))
            
            return results
        except Exception as e:
            print(f"Pixabay search error: {e}")
            return []
    
    def search_youtube(self, query: str, max_results: int = 10) -> List[VideoResult]:
        """Search YouTube using yt-dlp"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': f'ytsearch{max_results}',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(query, download=False)
                
                results = []
                for entry in search_results.get('entries', [])[:max_results]:
                    if entry:
                        results.append(VideoResult(
                            id=entry.get('id', ''),
                            title=entry.get('title', query),
                            url=f"https://youtube.com/watch?v={entry.get('id', '')}",
                            thumbnail=entry.get('thumbnail', ''),
                            duration=entry.get('duration', 0),
                            source=Platform.YOUTUBE,
                            description=entry.get('description', '')[:200] if entry.get('description') else None
                        ))
                
                return results
        except ImportError:
            print("yt-dlp not installed. Run: pip install yt-dlp")
            return []
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []
    
    def search(self, query: str, platform: Platform, max_results: int = 10) -> List[VideoResult]:
        """Search specific platform"""
        if platform == Platform.PEXELS:
            return self.search_pexels(query, max_results)
        elif platform == Platform.PIXABAY:
            return self.search_pixabay(query, max_results)
        elif platform == Platform.YOUTUBE:
            return self.search_youtube(query, max_results)
        else:
            return []
