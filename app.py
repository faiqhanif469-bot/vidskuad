"""
Flask API for AI Video Production System
Endpoints for script analysis, video search, and image generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pathlib import Path
import json
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from src.core.config import Config
from src.agents.crew import ProductionCrew
from src.tools.fast_search import FastVideoSearch
from src.tools.downloader import VideoDownloader
from src.tools.broll_extractor import BRollExtractor
from src.tools.flux_generator import FluxImageGenerator, integrate_with_image_fallback
from src.tools.premiere_exporter import PremiereExporter
from src.tools.capcut_exporter import CapCutExporter

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Serve the frontend"""
    return app.send_static_file('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'ai_agents': 'ready',
            'video_search': 'ready',
            'flux_generator': 'ready' if os.getenv('CLOUDFLARE_API_TOKEN') else 'not_configured'
        }
    })


@app.route('/api/analyze-script', methods=['POST'])
def analyze_script():
    """
    Analyze script with AI agents
    
    Body:
    {
        "script": "Your video script here...",
        "duration": 60
    }
    """
    try:
        data = request.json
        script = data.get('script')
        duration = data.get('duration', 60)
        
        if not script:
            return jsonify({'error': 'Script is required'}), 400
        
        # Run AI agents
        config = Config.load()
        crew = ProductionCrew(config)
        
        result = crew.analyze_script(script, duration)
        
        # Parse result
        import re
        json_match = re.search(r'\{.*\}', str(result), re.DOTALL)
        if json_match:
            plan = json.loads(json_match.group())
        else:
            return jsonify({'error': 'Failed to parse agent output'}), 500
        
        # Save plan
        plan_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'plan': plan,
            'scenes_count': len(plan.get('scenes', []))
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search-videos', methods=['POST'])
async def search_videos():
    """
    Search for videos for each scene
    
    Body:
    {
        "plan_id": "20240211_123456",
        "platforms": ["youtube"]
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        platforms = data.get('platforms', ['youtube'])
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        if not plan_path.exists():
            return jsonify({'error': 'Plan not found'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Search for videos
        searcher = FastVideoSearch()
        
        for scene in plan.get('scenes', []):
            for query_obj in scene.get('search_queries', []):
                query = query_obj.get('query', '')
                if not query:
                    continue
                
                results = await searcher.intelligent_search(
                    query=query,
                    context=scene.get('visual_context', ''),
                    platforms=platforms
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
        
        # Save enriched plan
        enriched_path = OUTPUT_DIR / f"plan_{plan_id}_enriched.json"
        with open(enriched_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'plan': plan
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-clips', methods=['POST'])
def download_clips():
    """
    Download and extract clips from videos
    
    Body:
    {
        "plan_id": "20240211_123456",
        "scene_numbers": [1, 2, 3]  // optional, defaults to all
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        scene_numbers = data.get('scene_numbers')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load enriched plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}_enriched.json"
        if not plan_path.exists():
            return jsonify({'error': 'Enriched plan not found. Run search-videos first.'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        downloader = VideoDownloader()
        extractor = BRollExtractor()
        
        extracted_clips = []
        
        scenes = plan.get('scenes', [])
        if scene_numbers:
            scenes = [s for s in scenes if s.get('scene_number') in scene_numbers]
        
        for scene in scenes:
            scene_num = scene.get('scene_number')
            scene_desc = scene.get('scene_description', '')
            
            # Get best video
            best_video = None
            for query_obj in scene.get('search_queries', []):
                videos = query_obj.get('sample_videos', [])
                if videos:
                    best_video = videos[0]
                    break
            
            if not best_video:
                continue
            
            try:
                # Download
                video_path = downloader.download(
                    url=best_video['url'],
                    output_dir=str(OUTPUT_DIR / "downloads")
                )
                
                if not video_path:
                    continue
                
                # Extract clip
                clip_path = extractor.extract_best_clip(
                    video_path=video_path,
                    duration=scene.get('duration', 5),
                    output_dir=str(OUTPUT_DIR / "clips")
                )
                
                if clip_path:
                    extracted_clips.append({
                        'scene': scene_desc,
                        'scene_number': scene_num,
                        'path': clip_path,
                        'source_url': best_video['url']
                    })
            
            except Exception as e:
                print(f"Error processing scene {scene_num}: {e}")
                continue
        
        # Save clips info
        clips_path = OUTPUT_DIR / f"clips_{plan_id}.json"
        with open(clips_path, 'w') as f:
            json.dump(extracted_clips, f, indent=2)
        
        return jsonify({
            'success': True,
            'plan_id': plan_id,
            'clips_extracted': len(extracted_clips),
            'clips': extracted_clips
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-images', methods=['POST'])
def generate_images():
    """
    Generate AI images for missing scenes using Cloudflare FLUX
    
    Body:
    {
        "plan_id": "20240211_123456",
        "provider": "cloudflare"  // or "modal"
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        provider = data.get('provider', 'cloudflare')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}_enriched.json"
        if not plan_path.exists():
            plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        
        if not plan_path.exists():
            return jsonify({'error': 'Plan not found'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Load extracted clips
        clips_path = OUTPUT_DIR / f"clips_{plan_id}.json"
        extracted_clips = []
        if clips_path.exists():
            with open(clips_path, 'r') as f:
                extracted_clips = json.load(f)
        
        # Generate images for missing scenes
        result = integrate_with_image_fallback(
            scenes=plan.get('scenes', []),
            extracted_clips=extracted_clips,
            output_dir=str(OUTPUT_DIR / f"images_{plan_id}"),
            provider=provider
        )
        
        return jsonify({
            'success': result.get('success', False),
            'plan_id': plan_id,
            'missing_scenes': result.get('missing_scenes', 0),
            'generated_images': result.get('generated_images', 0),
            'images': result.get('images', [])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-single-image', methods=['POST'])
def generate_single_image():
    """
    Generate a single image from prompt
    
    Body:
    {
        "prompt": "A rocket launching into space",
        "provider": "cloudflare"
    }
    """
    try:
        data = request.json
        prompt = data.get('prompt')
        provider = data.get('provider', 'cloudflare')
        
        if not prompt:
            return jsonify({'error': 'prompt is required'}), 400
        
        generator = FluxImageGenerator(provider=provider)
        
        # Generate image
        results = generator.generate_batch([prompt])
        
        if not results:
            return jsonify({'error': 'Image generation failed'}), 500
        
        # Save image
        image_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = OUTPUT_DIR / f"single_{image_id}.jpg"
        
        import base64
        from PIL import Image
        import io
        
        image_data = base64.b64decode(results[0]['image_b64'])
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(image_path, 'JPEG', quality=95)
        
        return jsonify({
            'success': True,
            'image_id': image_id,
            'image_path': str(image_path),
            'prompt': prompt
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files/<path:filename>', methods=['GET'])
def get_file(filename):
    """Serve generated files"""
    try:
        file_path = OUTPUT_DIR / filename
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/plans', methods=['GET'])
def list_plans():
    """List all production plans"""
    try:
        plans = []
        for plan_file in OUTPUT_DIR.glob("plan_*.json"):
            if '_enriched' not in plan_file.name:
                plan_id = plan_file.stem.replace('plan_', '')
                
                with open(plan_file, 'r') as f:
                    plan = json.load(f)
                
                plans.append({
                    'plan_id': plan_id,
                    'title': plan.get('title', 'Untitled'),
                    'scenes_count': len(plan.get('scenes', [])),
                    'created_at': plan_id
                })
        
        return jsonify({
            'success': True,
            'plans': sorted(plans, key=lambda x: x['plan_id'], reverse=True)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-premiere', methods=['POST'])
def export_premiere():
    """
    Export to Premiere Pro project
    
    Body:
    {
        "plan_id": "20240211_123456"
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        if not plan_path.exists():
            return jsonify({'error': 'Plan not found'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Load clips
        clips_path = OUTPUT_DIR / f"clips_{plan_id}.json"
        clips = []
        if clips_path.exists():
            with open(clips_path, 'r') as f:
                clips = json.load(f)
        
        # Load images
        images_dir = OUTPUT_DIR / f"images_{plan_id}"
        images = []
        if images_dir.exists():
            results_file = images_dir / "fallback_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
                    images = results.get('images', [])
        
        # Export to Premiere
        exporter = PremiereExporter()
        project_path = exporter.create_premiere_project(
            clips=clips,
            images=images,
            output_dir=str(OUTPUT_DIR),
            project_name=plan.get('title', 'AI_Video').replace(' ', '_')
        )
        
        return jsonify({
            'success': True,
            'project_path': project_path,
            'clips_count': len(clips),
            'images_count': len(images)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-capcut', methods=['POST'])
def export_capcut():
    """
    Export to CapCut project
    
    Body:
    {
        "plan_id": "20240211_123456"
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        if not plan_path.exists():
            return jsonify({'error': 'Plan not found'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Load clips
        clips_path = OUTPUT_DIR / f"clips_{plan_id}.json"
        clips = []
        if clips_path.exists():
            with open(clips_path, 'r') as f:
                clips = json.load(f)
        
        # Load images
        images_dir = OUTPUT_DIR / f"images_{plan_id}"
        images = []
        if images_dir.exists():
            results_file = images_dir / "fallback_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
                    images = results.get('images', [])
        
        # Export to CapCut
        exporter = CapCutExporter()
        project_path = exporter.create_capcut_project(
            clips=clips,
            images=images,
            output_dir=str(OUTPUT_DIR),
            project_name=plan.get('title', 'AI_Video').replace(' ', '_')
        )
        
        return jsonify({
            'success': True,
            'project_path': project_path,
            'clips_count': len(clips),
            'images_count': len(images)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-both', methods=['POST'])
def export_both():
    """
    Export to both Premiere Pro and CapCut
    
    Body:
    {
        "plan_id": "20240211_123456"
    }
    """
    try:
        data = request.json
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({'error': 'plan_id is required'}), 400
        
        # Load plan
        plan_path = OUTPUT_DIR / f"plan_{plan_id}.json"
        if not plan_path.exists():
            return jsonify({'error': 'Plan not found'}), 404
        
        with open(plan_path, 'r') as f:
            plan = json.load(f)
        
        # Load clips
        clips_path = OUTPUT_DIR / f"clips_{plan_id}.json"
        clips = []
        if clips_path.exists():
            with open(clips_path, 'r') as f:
                clips = json.load(f)
        
        # Load images
        images_dir = OUTPUT_DIR / f"images_{plan_id}"
        images = []
        if images_dir.exists():
            results_file = images_dir / "fallback_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
                    images = results.get('images', [])
        
        project_name = plan.get('title', 'AI_Video').replace(' ', '_')
        
        # Export to Premiere
        premiere_exporter = PremiereExporter()
        premiere_path = premiere_exporter.create_premiere_project(
            clips=clips,
            images=images,
            output_dir=str(OUTPUT_DIR),
            project_name=project_name
        )
        
        # Export to CapCut
        capcut_exporter = CapCutExporter()
        capcut_path = capcut_exporter.create_capcut_project(
            clips=clips,
            images=images,
            output_dir=str(OUTPUT_DIR),
            project_name=project_name
        )
        
        return jsonify({
            'success': True,
            'premiere_path': premiere_path,
            'capcut_path': capcut_path,
            'clips_count': len(clips),
            'images_count': len(images)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("🎬 AI VIDEO PRODUCTION API")
    print("=" * 80)
    print("\nEndpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/analyze-script - Analyze script with AI")
    print("  POST /api/search-videos - Search for videos")
    print("  POST /api/download-clips - Download and extract clips")
    print("  POST /api/generate-images - Generate AI images for missing scenes")
    print("  POST /api/generate-single-image - Generate single image from prompt")
    print("  POST /api/export-premiere - Export to Premiere Pro")
    print("  POST /api/export-capcut - Export to CapCut")
    print("  POST /api/export-both - Export to both editors")
    print("  GET  /api/plans - List all plans")
    print("  GET  /api/files/<filename> - Get generated files")
    print("\n" + "=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
