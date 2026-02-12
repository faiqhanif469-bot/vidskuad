"""
CapCut Project Exporter
Generates draft_content.json that can be imported into CapCut
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import uuid


class CapCutExporter:
    """Export video production to CapCut project"""
    
    def __init__(self):
        self.frame_rate = 30
        self.video_width = 1920
        self.video_height = 1080
    
    def create_capcut_project(
        self,
        clips: List[Dict],
        images: List[Dict],
        output_dir: str,
        project_name: str = "AI_Video_Production"
    ) -> str:
        """
        Create CapCut project folder with draft_content.json
        
        Args:
            clips: List of video clip dicts with paths
            images: List of image dicts with paths
            output_dir: Where to create the project folder
            project_name: Name of the project
        
        Returns:
            Path to the created project folder
        """
        print("\n" + "=" * 80)
        print("✂️ CREATING CAPCUT PROJECT")
        print("=" * 80)
        
        # Create project structure
        project_dir = Path(output_dir) / f"{project_name}_CapCut"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        media_dir = project_dir / "Media"
        media_dir.mkdir(exist_ok=True)
        
        clips_dir = media_dir / "Clips"
        clips_dir.mkdir(exist_ok=True)
        
        images_dir = media_dir / "Images"
        images_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 Project folder: {project_dir}")
        
        # Copy media files
        print("\n📦 Copying media files...")
        
        copied_clips = []
        for i, clip in enumerate(clips, 1):
            src_path = Path(clip['path'])
            if src_path.exists():
                dest_path = clips_dir / f"scene_{clip['scene_number']:03d}_{src_path.name}"
                shutil.copy2(src_path, dest_path)
                copied_clips.append({
                    **clip,
                    'capcut_path': str(dest_path),
                    'relative_path': str(dest_path.relative_to(project_dir))
                })
                print(f"   ✓ Clip {i}/{len(clips)}: {dest_path.name}")
        
        copied_images = []
        for i, img in enumerate(images, 1):
            src_path = Path(img['image_path'])
            if src_path.exists():
                dest_path = images_dir / f"scene_{img['scene_number']:03d}.jpg"
                shutil.copy2(src_path, dest_path)
                copied_images.append({
                    **img,
                    'capcut_path': str(dest_path),
                    'relative_path': str(dest_path.relative_to(project_dir))
                })
                print(f"   ✓ Image {i}/{len(images)}: {dest_path.name}")
        
        # Generate CapCut draft_content.json
        print("\n📝 Generating CapCut project file...")
        draft_content = self._generate_capcut_json(copied_clips, copied_images, project_name)
        
        json_path = project_dir / "draft_content.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(draft_content, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Project file: {json_path.name}")
        
        # Create instructions file
        instructions = self._create_instructions(project_name)
        instructions_path = project_dir / "README.txt"
        with open(instructions_path, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"   ✓ Instructions: {instructions_path.name}")
        
        # Create scene order file
        scene_order = self._create_scene_order(copied_clips, copied_images)
        order_path = project_dir / "scene_order.json"
        with open(order_path, 'w', encoding='utf-8') as f:
            json.dump(scene_order, f, indent=2)
        
        print(f"   ✓ Scene order: {order_path.name}")
        
        print("\n" + "=" * 80)
        print("✅ CAPCUT PROJECT READY!")
        print("=" * 80)
        print(f"\n📂 Location: {project_dir}")
        print(f"📊 Contents:")
        print(f"   - {len(copied_clips)} video clips")
        print(f"   - {len(copied_images)} AI-generated images")
        print(f"   - CapCut draft_content.json")
        print(f"   - Instructions for import")
        
        return str(project_dir)
    
    def _generate_capcut_json(
        self,
        clips: List[Dict],
        images: List[Dict],
        project_name: str
    ) -> Dict:
        """Generate CapCut draft_content.json format"""
        
        # Combine and sort by scene number
        all_media = []
        for clip in clips:
            all_media.append({
                'type': 'video',
                'scene_number': clip['scene_number'],
                'path': clip['capcut_path'],
                'duration': 5000000  # 5 seconds in microseconds
            })
        
        for img in images:
            all_media.append({
                'type': 'image',
                'scene_number': img['scene_number'],
                'path': img['capcut_path'],
                'duration': 5000000  # 5 seconds in microseconds
            })
        
        all_media.sort(key=lambda x: x['scene_number'])
        
        # Build CapCut JSON structure
        materials = {
            "videos": [],
            "images": [],
            "audios": []
        }
        
        tracks = []
        current_time = 0
        
        # Add materials and track segments
        for i, item in enumerate(all_media):
            material_id = str(uuid.uuid4())
            
            if item['type'] == 'video':
                materials['videos'].append({
                    "id": material_id,
                    "path": item['path'],
                    "type": "video",
                    "duration": item['duration'],
                    "width": self.video_width,
                    "height": self.video_height,
                    "fps": self.frame_rate
                })
            else:
                materials['images'].append({
                    "id": material_id,
                    "path": item['path'],
                    "type": "photo",
                    "duration": item['duration'],
                    "width": self.video_width,
                    "height": self.video_height
                })
            
            # Add to track
            tracks.append({
                "id": str(uuid.uuid4()),
                "type": item['type'],
                "material_id": material_id,
                "target_timerange": {
                    "start": current_time,
                    "duration": item['duration']
                },
                "source_timerange": {
                    "start": 0,
                    "duration": item['duration']
                },
                "enable_adjust": True,
                "enable_color_curves": True,
                "enable_color_match_adjust": False,
                "enable_color_wheels": True,
                "enable_lut": False,
                "enable_smart_color_adjust": False,
                "extra_material_refs": [],
                "hdr_settings": {
                    "intensity": 1.0,
                    "mode": 1
                },
                "is_placeholder": False,
                "is_tone_modify": False,
                "reverse": False,
                "speed": 1.0,
                "volume": 1.0
            })
            
            current_time += item['duration']
        
        # Build complete draft content
        draft_content = {
            "draft_fold": project_name,
            "draft_id": str(uuid.uuid4()),
            "draft_name": project_name,
            "draft_removable_storage_device": "",
            "draft_root": "",
            "draft_timeline": {
                "duration": current_time,
                "fps": self.frame_rate,
                "tracks": [
                    {
                        "attribute": 0,
                        "flag": 0,
                        "id": str(uuid.uuid4()),
                        "segments": tracks,
                        "type": "video"
                    }
                ],
                "video_target_resolution": {
                    "height": self.video_height,
                    "width": self.video_width
                }
            },
            "materials": materials,
            "platform": "windows",
            "version": "5.0.0"
        }
        
        return draft_content
    
    def _create_instructions(self, project_name: str) -> str:
        """Create instruction file for users"""
        return f"""
