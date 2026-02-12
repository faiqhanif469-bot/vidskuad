import requests
import base64
import os

# You need to provide your account ID
# Get it from: https://dash.cloudflare.com/ -> Workers & Pages -> Overview
ACCOUNT_ID = input("Enter your Cloudflare Account ID: ").strip()
API_TOKEN = "0noJgQOb4HgPp3a7W8NU_-DS2CUvEE0_dm5A3Z0j"

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "prompt": "A beautiful sunset over mountains, photorealistic, 4k quality"
}

print("🎨 Generating image with Cloudflare FLUX...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    # Save the image
    image_data = response.content
    output_path = "test_cloudflare_output.png"
    
    with open(output_path, "wb") as f:
        f.write(image_data)
    
    print(f"✅ Image generated successfully!")
    print(f"📁 Saved to: {output_path}")
else:
    print(f"❌ Error: {response.status_code}")
  