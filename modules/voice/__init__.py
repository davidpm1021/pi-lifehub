"""Voice recognition module for Pi Life Hub"""
from .api import router as voice_router
from .service import voice_service

__all__ = ["voice_router", "voice_service"]