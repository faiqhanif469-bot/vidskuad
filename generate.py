"""
🎬 B-Roll Generator - Interactive CLI
Connects all existing modules in proper workflow
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict

from parallel_pipeline import ParallelPipeline


class BRollGenerator:
    """Interactive B-Roll Generator - Connects existing modules"""
    
    def __init__(self):
        self.pipeline = None
        self.script_content = ""
        self.scenes = []
    
    def print_header(self):
        """Print welcome header"""
        print("\n" + "="*80)
        print("🎬 B-ROLL GENERATOR")
        print("="*80)
        print("Generate B-roll clips from your script automatically!")
        print("Powered by AI + 28 video archives")
        print("="*80 + "\n")
    
    def get_script_input(self) -> str:
        """Get script from user"""
        print("📝 STEP 1: Provide Your Script")
        print("-" * 80)
        print("Options:")
        print("  1. Enter script file path (e.g., scripts/space_race.txt)")
        print("  2. Type 'paste' to paste your script directly")
        print("  3. Type 'example' to use example script")
        print()
        
        choice = input("Your choice: ").strip().lower()
        
        if choice == 'example':
            return self._get_example_script()
        elif choice == 'paste':
            return self._get_pasted_script()
        else:
            return self._get_script_from_file(choice)
    
    def _get_example_script(self) -> str:
        """Return example script"""
        return """
The Space Race was one of humanity's greatest achievements. In 1957, the Soviet Union 
launched Sputnik, the first artificial satellite. This sparked a competition between 
superpowers that would define a generation.

NASA was formed in 1958 with a bold mission: reach the Moon. Engineers and scientists 
worked tirelessly in mission control, calculating trajectories and monitoring systems.

