import asyncio
import uuid
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
from .models import TimerInfo, TimerStatus, TimerType, TimerPreset, PomodoroConfig

logger = logging.getLogger(__name__)

class TimerService:
    """Timer service for managing countdown timers, stopwatches, and pomodoro sessions."""
    
    def __init__(self):
        self.timers: Dict[str, TimerInfo] = {}
        self.presets: Dict[str, TimerPreset] = {}
        self.pomodoro_config = PomodoroConfig()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        
        # Load presets and configuration
        self._load_presets()
        self._create_default_presets()
        
        # Start background task for timer updates
        asyncio.create_task(self._timer_update_loop())
    
    def get_all_timers(self) -> List[TimerInfo]:
        """Get all timers."""
        return list(self.timers.values())
    
    def get_timer(self, timer_id: str) -> Optional[TimerInfo]:
        """Get specific timer by ID."""
        return self.timers.get(timer_id)
    
    def create_timer(self, name: str, duration_seconds: int, 
                    timer_type: TimerType = TimerType.COUNTDOWN,
                    auto_start: bool = False, **kwargs) -> TimerInfo:
        """Create a new timer."""
        timer_id = str(uuid.uuid4())
        
        timer = TimerInfo(
            id=timer_id,
            name=name,
            timer_type=timer_type,
            duration_seconds=duration_seconds,
            remaining_seconds=duration_seconds if timer_type == TimerType.COUNTDOWN else 0,
            elapsed_seconds=0,
            status=TimerStatus.CREATED,
            created_at=datetime.now(),
            **kwargs
        )
        
        self.timers[timer_id] = timer
        
        if auto_start:
            self.start_timer(timer_id)
        
        logger.info(f"Created timer: {name} ({duration_seconds}s)")
        return timer
    
    def start_timer(self, timer_id: str) -> None:
        """Start a timer."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        timer = self.timers[timer_id]
        
        if timer.status == TimerStatus.RUNNING:
            return  # Already running
        
        timer.status = TimerStatus.RUNNING
        timer.started_at = datetime.now()
        
        # Start background task for this timer
        if timer_id in self.running_tasks:
            self.running_tasks[timer_id].cancel()
        
        self.running_tasks[timer_id] = asyncio.create_task(
            self._run_timer(timer_id)
        )
        
        logger.info(f"Started timer: {timer.name}")
    
    def pause_timer(self, timer_id: str) -> None:
        """Pause a timer."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        timer = self.timers[timer_id]
        
        if timer.status != TimerStatus.RUNNING:
            return  # Not running
        
        timer.status = TimerStatus.PAUSED
        timer.paused_at = datetime.now()
        
        # Cancel background task
        if timer_id in self.running_tasks:
            self.running_tasks[timer_id].cancel()
            del self.running_tasks[timer_id]
        
        logger.info(f"Paused timer: {timer.name}")
    
    def resume_timer(self, timer_id: str) -> None:
        """Resume a paused timer."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        timer = self.timers[timer_id]
        
        if timer.status != TimerStatus.PAUSED:
            return  # Not paused
        
        self.start_timer(timer_id)  # Reuse start logic
    
    def stop_timer(self, timer_id: str) -> None:
        """Stop and reset a timer."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        timer = self.timers[timer_id]
        timer.status = TimerStatus.STOPPED
        
        # Reset timer state
        if timer.timer_type == TimerType.COUNTDOWN:
            timer.remaining_seconds = timer.duration_seconds
            timer.elapsed_seconds = 0
        else:  # STOPWATCH
            timer.elapsed_seconds = 0
            timer.remaining_seconds = 0
        
        # Cancel background task
        if timer_id in self.running_tasks:
            self.running_tasks[timer_id].cancel()
            del self.running_tasks[timer_id]
        
        logger.info(f"Stopped timer: {timer.name}")
    
    def delete_timer(self, timer_id: str) -> None:
        """Delete a timer."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        # Stop timer first
        self.stop_timer(timer_id)
        
        # Remove from timers
        timer_name = self.timers[timer_id].name
        del self.timers[timer_id]
        
        logger.info(f"Deleted timer: {timer_name}")
    
    def update_timer(self, timer_id: str, updates: Dict[str, Any]) -> TimerInfo:
        """Update timer settings."""
        if timer_id not in self.timers:
            raise ValueError(f"Timer {timer_id} not found")
        
        timer = self.timers[timer_id]
        
        for key, value in updates.items():
            if hasattr(timer, key):
                setattr(timer, key, value)
        
        logger.info(f"Updated timer: {timer.name}")
        return timer
    
    async def _run_timer(self, timer_id: str):
        """Background task to run a timer."""
        try:
            timer = self.timers[timer_id]
            
            while timer.status == TimerStatus.RUNNING:
                await asyncio.sleep(1)  # Update every second
                
                if timer.timer_type == TimerType.COUNTDOWN:
                    timer.remaining_seconds -= 1
                    timer.elapsed_seconds += 1
                    
                    if timer.remaining_seconds <= 0:
                        timer.remaining_seconds = 0
                        timer.status = TimerStatus.COMPLETED
                        timer.completed_at = datetime.now()
                        
                        # Handle completion
                        await self._handle_timer_completion(timer_id)
                        break
                
                elif timer.timer_type == TimerType.STOPWATCH:
                    timer.elapsed_seconds += 1
                    timer.remaining_seconds = timer.elapsed_seconds
                
                elif timer.timer_type == TimerType.POMODORO:
                    # Pomodoro logic would go here
                    timer.remaining_seconds -= 1
                    timer.elapsed_seconds += 1
                    
                    if timer.remaining_seconds <= 0:
                        timer.status = TimerStatus.COMPLETED
                        timer.completed_at = datetime.now()
                        await self._handle_pomodoro_completion(timer_id)
                        break
        
        except asyncio.CancelledError:
            logger.debug(f"Timer task cancelled for {timer_id}")
        except Exception as e:
            logger.error(f"Error in timer task {timer_id}: {e}")
    
    async def _handle_timer_completion(self, timer_id: str):
        """Handle timer completion."""
        timer = self.timers[timer_id]
        
        logger.info(f"Timer completed: {timer.name}")
        
        # Play notification sound (if enabled)
        if timer.sound_enabled:
            await self._play_notification_sound()
        
        # Show notification
        message = timer.notification_message or f"Timer '{timer.name}' completed!"
        await self._show_notification(timer_id, message)
        
        # Auto-restart if enabled
        if timer.auto_restart:
            await asyncio.sleep(2)  # Brief pause
            timer.remaining_seconds = timer.duration_seconds
            timer.elapsed_seconds = 0
            timer.status = TimerStatus.CREATED
            self.start_timer(timer_id)
    
    async def _handle_pomodoro_completion(self, timer_id: str):
        """Handle pomodoro session completion."""
        # Pomodoro-specific completion logic
        await self._handle_timer_completion(timer_id)
    
    async def _play_notification_sound(self):
        """Play notification sound."""
        try:
            # Simple beep using system command
            import subprocess
            subprocess.run(["aplay", "/usr/share/sounds/alsa/Front_Left.wav"], 
                         check=False, capture_output=True)
        except Exception as e:
            logger.debug(f"Could not play notification sound: {e}")
    
    async def _show_notification(self, timer_id: str, message: str):
        """Show timer notification."""
        # In a real implementation, this would send notifications to the frontend
        logger.info(f"NOTIFICATION: {message}")
    
    async def _timer_update_loop(self):
        """Background loop to periodically update timer states."""
        try:
            while True:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                # Clean up completed timers older than 1 hour
                current_time = datetime.now()
                to_remove = []
                
                for timer_id, timer in self.timers.items():
                    if (timer.status == TimerStatus.COMPLETED and 
                        timer.completed_at and 
                        current_time - timer.completed_at > timedelta(hours=1)):
                        to_remove.append(timer_id)
                
                for timer_id in to_remove:
                    self.delete_timer(timer_id)
                    
        except Exception as e:
            logger.error(f"Error in timer update loop: {e}")
    
    def get_presets(self) -> List[TimerPreset]:
        """Get all timer presets."""
        return list(self.presets.values())
    
    def create_preset(self, preset: TimerPreset) -> TimerPreset:
        """Create a new timer preset."""
        if not preset.id:
            preset.id = str(uuid.uuid4())
        
        self.presets[preset.id] = preset
        self._save_presets()
        
        logger.info(f"Created preset: {preset.name}")
        return preset
    
    def delete_preset(self, preset_id: str) -> None:
        """Delete a timer preset."""
        if preset_id not in self.presets:
            raise ValueError(f"Preset {preset_id} not found")
        
        preset_name = self.presets[preset_id].name
        del self.presets[preset_id]
        self._save_presets()
        
        logger.info(f"Deleted preset: {preset_name}")
    
    def start_from_preset(self, preset_id: str) -> TimerInfo:
        """Start a timer from a preset."""
        if preset_id not in self.presets:
            raise ValueError(f"Preset {preset_id} not found")
        
        preset = self.presets[preset_id]
        
        timer = self.create_timer(
            name=preset.name,
            duration_seconds=preset.duration_seconds,
            timer_type=preset.timer_type,
            description=preset.description,
            sound_enabled=preset.sound_enabled,
            auto_restart=preset.auto_restart,
            notification_message=preset.notification_message,
            auto_start=True
        )
        
        return timer
    
    def _create_default_presets(self):
        """Create default timer presets."""
        if self.presets:
            return  # Already have presets
        
        default_presets = [
            TimerPreset(
                id="pomodoro-work",
                name="Pomodoro Work",
                duration_seconds=1500,  # 25 minutes
                timer_type=TimerType.POMODORO,
                description="25-minute focused work session",
                icon="🍅",
                color="#e74c3c"
            ),
            TimerPreset(
                id="pomodoro-break",
                name="Short Break",
                duration_seconds=300,  # 5 minutes
                timer_type=TimerType.COUNTDOWN,
                description="5-minute break",
                icon="☕",
                color="#3498db"
            ),
            TimerPreset(
                id="cooking-timer",
                name="Cooking",
                duration_seconds=600,  # 10 minutes
                timer_type=TimerType.COUNTDOWN,
                description="Kitchen timer",
                icon="👨‍🍳",
                color="#f39c12"
            ),
            TimerPreset(
                id="exercise",
                name="Exercise",
                duration_seconds=1800,  # 30 minutes
                timer_type=TimerType.COUNTDOWN,
                description="Workout session",
                icon="💪",
                color="#27ae60"
            ),
            TimerPreset(
                id="meditation",
                name="Meditation",
                duration_seconds=600,  # 10 minutes
                timer_type=TimerType.COUNTDOWN,
                description="Mindfulness session",
                icon="🧘",
                color="#9b59b6"
            )
        ]
        
        for preset in default_presets:
            self.presets[preset.id] = preset
        
        self._save_presets()
        logger.info("Created default timer presets")
    
    def _load_presets(self):
        """Load timer presets from file."""
        presets_file = os.path.join(os.path.dirname(__file__), "presets.json")
        try:
            if os.path.exists(presets_file):
                with open(presets_file, 'r') as f:
                    data = json.load(f)
                    for preset_id, preset_data in data.items():
                        self.presets[preset_id] = TimerPreset(**preset_data)
                logger.info(f"Loaded {len(self.presets)} timer presets")
        except Exception as e:
            logger.warning(f"Failed to load timer presets: {e}")
    
    def _save_presets(self):
        """Save timer presets to file."""
        presets_file = os.path.join(os.path.dirname(__file__), "presets.json")
        try:
            data = {preset_id: preset.dict() for preset_id, preset in self.presets.items()}
            with open(presets_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save timer presets: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get timer service status."""
        running_timers = [t for t in self.timers.values() if t.status == TimerStatus.RUNNING]
        paused_timers = [t for t in self.timers.values() if t.status == TimerStatus.PAUSED]
        completed_timers = [t for t in self.timers.values() if t.status == TimerStatus.COMPLETED]
        
        return {
            "total_timers": len(self.timers),
            "running_timers": len(running_timers),
            "paused_timers": len(paused_timers),
            "completed_timers": len(completed_timers),
            "available_presets": len(self.presets),
            "active_tasks": len(self.running_tasks),
            "service_status": "active"
        }
    
    def cleanup(self):
        """Cleanup timer service."""
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        self.running_tasks.clear()
        logger.info("Timer service cleaned up")