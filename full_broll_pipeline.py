"""
Complete B-Roll Pipeline
Connects: Script Analysis → Video Search → B-Roll Extraction → Package Creation
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List

# Import components
from enrich_plan import enrich_production_plan
from src.tools.broll_extractor import BRollExtractor
from src.tools.image_fallback import ImageFallbackGenerator


class FullBRollPipeline:
    """Complete pipeline from script to downloadable package"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.extractor = BRollExtractor()
        self.image_fallback = ImageFallbackGenerator()
    
    def _analyze_script(self, script_path: str) -> str:
        """Analyze script with AI agents"""
        from src.core.config import Config
        from src.agents.crew import ProductionCrew
        from src.utils.file_manager import FileManager
        
        # Load config
        config = Config.load()
        
        # Read script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Run AI analysis
        crew = ProductionCrew(config)
        result = crew.analyze_script(script_content)
        
        # Save plan
        file_manager = FileManager()
        plan_path = file_manager.save_production_plan(result, Path(script_path).stem)
        
        return plan_path
    
    def run(self, script_path: str, clips_per_scene: int = 1) -> Dict:
        """
        Run complete pipeline
        
        Args:
            script_path: Path to script file
            clips_per_scene: Number of clips to extract per scene
        
        Returns:
            Dict with results and package path
        """
        print("\n" + "="*80)
        print("🎬 FULL B-ROLL PIPELINE")
        print("="*80)
        print(f"Script: {script_path}")
        print(f"Clips per scene: {clips_per_scene}")
        print("="*80)
        
        start_time = time.time()
        
        # Step 1: Analyze script with AI
        print("\n📝 STEP 1: Analyzing script with AI...")
        step1_start = time.time()
        
        plan_path = self._analyze_script(script_path)
        
        step1_time = time.time() - step1_start
        print(f"✅ Script analyzed in {step1_time:.1f}s")
        print(f"   Output: {plan_path}")
        
        # Load plan
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        num_scenes = len(plan.get('scenes', []))
        print(f"   Found {num_scenes} scenes")
        
        # Step 2: Search videos
        print("\n🔍 STEP 2: Searching videos...")
        step2_start = time.time()
        
        enriched_plan = enrich_production_plan(plan_path)
        
        step2_time = time.time() - step2_start
        print(f"✅ Video search completed in {step2_time:.1f}s")
        
        # Count total videos found
        total_videos = sum(
            len(result.get('candidate_videos', []))
            for result in enriched_plan.get('video_search_results', [])
        )
        print(f"   Found {total_videos} candidate videos")
        
        # Step 3: Extract B-roll clips
        print("\n✂️ STEP 3: Extracting B-roll clips...")
        step3_start = time.time()
        
        all_clips = []
        scenes = enriched_plan.get('scenes', [])
        
        for i, scene in enumerate(scenes, 1):
            print(f"\n   Scene {i}/{len(scenes)}: {scene.get('scene_description', '')[:50]}...")
            
            # Get search results for this scene
            scene_results = next(
                (r for r in enriched_plan.get('video_search_results', [])
                 if r['scene_number'] == scene['scene_number']),
                None
            )
            
            if not scene_results or not scene_results.get('candidate_videos'):
                print(f"   ⚠️ No videos found for scene {i}")
                continue
            
            # Extract clips
            try:
                clips = self.extractor.extract_broll(
                    scene_description=scene.get('scene_description', ''),
                    keywords=scene.get('keywords', []),
                    clip_duration=4,
                    num_clips=clips_per_scene,
                    top_n_videos=min(3, len(scene_results['candidate_videos']))
                )
                
                all_clips.extend(clips)
                print(f"   ✅ Extracted {len(clips)} clips")
                
            except Exception as e:
                print(f"   ❌ Error extracting clips: {e}")
                continue
        
        step3_time = time.time() - step3_start
        print(f"\n✅ B-roll extraction completed in {step3_time:.1f}s")
        print(f"   Total clips extracted: {len(all_clips)}")
        
        # Step 3.5: Generate image prompts for missing scenes
        print("\n🎨 STEP 3.5: Checking for missing scenes...")
        step35_start = time.time()
        
        # Read original script for context
        script_content = ""
        try:
            with open(script_path, 'r') as f:
                script_content = f.read()
        except:
            pass
        
        image_prompts = self.image_fallback.generate_prompts_for_missing_scenes(
            scenes=enriched_plan.get('scenes', []),
            extracted_clips=all_clips,
            script_context=script_content[:500]  # First 500 chars for context
        )
        
        if image_prompts:
            # Save prompts
            prompts_path = self.output_dir / f"{Path(script_path).stem}_image_prompts.json"
            self.image_fallback.save_image_prompts(image_prompts, str(prompts_path))
        
        step35_time = time.time() - step35_start
        print(f"✅ Image fallback check completed in {step35_time:.1f}s")
        
        # Step 4: Create package
        print("\n📦 STEP 4: Creating package...")
        step4_start = time.time()
        
        package_path = self._create_package(all_clips, plan)
        
        step4_time = time.time() - step4_start
        print(f"✅ Package created in {step4_time:.1f}s")
        print(f"   Package: {package_path}")
        
        # Summary
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print("🎉 PIPELINE COMPLETE!")
        print("="*80)
        print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Scenes processed: {num_scenes}")
        print(f"Clips extracted: {len(all_clips)}")
        if image_prompts:
            print(f"⚠️ Missing scenes: {len(image_prompts)}")
            print(f"📝 Image prompts generated: {len(image_prompts)}")
            print(f"   Check: {Path(script_path).stem}_image_prompts.txt")
        print(f"Package: {package_path}")
        print("="*80)
        
        return {
            'success': True,
            'package_path': str(package_path),
            'num_scenes': num_scenes,
            'num_clips': len(all_clips),
            'num_missing_scenes': len(image_prompts),
            'image_prompts_generated': len(image_prompts) > 0,
            'total_time': total_time,
            'steps': {
                'script_analysis': step1_time,
                'video_search': step2_time,
                'clip_extraction': step3_time,
                'image_fallback': step35_time,
                'package_creation': step4_time
            }
        }
    
    def _create_package(self, clips: List[Dict], plan: Dict) -> Path:
        """Create downloadable package with clips and metadata"""
        
        # Create package directory
        script_name = Path(plan.get('title', 'video')).stem
        package_dir = self.output_dir / f"{script_name}_package"
        package_dir.mkdir(exist_ok=True)
        
        clips_dir = package_dir / "clips"
        clips_dir.mkdir(exist_ok=True)
        
        # Copy clips to package
        print("   Organizing clips...")
        clip_manifest = []
        
        for i, clip in enumerate(clips, 1):
            # Copy clip file
            src = Path(clip['path'])
            if src.exists():
                dst = clips_dir / f"clip_{i:04d}.mp4"
                
                # Copy file
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
                'title': plan.get('title'),
                'num_clips': len(clip_manifest),
                'clips': clip_manifest,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2)
        
        # Create README
        readme_path = package_dir / "README.txt"
        with open(readme_path, 'w') as f:
            f.write(f"""
B-Roll Package: {plan.get('title')}
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
1. Import clips into your video editor (DaVinci Resolve, Premiere Pro, etc.)
2. Arrange clips according to your script
3. Add transitions, effects, and audio
4. Export final video

Clip Sources:
""")
            # List unique sources
            sources = set(clip['source_video'] for clip in clip_manifest)
            for source in sources:
                f.write(f"  - {source}\n")
            
            f.write(f"""

Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        print(f"   ✅ Package created: {package_dir}")
        print(f"   📁 {len(clip_manifest)} clips")
        print(f"   📄 manifest.json")
        print(f"   📄 README.txt")
        
        return package_dir


def main():
    """Run full pipeline"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python full_broll_pipeline.py <script_path> [clips_per_scene]")
        print("\nExample:")
        print("  python full_broll_pipeline.py scripts/space_race.txt")
        print("  python full_broll_pipeline.py scripts/space_race.txt 3")
        sys.exit(1)
    
    script_path = sys.argv[1]
    clips_per_scene = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    if not os.path.exists(script_path):
        print(f"❌ Error: Script file not found: {script_path}")
        sys.exit(1)
    
    # Run pipeline
    pipeline = FullBRollPipeline()
    result = pipeline.run(script_path, clips_per_scene)
    
    if result['success']:
        print("\n✅ SUCCESS! Your B-roll package is ready!")
        print(f"\n📦 Package location: {result['package_path']}")
        print("\nNext steps:")
        print("1. Open the package folder")
        print("2. Import clips into your video editor")
        print("3. Create your final video!")
    else:
        print("\n❌ Pipeline failed. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
