"""
CrewAI tools for video search
"""

from crewai.tools import tool
from typing import List, Dict
from src.core.config import Config
from src.core.models import Platform
from src.tools.search_engine import VideoSearchEngine


# Initialize search engine (will be set by crew)
_search_engine = None


def initialize_search_tools(config: Config):
    """Initialize search engine for tools"""
    global _search_engine
    _search_engine = VideoSearchEngine(config)


@tool("Search YouTube for videos")
def search_youtube(query: str) -> str:
    """
    Search YouTube for videos matching the query.
    Returns a list of video results with titles, URLs, and descriptions.
    
    Args:
        query: Search query (be specific! e.g., "1950s factory workers assembly line")
    
    Returns:
        Formatted string with video results
    """
    if not _search_engine:
        return "Error: Search engine not initialized"
    
    results = _search_engine.search_youtube(query, max_results=5)
    
    if not results:
        return f"No YouTube videos found for: {query}"
    
    output = f"Found {len(results)} YouTube videos for '{query}':\n\n"
    for i, video in enumerate(results, 1):
        output += f"{i}. {video.title}\n"
        output += f"   URL: {video.url}\n"
        output += f"   Duration: {video.duration}s\n"
        if video.description:
            output += f"   Description: {video.description[:150]}...\n"
        output += "\n"
    
    return output


@tool("Search Pexels for stock videos")
def search_pexels(query: str) -> str:
    """
    Search Pexels for high-quality stock videos.
    Best for: Modern footage, professional quality, diverse subjects.
    
    Args:
        query: Search query (e.g., "solar panels sunny day", "wildfire drone footage")
    
    Returns:
        Formatted string with video results
    """
    if not _search_engine:
        return "Error: Search engine not initialized"
    
    results = _search_engine.search_pexels(query, max_results=5)
    
    if not results:
        return f"No Pexels videos found for: {query}"
    
    output = f"Found {len(results)} Pexels videos for '{query}':\n\n"
    for i, video in enumerate(results, 1):
        output += f"{i}. {video.title}\n"
        output += f"   URL: {video.url}\n"
        output += f"   Duration: {video.duration}s\n"
        output += f"   {video.description}\n\n"
    
    return output


@tool("Search Pixabay for free stock videos")
def search_pixabay(query: str) -> str:
    """
    Search Pixabay for free stock videos.
    Best for: Diverse content, free usage, various quality levels.
    
    Args:
        query: Search query (e.g., "community garden", "wind turbines")
    
    Returns:
        Formatted string with video results
    """
    if not _search_engine:
        return "Error: Search engine not initialized"
    
    results = _search_engine.search_pixabay(query, max_results=5)
    
    if not results:
        return f"No Pixabay videos found for: {query}"
    
    output = f"Found {len(results)} Pixabay videos for '{query}':\n\n"
    for i, video in enumerate(results, 1):
        output += f"{i}. {video.title}\n"
        output += f"   URL: {video.url}\n"
        output += f"   Duration: {video.duration}s\n"
        output += f"   {video.description}\n\n"
    
    return output


@tool("Search all platforms for videos")
def search_all_platforms(query: str) -> str:
    """
    Search YouTube, Pexels, and Pixabay simultaneously for videos.
    Use this when you want to compare results across platforms.
    
    Args:
        query: Search query
    
    Returns:
        Formatted string with results from all platforms
    """
    if not _search_engine:
        return "Error: Search engine not initialized"
    
    output = f"Searching all platforms for: '{query}'\n"
    output += "=" * 80 + "\n\n"
    
    # YouTube
    yt_results = _search_engine.search_youtube(query, max_results=3)
    output += f"YOUTUBE ({len(yt_results)} results):\n"
    for i, video in enumerate(yt_results, 1):
        output += f"  {i}. {video.title} - {video.url}\n"
    output += "\n"
    
    # Pexels
    pexels_results = _search_engine.search_pexels(query, max_results=3)
    output += f"PEXELS ({len(pexels_results)} results):\n"
    for i, video in enumerate(pexels_results, 1):
        output += f"  {i}. {video.title} - {video.url}\n"
    output += "\n"
    
    # Pixabay
    pixabay_results = _search_engine.search_pixabay(query, max_results=3)
    output += f"PIXABAY ({len(pixabay_results)} results):\n"
    for i, video in enumerate(pixabay_results, 1):
        output += f"  {i}. {video.title} - {video.url}\n"
    output += "\n"
    
    total = len(yt_results) + len(pexels_results) + len(pixabay_results)
    output += f"Total: {total} videos found across all platforms\n"
    
    return output


# Export all tools
SEARCH_TOOLS = [
    search_youtube,
    search_pexels,
    search_pixabay,
    search_all_platforms
]