On July 20, 1969, Neil Armstrong took humanity's first steps on the lunar surface. 
The Apollo program had succeeded, marking a new era in space exploration.
"""
    
    def _get_pasted_script(self) -> str:
        """Get script pasted by user"""
        print("\n📋 Paste your script below (press Ctrl+Z then Enter when done):")
        print("-" * 80)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines)
    
    def _get_script_from_file(self, filepath: str) -> str:
        """Read script from file"""
        if not os.path.exists(filepath):
            print(f"❌ Error: File not found: {filepath}")
            sys.exit(1)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_video_duration(self) -> int:
        """Ask user for target video duration"""
        print("\n⏱️ Video Duration")
        print("-" * 80)
        print("How long should the final video be?")
        print("  Examples: 60 (1 minute), 300 (5 minutes), 1620 (27 minutes)")
        print()
        
        duration_input = input("Duration in seconds [60]: ").strip()
        duration = int(duration_input) if duration_input.isdigit() else 60
        
        # Show in minutes for confirmation
        minutes = duration / 60
        print(f"✅ Target duration: {duration}s ({minutes:.1f} minutes)\n")
        
        return duration
    
    def analyze_script(self, script: str, duration: int) -> List[Dict]:
        """Analyze script using EXISTING AI agents (src/agents/crew.py)"""
        print("\n🔍 STEP 2: Analyzing Script with AI")
        print("-" * 80)
        print("Using AI agents to analyze your script...")
        print("This may take 1-2 minutes...\n")
        
        from src.core.config import Config
        from src.agents.crew import ProductionCrew
        
        # Load config (gets GROQ_API_KEY from .env)
        config = Config.load()
        
        if not config.model.groq_api_key:
            print("❌ Error: GROQ_API_KEY not found in .env file")
            print("\nPlease add your Groq API key to .env:")
            print("GROQ_API_KEY=your_key_here")
            sys.exit(1)
        
        # Create production crew (existing module)
        crew = ProductionCrew(config)
        
        # Run AI analysis (existing method)
        result = crew.analyze_script(script, duration=duration)
        
        # Parse CrewOutput object
        if hasattr(result, 'raw'):
            result_text = result.raw
        elif hasattr(result, 'output'):
            result_text = result.output
        else:
            result_text = str(result)
        
        # Extract JSON from result
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if not json_match:
            print("❌ Error: Could not parse AI response")
            sys.exit(1)
        
        plan = json.loads(json_match.group())
        
        # Extract scenes
        scenes = []
        for scene in plan.get('scenes', []):
            scenes.append({
                'scene_number': scene.get('scene_number', len(scenes) + 1),
                'description': scene.get('scene_description', ''),
                'keywords': scene.get('keywords', [])
            })
        
        print(f"✅ AI found {len(scenes)} scenes\n")
        
        # Show scenes
        for scene in scenes:
            print(f"Scene {scene['scene_number']}: {scene['description'][:80]}...")
            print(f"  Keywords: {', '.join(scene['keywords'][:5])}")
            print()
        
        return scenes
    
    def confirm_scenes(self, scenes: List[Dict]) -> bool:
        """Ask user to confirm scenes"""
        print("📋 Scene Analysis Complete")
        print("-" * 80)
        print(f"Total scenes: {len(scenes)}")
        print()
        
        choice = input("Continue with these scenes? (y/n) [y]: ").strip().lower()
        return choice in ['y', 'yes', '']
    
    def get_settings(self) -> Dict:
        """Get generation settings"""
        print("\n⚙️ STEP 3: Generation Settings")
        print("-" * 80)
        
        # Clips per scene
        print("How many clips per scene?")
        print("  Recommended: 1 (faster)")
        print("  Options: 1-3")
        clips_input = input("Clips per scene [1]: ").strip()
        clips_per_scene = int(clips_input) if clips_input.isdigit() else 1
        clips_per_scene = max(1, min(3, clips_per_scene))
        
        # Workers
        print("\nHow many parallel workers?")
        print("  Recommended: 10 (balanced)")
        print("  Options: 1-20")
        workers_input = input("Workers [10]: ").strip()
        workers = int(workers_input) if workers_input.isdigit() else 10
        workers = max(1, min(20, workers))
        
        print()
        print(f"✅ Settings:")
        print(f"   Clips per scene: {clips_per_scene}")
        print(f"   Parallel workers: {workers}")
        print()
        
        return {
            'clips_per_scene': clips_per_scene,
            'workers': workers
        }
    
    def generate(self, scenes: List[Dict], settings: Dict):
        """Generate B-roll using parallel_pipeline.py"""
        print("\n🚀 STEP 4: Generating B-Roll")
        print("-" * 80)
        print(f"Processing {len(scenes)} scenes with {settings['workers']} workers...")
        print("This may take a few minutes...\n")
        
        # Create pipeline (uses channel_video_finder.py + broll_extractor.py)
        self.pipeline = ParallelPipeline(max_workers=settings['workers'])
        
        # Run pipeline
        result = self.pipeline.run(
            scenes=scenes,
            clips_per_scene=settings['clips_per_scene']
        )
        
        return result
    
    def show_results(self, result: Dict):
        """Show generation results"""
        print("\n" + "="*80)
        print("🎉 GENERATION COMPLETE!")
        print("="*80)
        print(f"✅ Success: {result['success']}")
        print(f"📦 Package: {result['package_path']}")
        print(f"🎬 Scenes: {result['num_scenes']}")
        print(f"✂️ Clips: {result['num_clips']}")
        print(f"⏱️ Time: {result['total_time']:.1f}s ({result['total_time']/60:.1f} min)")
        print(f"⚡ Speed: {result['avg_time_per_scene']:.1f}s per scene")
        print("="*80)
        
        # Show package contents
        package_path = Path(result['package_path'])
        clips_dir = package_path / 'clips'
        
        if clips_dir.exists():
            clips = list(clips_dir.glob('*.mp4'))
            print(f"\n📁 Package Contents ({len(clips)} clips):")
            print("-" * 80)
            for clip in clips[:10]:
                size_kb = clip.stat().st_size / 1024
                print(f"  {clip.name} ({size_kb:.1f} KB)")
            if len(clips) > 10:
                print(f"  ... and {len(clips) - 10} more clips")
        
        print("\n📄 Files:")
        print(f"  - manifest.json (clip metadata)")
        print(f"  - README.txt (instructions)")
        print(f"  - clips/ folder ({result['num_clips']} video files)")
        
        print("\n💡 Next Steps:")
        print("  1. Open the package folder")
        print("  2. Import clips into your video editor")
        print("  3. Arrange clips according to your script")
        print("  4. Add transitions, effects, and audio")
        print("  5. Export your final video!")
        
        print(f"\n� Package location: {result['package_path']}")
        print("="*80 + "\n")
    
    def run(self):
        """Run the complete workflow"""
        try:
            # Header
            self.print_header()
            
            # Step 1: Get script
            self.script_content = self.get_script_input()
            
            # Step 1.5: Get video duration
            duration = self.get_video_duration()
            
            # Step 2: Analyze with AI
            self.scenes = self.analyze_script(self.script_content, duration)
            
            if not self.scenes:
                print("❌ Error: No scenes found")
                sys.exit(1)
            
            # Confirm scenes
            if not self.confirm_scenes(self.scenes):
                print("❌ Generation cancelled")
                sys.exit(0)
            
            # Step 3: Get settings
            settings = self.get_settings()
            
            # Step 4: Generate (uses parallel_pipeline → channel_video_finder → broll_extractor)
            result = self.generate(self.scenes, settings)
            
            # Step 5: Show results
            if result['success']:
                self.show_results(result)
            else:
                print("❌ Generation failed")
                sys.exit(1)
        
        except KeyboardInterrupt:
            print("\n\n❌ Cancelled by user (Ctrl+C)")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    generator = BRollGenerator()
    generator.run()


if __name__ == "__main__":
    main()
