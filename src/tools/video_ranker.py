"""
Video Ranking System
Uses fast search algorithm to rank videos for each scene
"""

import numpy as np
from typing import List, Dict
from src.tools.fast_search import FastVideoSearch


class VideoRanker:
    """Rank videos using the fast search algorithm"""
    
    def __init__(self):
        self.search = FastVideoSearch()
    
    def rank_by_metadata(
        self,
        videos: List[Dict],
        keywords: List[str]
    ) -> List[Dict]:
        """
        Simple ranking by title/description matching (for B-roll)
        
        Args:
            videos: List of videos
            keywords: Keywords to match
        
        Returns:
            Ranked videos with scores
        """
        if not videos:
            return []
        
        ranked = []
        keywords_lower = [k.lower() for k in keywords]
        
        for video in videos:
            if not video:  # Skip None videos
                continue
                
            title = (video.get('title') or '').lower()
            description = (video.get('description') or '').lower()
            
            # Count keyword matches
            score = 0
            for keyword in keywords_lower:
                if keyword in title:
                    score += 3  # Title matches worth more
                if keyword in description:
                    score += 1
            
            # Add channel tier bonus
            tier = video.get('channel_tier', 2)
            if tier == 1:
                score += 2
            
            video_copy = video.copy()
            video_copy['score'] = score
            ranked.append(video_copy)
        
        # Sort by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        return ranked
    
    def rank_videos_for_scene(
        self, 
        videos: List[Dict], 
        scene: Dict
    ) -> List[Dict]:
        """
        Rank videos for a specific scene
        
        Args:
            videos: List of candidate videos
            scene: Scene requirements
        
        Returns:
            Ranked list of videos with scores
        """
        if not videos:
            return []
        
        # Build query from scene
        query_data = {
            'keywords': scene.get('keywords', []),
            'context': scene.get('visual_context', '') + ' ' + scene.get('mood_tone', '')
        }
        
        # Calculate scores using vectorized algorithm
        scores = self.search.calculate_scores_vectorized(videos, query_data)
        
        # Add duration matching bonus
        target_duration = scene.get('duration_seconds', 10)
        duration_scores = self._calculate_duration_scores(videos, target_duration)
        
        # Combine scores
        final_scores = scores + duration_scores * 0.2
        
        # Sort by score
        sorted_indices = np.argsort(final_scores)[::-1]
        
        # Build ranked results
        ranked_videos = []
        for i in sorted_indices:
            video = videos[i].copy()
            video['relevance_score'] = float(final_scores[i])
            video['keyword_score'] = float(scores[i])
            video['duration_score'] = float(duration_scores[i])
            ranked_videos.append(video)
        
        return ranked_videos
    
    def _calculate_duration_scores(
        self, 
        videos: List[Dict], 
        target_duration: int
    ) -> np.ndarray:
        """
        Score videos based on duration suitability
        For 5-8 second clips, we want videos that are:
        - Long enough to extract clips from (>10 seconds)
        - Not too long (prefer <5 minutes for easier processing)
        """
        durations = np.array([v.get('duration', 0) for v in videos], dtype=np.float32)
        
        # Ideal range: 30 seconds to 5 minutes
        scores = np.zeros_like(durations)
        
        # Perfect range: 30s - 5min
        perfect_mask = (durations >= 30) & (durations <= 300)
        scores[perfect_mask] = 10.0
        
        # Good range: 10s - 30s or 5min - 10min
        good_mask = ((durations >= 10) & (durations < 30)) | ((durations > 300) & (durations <= 600))
        scores[good_mask] = 5.0
        
        # Acceptable: 10min - 30min
        ok_mask = (durations > 600) & (durations <= 1800)
        scores[ok_mask] = 2.0
        
        # Too short (< 10s) - penalize
        too_short_mask = durations < 10
        scores[too_short_mask] = -10.0
        
        return scores
    
    def select_best_videos(
        self, 
        ranked_videos: List[Dict], 
        required_clips: int = 1,
        max_per_channel: int = 2
    ) -> List[Dict]:
        """
        Select the best videos ensuring diversity
        
        Args:
            ranked_videos: Videos ranked by score
            required_clips: Number of clips needed
            max_per_channel: Max videos from same channel
        
        Returns:
            Selected videos
        """
        selected = []
        channel_counts = {}
        
        for video in ranked_videos:
            # Check if we have enough
            if len(selected) >= required_clips * 3:  # Get 3x for backup
                break
            
            # Check channel diversity
            channel = video.get('channel', 'unknown')
            if channel_counts.get(channel, 0) >= max_per_channel:
                continue
            
            # Add video
            selected.append(video)
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        return selected
    
    def rank_production_plan(self, enriched_plan: Dict) -> Dict:
        """
        Rank all videos in an enriched production plan
        
        Args:
            enriched_plan: Production plan with video candidates
        
        Returns:
            Plan with ranked and selected videos
        """
        print("\n" + "=" * 80)
        print("🏆 RANKING VIDEOS")
        print("=" * 80)
        
        ranked_plan = enriched_plan.copy()
        
        for i, result in enumerate(ranked_plan.get('video_search_results', [])):
            scene_num = result['scene_number']
            videos = result['candidate_videos']
            
            print(f"\n📊 Scene {scene_num}: Ranking {len(videos)} videos...")
            
            # Get corresponding scene
            scene = next(
                (s for s in enriched_plan['scenes'] if s['scene_number'] == scene_num),
                {}
            )
            
            # Rank videos
            ranked_videos = self.rank_videos_for_scene(videos, scene)
            
            # Select best
            required_clips = result.get('required_clips', 1)
            selected_videos = self.select_best_videos(ranked_videos, required_clips)
            
            # Update result
            ranked_plan['video_search_results'][i]['ranked_videos'] = ranked_videos
            ranked_plan['video_search_results'][i]['selected_videos'] = selected_videos
            ranked_plan['video_search_results'][i]['top_score'] = ranked_videos[0]['relevance_score'] if ranked_videos else 0
            
            if ranked_videos:
                print(f"   ✅ Top video: {ranked_videos[0]['title'][:60]}... (score: {ranked_videos[0]['relevance_score']:.2f})")
                print(f"   📺 Selected {len(selected_videos)} videos")
            else:
                print(f"   ⚠️  No videos found for this scene")
        
        print("\n" + "=" * 80)
        print("✅ RANKING COMPLETE")
        print("=" * 80)
        
        return ranked_plan


def main():
    """Test the ranker"""
    import json
    
    # Load enriched plan
    with open('output/test_production_plan_enriched.json', 'r') as f:
        enriched_plan = json.load(f)
    
    # Rank videos
    ranker = VideoRanker()
    ranked_plan = ranker.rank_production_plan(enriched_plan)
    
    # Save
    output_path = 'output/test_production_plan_ranked.json'
    with open(output_path, 'w') as f:
        json.dump(ranked_plan, f, indent=2)
    
    print(f"\n💾 Saved ranked plan to: {output_path}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📈 SUMMARY")
    print("=" * 80)
    for result in ranked_plan['video_search_results']:
        print(f"\nScene {result['scene_number']}:")
        print(f"  Candidates: {result['total_candidates']}")
        print(f"  Selected: {len(result['selected_videos'])}")
        print(f"  Top Score: {result['top_score']:.2f}")
        if result['selected_videos']:
            top = result['selected_videos'][0]
            print(f"  Best Video: {top['title'][:60]}...")
            print(f"  Channel: {top['channel']} (Tier {top['channel_tier']})")


if __name__ == '__main__':
    main()
