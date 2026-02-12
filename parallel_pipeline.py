"""
Parallel B-Roll Pipeline with Concurrent Downloads
Uses ThreadPoolExecutor for 10-15 parallel workers
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.tools.channel_video_finder import ChannelVideoFinder
from src.tools.broll_extractor import BRollExtractor


class ParallelPipeline:
    """Pipeline with parallel scene processing"""
    
    def __init__(self, output_dir: str = "output", max_workers: int = 10):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.max_workers = max_workers
        self.finder = ChannelVideoFinder()
        
        # Create unique run folder with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.output_dir / f"run_{timestamp}"
        self.run_dir.mkdir(exist_ok=True)
        
        # Create broll folder for this run
        self.broll_dir = self.run_dir / "broll"
        self.broll_dir.mkdir(exist_ok=True)
        
        # Pass the run-specific broll dir to extractor
        self.extractor = BRollExtractor(output_dir=str(self.broll_dir))
    
    def _process_scene(self, scene: Dict, scene_num: int, total_scenes: int, clips_per_scene: int) -> List[Dict]:
        """Process a single scene (runs in parallel)"""
        print(f"\n📍 Scene {scene_num}/{total_scenes}: {scene['description'][:60]}...")
        scene_start = time.time()
        
        # Format scene for finder
        scene_dict = {
            'scene_number': scene_num,
            'scene_description': scene['description'],
            'keywords': scene['keywords']
        }
        
        # Search for videos
        videos = self.finder.find_videos_for_scene(scene_dict, max_videos_per_channel=5)
        
        if not videos:
            print(f"   ⚠️ No videos found")
            return []
        
        # Extract clips - FIXED: Use top_n_videos=1 to get only 1 clip total
        print(f"\n   ✂️ Extracting {clips_per_scene} clips...")
        try:
            clips = self.extractor.extract_broll(
                scene_description=scene['description'],
                keywords=scene['keywords'],
                clip_duration=4,
                num_clips=clips_per_scene,
                top_n_videos=1  # FIXED: Only use top 1 video to get exactly clips_per_scene clips
            )
            
            scene_time = time.time() - scene_start
            print(f"   ✅ Scene {scene_num} done: {len(clips)} clips in {scene_time:.1f}s")
            return clips
            
        except Exception as e:
            print(f"   ❌ Scene {scene_num} error: {e}")
            return []
    
    def run(self, scenes: List[Dict], clips_per_scene: int = 1) -> Dict:
        """
        Run pipeline with parallel processing
        
        Args:
            scenes: List of scene dicts with 'description' and 'keywords'
            clips_per_scene: Number of clips to extract per scene
        
        Returns:
            Dict with results and package path
        """
        print("\n" + "="*80)
        print("🎬 PARALLEL B-ROLL PIPELINE")
        print("="*80)
        print(f"Run folder: {self.run_dir}")
        print(f"Scenes: {len(scenes)}")
        print(f"Clips per scene: {clips_per_scene}")
        print(f"Workers: {self.max_workers}")
        print("="*80)
        
        start_time = time.time()
        all_clips = []
        
        # Process scenes in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scenes
            futures = {
                executor.submit(
                    self._process_scene, 
                    scene, 
                    i, 
                    len(scenes),
                    clips_per_scene
                ): i 
                for i, scene in enumerate(scenes, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                scene_num = futures[future]
                try:
                    clips = future.result()
                    all_clips.extend(clips)
                except Exception as e:
                    print(f"❌ Scene {scene_num} failed: {e}")
        
        # Create package
        print(f"\n📦 Creating package...")
        package_path = self._create_package(all_clips, scenes)
        
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("🎉 PIPELINE COMPLETE!")
        print("="*80)
        print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Scenes processed: {len(scenes)}")
        print(f"Clips extracted: {len(all_clips)}")
        print(f"Average: {total_time/len(scenes):.1f}s per scene")
        print(f"Package: {package_path}")
        print("="*80)
        
        return {
            'success': True,
            'package_path': str(package_path),
            'num_scenes': len(scenes),
            'num_clips': len(all_clips),
            'total_time': total_time,
            'avg_time_per_scene': total_time / len(scenes) if scenes else 0
        }
    
    def _create_package(self, clips: List[Dict], scenes: List[Dict]) -> Path:
        """Create downloadable package"""
        
        package_dir = self.run_dir / "package"
        package_dir.mkdir(exist_ok=True)
        
        clips_dir = package_dir / "clips"
        clips_dir.mkdir(exist_ok=True)
        
        # Copy clips
        print("   Organizing clips...")
        clip_manifest = []
        
        for i, clip in enumerate(clips, 1):
            src = Path(clip['path'])
            if src.exists():
                dst = clips_dir / f"clip_{i:04d}.mp4"
                
                import shutil
                shutil.copy2(src, dst)
                
                clip_manifest.append({
                    'id': i,
                    'filename': dst.name,
                    'scene': clip['scene'],
                    'source_video': clip['video_title'],
                    'source_url': clip['video_url'],
                    'start_time': clip['start_time'],
                    'duration': clip['duration']
                })
        
        # Create manifest
        manifest_path = package_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump({
                'num_clips': len(clip_manifest),
                'clips': clip_manifest,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2)
        
        # Create README
        readme_path = package_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(f"""
B-Roll Package
{'='*80}

Contents:
- {len(clip_manifest)} video clips in /clips folder
- manifest.json with clip metadata

Clips:
""")
            for clip in clip_manifest:
                f.write(f"  {clip['filename']}: {clip['scene']}\n")
            
            f.write(f"""

Usage:
1. Import clips into your video editor
2. Arrange clips according to your script
3. Add transitions, effects, and audio
4. Export final video

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        print(f"   ✅ Package: {package_dir}")
        print(f"   📁 {len(clip_manifest)} clips")
        
        return package_dir


def main():
    """Example usage"""
    
    # Example: 10 scenes to test parallel processing
    scenes = [
        {'description': 'Rocket launching into space', 'keywords': ['rocket', 'launch', 'space', 'liftoff', 'NASA']},
        {'description': 'Astronauts in mission control', 'keywords': ['mission control', 'NASA', 'astronauts', 'space center']},
        {'description': 'Moon landing footage', 'keywords': ['moon landing', 'Apollo', 'lunar', 'astronaut']},
        {'description': 'Satellite in orbit', 'keywords': ['satellite', 'orbit', 'space', 'Earth']},
        {'description': 'Space shuttle launch', 'keywords': ['space shuttle', 'launch', 'NASA', 'Kennedy']},
        {'description': 'Astronaut spacewalk', 'keywords': ['spacewalk', 'EVA', 'astronaut', 'space']},
        {'description': 'Mars rover on surface', 'keywords': ['Mars', 'rover', 'Curiosity', 'Perseverance']},
        {'description': 'International Space Station', 'keywords': ['ISS', 'space station', 'orbit', 'astronauts']},
        {'description': 'Rocket engine test', 'keywords': ['rocket', 'engine', 'test', 'fire', 'NASA']},
        {'description': 'Mission control celebration', 'keywords': ['mission control', 'celebration', 'success', 'NASA']}
    ]
    
    # Run pipeline with 10 workers
    pipeline = ParallelPipeline(max_workers=10)
    result = pipeline.run(scenes, clips_per_scene=1)
    
    if result['success']:
        print("\n✅ SUCCESS! Your B-roll package is ready!")
        print(f"\n📦 Package: {result['package_path']}")
        print(f"⚡ Speed: {result['avg_time_per_scene']:.1f}s per scene")
    else:
        print("\n❌ Pipeline failed")


if __name__ == "__main__":
    main()
