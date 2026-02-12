"""Test deployed FLUX endpoint"""
import modal
import base64
from pathlib import Path

print("🚀 Testing FLUX endpoint...")

# Lookup deployed class
FluxImageGenerator = modal.Cls.from_name("flux-klein-image-generator", "FluxImageGenerator")

prompts = [
    "Rocket launching, dramatic flames, photorealistic",
    "Astronaut in space, peaceful, high detail",
]

generator = FluxImageGenerator()
results = generator.generate_batch.remote(prompts=prompts, width=1024, height=1024)

# Save images
output_dir = Path("output/test_images")
output_dir.mkdir(parents=True, exist_ok=True)

for i, result in enumerate(results):
    img_data = base64.b64decode(result['image'])
    filepath = output_dir / f"test_{i+1}.png"
    with open(filepath, 'wb') as f:
        f.write(img_data)
    print(f"✅ Saved: {filepath}")

print(f"\n🎉 Generated {len(results)} images!")
