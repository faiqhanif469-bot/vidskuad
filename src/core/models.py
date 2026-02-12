"""
Data models for AI Video Production System
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum


class Platform(Enum):
    """Video platforms"""
    YOUTUBE = "youtube"
    PEXELS = "pexels"
    PIXABAY = "pixabay"
    BRITISH_PATHE = "british_pathe"
    AP_ARCHIVE = "ap_archive"
    INTERNET_ARCHIVE = "internet_archive"


class Priority(Enum):
    """Search query priority"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SearchQuery:
    """Search query with metadata"""
    query: str
    reasoning: str
    priority: Priority
    platform: Platform
    validated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': self.query,
            'reasoning': self.reasoning,
            'priority': self.priority.value,
            'platform': self.platform.value,
            'validated': self.validated
        }


@dataclass
class Scene:
    """Video scene with requirements"""
    scene_number: int
    scene_description: str
    duration_seconds: float
    visual_context: str
    mood_tone: str
    required_clips: int
    search_queries: List[SearchQuery]
    keywords: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'scene_number': self.scene_number,
            'scene_description': self.scene_description,
            'duration_seconds': self.duration_seconds,
            'visual_context': self.visual_context,
            'mood_tone': self.mood_tone,
            'required_clips': self.required_clips,
            'search_queries': [q.to_dict() for q in self.search_queries],
            'keywords': self.keywords
        }


@dataclass
class ProductionPlan:
    """Complete video production plan"""
    title: str
    total_duration: float
    overall_theme: str
    target_audience: str
    visual_style: str
    scenes: List[Scene]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'title': self.title,
            'total_duration': self.total_duration,
            'overall_theme': self.overall_theme,
            'target_audience': self.target_audience,
            'visual_style': self.visual_style,
            'scenes': [s.to_dict() for s in self.scenes]
        }


@dataclass
class VideoResult:
    """Video search result"""
    id: str
    title: str
    url: str
    thumbnail: str
    duration: int
    source: Platform
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'thumbnail': self.thumbnail,
            'duration': self.duration,
            'source': self.source.value,
            'description': self.description
        }


@dataclass
class ScriptAnalysis:
    """Initial script analysis"""
    overall_theme: str
    emotional_arc: str
    target_audience: str
    visual_style: str
    key_moments: List[str]
    pacing_notes: str
