"""
Complete Video Production Pipeline with Verification
Stages 1-3: Script → Production Plan → Video Search → Verification
"""

import sys
import json
from pathlib import Path

# Stage 1: AI Agents
from src.agents.crew import create_production_crew

# Stage 2: Video Search
from src.tools.channel_video_finder import ChannelVideoFinder
from src.tools.video_ranker import VideoRanker

# Stage 3: Video Verification
from src.tools.video_verifier import VideoVerifier


def run_complete_pipeline(script_path: str, use_clip: bool = True):
    """
    Run complete pipeline from script to verified videos
    
    Args:
        script_path: Path to script file
        use_clip: Whether to use CLIP verification
    """
    print("="*80)
    print("🎬 COMPLETE VIDEO PRODUCTION PIPELINE")
    print("="*80)
    print(f"Script: {script_path}")
    print(f"CLIP Verification: {'Enabled' if use_clip else 'Disabled'}")
    print("="*80)
    
    # Read script
    with open(script_path, 'r') as f:
        script = f.read()
    
    print(f"\n📝 Script loaded ({len(script)} characters)")
    
    # =========================================================================
    # STAGE 1: AI AGENTS - Create Production Plan
    # =========================================================================
    print("\n" + "="*80)
    print("STAGE 1: AI AGENTS - PRODUCTION PLANNING")
    print("="*80)
    
    print("\n🤖 Initializing AI agents...")
    crew = create_production_crew(script, target_duration=60.0)
    
    print("🚀 Running multi-agent analysis...")
    result = crew.kickoff()
    
    # Parse production plan
    import re
    json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
    if not json_match:
        print("❌ Failed to extract production plan")
        return
    
    production_plan = json.loads(json_match.group())
    
    # Save production plan
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    plan_path = output_dir / "production_plan.json"
    with open(plan_path, 'w') as f:
        json.dump(production_plan, f, indent=2)
    
    print(f"\n✅ Production plan created")
    print(f"   Scenes: {len(production_plan.get('scenes', []))}")
    print(f"   Duration: {production_plan.get('total_duration')}s")
    print(f"   Saved to: {plan_path}")
    
    # =========================================================================
    # STAGE 2: VIDEO SEARCH - Find Candidate Videos
    # =========================================================================
    print("\n" + "="*80)
    print("STAGE 2: VIDEO SEARCH - FINDING CANDIDATES")
    print("="*80)
    
    print("\n🔍 Searching 15 clean archive channels...")
    finder = ChannelVideoFinder()
    enriched_plan = finder.find_videos_for_production_plan(production_plan)
    
    print("\n📊 Ranking videos...")
    ranker = VideoRanker()
    ranked_plan = ranker.rank_production_plan(enriched_plan)
    
    # Save enriched plan
    enriched_path = output_dir / "production_plan_enriched.json"
    with open(enriched_path, 'w') as f:
        json.dump(ranked_plan, f, indent=2)
    
    total_candidates = sum(
        r['total_candidates'] 
        for r in ranked_plan['video_search_results']
    )
    
    print(f"\n✅ Video search complete")
    print(f"   Total candidates: {total_candidates}")
    print(f"   Saved to: {enriched_path}")
    
    # =========================================================================
    # STAGE 3: VIDEO VERIFICATION - Verify Content
    # =========================================================================
    print("\n" + "="*80)
    print("STAGE 3: VIDEO VERIFICATION - VERIFYING CONTENT")
    print("="*80)
    
    print(f"\n🔬 Initializing verification system...")
    print(f"   - Transcript extraction")
    print(f"   - TF-IDF/BM25 matching")
    print(f"   - Frame extraction")
    if use_clip:
        print(f"   - CLIP visual verification")
    
    verifier = VideoVerifier(use_clip=use_clip)
    
    print(f"\n🚀 Starting verification...")
    verified_plan = verifier.verify_production_plan(
        ranked_plan,
        output_path=str(output_dir / "production_plan_verified.json")
    )
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE")
    print("="*80)
    
    print("\n📊 Summary:")
    print(f"   Stage 1: Production plan created ({len(production_plan['scenes'])} scenes)")
    print(f"   Stage 2: {total_candidates} candidate videos found")
    print(f"   Stage 3: Videos verified with timestamps")
    
    print("\n📁 Output Files:")
    print(f"   1. {plan_path}")
    print(f"   2. {enriched_path}")
    print(f"   3. {output_dir / 'production_plan_verified.json'}")
    
    print("\n🎯 Next Steps:")
    print("   Stage 4: Download verified videos")
    print("   Stage 5: Extract 5-8 second clips")
    print("   Stage 6: Assemble final video")
    print("   Stage 7: Add voiceover")
    
    print("\n" + "="*80)
    print("🚀 Ready for Stage 4: Clip Extraction!")
    print("="*80)


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python full_pipeline_with_verification.py <script.txt> [--no-clip]")
        print("\nExample:")
        print("  python full_pipeline_with_verification.py scripts/space_race.txt")
        print("  python full_pipeline_with_verification.py scripts/space_race.txt --no-clip")
        sys.exit(1)
    
    script_path = sys.argv[1]
    use_clip = '--no-clip' not in sys.argv
    
    if not Path(script_path).exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
    
    run_complete_pipeline(script_path, use_clip=use_clip)


if __name__ == '__main__':
    main()
