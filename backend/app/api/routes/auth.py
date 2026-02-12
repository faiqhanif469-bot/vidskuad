"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.dependencies import verify_firebase_token, get_current_user

router = APIRouter()


class TokenVerifyRequest(BaseModel):
    """Token verification request"""
    token: str


@router.post("/verify")
async def verify_token(request: TokenVerifyRequest):
    """
    Verify Firebase token
    
    Frontend sends Firebase token, backend verifies it
    """
    try:
        from firebase_admin import auth
        
        decoded_token = auth.verify_id_token(request.token)
        
        return {
            'success': True,
            'user_id': decoded_token['uid'],
            'email': decoded_token.get('email')
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get current user info
    """
    return {
        'user_id': user['user_id'],
        'email': user['email'],
        'subscription_tier': user.get('subscription_tier', 'free'),
        'videos_created_this_month': user.get('videos_created_this_month', 0),
        'created_at': user.get('created_at')
    }
