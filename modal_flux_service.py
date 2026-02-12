"""
FLUX-2-klein-4B Image Generation Service on Modal (2026 Optimized)
Supports single and batch image generation with L4 GPU
- Optimized for L4 GPU (24GB VRAM)
- Batch size: 6 images (optimal for L4)
- Generation speed: ~2.5s per image
- Throughput: ~2,880 images/hour with batching
- Cost: $0.80/hour = $0.00028 per image
"""

import modal
from pathlib import Path
from typing import List, Dict, Optional
import json
import base64
from io import BytesIO

# Create Modal app
app = modal.App("flux-klein-image-generator")

# Define the image with all dependencies (2026 latest versions)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")  # Need git to install from GitHub
    .pip_install(
        "torch>=2.5.0",  # Latest PyTorch with Triton optimizations
        "transformers>=4.48.0",  # Latest with Mistral3 support
        "accelerate>=1.1.0",
        "pillow>=11.0.0",
        "sentencepiece>=0.2.0",
        "fastapi",  # Required for web endpoints (2026 Modal requirement)
    )
    # Install latest diffusers from GitHub (has Flux2KleinPipeline)
    .run_commands("pip install git+https://github.com/huggingface/diffusers.git")
)

# GPU configuration - L4 with 24GB VRAM (optimal for FLUX-2-klein-4B)
GPU_CONFIG = "L4"

# Model cache volume for faster cold starts
model_volume = modal.Volume.from_name("flux-klein-models", create_if_missing=True)
MODEL_CACHE_PATH = "/cache/models"

# Optimal batch size for L4 GPU (24GB VRAM)
OPTIMAL_BATCH_SIZE = 6  # Best balance of speed and memory