================================================================================
CAPCUT PROJECT - {project_name}
================================================================================

📂 FOLDER STRUCTURE:
   {project_name}_CapCut/
   ├── draft_content.json          ← CapCut project file
   ├── Media/
   │   ├── Clips/                  ← Video clips
   │   └── Images/                 ← AI-generated images
   ├── scene_order.json            ← Scene metadata
   └── README.txt                  ← This file

================================================================================
HOW TO IMPORT INTO CAPCUT:
================================================================================

METHOD 1: Import Project (Desktop)
-----------------------------------
1. Open CapCut Desktop App
2. Click "Import Project"
3. Navigate to this folder
4. Select "draft_content.json"
5. Click "Open"
6. All media will be loaded on timeline

METHOD 2: Drag & Drop (Desktop)
--------------------------------
1. Open CapCut Desktop App
2. Create New Project
3. Drag entire "Media" folder into CapCut
4. Arrange clips on timeline by scene number

METHOD 3: Mobile (CapCut App)
------------------------------
1. Transfer this folder to your phone
2. Open CapCut mobile app
3. Tap "New Project"
4. Select all files from Media/Clips and Media/Images
5. Arrange by scene number

================================================================================
EDITING TIPS:
================================================================================

✓ All clips are pre-organized by scene number
✓ Video clips are in Media/Clips/
✓ AI-generated images are in Media/Images/
✓ Default duration for images: 5 seconds
✓ Recommended: Add transitions (swipe, fade, zoom)
✓ Recommended: Add background music from CapCut library
✓ Recommended: Add text/captions for narration
✓ Recommended: Apply filters for consistent look

================================================================================
CAPCUT FEATURES TO USE:
================================================================================

🎨 Effects:
   - Transitions between scenes
   - Filters for mood/tone
   - Speed adjustments

🎵 Audio:
   - Background music from library
   - Sound effects
   - Voiceover recording

📝 Text:
   - Captions/subtitles
   - Title cards
   - Lower thirds

✨ Advanced:
   - Keyframe animations
   - Chroma key (green screen)
   - Picture-in-picture

================================================================================
EXPORT SETTINGS (Recommended):
================================================================================

Resolution: 1080p (1920x1080)
Frame Rate: 30 fps
Quality: High
Format: MP4

For Social Media:
- YouTube: 1080p, 16:9
- Instagram: 1080x1080 (square) or 1080x1920 (story)
- TikTok: 1080x1920 (vertical)

================================================================================
NEED HELP?
================================================================================

- Check scene_order.json for scene descriptions
- Keep Media folder in same location as draft_content.json
- If clips don't load, check file paths in draft_content.json

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================
"""
    
    def _create_scene_order(self, clips: List[Dict], images: List[Dict]) -> Dict:
        """Create scene order metadata"""
        scenes = []
        
        for clip in clips:
            scenes.append({
                'scene_number': clip['scene_number'],
                'type': 'video',
                'description': clip.get('scene', ''),
                'file': clip['relative_path'],
                'source': clip.get('source_url', '')
            })
        
        for img in images:
            scenes.append({
                'scene_number': img['scene_number'],
                'type': 'image',
                'description': img.get('scene_description', ''),
                'file': img['relative_path'],
                'prompt': img.get('image_prompt', '')
            })
        
        scenes.sort(key=lambda x: x['scene_number'])
        
        return {
            'project_name': 'AI Video Production',
            'created_at': datetime.now().isoformat(),
            'total_scenes': len(scenes),
            'video_clips': len(clips),
            'ai_images': len(images),
            'scenes': scenes
        }


def main():
    """Test the exporter"""
    # Example data
    clips = [
        {
            'scene_number': 1,
            'scene': 'rocket launching',
            'path': 'output/clips/clip1.mp4',
            'source_url': 'https://youtube.com/watch?v=example'
        }
    ]
    
    images = [
        {
            'scene_number': 2,
            'scene_description': 'astronaut in space',
            'image_path': 'output/images/scene_002.jpg',
            'image_prompt': 'astronaut floating in space'
        }
    ]
    
    exporter = CapCutExporter()
    project_path = exporter.create_capcut_project(
        clips=clips,
        images=images,
        output_dir='output',
        project_name='Test_Video'
    )
    
    print(f"\n✅ Project created: {project_path}")


if __name__ == '__main__':
    main()
