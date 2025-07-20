"""Voice module API endpoints"""
from fastapi import APIRouter, HTTPException
import logging

from .service import voice_service
from .models import VoiceResponse, MicrophoneStatus

logger = logging.getLogger("pi_life_hub.voice.api")

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.get("/status", response_model=MicrophoneStatus)
async def get_voice_status():
    """Get voice recognition status"""
    try:
        return voice_service.get_microphone_status()
    except Exception as e:
        logger.error(f"Failed to get voice status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get voice status")

@router.post("/listen", response_model=VoiceResponse)
async def listen_for_command():
    """Listen for a single voice command"""
    try:
        response = voice_service.listen_for_command()
        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice command failed: {e}")
        raise HTTPException(status_code=500, detail="Voice command failed")

@router.post("/start")
async def start_continuous_listening():
    """Start continuous voice listening"""
    try:
        # Define callback for handling voice commands
        def handle_command(response: VoiceResponse):
            logger.info(f"Voice command received: {response.action}")
            # Commands will be processed by frontend via WebSocket
            
        voice_service.start_continuous_listening(handle_command)
        return {"status": "listening", "message": "Voice recognition started"}
    except Exception as e:
        logger.error(f"Failed to start listening: {e}")
        raise HTTPException(status_code=500, detail="Failed to start voice recognition")

@router.post("/stop")
async def stop_continuous_listening():
    """Stop continuous voice listening"""
    try:
        voice_service.stop_listening()
        return {"status": "stopped", "message": "Voice recognition stopped"}
    except Exception as e:
        logger.error(f"Failed to stop listening: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop voice recognition")