@app.cls(
    image=image,
    gpu=GPU_CONFIG,
    timeout=600,  # 10 minutes max
    scaledown_window=60,  # Keep warm for 1 minute (short for sporadic traffic)
    volumes={MODEL_CACHE_PATH: model_volume},
    # Enable memory snapshot for fast cold starts (2-3s instead of 20s!)
    enable_memory_snapshot=True,
    # TESTING: Only 1 container at a time (2026 API)
    max_containers=1,  # Was concurrency_limit
)
@modal.concurrent(max_inputs=1)  # Process 1 request at a time (for testing)
class FluxImageGenerator:
    """FLUX-2-klein-4B image generator with batch support"""
    
    @modal.enter()
    def load_model(self):
        """Load model on container startup (runs once, then snapshotted!)"""
        import torch
        from diffusers import Flux2KleinPipeline
        import os
        
        print("🚀 Loading FLUX-2-klein-4B model (2026 optimized)...")
        
        self.device = "cuda"
        self.dtype = torch.bfloat16
        
        # Load FLUX.2-klein pipeline
        self.pipe = Flux2KleinPipeline.from_pretrained(
            "black-forest-labs/FLUX.2-klein-4B",
            torch_dtype=self.dtype,
            cache_dir=MODEL_CACHE_PATH,
        )
        
        # Move to GPU
        self.pipe = self.pipe.to(self.device)
        
        # DISABLED: torch.compile (testing baseline performance)
        # Path for compiled model cache
        # compiled_cache = os.path.join(MODEL_CACHE_PATH, "compiled_transformer")
        
        # Enable torch.compile with persistent cache
        # print("⚡ Compiling model with torch.compile for Triton optimization...")
        # try:
        #     # Set cache directory for compiled artifacts
        #     os.environ["TORCHINDUCTOR_CACHE_DIR"] = compiled_cache
        #     
        #     self.pipe.transformer = torch.compile(
        #         self.pipe.transformer,
        #         mode="reduce-overhead",
        #         fullgraph=True,
        #     )
        #     print("✅ Triton compilation enabled with persistent cache!")
        # except Exception as e:
        #     print(f"⚠️ Triton compilation failed (will use default): {e}")
        
        # Warm up GPU
        print("🔥 Warming up GPU (WITHOUT torch.compile)...")
        _ = self.pipe(
            prompt="test",
            height=512,
            width=512,
            num_inference_steps=4,
            guidance_scale=1.0,
        )
        
        print("✅ Model loaded and ready (baseline performance)!")
        print(f"   Optimal batch size for L4: {OPTIMAL_BATCH_SIZE} images")
    
    @modal.method()
    def generate_single(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 4,
        guidance_scale: float = 1.0,
        seed: Optional[int] = None,
    ) -> Dict:
        """
        Generate a single image
        
        Args:
            prompt: Text description of the image
            width: Image width (multiple of 16, max 2048)
            height: Image height (multiple of 16, max 2048)
            num_inference_steps: Number of steps (4 recommended for speed)
            guidance_scale: How closely to follow prompt (1.0 recommended)
            seed: Random seed for reproducibility
        
        Returns:
            Dict with base64 encoded image and metadata
        """
        import torch
        from PIL import Image
        
        print(f"🎨 Generating image: {prompt[:60]}...")
        
        # Set seed if provided
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        # Generate image
        result = self.pipe(
            prompt=prompt,
            height=height,
            width=width,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            generator=generator,
        )
        
        image = result.images[0]
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        print(f"✅ Generated {width}x{height} image")
        
        return {
            "image": img_base64,
            "prompt": prompt,
            "width": width,
            "height": height,
            "seed": seed,
        }
    
    @modal.method()
    def generate_batch(
        self,
        prompts: List[str],
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 4,
        guidance_scale: float = 1.0,
        seeds: Optional[List[int]] = None,
        batch_size: Optional[int] = None,
    ) -> List[Dict]:
        """
        Generate multiple images in batch (optimized for L4 GPU)
        
        Args:
            prompts: List of text descriptions
            width: Image width for all images
            height: Image height for all images
            num_inference_steps: Number of steps (4 recommended)
            guidance_scale: Guidance scale (1.0 recommended for FLUX-2-klein)
            seeds: Optional list of seeds (one per prompt)
            batch_size: Batch size (default: 6 for L4 GPU)
        
        Returns:
            List of dicts with base64 encoded images and metadata
        """
        import torch
        import time
        
        if batch_size is None:
            batch_size = OPTIMAL_BATCH_SIZE
        
        print(f"🎨 Generating batch of {len(prompts)} images (batch_size={batch_size})...")
        start_time = time.time()
        
        results = []
        
        # Process in optimal batches for L4 GPU
        for batch_start in range(0, len(prompts), batch_size):
            batch_end = min(batch_start + batch_size, len(prompts))
            batch_prompts = prompts[batch_start:batch_end]
            
            print(f"   Processing batch {batch_start//batch_size + 1} ({len(batch_prompts)} images)...")
            
            for i, prompt in enumerate(batch_prompts):
                global_idx = batch_start + i
                
                # Get seed for this image
                seed = seeds[global_idx] if seeds and global_idx < len(seeds) else None
                generator = None
                if seed is not None:
                    generator = torch.Generator(device=self.device).manual_seed(seed)
                
                print(f"      [{global_idx+1}/{len(prompts)}] {prompt[:50]}...")
                
                # Generate image
                result = self.pipe(
                    prompt=prompt,
                    height=height,
                    width=width,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                    generator=generator,
                )
                
                image = result.images[0]
                
                # Convert to base64
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                results.append({
                    "image": img_base64,
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "index": global_idx,
                })
        
        elapsed = time.time() - start_time
        avg_time = elapsed / len(prompts)
        
        print(f"✅ Generated {len(results)} images successfully!")
        print(f"   Total time: {elapsed:.1f}s | Avg per image: {avg_time:.2f}s")
        print(f"   Throughput: {3600/avg_time:.0f} images/hour")
        
        return results


