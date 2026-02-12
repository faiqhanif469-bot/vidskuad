"""
Test OpenAI-compatible API for FLUX image generation
"""
import requests
import base64
import time
from pathlib import Path

# Your Modal endpoint URL (get this after deployment)
# Format: https://your-username--flux-klein-image-generator-openai-compatible-api.modal.run
ENDPOINT_URL = "https://faiq84016--flux-klein-image-generator-openai-compatible-api.modal.run"

def test_single_image():
    """Test generating a single image"""
    print("\n" + "="*80)
    print("TEST 1: Single Image Generation")
    print("="*80)
    
    start = time.time()
    
    response = requests.post(
        ENDPOINT_URL,
        json={
            "model": "flux-klein-4b",
            "prompt": "A cat holding a sign that says hello world",
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json"
        }
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        
        # Save image
        img_data = base64.b64decode(data["data"][0]["b64_json"])
        output_path = Path("output/test_single.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(img_data)
        
        print(f"✅ Success!")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Saved to: {output_path}")
        print(f"   Throughput: {3600/elapsed:.0f} images/hour")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_batch_images():
    """Test generating multiple images"""
    print("\n" + "="*80)
    print("TEST 2: Batch Image Generation (6 images)")
    print("="*80)
    
    start = time.time()
    
    response = requests.post(
        ENDPOINT_URL,
        json={
            "model": "flux-klein-4b",
            "prompt": "A beautiful landscape with mountains and lakes",
            "n": 6,  # Optimal batch size for L4
            "size": "1024x1024",
            "response_format": "b64_json"
        }
    )
    
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        
        # Save images
        for i, img in enumerate(data["data"]):
            img_data = base64.b64decode(img["b64_json"])
            output_path = Path(f"output/test_batch_{i+1}.png")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(img_data)
        
        avg_time = elapsed / 6
        
        print(f"✅ Success!")
        print(f"   Total time: {elapsed:.2f}s")
        print(f"   Avg per image: {avg_time:.2f}s")
        print(f"   Throughput: {3600/avg_time:.0f} images/hour")
        print(f"   Saved 6 images to: output/test_batch_*.png")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_different_sizes():
    """Test different image sizes"""
    print("\n" + "="*80)
    print("TEST 3: Different Image Sizes")
    print("="*80)
    
    sizes = ["512x512", "1024x1024", "1024x768"]
    
    for size in sizes:
        print(f"\n   Testing {size}...")
        start = time.time()
        
        response = requests.post(
            ENDPOINT_URL,
            json={
                "model": "flux-klein-4b",
                "prompt": "A futuristic city at sunset",
                "n": 1,
                "size": size,
                "response_format": "b64_json"
            }
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            print(f"      ✅ {size}: {elapsed:.2f}s")
        else:
            print(f"      ❌ {size}: Error {response.status_code}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 FLUX-2-klein-4B OpenAI API Speed Test")
    print("="*80)
    print("\n⚠️  Make sure to update ENDPOINT_URL in this file first!")
    print("   Get it from: modal app list")
    
    if ENDPOINT_URL == "YOUR_ENDPOINT_URL_HERE":
        print("\n❌ Please update ENDPOINT_URL first!")
        print("\nAfter deployment, run:")
        print("   modal app list")
        print("   # Copy the openai_compatible_api URL")
        print("   # Update ENDPOINT_URL in this file")
        exit(1)
    
    # Run tests
    test_single_image()
    test_batch_images()
    test_different_sizes()
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE!")
    print("="*80)
    print("\nExpected Performance (L4 GPU):")
    print("   Single image: ~2.5s")
    print("   Batch of 6: ~15s (2.5s per image)")
    print("   Throughput: ~2,880 images/hour")
    print("   Cost: $0.00028 per image")
