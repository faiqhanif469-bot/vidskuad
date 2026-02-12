"""
Complete AI Video Production Pipeline
Step 1: AI agents analyze script and create production plan
Step 2: Fast search finds real videos for each scene
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from src.core.config import Config
from src.agents.crew import ProductionCrew
from src.tools.fast_search import FastVideoSearch


def load_script(script_path: str = None) -> tuple[str, float]:
    """Load script from file or use example"""
    if script_path and Path(script_path).exists():
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        print(f"✓ Loaded script from: {script_path}")
    else:
        # Use example script
        script_path = "scripts/climate_change.txt"
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        print(f"✓ Using example script: {script_path}")
    
    # Get target duration
    duration = float(input("\nTarget video duration in seconds (default 60): ") or "60")
    
    print(f"✓ Script loaded ({len(script)} characters)")
    print(f"✓ Target duration: {duration}s")
    
    return script, duration


async def run_full_pipeline(script: str, duration: float):
    """Run complete pipeline: AI agents → Video search"""
    
    print("\n" + "=" * 80)
    print("🎬 AI VIDEO PRODUCTION PIPELINE")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ========================================================================
    # STEP 1: AI AGENTS - Analyze script and create production plan
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 1: AI AGENTS - SCRIPT ANALYSIS")
    print("=" * 80)
    print("\nInitializing AI agents (Groq/Llama 70B)...")
    
    config = Config.load()
    crew = ProductionCrew(config)
    
    print("✓ Agents initialized")
    print("\n🤖 Running multi-agent analysis...")
    print("   This will take 1-3 minutes as agents work sequentially.")
    print("   You'll see each agent's thinking process below.\n")
    
    try:
        result = crew.analyze_script(script, duration)
        
        # Parse result (it's a string with JSON)
        result_str = str(result)
        
        # Extract JSON from result
        import re
        json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            print("❌ Could not parse agent output as JSON")
            return None
        
        # Save production plan
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        plan_path = output_dir / "production_plan.json"
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print("\n✅ STEP 1 COMPLETE!")
        print(f"✓ Production plan saved: {plan_path}")
        print(f"✓ Scenes created: {len(plan.get('scenes', []))}")
        
    except Exception as e:
        print(f"\n❌ Agent analysis error: {e}")
        print("\nTrying to continue with existing plan if available...")
        
        plan_path = Path("output/production_plan.json")
        if not plan_path.exists():
            print("No existing plan found. Exiting.")
            return None
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        print(f"✓ Loaded existing plan: {plan_path}")
    
    # ========================================================================
    # STEP 2: FAST SEARCH - Find real videos
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 2: FAST SEARCH - FINDING VIDEOS")
    print("=" * 80)
    print("\nInitializing fast search engine (NumPy-powered)...")
    
    searcher = FastVideoSearch()
    print("✓ Search engine ready")
    
    total_queries = 0
    total_results = 0
    
    for scene in plan.get('scenes', []):
        scene_num = scene.get('scene_number', '?')
        scene_desc = scene.get('scene_description', 'Unknown')
        
        print(f"\n📹 Scene {scene_num}: {scene_desc}")
        
        for query_obj in scene.get('search_queries', []):
            query = query_obj.get('query', '')
            context = scene.get('visual_context', '')
            platform = query_obj.get('platform', 'YouTube')
            
            if not query:
                continue
            
            total_queries += 1
            print(f"\n   🔎 Searching: \"{query}\"")
            
            try:
                results = await searcher.intelligent_search(
                    query=query,
                    context=context,
                    platforms=[platform.lower()]
                )
                
                query_obj['results_found'] = len(results)
                query_obj['sample_videos'] = [
                    {
                        'title': r['title'],
                        'url': r['url'],
                        'duration': r['duration'],
                        'platform': r['platform'],
                        'relevance_score': round(r['relevance_score'], 2)
                    }
                    for r in results[:5]
                ]
                
                total_results += len(results)
                
                if results:
                    print(f"      ✓ Found {len(results)} videos")
                    print(f"      🏆 Top: {results[0]['title'][:60]}...")
                else:
                    print(f"      ⚠️  No videos found")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                query_obj['results_found'] = 0
                query_obj['sample_videos'] = []
    
    # Add metadata
    plan['enrichment_metadata'] = {
        'enriched_at': datetime.now().isoformat(),
        'total_queries': total_queries,
        'total_results_found': total_results,
        'search_engine': 'FastVideoSearch v1.0'
    }
    
    # Save enriched plan
    enriched_path = output_dir / "production_plan_enriched.json"
    with open(enriched_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print("\n✅ STEP 2 COMPLETE!")
    print(f"✓ Enriched plan saved: {enriched_path}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🎉 PIPELINE COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Title: {plan.get('title', 'Untitled')}")
    print(f"   Duration: {plan.get('total_duration', 0)}s")
    print(f"   Scenes: {len(plan.get('scenes', []))}")
    print(f"   Search queries: {total_queries}")
    print(f"   Videos found: {total_results}")
    print(f"   Avg per query: {total_results / total_queries if total_queries > 0 else 0:.1f}")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   Production plan: {plan_path}")
    print(f"   Enriched plan: {enriched_path}")
    
    print(f"\n✨ Next steps:")
    print(f"   1. Review the enriched plan: {enriched_path}")
    print(f"   2. Download videos using the URLs provided")
    print(f"   3. Edit and assemble your video!")
    
    print("\n" + "=" * 80)
    
    return plan


def main():
    """Main entry point"""
    print("=" * 80)
    print("AI VIDEO PRODUCTION SYSTEM")
    print("=" * 80)
    
    print("\nOptions:")
    print("1. Enter script directly")
    print("2. Load from file (scripts/)")
    print("3. Use example script")
    
    choice = input("\nChoice (1-3): ").strip() or "3"
    
    if choice == "1":
        print("\nEnter your script (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        script = "\n".join(lines)
        duration = float(input("\nTarget duration in seconds: ") or "60")
    
    elif choice == "2":
        script_path = input("Enter script file path: ").strip()
        script, duration = load_script(script_path)
    
    else:
        print("\n✓ Using example climate change script")
        script, duration = load_script()
    
    # Run pipeline
    asyncio.run(run_full_pipeline(script, duration))


if __name__ == '__main__':
    main()
