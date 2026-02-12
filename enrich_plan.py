"""
Enrich Production Plan with Videos
Complete pipeline: AI agents → Video search → Ranking
"""

import json
import sys
from src.tools.channel_video_finder import ChannelVideoFinder
from src.tools.video_ranker import VideoRanker


def enrich_production_plan(plan_path: str, output_path: str = None):
    """
    Take a production plan and enrich it with ranked videos
    
    Args:
        plan_path: Path to production plan JSON
        output_path: Where to save enriched plan (optional)
    """
    print("=" * 80)
    print("🎬 PRODUCTION PLAN ENRICHMENT PIPELINE")
    print("=" * 80)
    
    # 1. Load production plan
    print(f"\n📂 Loading production plan: {plan_path}")
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    print(f"   Title: {plan.get('title')}")
    print(f"   Scenes: {len(plan.get('scenes', []))}")
    print(f"   Duration: {plan.get('total_duration')}s")
    
    # 2. Find videos from clean channels
    print("\n" + "=" * 80)
    print("STEP 1: SEARCHING CLEAN ARCHIVE CHANNELS")
    print("=" * 80)
    
    finder = ChannelVideoFinder()
    enriched_plan = finder.find_videos_for_production_plan(plan)
    
    # 3. Rank videos
    print("\n" + "=" * 80)
    print("STEP 2: RANKING VIDEOS")
    print("=" * 80)
    
    ranker = VideoRanker()
    ranked_plan = ranker.rank_production_plan(enriched_plan)
    
    # 4. Save results
    if output_path is None:
        output_path = plan_path.replace('.json', '_enriched.json')
    
    print(f"\n💾 Saving enriched plan to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(ranked_plan, f, indent=2)
    
    # 5. Print final summary
    print("\n" + "=" * 80)
    print("✅ ENRICHMENT COMPLETE")
    print("=" * 80)
    
    total_candidates = sum(
        r['total_candidates'] 
        for r in ranked_plan['video_search_results']
    )
    total_selected = sum(
        len(r['selected_videos']) 
        for r in ranked_plan['video_search_results']
    )
    
    print(f"\n📊 Statistics:")
    print(f"   Total candidates found: {total_candidates}")
    print(f"   Total videos selected: {total_selected}")
    print(f"   Average candidates per scene: {total_candidates / len(plan['scenes']):.1f}")
    print(f"   Average selected per scene: {total_selected / len(plan['scenes']):.1f}")
    
    print(f"\n🎯 Scene Breakdown:")
    for result in ranked_plan['video_search_results']:
        print(f"\n   Scene {result['scene_number']}: {result['scene_description'][:60]}...")
        print(f"      Duration: {result['duration_seconds']}s")
        print(f"      Required clips: {result['required_clips']}")
        print(f"      Candidates: {result['total_candidates']}")
        print(f"      Selected: {len(result['selected_videos'])}")
        
        if result['selected_videos']:
            top = result['selected_videos'][0]
            print(f"      🏆 Best: {top['title'][:50]}...")
            print(f"         Channel: {top['channel']} (Tier {top['channel_tier']})")
            print(f"         Score: {top['relevance_score']:.2f}")
            print(f"         URL: {top['url']}")
    
    print("\n" + "=" * 80)
    print("🚀 Ready for video download and assembly!")
    print("=" * 80)
    
    return ranked_plan


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python enrich_plan.py <production_plan.json> [output.json]")
        print("\nExample:")
        print("  python enrich_plan.py output/test_production_plan.json")
        sys.exit(1)
    
    plan_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    enrich_production_plan(plan_path, output_path)


if __name__ == '__main__':
    main()
