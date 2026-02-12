"""
Enterprise-Grade Video Verification Pipeline
Complete system: Transcript + Frame + CLIP verification
"""

import json
import time
from typing import List, Dict, Optional
from pathlib import Path
import logging

from src.tools.transcript_extractor import TranscriptExtractor
from src.tools.transcript_matcher import TranscriptMatcher
from src.tools.frame_extractor import FrameExtractor
from src.tools.clip_verifier import CLIPVerifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoVerifier:
    """Complete video verification pipeline"""
    
    def __init__(
        self,
        use_clip: bool = True,
        cache_dir: str = "cache"
    ):
        """
        Initialize video verifier
        
        Args:
            use_clip: Whether to use CLIP verification (requires GPU for best performance)
            cache_dir: Directory for caching
        """
        self.transcript_extractor = TranscriptExtractor()
        self.transcript_matcher = TranscriptMatcher()
        self.frame_extractor = FrameExtractor(cache_dir=f"{cache_dir}/frames")
        
        self.use_clip = use_clip
        self.clip_verifier = None
        
        if use_clip:
            try:
                self.clip_verifier = CLIPVerifier()
                logger.info("CLIP verification enabled")
            except Exception as e:
                logger.warning(f"CLIP not available: {e}. Falling back to transcript-only")
                self.use_clip = False
    
    def verify_single_video(
        self,
        video: Dict,
        scene: Dict,
        extract_frames: bool = True
    ) -> Dict:
        """
        Verify single video against scene requirements
        
        Args:
            video: Video dict with url, title, etc.
            scene: Scene dict with keywords, description, etc.
            extract_frames: Whether to extract and verify frames
        
        Returns:
            Enriched video dict with verification scores
        """
        video_url = video.get('url')
        logger.info(f"Verifying video: {video.get('title', '')[:50]}...")
        
        result = video.copy()
        result['verification'] = {
            'transcript_available': False,
            'transcript_score': 0.0,
            'visual_score': 0.0,
            'combined_score': 0.0,
            'best_timestamp': None,
            'verified': False
        }
        
        # Step 1: Extract transcript
        transcript_segments = self.transcript_extractor.extract_transcript(video_url)
        
        if transcript_segments:
            result['verification']['transcript_available'] = True
            result['transcript_segments'] = [seg.to_dict() for seg in transcript_segments]
            result['transcript_text'] = self.transcript_extractor.get_full_transcript_text(transcript_segments)
            
            # Step 2: Find best segments
            keywords = scene.get('keywords', [])
            best_segments = self.transcript_extractor.extract_best_segments(
                transcript_segments,
                keywords,
                min_duration=5.0,
                max_duration=15.0
            )
            
            if best_segments:
                best_seg = best_segments[0]
                result['verification']['best_timestamp'] = best_seg['start_time']
                result['verification']['transcript_score'] = min(best_seg['keyword_count'] / len(keywords), 1.0)
                result['best_segments'] = best_segments[:3]
                
                # Step 3: Extract frames at best timestamps (if enabled)
                if extract_frames and self.use_clip and self.clip_verifier:
                    timestamps = [seg['start_time'] for seg in best_segments[:3]]
                    frames = self.frame_extractor.extract_frames_at_timestamps(video_url, timestamps)
                    
                    if frames:
                        # Step 4: CLIP verification
                        scene_desc = scene.get('scene_description', '')
                        visual_context = scene.get('visual_context', '')
                        
                        clip_result = self.clip_verifier.verify_video_content(
                            frames,
                            scene_desc,
                            visual_context,
                            keywords
                        )
                        
                        result['verification']['visual_score'] = clip_result['confidence']
                        result['verification']['verified'] = clip_result['verified']
                        result['extracted_frames'] = frames
        
        # Calculate combined score
        transcript_score = result['verification']['transcript_score']
        visual_score = result['verification']['visual_score']
        
        if self.use_clip and visual_score > 0:
            # Weighted combination
            combined = transcript_score * 0.4 + visual_score * 0.6
        else:
            # Transcript only
            combined = transcript_score
        
        result['verification']['combined_score'] = combined
        
        logger.info(f"  Transcript: {transcript_score:.2f}, Visual: {visual_score:.2f}, Combined: {combined:.2f}")
        
        return result
    
    def verify_videos_for_scene(
        self,
        videos: List[Dict],
        scene: Dict,
        top_k: int = 5,
        max_videos_to_verify: int = 20
    ) -> List[Dict]:
        """
        Verify multiple videos for a scene
        
        Args:
            videos: List of candidate videos
            scene: Scene requirements
            top_k: Number of top videos to return
            max_videos_to_verify: Max videos to fully verify (for speed)
        
        Returns:
            List of verified and ranked videos
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Verifying videos for Scene {scene.get('scene_number')}")
        logger.info(f"{'='*80}")
        
        # Limit to top candidates
        videos_to_verify = videos[:max_videos_to_verify]
        
        verified_videos = []
        
        for i, video in enumerate(videos_to_verify, 1):
            logger.info(f"\n[{i}/{len(videos_to_verify)}] Processing...")
            
            try:
                verified = self.verify_single_video(video, scene, extract_frames=True)
                verified_videos.append(verified)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error verifying video: {e}")
                continue
        
        # Sort by combined score
        verified_videos.sort(key=lambda x: x['verification']['combined_score'], reverse=True)
        
        # Log results
        logger.info(f"\n{'='*80}")
        logger.info(f"Verification Complete")
        logger.info(f"{'='*80}")
        logger.info(f"Verified: {len(verified_videos)} videos")
        logger.info(f"\nTop {min(3, len(verified_videos))} matches:")
        
        for i, video in enumerate(verified_videos[:3], 1):
            ver = video['verification']
            logger.info(f"\n{i}. {video['title'][:60]}...")
            logger.info(f"   Combined Score: {ver['combined_score']:.3f}")
            logger.info(f"   Transcript: {ver['transcript_score']:.3f}, Visual: {ver['visual_score']:.3f}")
            if ver['best_timestamp']:
                logger.info(f"   Best Timestamp: {ver['best_timestamp']:.1f}s")
        
        return verified_videos[:top_k]
    
    def verify_production_plan(
        self,
        enriched_plan: Dict,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Verify all videos in production plan
        
        Args:
            enriched_plan: Production plan with candidate videos
            output_path: Where to save verified plan
        
        Returns:
            Plan with verified videos
        """
        logger.info("\n" + "="*80)
        logger.info("VIDEO VERIFICATION PIPELINE")
        logger.info("="*80)
        logger.info(f"Title: {enriched_plan.get('title')}")
        logger.info(f"Scenes: {len(enriched_plan.get('scenes', []))}")
        logger.info(f"CLIP Enabled: {self.use_clip}")
        logger.info("="*80)
        
        verified_plan = enriched_plan.copy()
        
        for i, result in enumerate(verified_plan.get('video_search_results', [])):
            scene_num = result['scene_number']
            candidates = result.get('candidate_videos', [])
            
            # Get corresponding scene
            scene = next(
                (s for s in enriched_plan['scenes'] if s['scene_number'] == scene_num),
                {}
            )
            
            # Verify videos
            verified = self.verify_videos_for_scene(
                candidates,
                scene,
                top_k=5,
                max_videos_to_verify=10  # Limit for speed
            )
            
            # Update result
            verified_plan['video_search_results'][i]['verified_videos'] = verified
            verified_plan['video_search_results'][i]['verification_complete'] = True
        
        # Save if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(verified_plan, f, indent=2)
            logger.info(f"\n💾 Saved verified plan to: {output_path}")
        
        logger.info("\n" + "="*80)
        logger.info("✅ VERIFICATION COMPLETE")
        logger.info("="*80)
        
        return verified_plan


def main():
    """Test video verification"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.tools.video_verifier <enriched_plan.json>")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    
    # Load enriched plan
    with open(plan_path, 'r') as f:
        enriched_plan = json.load(f)
    
    # Verify
    verifier = VideoVerifier(use_clip=True)
    verified_plan = verifier.verify_production_plan(
        enriched_plan,
        output_path=plan_path.replace('.json', '_verified.json')
    )
    
    print("\n✅ Verification complete!")


if __name__ == '__main__':
    main()
