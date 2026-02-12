"""
Quick test script for FLUX image generation
Run this to verify Modal setup and generate test images
"""

import sys
from pathlib import Path


def check_modal_setup():
    """Check if Modal is properly set up"""
    print("🔍 Checking Modal setup...\n")
    
    # Check if Modal is installed
    try:
        import modal
        print("✅ Modal SDK installed")
    except ImportError:
        print("❌ Modal SDK not found")
        print("\nInstall with:")
        print("  pip install modal")
        return False
    
    # Check if authenticated
    try:
        # Try to create a simple app to test auth
        test_app = modal.App("test-auth")
        print("✅ Modal authentication working")
    except Exception as e:
        print("❌ Modal authentication failed")
        print("\nAuthenticate with:")
        print("  modal token new")
        return False
    
    print("\n✅ Modal setup complete!\n")
    return True


def test_single_image():
    """Test generating a single image"""
    print("="*80)
    print("TEST 1: Single Image Generation")
    print("="*80)
    
    try:
        import modal
        import base64
        from pathlib import Path
        
        print("\n🎨 Generating single test image...")
        
        # Lookup deployed app
        app = modal.Lookup("flux-klein-image-generator", "main")
        FluxImageGenerator = app.cls("FluxImageGenerator")
        
        generator = FluxImageGenerator()
        result = generator.generate_single.remote(
            prompt="A majestic rocket launching into space with flames and smoke, dramatic lighting, photorealistic, 4K",
            width=1024,
            height=1024,
        )
        
        # Save image
        output_dir = Path("output/test_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        img_data = base64.b64decode(result['image'])
        filepath = output_dir / "test_single.png"
        
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        print(f"✅ Image saved to: {filepath}")
        print(f"   Size: {result['width']}x{result['height']}")
        print(f"   Prompt: {result['prompt'][:60]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_batch_generation():
    """Test generating multiple images in batch"""
    print("\n" + "="*80)
    print("TEST 2: Batch Generation (3 images)")
    print("="*80)
    
    try:
        import modal
        import base64
        from pathlib import Path
        
        print("\n🎨 Generating batch of 3 images...")
        
        prompts = [
            "Rocket launching from launch pad, dramatic flames and smoke, photorealistic",
            "Astronaut floating in space with Earth in background, peaceful, high detail",
            "NASA mission control room in 1960s, vintage documentary style",
        ]
        
        # Lookup deployed app
        app = modal.Lookup("flux-klein-image-generator", "main")
        FluxImageGenerator = app.cls("FluxImageGenerator")
        
        generator = FluxImageGenerator()
        results = generator.generate_batch.remote(
            prompts=prompts,
            width=1024,
            height=1024,
        )
        
        # Save images
        output_dir = Path("output/test_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, result in enumerate(results):
            img_data = base64.b64decode(result['image'])
            filepath = output_dir / f"test_batch_{i+1}.png"
            
            with open(filepath, 'wb') as f:
                f.write(img_data)
            
            print(f"   ✅ Image {i+1}: {filepath}")
            print(f"      Prompt: {result['prompt'][:50]}...")
        
        print(f"\n✅ Generated {len(results)} images successfully!")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_workflow():
    """Test the complete workflow with scene prompts"""
    print("\n" + "="*80)
    print("TEST 3: Full Workflow (Scene Prompts)")
    print("="*80)
    
    try:
        import modal
        
        print("\n🎨 Testing full workflow with scene data...")
        
        scene_prompts = [
            {
                'scene_number': 1,
                'scene_description': 'rocket launching into space',
                'image_prompt': 'Powerful rocket launching from Kennedy Space Center with massive flames and smoke clouds, dramatic lighting, photorealistic NASA footage style, high quality, 4K',
            },
            {
                'scene_number': 2,
                'scene_description': 'astronaut on moon surface',
                'image_prompt': 'Astronaut in white spacesuit standing on lunar surface with American flag, Earth visible in black sky, historical moon landing photography style, high detail',
            },
        ]
        
        # Lookup deployed app
        app = modal.Lookup("flux-klein-image-generator", "main")
        generate_from_scene_prompts = app.function("generate_from_scene_prompts")
        
        result = generate_from_scene_prompts.remote(
            scene_prompts=scene_prompts,
            output_dir="output/test_images/workflow"
        )
        
        if result['success']:
            print(f"\n✅ Workflow complete!")
            print(f"   Generated: {result['total_images']} images")
            print(f"   Output: {result['images'][0]['filepath'].rsplit('/', 1)[0]}")
            
            for img in result['images']:
                print(f"   - Scene {img['scene_number']}: {Path(img['filepath']).name}")
            
            return True
        else:
            print("❌ Workflow failed")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_integration():
    """Test integration with image_fallback.py"""
    print("\n" + "="*80)
    print("TEST 4: Integration with Image Fallback")
    print("="*80)
    
    try:
        from src.tools.flux_generator import integrate_with_image_fallback
        
        print("\n🎨 Testing integration with image fallback system...")
        
        # Test scenes
        scenes = [
            {
                'scene_number': 1,
                'scene_description': 'rocket launching into space',
                'keywords': ['rocket', 'launch', 'space'],
                'visual_context': 'powerful rocket lifting off',
                'mood_tone': 'dramatic'
            },
            {
                'scene_number': 2,
                'scene_description': 'astronaut floating in space',
                'keywords': ['astronaut', 'spacewalk', 'orbit'],
                'visual_context': 'astronaut in spacesuit floating',
                'mood_tone': 'peaceful'
            },
        ]
        
        # Simulate: No clips found (all need images)
        extracted_clips = []
        
        result = integrate_with_image_fallback(
            scenes=scenes,
            extracted_clips=extracted_clips,
            output_dir="output/test_images/integration"
        )
        
        if result['success']:
            print(f"\n✅ Integration test complete!")
            print(f"   Missing scenes: {result['missing_scenes']}")
            print(f"   Generated images: {result['generated_images']}")
            return True
        else:
            print("❌ Integration test failed")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 FLUX IMAGE GENERATION TEST SUITE")
    print("="*80)
    print()
    
    # Check setup
    if not check_modal_setup():
        print("\n❌ Setup incomplete. Please fix the issues above and try again.")
        return
    
    # Run tests
    tests = [
        ("Single Image", test_single_image),
        ("Batch Generation", test_batch_generation),
        ("Full Workflow", test_full_workflow),
        ("Integration", test_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your FLUX setup is working perfectly.")
        print("\nNext steps:")
        print("  1. Check generated images in output/test_images/")
        print("  2. Integrate into your pipeline")
        print("  3. Deploy to Modal: modal deploy modal_flux_service.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("  - Modal not authenticated: modal token new")
        print("  - First run takes time to download model (~5-10 min)")
        print("  - Check Modal dashboard for detailed errors")


if __name__ == "__main__":
    main()
