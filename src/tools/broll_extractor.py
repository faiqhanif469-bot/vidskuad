"""
B-Roll Clip Extractor
Simple approach: Search → Rank → Download random 3-5s clip from best video
No AI verification needed - just grab any clip that matches description
"""

import random
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import yt_dlp

from src.tools.channel_video_finder import ChannelVideoFinder
from src.tools.video_ranker import VideoRanker


class BRollExtractor:
    """Extract random 3-5 second B-roll clips from best matching videos"""
    
    def __init__(self, output_dir: str = "output/broll"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.finder = ChannelVideoFinder()
        self.ranker = VideoRanker()
    
    def extract_broll(
        self,
        scene_description: str,
        keywords: List[str],
        clip_duration: int = 4,  # 3-5 seconds
        num_clips: int = 1,  # How many clips to extract
        top_n_videos: int = 3  # Extract from top N videos
    ) -> List[Dict]:
        """
        Extract random B-roll clips from best matching videos
        
        Args:
            scene_description: What you're looking for (e.g., "rocket launching")
            keywords: Search keywords
            clip_duration: Length of clip in seconds (default 4)
            num_clips: How many clips to extract per video
            top_n_videos: Extract from top N videos (default 3)
        
        Returns:
            List of extracted clips with metadata
        """
        print(f"\n🎬 B-ROLL EXTRACTION")
        print(f"📝 Scene: {scene_description}")
        print(f"🔍 Keywords: {keywords}")
        print("=" * 80)
        
        # Step 1: Search for videos
        print("\n🔍 STEP 1: Searching videos...")
        
        # Create a scene dict for the finder
        scene = {
            'scene_description': scene_description,
            'keywords': keywords,
            'visual_context': scene_description,
            'scene_number': 1
        }
        
        videos = self.finder.find_videos_for_scene(scene, max_videos_per_channel=10)
        print(f"✅ Found {len(videos)} candidate videos")
        
        if not videos:
            print("❌ No videos found")
            return []
        
        # Step 2: Rank by title/description
        print("\n📊 STEP 2: Ranking by title/description...")
        ranked = self.ranker.rank_by_metadata(videos, keywords)
        top_videos = ranked[:top_n_videos]
        
        print(f"✅ Top {len(top_videos)} videos selected:")
        for i, video in enumerate(top_videos, 1):
            print(f"   {i}. {video['title'][:60]}... (Score: {video.get('score', 0):.2f})")
        
        # Step 3: Extract random clips from top videos
        print(f"\n✂️ STEP 3: Extracting {clip_duration}s clips...")
        extracted_clips = []
        
        for i, video in enumerate(top_videos, 1):
            print(f"\n📹 Video {i}/{len(top_videos)}: {video['title'][:50]}...")
            
            clips = self._extract_random_clips(
                video,
                scene_description,
                clip_duration,
                num_clips
            )
            
            extracted_clips.extend(clips)
        
        print(f"\n✅ Extracted {len(extracted_clips)} clips total")
        return extracted_clips
    
    def _extract_random_clips(
        self,
        video: Dict,
        scene_description: str,
        duration: int,
        num_clips: int
    ) -> List[Dict]:
        """Extract random clips from a video"""
        
        # Get video duration
        video_duration = self._get_video_duration(video['url'])
        if not video_duration:
            print(f"   ❌ Could not get video duration")
            return []
        
        print(f"   📏 Video duration: {video_duration}s")
        
        # Generate random start times
        # Avoid first/last 10 seconds (often has intros/outros)
        safe_start = 10
        safe_end = max(safe_start + duration, video_duration - 10)
        
        if safe_end - safe_start < duration:
            print(f"   ⚠️ Video too short ({video_duration}s)")
            return []
        
        clips = []
        for i in range(num_clips):
            # Random start time
            start_time = random.randint(safe_start, safe_end - duration)
            
            # Extract clip with unique filename (include video ID)
            clip_path = self._download_clip(
                video['url'],
                video['id'],  # Add video ID for unique filename
                start_time,
                duration,
                scene_description,
                i + 1
            )
            
            if clip_path:
                clips.append({
                    'path': clip_path,
                    'video_url': video['url'],
                    'video_title': video['title'],
                    'start_time': start_time,
                    'duration': duration,
                    'scene': scene_description
                })
                print(f"   ✅ Clip {i+1}: {start_time}s - {start_time + duration}s")
        
        return clips
    
    def _get_video_duration(self, url: str) -> Optional[int]:
        """Get video duration without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return int(info.get('duration', 0))
        
        except Exception as e:
            print(f"   ⚠️ Error getting duration: {e}")
            return None
    
    def _download_clip(
        self,
        url: str,
        video_id: str,
        start_time: int,
        duration: int,
        scene_description: str,
        clip_number: int
    ) -> Optional[str]:
        """Download ONLY the specific segment (not full video) using yt-dlp + ffmpeg"""
        
        # Create safe filename with video ID for uniqueness
        safe_name = "".join(c for c in scene_description if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.replace(' ', '_')[:30]
        
        output_path = self.output_dir / f"{safe_name}_{video_id}_{clip_number}.mp4"
        
        try:
            # yt-dlp with download_ranges to download ONLY the segment
            # This downloads only the bytes needed, not the full video!
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'outtmpl': str(output_path),
                'quiet': True,
                'no_warnings': True,
                # Download only the specific time range
                'download_ranges': lambda info_dict, ydl: [{
                    'start_time': start_time,
                    'end_time': start_time + duration
                }],
                'force_keyframes_at_cuts': True,  # Ensure clean cuts
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if output_path.exists():
                return str(output_path)
            else:
                print(f"   ❌ Clip not created")
                return None
        
        except Exception as e:
            print(f"   ❌ Error downloading clip: {e}")
            return None
    
    def extract_multiple_scenes(
        self,
        scenes: List[Dict],
        clips_per_scene: int = 3
    ) -> Dict[str, List[Dict]]:
        """
        Extract B-roll for multiple scenes
        
        Args:
            scenes: List of scene dicts with 'description' and 'keywords'
            clips_per_scene: How many clips to extract per scene
        
        Returns:
            Dict mapping scene description to list of clips
        """
        results = {}
        
        print(f"\n🎬 BATCH B-ROLL EXTRACTION")
        print(f"📝 Processing {len(scenes)} scenes")
        print(f"✂️ Extracting {clips_per_scene} clips per scene")
        print("=" * 80)
        
        for i, scene in enumerate(scenes, 1):
            print(f"\n\n{'='*80}")
            print(f"SCENE {i}/{len(scenes)}")
            print(f"{'='*80}")
            
            clips = self.extract_broll(
                scene_description=scene['description'],
                keywords=scene['keywords'],
                num_clips=clips_per_scene,
                top_n_videos=3  # Get clips from top 3 videos
            )
            
            results[scene['description']] = clips
        
        # Summary
        print(f"\n\n{'='*80}")
        print("📊 EXTRACTION SUMMARY")
        print(f"{'='*80}")
        total_clips = sum(len(clips) for clips in results.values())
        print(f"✅ Total clips extracted: {total_clips}")
        print(f"📁 Output directory: {self.output_dir}")
        
        return results


def main():
    """Test B-roll extraction"""
    
    extractor = BRollExtractor()
    
    # Test single scene
    print("Testing single scene extraction...")
    clips = extractor.extract_broll(
        scene_description="rocket launching into space",
        keywords=["rocket", "launch", "space", "NASA"],
        clip_duration=4,
        num_clips=1,
        top_n_videos=3  # Extract from top 3 videos
    )
    
    print(f"\n✅ Extracted {len(clips)} clips")
    for clip in clips:
        print(f"   📁 {clip['path']}")
        print(f"   🎬 From: {clip['video_title'][:60]}...")
        print(f"   ⏱️ Time: {clip['start_time']}s - {clip['start_time'] + clip['duration']}s")
        print()


if __name__ == "__main__":
    main()
