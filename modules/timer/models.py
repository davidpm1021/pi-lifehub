from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TimerStatus(str, Enum):
    """Timer status enumeration."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"

class TimerType(str, Enum):
    """Timer type enumeration."""
    COUNTDOWN = "countdown"
    STOPWATCH = "stopwatch"
    POMODORO = "pomodoro"

class TimerInfo(BaseModel):
    """Timer information model."""
    id: str
    name: str
    timer_type: TimerType = TimerType.COUNTDOWN
    duration_seconds: int  # Original duration
    remaining_seconds: int  # Current remaining time
    elapsed_seconds: int = 0  # Time elapsed
    status: TimerStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    description: Optional[str] = None
    sound_enabled: bool = True
    auto_restart: bool = False
    notification_message: Optional[str] = None

class TimerCreateRequest(BaseModel):
    """Request model for creating a timer."""
    name: str
    duration_seconds: int
    timer_type: TimerType = TimerType.COUNTDOWN
    description: Optional[str] = None
    sound_enabled: bool = True
    auto_restart: bool = False
    auto_start: bool = False
    notification_message: Optional[str] = None

class TimerUpdateRequest(BaseModel):
    """Request model for updating a timer."""
    name: Optional[str] = None
    duration_seconds: Optional[int] = None
    description: Optional[str] = None
    sound_enabled: Optional[bool] = None
    auto_restart: Optional[bool] = None
    notification_message: Optional[str] = None

class TimerPreset(BaseModel):
    """Timer preset model."""
    id: str
    name: str
    duration_seconds: int
    timer_type: TimerType = TimerType.COUNTDOWN
    description: Optional[str] = None
    sound_enabled: bool = True
    auto_restart: bool = False
    notification_message: Optional[str] = None
    icon: Optional[str] = None  # Icon name or emoji
    color: str = "#007bff"  # Color for UI display

class PomodoroConfig(BaseModel):
    """Pomodoro timer configuration."""
    work_duration: int = 1500  # 25 minutes
    short_break_duration: int = 300  # 5 minutes
    long_break_duration: int = 900  # 15 minutes
    sessions_until_long_break: int = 4
    auto_start_breaks: bool = True
    auto_start_work: bool = False

class TimerNotification(BaseModel):
    """Timer notification model."""
    timer_id: str
    timer_name: str
    event_type: str  # started, paused, completed, etc.
    message: str
    timestamp: datetime
    acknowledged: bool = False

class TimerStatistics(BaseModel):
    """Timer usage statistics."""
    total_timers_created: int
    total_time_tracked: int  # seconds
    completed_timers: int
    average_duration: float  # seconds
    most_used_preset: Optional[str] = None
    daily_usage: Dict[str, int] = {}  # date -> seconds
    weekly_usage: Dict[str, int] = {}  # week -> seconds