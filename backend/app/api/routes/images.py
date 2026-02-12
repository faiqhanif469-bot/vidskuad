"""
Image Generation Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import get_current_user

router = APIRouter()


class ImageGenerateRequest(BaseModel):
    """Single image generation request"""
    prompt: str
    provider: str = "cloudflare"


@router.post("/generate")
async def generate_single_image(
    request: ImageGenerateRequest,
    user: dict = Depends(get_current_user)
):
    """
    Generate a single image from prompt
    """
    try:
        from src.tools.flux_generator import FluxImageGenerator
        import uuid
        import os
        from app.services.storage_service import StorageService
        
        # Generate image
        generator = FluxImageGenerator(provider=request.provider)
        results = generator.generate_batch([request.prompt])
        
        if not results:
            raise HTTPException(status_code=500, detail="Image generation failed")
        
        # Save image
        image_id = str(uuid.uuid4())
        output_dir = f"temp/{user['user_id']}/images"
        os.makedirs(output_dir, exist_ok=True)
        
        image_path = f"{output_dir}/{image_id}.jpg"
        
        import base64
        from PIL import Image
        import io
        
        image_data = base64.b64decode(results[0]['image_b64'])
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img.save(image_path, 'JPEG', quality=95)
        
        # Upload to storage
        storage = StorageService()
        url = storage.upload_file(image_path, f"{user['user_id']}/images/{image_id}.jpg")
        
        # Clean up local file
        os.remove(image_path)
        
        return {
            'success': True,
            'image_id': image_id,
            'image_url': url,
            'prompt': request.prompt
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
