from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
from .service import TimerService
from .models import TimerInfo, TimerCreateRequest, TimerUpdateRequest, TimerPreset

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/timer", tags=["timer"])

# Initialize timer service
timer_service = TimerService()

@router.get("/list")
async def list_timers() -> List[TimerInfo]:
    """Get all active timers."""
    try:
        timers = timer_service.get_all_timers()
        return timers
    except Exception as e:
        logger.error(f"Failed to list timers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timers")

@router.get("/{timer_id}")
async def get_timer(timer_id: str) -> TimerInfo:
    """Get specific timer by ID."""
    try:
        timer = timer_service.get_timer(timer_id)
        if not timer:
            raise HTTPException(status_code=404, detail="Timer not found")
        return timer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timer")

@router.post("/create")
async def create_timer(request: TimerCreateRequest) -> TimerInfo:
    """Create a new timer."""
    try:
        timer = timer_service.create_timer(
            name=request.name,
            duration_seconds=request.duration_seconds,
            auto_start=request.auto_start
        )
        return timer
    except Exception as e:
        logger.error(f"Failed to create timer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create timer")

@router.post("/{timer_id}/start")
async def start_timer(timer_id: str) -> Dict[str, str]:
    """Start a timer."""
    try:
        timer_service.start_timer(timer_id)
        return {"status": "started", "timer_id": timer_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start timer")

@router.post("/{timer_id}/pause")
async def pause_timer(timer_id: str) -> Dict[str, str]:
    """Pause a timer."""
    try:
        timer_service.pause_timer(timer_id)
        return {"status": "paused", "timer_id": timer_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to pause timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause timer")

@router.post("/{timer_id}/resume")
async def resume_timer(timer_id: str) -> Dict[str, str]:
    """Resume a paused timer."""
    try:
        timer_service.resume_timer(timer_id)
        return {"status": "resumed", "timer_id": timer_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to resume timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume timer")

@router.post("/{timer_id}/stop")
async def stop_timer(timer_id: str) -> Dict[str, str]:
    """Stop and reset a timer."""
    try:
        timer_service.stop_timer(timer_id)
        return {"status": "stopped", "timer_id": timer_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to stop timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop timer")

@router.delete("/{timer_id}")
async def delete_timer(timer_id: str) -> Dict[str, str]:
    """Delete a timer."""
    try:
        timer_service.delete_timer(timer_id)
        return {"status": "deleted", "timer_id": timer_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete timer")

@router.put("/{timer_id}")
async def update_timer(timer_id: str, request: TimerUpdateRequest) -> TimerInfo:
    """Update timer settings."""
    try:
        timer = timer_service.update_timer(timer_id, request.dict(exclude_unset=True))
        return timer
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update timer {timer_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update timer")

@router.get("/presets/list")
async def list_presets() -> List[TimerPreset]:
    """Get all timer presets."""
    try:
        presets = timer_service.get_presets()
        return presets
    except Exception as e:
        logger.error(f"Failed to list presets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get presets")

@router.post("/presets/create")
async def create_preset(preset: TimerPreset) -> TimerPreset:
    """Create a new timer preset."""
    try:
        created_preset = timer_service.create_preset(preset)
        return created_preset
    except Exception as e:
        logger.error(f"Failed to create preset: {e}")
        raise HTTPException(status_code=500, detail="Failed to create preset")

@router.post("/presets/{preset_id}/start")
async def start_preset_timer(preset_id: str) -> TimerInfo:
    """Start a timer from a preset."""
    try:
        timer = timer_service.start_from_preset(preset_id)
        return timer
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start preset timer {preset_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to start preset timer")

@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: str) -> Dict[str, str]:
    """Delete a timer preset."""
    try:
        timer_service.delete_preset(preset_id)
        return {"status": "deleted", "preset_id": preset_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete preset {preset_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete preset")

@router.get("/status")
async def get_timer_status() -> Dict[str, Any]:
    """Get timer service status."""
    try:
        status = timer_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get timer status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get timer status")