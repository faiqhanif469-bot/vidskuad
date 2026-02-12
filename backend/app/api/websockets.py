"""
WebSocket Routes for Real-time Progress Updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from firebase_admin import firestore
import asyncio
import json

from app.dependencies import db

router = APIRouter()


@router.websocket("/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates
    DISABLED: Requires Firebase/Firestore
    
    Use polling via GET /api/videos/status/{job_id} instead
    """
    await websocket.accept()
    await websocket.send_json({
        'error': 'WebSocket not available. Use polling via /api/videos/status/{job_id}'
    })
    await websocket.close()
