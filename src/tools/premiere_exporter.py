"""
Adobe Premiere Pro Project Exporter
Generates .prproj XML that can be imported into Premiere Pro
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import shutil


class PremiereExporter:
    """Export video production to Premiere Pro project"""
    
    def __init__(self):
        self.frame_rate = 30
        self.video_width = 1920
        self.video_height = 1080
    
    def create_premiere_project(
        self,
        clips: List[Dict],
        images: List[Dict],
        output_dir: str,
        project_name: str = "AI_Video_Production"
    ) -> str:
        """
        Create Premiere Pro project folder with XML and media
        
        Args:
            clips: List of video clip dicts with paths
            images: List of image dicts with paths
            output_dir: Where to create the project folder
            project_name: Name of the project
        
        Returns:
            Path to the created project folder
        """
        print("\n" + "=" * 80)
        print("🎬 CREATING PREMIERE PRO PROJECT")
        print("=" * 80)
        
        # Create project structure
        project_dir = Path(output_dir) / f"{project_name}_Premiere"
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
                    'premiere_path': str(dest_path.relative_to(project_dir))
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
                    'premiere_path': str(dest_path.relative_to(project_dir))
                })
                print(f"   ✓ Image {i}/{len(images)}: {dest_path.name}")
        
        # Generate XML project file
        print("\n📝 Generating Premiere Pro XML...")
        xml_content = self._generate_premiere_xml(copied_clips, copied_images, project_name)
        
        xml_path = project_dir / f"{project_name}.xml"
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"   ✓ XML file: {xml_path.name}")
        
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
        print("✅ PREMIERE PRO PROJECT READY!")
        print("=" * 80)
        print(f"\n📂 Location: {project_dir}")
        print(f"📊 Contents:")
        print(f"   - {len(copied_clips)} video clips")
        print(f"   - {len(copied_images)} AI-generated images")
        print(f"   - Premiere Pro XML file")
        print(f"   - Instructions for import")
        
        return str(project_dir)
    
    def _generate_premiere_xml(
        self,
        clips: List[Dict],
        images: List[Dict],
        project_name: str
    ) -> str:
        """Generate Final Cut Pro XML (compatible with Premiere)"""
        
        # Combine and sort by scene number
        all_media = []
        for clip in clips:
            all_media.append({
                'type': 'video',
                'scene_number': clip['scene_number'],
                'path': clip['premiere_path'],
                'duration': 5.0  # Default duration
            })
        
        for img in images:
            all_media.append({
                'type': 'image',
                'scene_number': img['scene_number'],
                'path': img['premiere_path'],
                'duration': 5.0  # Default image duration
            })
        
        all_media.sort(key=lambda x: x['scene_number'])
        
        # Build XML
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5">
    <project>
        <name>{project_name}</name>
        <children>
            <bin>
                <name>Media</name>
                <children>
                    <bin>
                        <name>Clips</name>
                        <children>
'''
        
        # Add video clips
        for i, item in enumerate(all_media):
            if item['type'] == 'video':
                xml += f'''
                            <clip id="clip-{i+1}">
                                <name>Scene {item['scene_number']:03d}</name>
                                <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                <rate>
                                    <timebase>{self.frame_rate}</timebase>
                                </rate>
                                <media>
                                    <video>
                                        <track>
                                            <clipitem id="clipitem-{i+1}">
                                                <name>Scene {item['scene_number']:03d}</name>
                                                <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                                <rate>
                                                    <timebase>{self.frame_rate}</timebase>
                                                </rate>
                                                <file id="file-{i+1}">
                                                    <name>{Path(item['path']).name}</name>
                                                    <pathurl>file://localhost/{item['path'].replace('\\', '/')}</pathurl>
                                                    <rate>
                                                        <timebase>{self.frame_rate}</timebase>
                                                    </rate>
                                                    <media>
                                                        <video>
                                                            <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                                            <samplecharacteristics>
                                                                <width>{self.video_width}</width>
                                                                <height>{self.video_height}</height>
                                                            </samplecharacteristics>
                                                        </video>
                                                    </media>
                                                </file>
                                            </clipitem>
                                        </track>
                                    </video>
                                </media>
                            </clip>
'''
        
        xml += '''
                        </children>
                    </bin>
                    <bin>
                        <name>Images</name>
                        <children>
'''
        
        # Add images
        for i, item in enumerate(all_media):
            if item['type'] == 'image':
                xml += f'''
                            <clip id="clip-img-{i+1}">
                                <name>Scene {item['scene_number']:03d}</name>
                                <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                <rate>
                                    <timebase>{self.frame_rate}</timebase>
                                </rate>
                                <media>
                                    <video>
                                        <track>
                                            <clipitem id="clipitem-img-{i+1}">
                                                <name>Scene {item['scene_number']:03d}</name>
                                                <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                                <file id="file-img-{i+1}">
                                                    <name>{Path(item['path']).name}</name>
                                                    <pathurl>file://localhost/{item['path'].replace('\\', '/')}</pathurl>
                                                    <media>
                                                        <video>
                                                            <duration>{int(item['duration'] * self.frame_rate)}</duration>
                                                            <samplecharacteristics>
                                                                <width>{self.video_width}</width>
                                                                <height>{self.video_height}</height>
                                                            </samplecharacteristics>
                                                        </video>
                                                    </media>
                                                </file>
                                            </clipitem>
                                        </track>
                                    </video>
                                </media>
                            </clip>
'''
        
        xml += '''
                        </children>
                    </bin>
                </children>
            </bin>
            <sequence>
                <name>Main Timeline</name>
                <duration>''' + str(int(sum(item['duration'] for item in all_media) * self.frame_rate)) + '''</duration>
                <rate>
                    <timebase>''' + str(self.frame_rate) + '''</timebase>
                </rate>
                <media>
                    <video>
                        <format>
                            <samplecharacteristics>
                                <width>''' + str(self.video_width) + '''</width>
                                <height>''' + str(self.video_height) + '''</height>
                            </samplecharacteristics>
                        </format>
                        <track>
'''
        
        # Add clips to timeline in order
        current_time = 0
        for i, item in enumerate(all_media):
            duration_frames = int(item['duration'] * self.frame_rate)
            xml += f'''
                            <clipitem id="timeline-{i+1}">
                                <name>Scene {item['scene_number']:03d}</name>
                                <start>{current_time}</start>
                                <end>{current_time + duration_frames}</end>
                                <in>0</in>
                                <out>{duration_frames}</out>
                            </clipitem>
'''
            current_time += duration_frames
        
        xml += '''
                        </track>
                    </video>
                </media>
            </sequence>
        </children>
    </project>
</xmeml>
'''
        
        return xml
    
    def _create_instructions(self, project_name: str) -> str:
        """Create instruction file for users"""
        return f"""
