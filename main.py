"""
Main entry point for AI Video Production System
"""

import sys
import json
from pathlib import Path

from src.core.config import Config
from src.agents.crew import ProductionCrew
from src.utils.file_manager import FileManager
from src.utils.parser import ProductionPlanParser


def main():
    """Main execution"""
    print("=" * 80)
    print("AI VIDEO PRODUCTION SYSTEM")
    print("Multi-Agent Script Analysis & B-Roll Planning")
    print("=" * 80)
    
    # Load configuration
    try:
        config = Config.load()
        print("\n✓ Configuration loaded")
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease set GEMINI_API_KEY in .env file")
        print("Get your key from: https://aistudio.google.com/app/apikey")
        return 1
    
    # Initialize components
    file_manager = FileManager()
    parser = ProductionPlanParser()
    
    # Get script input
    print("\n" + "-" * 80)
    print("SCRIPT INPUT")
    print("-" * 80)
    print("\nOptions:")
    print("1. Enter script directly")
    print("2. Load from file (scripts/)")
    print("3. Use example script")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        print("\nEnter your script (press Ctrl+D or Ctrl+Z when done):")
        script_lines = []
        try:
            while True:
                line = input()
                script_lines.append(line)
        except EOFError:
            pass
        script = "\n".join(script_lines)
    
    elif choice == "2":
        filename = input("Enter filename (in scripts/): ").strip()
        try:
            script = file_manager.load_text(filename, "scripts")
        except FileNotFoundError:
            print(f"❌ File not found: scripts/{filename}")
            return 1
    
    else:  # Example script
        script = """
Climate change is reshaping our world at an unprecedented pace. 

Over the past century, global temperatures have risen by 1.1 degrees Celsius, 
triggering extreme weather events across the globe. From devastating wildfires 
in California to catastrophic floods in Europe, the impacts are undeniable.

Scientists warn that without immediate action, we face a future of rising sea 
levels, food shortages, and mass displacement. But there is hope.

Renewable energy technologies are advancing rapidly. Solar and wind power are 
now cheaper than fossil fuels in many regions. Electric vehicles are becoming 
mainstream. Communities worldwide are taking action.

The question is not whether we can solve this crisis, but whether we will act 
fast enough. The time for change is now.
"""
        print("\n✓ Using example climate change script")
    
    # Get duration
    duration_input = input("\nTarget video duration in seconds (default 60): ").strip()
    duration = float(duration_input) if duration_input else 60.0
    
    print(f"\n✓ Script loaded ({len(script)} characters)")
    print(f"✓ Target duration: {duration}s")
    
    # Initialize crew
    print("\n" + "-" * 80)
    print("INITIALIZING AI AGENTS")
    print("-" * 80)
    
    crew = ProductionCrew(config)
    
    # Run analysis
    print("\n" + "-" * 80)
    print("RUNNING MULTI-AGENT ANALYSIS")
    print("-" * 80)
    print("\nThis will take 1-3 minutes as agents work sequentially...")
    print("You'll see each agent's thinking process below.\n")
    
    try:
        result = crew.analyze_script(script, duration)
    except Exception as e:
        print(f"\n❌ Analysis error: {e}")
        return 1
    
    # Parse result
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    result_str = str(result)
    plan_data = parser.extract_json(result_str)
    
    if plan_data and parser.validate_plan(plan_data):
        # Save JSON
        output_file = file_manager.save_json(plan_data, "production_plan.json")
        print(f"\n✓ Production plan saved: {output_file}")
        
        # Print summary
        print("\n" + "-" * 80)
        print("PRODUCTION PLAN SUMMARY")
        print("-" * 80)
        print(f"\nTitle: {plan_data.get('title', 'N/A')}")
        print(f"Duration: {plan_data.get('total_duration', 'N/A')}s")
        print(f"Theme: {plan_data.get('overall_theme', 'N/A')}")
        print(f"Audience: {plan_data.get('target_audience', 'N/A')}")
        print(f"Style: {plan_data.get('visual_style', 'N/A')}")
        print(f"\nTotal Scenes: {len(plan_data.get('scenes', []))}")
        
        # Scene breakdown
        for scene in plan_data.get('scenes', []):
            print(f"\n  Scene {scene['scene_number']}: {scene['scene_description'][:60]}...")
            print(f"    Duration: {scene['duration_seconds']}s")
            print(f"    Clips needed: {scene.get('required_clips', 'N/A')}")
            print(f"    Queries: {len(scene.get('search_queries', []))}")
        
        print("\n" + "-" * 80)
        print("NEXT STEPS")
        print("-" * 80)
        print("\n1. Review production_plan.json")
        print("2. Use search queries to find footage on recommended platforms")
        print("3. Download clips using the downloader module")
        print("4. Edit according to scene timing and requirements")
        
    else:
        # Save raw output
        output_file = file_manager.save_text(result_str, "raw_output.txt")
        print(f"\n⚠️  Could not parse as valid JSON")
        print(f"✓ Raw output saved: {output_file}")
    
    print("\n" + "=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
