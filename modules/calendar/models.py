"""
Data models for Google Calendar integration.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class CalendarEvent(BaseModel):
    """Represents a calendar event."""
    id: str
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: str = ""
    calendar_id: str = "primary"
    calendar_name: str = "Calendar"
    is_all_day: bool = False
    attendees: List[str] = []
    organizer: Optional[str] = None
    status: str = "confirmed"
    
    @property
    def duration_hours(self) -> float:
        """Get event duration in hours."""
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600
    
    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming (not started yet)."""
        return self.start_time > datetime.now()
    
    @property
    def is_ongoing(self) -> bool:
        """Check if event is currently ongoing."""
        now = datetime.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_past(self) -> bool:
        """Check if event has ended."""
        return self.end_time < datetime.now()
    
    @property
    def event_type(self) -> str:
        """Categorize event type."""
        if self.is_all_day:
            return "all_day"
        elif self.duration_hours >= 24:
            return "multi_day"
        elif self.duration_hours >= 4:
            return "long_event"
        else:
            return "event"
    
    def formatted_time(self) -> str:
        """Get formatted time string."""
        if self.is_all_day:
            return "All day"
        
        time_format = "%I:%M %p"  # 12-hour format
        start = self.start_time.strftime(time_format).lstrip('0')
        end = self.end_time.strftime(time_format).lstrip('0')
        
        if self.start_time.date() == self.end_time.date():
            return f"{start} - {end}"
        else:
            return f"{start}"


class CalendarSummary(BaseModel):
    """Summary of calendar events for dashboard display."""
    today_events: List[CalendarEvent] = []
    upcoming_events: List[CalendarEvent] = []
    next_event: Optional[CalendarEvent] = None
    total_events: int = 0
    last_updated: datetime
    
    @property
    def has_events_today(self) -> bool:
        return len(self.today_events) > 0
    
    @property
    def busy_today(self) -> bool:
        """Check if today is busy (3+ events)."""
        return len(self.today_events) >= 3


class CalendarStatus(BaseModel):
    """Status of the calendar service."""
    authenticated: bool = False
    calendars_count: int = 0
    last_sync: Optional[datetime] = None
    next_sync: Optional[datetime] = None
    error_message: Optional[str] = None
    api_calls_today: int = 0
    quota_remaining: int = 1000


class CalendarConfig(BaseModel):
    """Configuration for Google Calendar service."""
    credentials_file: str = "credentials.json"
    token_file: str = "token.json"
    scopes: List[str] = ["https://www.googleapis.com/auth/calendar.readonly"]
    calendar_ids: List[str] = ["primary"]
    max_events: int = 10
    days_ahead: int = 7
    timezone: str = "America/New_York"