================================================================================
PREMIERE PRO PROJECT - {project_name}
================================================================================

📂 FOLDER STRUCTURE:
   {project_name}_Premiere/
   ├── {project_name}.xml          ← Import this into Premiere Pro
   ├── Media/
   │   ├── Clips/                  ← Video clips
   │   └── Images/                 ← AI-generated images
   ├── scene_order.json            ← Scene metadata
   └── README.txt                  ← This file

================================================================================
HOW TO IMPORT INTO PREMIERE PRO:
================================================================================

METHOD 1: Import XML (Recommended)
-----------------------------------
1. Open Adobe Premiere Pro
2. File → Import...
3. Select "{project_name}.xml"
4. Click "Import"
5. All media will be organized in bins
6. Open "Main Timeline" sequence to start editing

METHOD 2: Manual Import
-----------------------
1. Open Adobe Premiere Pro
2. Create New Project
3. File → Import... → Select entire "Media" folder
4. Drag clips to timeline in scene order (see scene_order.json)

================================================================================
EDITING TIPS:
================================================================================

✓ All clips are pre-organized by scene number
✓ Video clips are in Media/Clips/
✓ AI-generated images are in Media/Images/
✓ Default duration for images: 5 seconds (adjust as needed)
✓ Recommended: Add transitions between scenes
✓ Recommended: Add background music
✓ Recommended: Add text overlays for narration

================================================================================
EXPORT SETTINGS (Recommended):
================================================================================

Format: H.264
Preset: YouTube 1080p HD
Resolution: 1920x1080
Frame Rate: 30 fps
Bitrate: VBR, 2 pass, Target 10 Mbps

================================================================================
NEED HELP?
================================================================================

- Check scene_order.json for scene descriptions
- All media files are relative to this project folder
- Keep this folder structure intact for proper linking

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
                'file': clip['premiere_path'],
                'source': clip.get('source_url', '')
            })
        
        for img in images:
            scenes.append({
                'scene_number': img['scene_number'],
                'type': 'image',
                'description': img.get('scene_description', ''),
                'file': img['premiere_path'],
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
    
    exporter = PremiereExporter()
    project_path = exporter.create_premiere_project(
        clips=clips,
        images=images,
        output_dir='output',
        project_name='Test_Video'
    )
    
    print(f"\n✅ Project created: {project_path}")


if __name__ == '__main__':
    main()
