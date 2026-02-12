"""
FLUX Image Generator Integration
Supports both Modal and Cloudflare Workers AI
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Literal
import subprocess
import sys
import os
import base64
import requests


class FluxImageGenerator:
    """Generate images using FLUX-2-klein-4B on Modal or Cloudflare Workers AI"""
    
    def __init__(self, provider: Literal["modal", "cloudflare"] = "cloudflare"):
        """
        Initialize the generator
        
        Args:
            provider: "modal" or "cloudflare" (default: cloudflare for free tier)
        """
        self.provider = provider
        
        if provider == "modal":
            self.check_modal_installed()
        elif provider == "cloudflare":
            self.check_cloudflare_credentials()
    
    def check_modal_installed(self):
        """Check if Modal is installed"""
        try:
            import modal
            print("✅ Modal SDK found")
        except ImportError:
            print("⚠️  Modal SDK not found. Install with: pip install modal")
            print("   Then authenticate with: modal token new")
    
    def check_cloudflare_credentials(self):
        """Check if Cloudflare credentials are set"""
        self.cf_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.cf_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
        
        if not self.cf_account_id or not self.cf_api_token:
            print("⚠️  Cloudflare credentials not found!")
            print("   Set environment variables:")
            print("   - CLOUDFLARE_ACCOUNT_ID")
            print("   - CLOUDFLARE_API_TOKEN")
            print("\n   Get them from: https://dash.cloudflare.com/")
            print("   Workers AI page -> Use REST API")
        else:
            print("✅ Cloudflare credentials found")
    
    def generate_images_from_prompts(
        self,
        prompts: List[Dict],
        output_dir: str = "output/generated_images",
        width: int = 1024,
        height: int = 1024,
    ) -> List[Dict]:
        """
        Generate images from prompt data
        
        Args:
            prompts: List of dicts with 'scene_number', 'scene_description', 'image_prompt'
            output_dir: Where to save generated images
            width: Image width
            height: Image height
        
        Returns:
            List of dicts with generated image info
        """
        print(f"\n🚀 Generating {len(prompts)} images with FLUX on {self.provider.upper()}...")
        
        if self.provider == "modal":
            return self._generate_with_modal(prompts, output_dir, width, height)
        elif self.provider == "cloudflare":
            return self._generate_with_cloudflare(prompts, output_dir, width, height)
    
    def _generate_with_modal(
        self,
        prompts: List[Dict],
        output_dir: str,
        width: int,
        height: int,
    ) -> List[Dict]:
        """Generate images using Modal"""
        try:
            # Use Modal lookup to call deployed function
            import modal
            
            # Lookup the deployed app
            app = modal.Lookup("flux-klein-image-generator", "main")
            generate_from_scene_prompts = app.function("generate_from_scene_prompts")
            
            # Call Modal function
            result = generate_from_scene_prompts.remote(
                scene_prompts=prompts,
                output_dir=output_dir,
            )
            
            if result['success']:
                print(f"✅ Successfully generated {result['total_images']} images")
                return result['images']
            else:
                print("❌ Image generation failed")
                return []
        
        except Exception as e:
            print(f"❌ Error generating images: {e}")
            print("\nMake sure:")
            print("  1. Modal is installed: pip install modal")
            print("  2. You're authenticated: modal token new")
            print("  3. Service is deployed: modal deploy modal_flux_service.py")
            return []
    
    def _generate_with_cloudflare(
        self,
        prompts: List[Dict],
        output_dir: str,
        width: int,
        height: int,
    ) -> List[Dict]:
        """Generate images using Cloudflare Workers AI"""
        if not self.cf_account_id or not self.cf_api_token:
            print("❌ Cloudflare credentials not set")
            return []
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_images = []
        
        # Cloudflare API endpoint - use flux-1-schnell (works with simple API)
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {
            "Authorization": f"Bearer {self.cf_api_token}",
        }
        
        for i, prompt_data in enumerate(prompts, 1):
            scene_num = prompt_data.get('scene_number', i)
            prompt = prompt_data.get('image_prompt', '')
            
            print(f"\n[{i}/{len(prompts)}] Scene {scene_num}: Generating...")
            
            try:
                # Call Cloudflare API with JSON payload
                payload = {
                    "prompt": prompt
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    from PIL import Image
                    import io
                    
                    # Cloudflare returns JSON with base64 image
                    result = response.json()
                    
                    if result.get('success') and result.get('result', {}).get('image'):
                        image_b64 = result['result']['image']
                        image_data = base64.b64decode(image_b64)
                        
                        # Open image and convert to JPG
                        try:
                            img = Image.open(io.BytesIO(image_data))
                            
                            # Convert to RGB if needed
                            if img.mode in ('RGBA', 'LA', 'P'):
                                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                                img = rgb_img
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Save as JPG
                            image_filename = f"scene_{scene_num:03d}.jpg"
                            image_path = output_path / image_filename
                            
                            img.save(image_path, 'JPEG', quality=95, optimize=True)
                        except Exception as e:
                            print(f"❌ Error converting image: {e}")
                            continue
                    else:
                        print(f"❌ No image in response")
                        continue
                    
                    generated_images.append({
                        'scene_number': scene_num,
                        'scene_description': prompt_data.get('scene_description', ''),
                        'image_prompt': prompt,
                        'image_path': str(image_path),
                        'provider': 'cloudflare',
                    })
                    
                    print(f"✅ Saved: {image_path}")
                else:
                    print(f"❌ API error {response.status_code}: {response.text}")
            
            except Exception as e:
                print(f"❌ Error generating scene {scene_num}: {e}")
                continue
        
        print(f"\n✅ Generated {len(generated_images)}/{len(prompts)} images")
        return generated_images
    
    def generate_batch(
        self,
        prompts: List[str],
        width: int = 1024,
        height: int = 1024,
    ) -> List[Dict]:
        """
        Generate images from simple prompt list
        
        Args:
            prompts: List of text prompts
            width: Image width
            height: Image height
        
        Returns:
            List of dicts with base64 encoded images
        """
        if self.provider == "modal":
            return self._generate_batch_modal(prompts, width, height)
        elif self.provider == "cloudflare":
            return self._generate_batch_cloudflare(prompts, width, height)
    
    def _generate_batch_modal(
        self,
        prompts: List[str],
        width: int,
        height: int,
    ) -> List[Dict]:
        """Generate batch with Modal"""
        try:
            import modal
            
            # Lookup the deployed app
            app = modal.Lookup("flux-klein-image-generator", "main")
            FluxImageGenerator = app.cls("FluxImageGenerator")
            
            generator = FluxImageGenerator()
            results = generator.generate_batch.remote(
                prompts=prompts,
                width=width,
                height=height,
            )
            
            return results
        
        except Exception as e:
            print(f"❌ Error in batch generation: {e}")
            return []
    
    def _generate_batch_cloudflare(
        self,
        prompts: List[str],
        width: int,
        height: int,
    ) -> List[Dict]:
        """Generate batch with Cloudflare"""
        if not self.cf_account_id or not self.cf_api_token:
            print("❌ Cloudflare credentials not set")
            return []
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"
        headers = {
            "Authorization": f"Bearer {self.cf_api_token}",
        }
        
        results = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"[{i}/{len(prompts)}] Generating...")
            
            try:
                payload = {
                    "prompt": prompt
                }
                
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    # Get raw image bytes and encode to base64
                    image_data = response.content
                    image_b64 = base64.b64encode(image_data).decode('utf-8')
                    
                    results.append({
                        'prompt': prompt,
                        'image_b64': image_b64,
                        'provider': 'cloudflare',
                    })
                    print(f"✅ Generated")
                else:
                    print(f"❌ API error {response.status_code}")
            
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
        
        return results


def integrate_with_image_fallback(
    scenes: List[Dict],
    extracted_clips: List[Dict],
    output_dir: str = "output/generated_images",
    provider: Literal["modal", "cloudflare"] = "cloudflare",
) -> Dict:
    """
    Complete workflow: Check missing scenes, generate prompts, create images
    
    Args:
        scenes: All scenes from production plan
        extracted_clips: Successfully extracted clips
        output_dir: Where to save generated images
        provider: "modal" or "cloudflare" (default: cloudflare)
    
    Returns:
        Dict with results
    """
    from src.tools.image_fallback import ImageFallbackGenerator
    
    print("\n" + "="*80)
    print("🎨 IMAGE FALLBACK WITH FLUX GENERATION")
    print("="*80)
    
    # Step 1: Generate prompts for missing scenes
    fallback_gen = ImageFallbackGenerator()
    prompts = fallback_gen.generate_prompts_for_missing_scenes(
        scenes=scenes,
        extracted_clips=extracted_clips,
    )
    
    if not prompts:
        print("\n✅ No missing scenes - all have video clips!")
        return {
            'success': True,
            'missing_scenes': 0,
            'generated_images': 0,
        }
    
    # Step 2: Generate images with FLUX
    flux_gen = FluxImageGenerator(provider=provider)
    generated_images = flux_gen.generate_images_from_prompts(
        prompts=prompts,
        output_dir=output_dir,
    )
    
    # Step 3: Save combined results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results_file = output_path / "fallback_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'missing_scenes': len(prompts),
            'generated_images': len(generated_images),
            'prompts': prompts,
            'images': generated_images,
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    print("\n" + "="*80)
    print("✅ COMPLETE!")
    print("="*80)
    print(f"Missing scenes: {len(prompts)}")
    print(f"Generated images: {len(generated_images)}")
    
    return {
        'success': True,
        'missing_scenes': len(prompts),
        'generated_images': len(generated_images),
        'images': generated_images,
        'results_file': str(results_file),
    }


def main():
    """Test the integration"""
    
    # Example: Some scenes with clips, some without
    scenes = [
        {
            'scene_number': 1,
            'scene_description': 'rocket launching into space',
            'keywords': ['rocket', 'launch', 'space', 'NASA'],
            'visual_context': 'powerful rocket lifting off from launch pad',
            'mood_tone': 'dramatic, powerful'
        },
        {
            'scene_number': 2,
            'scene_description': 'astronaut floating in space',
            'keywords': ['astronaut', 'spacewalk', 'orbit', 'Earth'],
            'visual_context': 'astronaut in white spacesuit floating with Earth in background',
            'mood_tone': 'peaceful, awe-inspiring'
        },
        {
            'scene_number': 3,
            'scene_description': 'mission control room with engineers',
            'keywords': ['mission control', 'engineers', 'computers', 'NASA'],
            'visual_context': 'busy control room with multiple screens and people working',
            'mood_tone': 'focused, intense'
        }
    ]
    
    # Simulate: Only scene 1 has clips
    extracted_clips = [
        {
            'scene': 'rocket launching into space',
            'path': 'output/clip1.mp4'
        }
    ]
    
    # Run complete workflow
    result = integrate_with_image_fallback(
        scenes=scenes,
        extracted_clips=extracted_clips,
        output_dir="output/generated_images",
    )
    
    print(f"\n✅ Generated {result['generated_images']} images for {result['missing_scenes']} missing scenes")


if __name__ == "__main__":
    main()
