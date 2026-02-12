"""
Automated Video Finder for Clean Archive Channels
Searches the 15 watermark-free channels and finds perfect clips
"""

import yt_dlp
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChannelInfo:
    """Clean archive channel information"""
    name: str
    handle: str
    url: str
    tier: int
    categories: List[str]
    time_periods: List[str]
    best_for: List[str]


class ChannelVideoFinder:
    """Find videos from our 15 clean archive channels"""
    
    def __init__(self):
        self.channels = self._load_channels()
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',  # Fast extraction for channel videos
            'playlistend': 50,  # Limit to recent 50 videos per channel
        }
    
    def _load_channels(self) -> List[ChannelInfo]:
        """Load our 15 clean archive channels"""
        return [
            # TIER 1 - Must Use
            ChannelInfo(
                name="Periscope Film",
                handle="@PeriscopeFilm",
                url="https://www.youtube.com/@PeriscopeFilm",
                tier=1,
                categories=["war", "military", "aviation", "disasters", "cold_war"],
                time_periods=["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["military", "aviation", "industrial", "cold war", "disasters"]
            ),
            ChannelInfo(
                name="A/V Geeks",
                handle="@avgeeks",
                url="https://www.youtube.com/@avgeeks",
                tier=1,
                categories=["culture", "education", "technology", "social"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["culture", "social movements", "technology", "education"]
            ),
            ChannelInfo(
                name="U.S. National Archives",
                handle="@usnationalarchives",
                url="https://www.youtube.com/@usnationalarchives",
                tier=1,
                categories=["war", "military", "politics", "news", "space"],
                time_periods=["1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["military", "politics", "news events", "early space"]
            ),
            ChannelInfo(
                name="NASA",
                handle="@NASA",
                url="https://www.youtube.com/@NASA",
                tier=1,
                categories=["space", "science", "technology"],
                time_periods=["1950s", "1960s", "1970s", "1980s", "1990s"],
                best_for=["space race", "science", "technology"]
            ),
            ChannelInfo(
                name="Library of Congress",
                handle="@libraryofcongress",
                url="https://www.youtube.com/@libraryofcongress",
                tier=1,
                categories=["culture", "politics", "early_history"],
                time_periods=["1890s", "1900s", "1910s", "1920s", "1930s"],
                best_for=["early culture", "events", "inventions"]
            ),
            ChannelInfo(
                name="Computer History Museum",
                handle="@ComputerHistory",
                url="https://www.youtube.com/@ComputerHistory",
                tier=1,
                categories=["technology", "science"],
                time_periods=["1950s", "1960s", "1970s", "1980s", "1990s"],
                best_for=["technology", "inventions", "computers"]
            ),
            
            # TIER 2 - Good to Use
            ChannelInfo(
                name="FootageArchive",
                handle="@FootageArchive",
                url="https://www.youtube.com/@FootageArchive",
                tier=2,
                categories=["war", "politics", "general"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["general historical", "wars", "politics"]
            ),
            ChannelInfo(
                name="PublicDomainFootage",
                handle="@PublicDomainFootage",
                url="https://www.youtube.com/@PublicDomainFootage",
                tier=2,
                categories=["war", "culture", "technology"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s"],
                best_for=["wars", "fashion", "inventions"]
            ),
            ChannelInfo(
                name="Travel Film Archive",
                handle="@travelfilmarchive",
                url="https://www.youtube.com/@travelfilmarchive",
                tier=2,
                categories=["culture", "travel"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s"],
                best_for=["culture", "travel", "society"]
            ),
            ChannelInfo(
                name="Public Domain Archive",
                handle="@publicdomainarchive1",
                url="https://www.youtube.com/@publicdomainarchive1",
                tier=2,
                categories=["general"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s"],
                best_for=["rare vintage clips"]
            ),
            ChannelInfo(
                name="4K Historical Footage",
                handle="@4khistoricalfootage",
                url="https://www.youtube.com/@4khistoricalfootage",
                tier=2,
                categories=["general"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s"],
                best_for=["archive collections", "upscaled vintage"]
            ),
            ChannelInfo(
                name="Buyout Footage",
                handle="@buyoutfootage",
                url="https://www.youtube.com/@buyoutfootage",
                tier=2,
                categories=["general"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s"],
                best_for=["public domain stock"]
            ),
            
            # NEW TIER 1 CHANNELS - High Quality Archives
            ChannelInfo(
                name="British Pathé",
                handle="@britishpathe",
                url="https://www.youtube.com/@britishpathe",
                tier=1,
                categories=["uk_history", "news", "culture", "fashion", "industry", "royal"],
                time_periods=["1890s", "1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s"],
                best_for=["UK history", "British newsreels", "royal family", "fashion", "high street", "British industry", "daily life"]
            ),
            ChannelInfo(
                name="Public Resource",
                handle="@PublicResourceOrg",
                url="https://www.youtube.com/@PublicResourceOrg",
                tier=1,
                categories=["government", "cold_war", "industry", "technology", "social"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["US government films", "Cold War", "industry", "technology", "social issues"]
            ),
            ChannelInfo(
                name="The Film Detective",
                handle="@thefilmdetective",
                url="https://www.youtube.com/@thefilmdetective",
                tier=1,
                categories=["cinema", "news", "culture"],
                time_periods=["1920s", "1930s", "1940s", "1950s", "1960s"],
                best_for=["classic films", "newsreels", "historical events", "restored footage"]
            ),
            ChannelInfo(
                name="Internet Archive",
                handle="@internetarchive",
                url="https://www.youtube.com/@internetarchive",
                tier=1,
                categories=["general", "rare", "culture"],
                time_periods=["1890s", "1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["rare footage", "public domain", "diverse content"]
            ),
            
            # TIER 2 - Corporate & Industry Archives
            ChannelInfo(
                name="AT&T Tech Channel",
                handle="@atttechchannel",
                url="https://www.youtube.com/@atttechchannel",
                tier=2,
                categories=["technology", "corporate", "industry"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["vintage tech", "corporate films", "telecommunications"]
            ),
            ChannelInfo(
                name="GM Heritage Center",
                handle="@gmheritagecenter",
                url="https://www.youtube.com/@gmheritagecenter",
                tier=2,
                categories=["automotive", "industry", "manufacturing"],
                time_periods=["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["automotive history", "manufacturing", "industrial decline"]
            ),
            ChannelInfo(
                name="Ford Motor Company",
                handle="@ford",
                url="https://www.youtube.com/@ford",
                tier=2,
                categories=["automotive", "industry", "corporate"],
                time_periods=["1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["automotive", "promotional films", "manufacturing"]
            ),
            
            # TIER 2 - TV & Commercial Archives
            ChannelInfo(
                name="Rick88888888",
                handle="@rick88888888",
                url="https://www.youtube.com/@rick88888888",
                tier=2,
                categories=["tv", "commercials", "uk_culture"],
                time_periods=["1950s", "1960s", "1970s", "1980s", "1990s"],
                best_for=["British TV", "old commercials", "nostalgic UK content"]
            ),
            ChannelInfo(
                name="Classic TV Commercials",
                handle="@bionic70",
                url="https://www.youtube.com/@bionic70",
                tier=2,
                categories=["commercials", "advertising", "brands"],
                time_periods=["1950s", "1960s", "1970s", "1980s", "1990s"],
                best_for=["vintage commercials", "brand history", "advertising"]
            ),
            
            # TIER 2 - International Archives
            ChannelInfo(
                name="Bundesarchiv",
                handle="@bundesarchiv",
                url="https://www.youtube.com/@bundesarchiv",
                tier=2,
                categories=["german_history", "european", "war"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s"],
                best_for=["German history", "European history", "Creative Commons"]
            ),
            ChannelInfo(
                name="National Film Board of Canada",
                handle="@NFB",
                url="https://www.youtube.com/@NFB",
                tier=2,
                categories=["canadian", "documentary", "culture"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s"],
                best_for=["Canadian documentaries", "high quality", "Creative Commons"]
            ),
            
            # FOOD & COOKING
            ChannelInfo(
                name="Food Wishes",
                handle="@foodwishes",
                url="https://www.youtube.com/@foodwishes",
                tier=2,
                categories=["food", "cooking", "recipes"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["cooking tutorials", "recipes", "food preparation"]
            ),
            ChannelInfo(
                name="Yeung Man Cooking",
                handle="@YEUNGMANCOOKING",
                url="https://www.youtube.com/@YEUNGMANCOOKING",
                tier=2,
                categories=["food", "cooking", "vegan"],
                time_periods=["2010s", "2020s"],
                best_for=["vegan cooking", "plant-based recipes", "Asian cuisine"]
            ),
            
            # HEALTH & FITNESS
            ChannelInfo(
                name="Nucleus Medical Media",
                handle="@nucleusmedicalmedia",
                url="https://www.youtube.com/@nucleusmedicalmedia",
                tier=1,
                categories=["health", "medical", "science", "anatomy"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["medical animations", "health education", "anatomy", "diseases"]
            ),
            ChannelInfo(
                name="The Anatomy Lab",
                handle="@theanatomylab",
                url="https://www.youtube.com/@theanatomylab",
                tier=1,
                categories=["health", "anatomy", "medical", "education"],
                time_periods=["2010s", "2020s"],
                best_for=["human anatomy", "medical education", "body systems"]
            ),
            ChannelInfo(
                name="SciShow",
                handle="@SciShow",
                url="https://www.youtube.com/@SciShow",
                tier=1,
                categories=["science", "health", "education", "nature"],
                time_periods=["2010s", "2020s"],
                best_for=["science education", "health topics", "nature", "research"]
            ),
            
            # VEHICLES & AUTOMOTIVE
            ChannelInfo(
                name="Fully Charged Show",
                handle="@fullychargedshow",
                url="https://www.youtube.com/@fullychargedshow",
                tier=2,
                categories=["automotive", "electric_vehicles", "technology", "sustainability"],
                time_periods=["2010s", "2020s"],
                best_for=["electric vehicles", "EV technology", "sustainable transport"]
            ),
            ChannelInfo(
                name="BYD Company",
                handle="@BYDCompany",
                url="https://www.youtube.com/@BYDCompany",
                tier=2,
                categories=["automotive", "electric_vehicles", "manufacturing"],
                time_periods=["2010s", "2020s"],
                best_for=["electric vehicles", "Chinese automotive", "EV manufacturing"]
            ),
            
            # MANUFACTURING & INDUSTRIAL
            ChannelInfo(
                name="Business Insider",
                handle="@BusinessInsider",
                url="https://www.youtube.com/@BusinessInsider",
                tier=1,
                categories=["business", "manufacturing", "industry", "technology"],
                time_periods=["2010s", "2020s"],
                best_for=["manufacturing processes", "business", "industry insights"]
            ),
            ChannelInfo(
                name="Free Documentary",
                handle="@FreeDocumentary",
                url="https://www.youtube.com/@FreeDocumentary",
                tier=1,
                categories=["documentary", "history", "science", "nature", "culture"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["documentaries", "history", "science", "nature"]
            ),
            ChannelInfo(
                name="National Geographic",
                handle="@NatGeo",
                url="https://www.youtube.com/@NatGeo",
                tier=1,
                categories=["nature", "science", "geography", "culture", "wildlife"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["nature", "wildlife", "geography", "exploration"]
            ),
            ChannelInfo(
                name="Process X",
                handle="@processx",
                url="https://www.youtube.com/@processx",
                tier=2,
                categories=["manufacturing", "industrial", "processes"],
                time_periods=["2010s", "2020s"],
                best_for=["manufacturing processes", "industrial production", "how things are made"]
            ),
            
            # AVIATION & AEROSPACE
            ChannelInfo(
                name="Smithsonian Channel",
                handle="@SmithsonianChannel",
                url="https://www.youtube.com/@SmithsonianChannel",
                tier=1,
                categories=["aviation", "aerospace", "history", "science", "culture"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["aviation history", "aerospace", "American history", "science"]
            ),
            ChannelInfo(
                name="European Space Agency",
                handle="@EuropeanSpaceAgency",
                url="https://www.youtube.com/@EuropeanSpaceAgency",
                tier=1,
                categories=["space", "aerospace", "science", "technology"],
                time_periods=["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["space exploration", "satellites", "European space programs"]
            ),
            
            # MILITARY & WAR
            ChannelInfo(
                name="NATO",
                handle="@NATO",
                url="https://www.youtube.com/@NATO",
                tier=2,
                categories=["military", "defense", "international"],
                time_periods=["1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["NATO operations", "military alliance", "defense"]
            ),
            
            # NAVY & MARITIME
            ChannelInfo(
                name="US Navy",
                handle="@USNavy",
                url="https://www.youtube.com/@USNavy",
                tier=1,
                categories=["military", "navy", "maritime", "defense"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["naval operations", "ships", "maritime", "US military"]
            ),
            ChannelInfo(
                name="Royal Navy",
                handle="@RoyalNavy",
                url="https://www.youtube.com/@RoyalNavy",
                tier=1,
                categories=["military", "navy", "maritime", "defense", "uk"],
                time_periods=["1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["British naval operations", "ships", "maritime", "UK military"]
            ),
            
            # CITIES & TRAVEL
            ChannelInfo(
                name="4K Urban Life",
                handle="@4KUrbanLife",
                url="https://www.youtube.com/@4KUrbanLife",
                tier=2,
                categories=["cities", "urban", "travel", "culture"],
                time_periods=["2010s", "2020s"],
                best_for=["city walks", "urban exploration", "street scenes"]
            ),
            ChannelInfo(
                name="J Utah",
                handle="@JUtah",
                url="https://www.youtube.com/@JUtah",
                tier=2,
                categories=["cities", "urban", "travel"],
                time_periods=["2010s", "2020s"],
                best_for=["city tours", "urban landscapes", "travel"]
            ),
            ChannelInfo(
                name="Expoza Travel",
                handle="@ExpozaTravel",
                url="https://www.youtube.com/@ExpozaTravel",
                tier=2,
                categories=["travel", "cities", "culture"],
                time_periods=["2010s", "2020s"],
                best_for=["travel videos", "destinations", "cultural exploration"]
            ),
            
            # SCIENCE & NATURE
            ChannelInfo(
                name="BBC Earth",
                handle="@BBCEarth",
                url="https://www.youtube.com/@BBCEarth",
                tier=1,
                categories=["nature", "wildlife", "science", "documentary"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["nature documentaries", "wildlife", "planet Earth"]
            ),
            ChannelInfo(
                name="KQED Deep Look",
                handle="@KQEDDeepLook",
                url="https://www.youtube.com/@KQEDDeepLook",
                tier=1,
                categories=["nature", "science", "wildlife", "microscopic"],
                time_periods=["2010s", "2020s"],
                best_for=["microscopic nature", "insects", "wildlife close-ups"]
            ),
            
            # ARCHITECTURE & REAL ESTATE
            ChannelInfo(
                name="Amazing Architecture",
                handle="@AmazingArchitecture",
                url="https://www.youtube.com/@AmazingArchitecture",
                tier=2,
                categories=["architecture", "design", "buildings"],
                time_periods=["2010s", "2020s"],
                best_for=["modern architecture", "building design", "architectural tours"]
            ),
            
            # GENERAL NEWS & MEDIA
            ChannelInfo(
                name="Reuters",
                handle="@Reuters",
                url="https://www.youtube.com/@Reuters",
                tier=1,
                categories=["news", "current_events", "international", "business"],
                time_periods=["2000s", "2010s", "2020s"],
                best_for=["news footage", "current events", "international news"]
            ),
            ChannelInfo(
                name="AP Archive",
                handle="@APArchive",
                url="https://www.youtube.com/@APArchive",
                tier=1,
                categories=["news", "history", "current_events"],
                time_periods=["1900s", "1910s", "1920s", "1930s", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["historical news", "news archive", "major events"]
            ),
            ChannelInfo(
                name="ESPN",
                handle="@espn",
                url="https://www.youtube.com/@espn",
                tier=2,
                categories=["sports", "athletics", "competition"],
                time_periods=["1980s", "1990s", "2000s", "2010s", "2020s"],
                best_for=["sports highlights", "athletics", "competitions"]
            ),
        ]
    
    def select_channels_for_scene(self, scene: Dict) -> List[ChannelInfo]:
        """
        Intelligently select which channels to search based on scene requirements
        
        Args:
            scene: Scene dict with keywords, visual_context, etc.
        
        Returns:
            List of channels ranked by relevance
        """
        keywords = scene.get('keywords', [])
        visual_context = scene.get('visual_context', '').lower()
        mood = scene.get('mood_tone', '').lower()
        
        # Combine all text for matching
        scene_text = ' '.join(keywords).lower() + ' ' + visual_context + ' ' + mood
        
        # Score each channel
        channel_scores = []
        for channel in self.channels:
            score = 0
            
            # Category matching (high weight)
            for category in channel.categories:
                if category.replace('_', ' ') in scene_text:
                    score += 10
            
            # Best-for matching (highest weight)
            for best in channel.best_for:
                if best in scene_text:
                    score += 15
            
            # Tier bonus (prefer tier 1)
            if channel.tier == 1:
                score += 5
            
            channel_scores.append((channel, score))
        
        # Sort by score
        channel_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top channels with score > 0, or top 3 if none match
        relevant = [ch for ch, score in channel_scores if score > 0]
        if not relevant:
            relevant = [ch for ch, _ in channel_scores[:3]]
        
        return relevant[:5]  # Limit to top 5 channels
    
    def search_channel_videos(
        self, 
        channel: ChannelInfo, 
        search_query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Search a specific channel for videos matching the query
        
        Args:
            channel: Channel to search
            search_query: Search keywords
            max_results: Max videos to return
        
        Returns:
            List of video metadata dicts
        """
        print(f"  🔍 Searching {channel.name} for: {search_query}")
        
        try:
            # Use yt-dlp to search the channel
            search_url = f"{channel.url}/search?query={search_query.replace(' ', '+')}"
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract channel search results
                result = ydl.extract_info(search_url, download=False)
                
                if not result or 'entries' not in result:
                    print(f"    ⚠️  No results from {channel.name}")
                    return []
                
                videos = []
                for entry in result['entries']:
                    if not entry:
                        continue
                    
                    # Skip playlists (they start with PL)
                    video_id = entry.get('id', '')
                    if video_id.startswith('PL') or video_id.startswith('UU'):
                        continue
                    
                    # Skip if no duration (likely a playlist)
                    if not entry.get('duration'):
                        continue
                    
                    # Build video dict from flat extraction
                    videos.append({
                        'id': video_id,
                        'title': entry.get('title', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'duration': entry.get('duration', 0),
                        'description': entry.get('description', ''),
                        'tags': [],  # Not available in flat extraction
                        'views': entry.get('view_count', 0),
                        'upload_date': entry.get('upload_date', ''),
                        'thumbnail': entry.get('thumbnail', ''),
                        'channel': channel.name,
                        'channel_handle': channel.handle,
                        'channel_tier': channel.tier,
                        'platform': 'youtube',
                    })
                    
                    if len(videos) >= max_results:
                        break
                
                print(f"    ✅ Found {len(videos)} videos from {channel.name}")
                return videos
                
        except Exception as e:
            print(f"    ❌ Error searching {channel.name}: {e}")
            return []
    
    def find_videos_for_scene(
        self, 
        scene: Dict,
        max_videos_per_channel: int = 10
    ) -> List[Dict]:
        """
        Find best videos for a scene from our clean channels
        
        Args:
            scene: Scene dict from production plan
            max_videos_per_channel: Max videos to get from each channel
        
        Returns:
            List of candidate videos with metadata
        """
        print(f"\n🎬 Finding videos for Scene {scene.get('scene_number')}:")
        print(f"   Description: {scene.get('scene_description', '')[:80]}...")
        
        # 1. Select relevant channels
        relevant_channels = self.select_channels_for_scene(scene)
        print(f"   📺 Selected {len(relevant_channels)} channels:")
        for ch in relevant_channels:
            print(f"      - {ch.name} (Tier {ch.tier})")
        
        # 2. Get search queries from scene
        search_queries = scene.get('search_queries', [])
        if not search_queries:
            # Fallback to keywords
            keywords = scene.get('keywords', [])
            if keywords:
                search_queries = [{'query': ' '.join(keywords), 'priority': 'medium'}]
        
        # 3. Search each channel
        all_videos = []
        for query_obj in search_queries[:2]:  # Limit to top 2 queries
            query = query_obj.get('query', '') if isinstance(query_obj, dict) else query_obj
            
            print(f"\n   🔎 Query: {query}")
            
            for channel in relevant_channels:
                videos = self.search_channel_videos(
                    channel, 
                    query, 
                    max_videos_per_channel
                )
                all_videos.extend(videos)
                
                # Rate limiting
                time.sleep(0.5)
        
        # 4. Deduplicate
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video['id'] not in seen_ids:
                seen_ids.add(video['id'])
                unique_videos.append(video)
        
        print(f"\n   ✅ Found {len(unique_videos)} unique videos for this scene")
        return unique_videos
    
    def find_videos_for_production_plan(
        self, 
        production_plan: Dict
    ) -> Dict:
        """
        Find videos for all scenes in a production plan
        
        Args:
            production_plan: Full production plan from AI agents
        
        Returns:
            Production plan enriched with video candidates
        """
        print("=" * 80)
        print("🎥 AUTOMATED VIDEO FINDER")
        print("=" * 80)
        print(f"Title: {production_plan.get('title')}")
        print(f"Scenes: {len(production_plan.get('scenes', []))}")
        print("=" * 80)
        
        enriched_plan = production_plan.copy()
        enriched_plan['video_search_results'] = []
        
        for scene in production_plan.get('scenes', []):
            # Find videos for this scene
            videos = self.find_videos_for_scene(scene)
            
            # Add to results
            enriched_plan['video_search_results'].append({
                'scene_number': scene.get('scene_number'),
                'scene_description': scene.get('scene_description'),
                'required_clips': scene.get('required_clips', 1),
                'duration_seconds': scene.get('duration_seconds'),
                'candidate_videos': videos,
                'total_candidates': len(videos)
            })
        
        print("\n" + "=" * 80)
        print("✅ VIDEO SEARCH COMPLETE")
        print("=" * 80)
        
        # Summary
        total_videos = sum(
            len(r['candidate_videos']) 
            for r in enriched_plan['video_search_results']
        )
        print(f"Total videos found: {total_videos}")
        print(f"Average per scene: {total_videos / len(production_plan.get('scenes', [])):.1f}")
        
        return enriched_plan


def main():
    """Test the video finder"""
    # Load test production plan
    with open('output/test_production_plan.json', 'r') as f:
        plan = json.load(f)
    
    # Find videos
    finder = ChannelVideoFinder()
    enriched_plan = finder.find_videos_for_production_plan(plan)
    
    # Save results
    output_path = 'output/test_production_plan_enriched.json'
    with open(output_path, 'w') as f:
        json.dump(enriched_plan, f, indent=2)
    
    print(f"\n💾 Saved enriched plan to: {output_path}")


if __name__ == '__main__':
    main()
