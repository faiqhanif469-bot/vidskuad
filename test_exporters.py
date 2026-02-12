"""
Test Premiere Pro and CapCut Exporters
"""

from src.tools.premiere_exporter import PremiereExporter
from src.tools.capcut_exporter import CapCutExporter


def test_exporters():
    """Test both exporters with sample data"""
    
    print("=" * 80)
    print("🎬 TESTING VIDEO EDITING SOFTWARE EXPORTERS")
    print("=" * 80)
    
    # Sample data (replace with your actual clips and images)
    clips = [
        {
            'scene_number': 1,
            'scene': 'Climate change introduction',
            'path': 'output/clips/scene_001.mp4',
            'source_url': 'https://youtube.com/watch?v=example1'
        },
        {
            'scene_number': 3,
            'scene': 'Rising sea levels',
            'path': 'output/clips/scene_003.mp4',
            'source_url': 'https://youtube.com/watch?v=example2'
        }
    ]
    
    images = [
        {
            'scene_number': 2,
            'scene_description': 'Melting glaciers',
            'image_path': 'output/generated_images/scene_002.jpg',
            'image_prompt': 'Massive glacier melting into ocean, dramatic lighting'
        },
        {
            'scene_number': 4,
            'scene_description': 'Renewable energy',
            'image_path': 'output/generated_images/scene_004.jpg',
            'image_prompt': 'Solar panels and wind turbines, sustainable future'
        }
    ]
    
    project_name = "Climate_Change_Video"
    
    # Test Premiere Pro Exporter
    print("\n" + "=" * 80)
    print("TEST 1: PREMIERE PRO EXPORTER")
    print("=" * 80)
    
    premiere_exporter = PremiereExporter()
    premiere_path = premiere_exporter.create_premiere_project(
        clips=clips,
        images=images,
        output_dir='output',
        project_name=project_name
    )
    
    print(f"\n✅ Premiere Pro project created!")
    print(f"📂 Location: {premiere_path}")
    print(f"\n📝 To use:")
    print(f"   1. Open Adobe Premiere Pro")
    print(f"   2. File → Import")
    print(f"   3. Select: {premiere_path}/{project_name}.xml")
    print(f"   4. Start editing!")
    
    # Test CapCut Exporter
    print("\n" + "=" * 80)
    print("TEST 2: CAPCUT EXPORTER")
    print("=" * 80)
    
    capcut_exporter = CapCutExporter()
    capcut_path = capcut_exporter.create_capcut_project(
        clips=clips,
        images=images,
        output_dir='output',
        project_name=project_name
    )
    
    print(f"\n✅ CapCut project created!")
    print(f"📂 Location: {capcut_path}")
    print(f"\n📝 To use:")
    print(f"   1. Open CapCut Desktop App")
    print(f"   2. Click 'Import Project'")
    print(f"   3. Select: {capcut_path}/draft_content.json")
    print(f"   4. Start editing!")
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎉 ALL TESTS COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   Video clips: {len(clips)}")
    print(f"   AI images: {len(images)}")
    print(f"   Total scenes: {len(clips) + len(images)}")
    print(f"\n📁 Projects created:")
    print(f"   ✓ Premiere Pro: {premiere_path}")
    print(f"   ✓ CapCut: {capcut_path}")
    print(f"\n✨ Both projects are ready to import!")
    print(f"   Choose your preferred editing software and start creating!")


if __name__ == '__main__':
    test_exporters()
