"""
Complete AI Video Production Pipeline with Image Fallback
Step 1: AI agents analyze script and create production plan
Step 2: Fast search finds real videos for each scene
Step 3: Extract clips from videos
Step 4: Generate AI images for missing scenes using Cloudflare FLUX
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from src.core.config import Config
from src.agents.crew import ProductionCrew
from src.tools.fast_search import FastVideoSearch
from src.tools.downloader import VideoDownloader
from src.tools.broll_extractor import BRollExtractor
from src.tools.flux_generator import integrate_with_image_fallback
from src.tools.premiere_exporter import PremiereExporter
from src.tools.capcut_exporter import CapCutExporter


async def run_pipeline_with_flux(script: str, duration: float):
    """Run complete pipeline with image fallback"""
    
    print("\n" + "=" * 80)
    print("🎬 AI VIDEO PRODUCTION PIPELINE WITH IMAGE FALLBACK")
    print("=" * 80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # ========================================================================
    # STEP 1: AI AGENTS - Analyze script
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 1: AI AGENTS - SCRIPT ANALYSIS")
    print("=" * 80)
    
    config = Config.load()
    crew = ProductionCrew(config)
    
    print("🤖 Running multi-agent analysis...")
    
    try:
        result = crew.analyze_script(script, duration)
        
        # Parse result
        import re
        json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            print("❌ Could not parse agent output")
            return None
        
        plan_path = output_dir / "production_plan.json"
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ STEP 1 COMPLETE - {len(plan.get('scenes', []))} scenes created")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        plan_path = output_dir / "production_plan.json"
        if not plan_path.exists():
            return None
        with open(plan_path, 'r') as f:
            plan = json.load(f)
    
    # ========================================================================
    # STEP 2: FAST SEARCH - Find videos
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 2: FAST SEARCH - FINDING VIDEOS")
    print("=" * 80)
    
    searcher = FastVideoSearch()
    
    for scene in plan.get('scenes', []):
        scene_num = scene.get('scene_number', '?')
        scene_desc = scene.get('scene_description', '')
        
        print(f"\n📹 Scene {scene_num}: {scene_desc}")
        
        for query_obj in scene.get('search_queries', []):
            query = query_obj.get('query', '')
            if not query:
                continue
            
            print(f"   🔎 Searching: \"{query}\"")
            
            try:
                results = await searcher.intelligent_search(
                    query=query,
                    context=scene.get('visual_context', ''),
                    platforms=['youtube']
                )
                
                query_obj['results_found'] = len(results)
                query_obj['sample_videos'] = [
                    {
                        'title': r['title'],
                        'url': r['url'],
                        'duration': r['duration'],
                        'relevance_score': round(r['relevance_score'], 2)
                    }
                    for r in results[:3]
                ]
                
                if results:
                    print(f"      ✓ Found {len(results)} videos")
                else:
                    print(f"      ⚠️  No videos found")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                query_obj['results_found'] = 0
                query_obj['sample_videos'] = []
    
    enriched_path = output_dir / "production_plan_enriched.json"
    with open(enriched_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ STEP 2 COMPLETE")
    
    # ========================================================================
    # STEP 3: DOWNLOAD & EXTRACT CLIPS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 3: DOWNLOADING & EXTRACTING CLIPS")
    print("=" * 80)
    
    downloader = VideoDownloader()
    extractor = BRollExtractor()
    
    extracted_clips = []
    
    for scene in plan.get('scenes', []):
        scene_num = scene.get('scene_number', '?')
        scene_desc = scene.get('scene_description', '')
        
        print(f"\n📹 Scene {scene_num}: {scene_desc}")
        
        # Get best video from search results
        best_video = None
        for query_obj in scene.get('search_queries', []):
            videos = query_obj.get('sample_videos', [])
            if videos:
                best_video = videos[0]
                break
        
        if not best_video:
            print(f"   ⚠️  No videos available - will use AI image fallback")
            continue
        
        try:
            # Download video
            print(f"   ⬇️  Downloading: {best_video['title'][:50]}...")
            video_path = downloader.download(
                url=best_video['url'],
                output_dir=str(output_dir / "downloads")
            )
            
            if not video_path:
                print(f"   ❌ Download failed")
                continue
            
            print(f"   ✓ Downloaded")
            
            # Extract clip
            print(f"   ✂️  Extracting clip...")
            clip_path = extractor.extract_best_clip(
                video_path=video_path,
                duration=scene.get('duration', 5),
                output_dir=str(output_dir / "clips")
            )
            
            if clip_path:
                print(f"   ✓ Extracted: {Path(clip_path).name}")
                extracted_clips.append({
                    'scene': scene_desc,
                    'scene_number': scene_num,
                    'path': clip_path,
                    'source_url': best_video['url']
                })
            else:
                print(f"   ❌ Extraction failed")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ STEP 3 COMPLETE - {len(extracted_clips)} clips extracted")
    
    # ========================================================================
    # STEP 4: IMAGE FALLBACK - Generate AI images for missing scenes
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 4: IMAGE FALLBACK - CLOUDFLARE FLUX")
    print("=" * 80)
    
    result = integrate_with_image_fallback(
        scenes=plan.get('scenes', []),
        extracted_clips=extracted_clips,
        output_dir=str(output_dir / "generated_images"),
        provider="cloudflare"  # Use free Cloudflare tier
    )
    
    # ========================================================================
    # STEP 5: EXPORT TO PREMIERE PRO & CAPCUT
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STEP 5: EXPORTING TO EDITING SOFTWARE")
    print("=" * 80)
    
    # Export to Premiere Pro
    print("\n🎬 Creating Premiere Pro project...")
    premiere_exporter = PremiereExporter()
    premiere_path = premiere_exporter.create_premiere_project(
        clips=extracted_clips,
        images=result.get('images', []),
        output_dir=str(output_dir),
        project_name=plan.get('title', 'AI_Video').replace(' ', '_')
    )
    
    # Export to CapCut
    print("\n✂️ Creating CapCut project...")
    capcut_exporter = CapCutExporter()
    capcut_path = capcut_exporter.create_capcut_project(
        clips=extracted_clips,
        images=result.get('images', []),
        output_dir=str(output_dir),
        project_name=plan.get('title', 'AI_Video').replace(' ', '_')
    )
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("🎉 PIPELINE COMPLETE!")
    print("=" * 80)
    
    total_scenes = len(plan.get('scenes', []))
    clips_count = len(extracted_clips)
    images_count = result.get('generated_images', 0)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Title: {plan.get('title', 'Untitled')}")
    print(f"   Total scenes: {total_scenes}")
    print(f"   Video clips: {clips_count}")
    print(f"   AI images: {images_count}")
    print(f"   Coverage: {clips_count + images_count}/{total_scenes} scenes")
    
    print(f"\n📁 OUTPUT:")
    print(f"   Production plan: {enriched_path}")
    print(f"   Video clips: {output_dir / 'clips'}")
    print(f"   AI images: {output_dir / 'generated_images'}")
    print(f"   Premiere Pro: {premiere_path}")
    print(f"   CapCut: {capcut_path}")
    
    if result.get('results_file'):
        print(f"   Fallback results: {result['results_file']}")
    
    print(f"\n✨ Next steps:")
    print(f"   1. Open Premiere Pro → Import → {premiere_path}/*.xml")
    print(f"   2. OR Open CapCut → Import Project → {capcut_path}/draft_content.json")
    print(f"   3. Edit and export your final video!")
    print(f"   4. Both projects are ready to use - just drag and drop!")
    
    return plan


def main():
    """Main entry point"""
    print("=" * 80)
    print("AI VIDEO PRODUCTION WITH IMAGE FALLBACK")
    print("=" * 80)
    
    print("\nThis pipeline will:")
    print("  1. Analyze your script with AI agents")
    print("  2. Search for real videos")
    print("  3. Download and extract clips")
    print("  4. Generate AI images for missing scenes (FREE with Cloudflare)")
    
    # Get script
    print("\nOptions:")
    print("1. Use example script")
    print("2. Load from file")
    
    choice = input("\nChoice (1-2, default 1): ").strip() or "1"
    
    if choice == "2":
        script_path = input("Enter script file path: ").strip()
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        duration = float(input("Target duration in seconds: ") or "60")
    else:
        # Use example
        script_path = "scripts/climate_change.txt"
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        duration = 60.0
        print(f"\n✓ Using example: {script_path}")
    
    # Run pipeline
    asyncio.run(run_pipeline_with_flux(script, duration))


if __name__ == '__main__':
    main()