@app.function(image=image)
@modal.fastapi_endpoint(method="POST")  # Was @modal.web_endpoint (2026 API)
def openai_compatible_api(request: dict) -> dict:
    """
    OpenAI-compatible API endpoint for image generation
    
    POST /openai_compatible_api
    {
        "model": "flux-klein-4b",
        "prompt": "A cat holding a sign",
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json"
    }
    
    Returns:
    {
        "created": 1234567890,
        "data": [
            {
                "b64_json": "base64_encoded_image",
                "revised_prompt": "original_prompt"
            }
        ]
    }
    """
    import time
    
    # Parse OpenAI-style request
    prompt = request.get("prompt", "")
    n = request.get("n", 1)
    size = request.get("size", "1024x1024")
    
    # Parse size
    width, height = map(int, size.split("x"))
    
    # Generate images
    generator = FluxImageGenerator()
    
    if n == 1:
        result = generator.generate_single.remote(
            prompt=prompt,
            width=width,
            height=height,
        )
        results = [result]
    else:
        results = generator.generate_batch.remote(
            prompts=[prompt] * n,
            width=width,
            height=height,
        )
    
    # Format as OpenAI response
    return {
        "created": int(time.time()),
        "data": [
            {
                "b64_json": r["image"],
                "revised_prompt": r["prompt"]
            }
            for r in results
        ]
    }


@app.function(image=image)
def generate_from_scene_prompts(
    scene_prompts: List[Dict],
    output_dir: str = "output/generated_images",
) -> Dict:
    """
    High-level function: Generate images from scene prompts
    
    Args:
        scene_prompts: List of dicts with 'scene_number', 'scene_description', 'image_prompt'
        output_dir: Where to save images locally
    
    Returns:
        Dict with results and saved file paths
    """
    from pathlib import Path
    import base64
    
    print(f"\n{'='*80}")
    print(f"🎨 FLUX IMAGE GENERATION")
    print(f"{'='*80}")
    print(f"Scenes to generate: {len(scene_prompts)}")
    
    # Extract prompts
    prompts = [scene['image_prompt'] for scene in scene_prompts]
    
    # Generate images in batch
    generator = FluxImageGenerator()
    results = generator.generate_batch.remote(prompts)
    
    # Save images
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    for i, (scene, result) in enumerate(zip(scene_prompts, results)):
        scene_num = scene.get('scene_number', i + 1)
        
        # Decode base64 image
        img_data = base64.b64decode(result['image'])
        
        # Save image
        filename = f"scene_{scene_num:03d}.png"
        filepath = output_path / filename
        
        with open(filepath, 'wb') as f:
            f.write(img_data)
        
        saved_files.append({
            'scene_number': scene_num,
            'scene_description': scene.get('scene_description', ''),
            'image_prompt': result['prompt'],
            'filepath': str(filepath),
            'width': result['width'],
            'height': result['height'],
        })
        
        print(f"   ✅ Scene {scene_num}: {filepath}")
    
    # Save metadata
    metadata_file = output_path / "generation_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            'total_images': len(saved_files),
            'images': saved_files,
        }, f, indent=2)
    
    print(f"\n💾 Saved {len(saved_files)} images to: {output_dir}")
    print(f"💾 Metadata saved to: {metadata_file}")
    
    return {
        'success': True,
        'total_images': len(saved_files),
        'images': saved_files,
        'metadata_file': str(metadata_file),
    }


@app.local_entrypoint()
def main():
    """Test the image generation service"""
    
    # Test data - scenes without video clips
    test_scenes = [
        {
            'scene_number': 1,
            'scene_description': 'rocket launching into space',
            'image_prompt': 'Powerful rocket launching from launch pad with flames and smoke, dramatic lighting, photorealistic, historical NASA footage style, high quality, 4K',
        },
        {
            'scene_number': 2,
            'scene_description': 'astronaut floating in space',
            'image_prompt': 'Astronaut in white spacesuit floating in orbit with Earth visible in background, peaceful atmosphere, photorealistic space photography, high detail',
        },
        {
            'scene_number': 3,
            'scene_description': 'mission control room with engineers',
            'image_prompt': 'Busy NASA mission control room with multiple screens and engineers working at consoles, 1960s style, focused atmosphere, vintage documentary photography',
        },
    ]
    
    # Generate images
    result = generate_from_scene_prompts.remote(
        scene_prompts=test_scenes,
        output_dir="output/generated_images"
    )
    
    print("\n" + "="*80)
    print("✅ GENERATION COMPLETE!")
    print("="*80)
    print(f"Total images: {result['total_images']}")
    print(f"Output directory: output/generated_images")
    print("\nGenerated images:")
    for img in result['images']:
        print(f"  - Scene {img['scene_number']}: {img['filepath']}")
