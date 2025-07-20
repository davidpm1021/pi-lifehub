"""Voice module data models"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class VoiceCommand(BaseModel):
    """Voice command model"""
    raw_text: str
    command: Optional[str] = None
    confidence: float = 0.0
    timestamp: datetime = datetime.now()
    
class VoiceResponse(BaseModel):
    """Voice command response"""
    success: bool
    command: Optional[str] = None
    action: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None
    
class MicrophoneStatus(BaseModel):
    """Microphone device status"""
    connected: bool
    device_name: Optional[str] = None
    device_index: Optional[int] = None
    sample_rate: int
    error: Optional[str] = None