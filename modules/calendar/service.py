"""
Google Calendar service for Pi Life Hub.
Handles authentication and calendar data fetching.
"""

import os
import logging
import asyncio
import pytz
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import CalendarEvent, CalendarConfig, CalendarSummary, CalendarStatus
from .config import CalendarConfigManager

logger = logging.getLogger(__name__)


class CalendarService:
    """Google Calendar service for family dashboard."""
    
    def __init__(self):
        self.config_manager = CalendarConfigManager()
        self.config = self.config_manager.load_config()
        self.service = None
        self.last_sync: Optional[datetime] = None
        self.cached_events: List[CalendarEvent] = []
        self.api_calls_today = 0
        self.error_message: Optional[str] = None
        
        # Try to authenticate on initialization
        try:
            self._authenticate()
        except Exception as e:
            logger.warning(f"Failed to authenticate on initialization: {e}")
            self.error_message = str(e)
    
    def _authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        try:
            creds = None
            credentials_path = os.path.join(os.path.dirname(__file__), self.config.credentials_file)
            token_path = os.path.join(os.path.dirname(__file__), self.config.token_file)
            
            # Load existing token
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.config.scopes)
            
            # If there are no valid credentials, request authorization
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        logger.info("Refreshed Google Calendar credentials")
                    except Exception as e:
                        logger.warning(f"Failed to refresh credentials: {e}")
                        # Fall back to full auth flow
                        creds = None
                
                if not creds:
                    if not os.path.exists(credentials_path):
                        raise FileNotFoundError(f"Google credentials file not found: {credentials_path}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, self.config.scopes)
                    
                    # Try console-based auth for headless environments
                    try:
                        creds = flow.run_console()
                        logger.info("Completed Google Calendar console authentication flow")
                    except Exception as console_error:
                        logger.warning(f"Console auth failed: {console_error}")
                        # Fallback to local server (requires manual URL opening)
                        try:
                            creds = flow.run_local_server(port=8080, open_browser=False)
                            logger.info("Completed Google Calendar server authentication flow - manual URL opening required")
                        except Exception as server_error:
                            logger.error(f"Both console and server auth failed: {server_error}")
                            raise Exception("Authentication failed - please set up OAuth manually")
                
                # Save credentials for future use
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info("Saved Google Calendar token")
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=creds)
            self.error_message = None
            logger.info("Google Calendar service authenticated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Calendar: {e}")
            self.error_message = str(e)
            self.service = None
            return False
    
    async def get_events(self, days_ahead: Optional[int] = None) -> List[CalendarEvent]:
        """Get calendar events for the specified number of days ahead."""
        if not self.service:
            if not self._authenticate():
                return []
        
        days_ahead = days_ahead or self.config.days_ahead
        
        try:
            # Calculate time range
            now = datetime.now(timezone.utc)
            time_min = now.isoformat()
            time_max = (now + timedelta(days=days_ahead)).isoformat()
            
            events = []
            
            # Fetch events from each configured calendar
            for calendar_id in self.config.calendar_ids:
                try:
                    # Call the Calendar API
                    events_result = self.service.events().list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        maxResults=self.config.max_events,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    calendar_events = events_result.get('items', [])
                    self.api_calls_today += 1
                    
                    # Get calendar name
                    calendar_name = "Calendar"
                    try:
                        calendar_info = self.service.calendars().get(calendarId=calendar_id).execute()
                        calendar_name = calendar_info.get('summary', calendar_id)
                        self.api_calls_today += 1
                    except:
                        pass
                    
                    # Convert to CalendarEvent objects
                    for event in calendar_events:
                        try:
                            calendar_event = self._parse_event(event, calendar_id, calendar_name)
                            if calendar_event:
                                events.append(calendar_event)
                        except Exception as e:
                            logger.warning(f"Failed to parse event {event.get('id', 'unknown')}: {e}")
                            
                except HttpError as error:
                    logger.error(f"Failed to fetch events from calendar {calendar_id}: {error}")
                    if error.resp.status == 404:
                        logger.warning(f"Calendar {calendar_id} not found or not accessible")
                    continue
            
            # Sort all events by start time
            events.sort(key=lambda e: e.start_time)
            
            # Cache the events
            self.cached_events = events
            self.last_sync = datetime.now()
            
            logger.info(f"Fetched {len(events)} events from {len(self.config.calendar_ids)} calendars")
            return events
            
        except Exception as e:
            logger.error(f"Failed to get calendar events: {e}")
            self.error_message = str(e)
            return self.cached_events  # Return cached events if available
    
    def _parse_event(self, event: Dict[str, Any], calendar_id: str, calendar_name: str) -> Optional[CalendarEvent]:
        """Parse a Google Calendar API event into a CalendarEvent object."""
        try:
            # Extract start and end times
            start = event['start']
            end = event['end']
            
            # Handle all-day events
            is_all_day = 'date' in start
            
            if is_all_day:
                start_time = datetime.fromisoformat(start['date']).replace(hour=0, minute=0)
                end_time = datetime.fromisoformat(end['date']).replace(hour=23, minute=59)
            else:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
            
            # Convert to local timezone (Eastern Time)
            local_tz = pytz.timezone(self.config.timezone)
            start_time = start_time.astimezone(local_tz).replace(tzinfo=None)
            end_time = end_time.astimezone(local_tz).replace(tzinfo=None)
            
            # Extract attendees
            attendees = []
            if 'attendees' in event:
                attendees = [attendee.get('email', '') for attendee in event['attendees']]
            
            # Extract organizer
            organizer = None
            if 'organizer' in event:
                organizer = event['organizer'].get('email', event['organizer'].get('displayName', ''))
            
            return CalendarEvent(
                id=event['id'],
                title=event.get('summary', 'No Title'),
                description=event.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                location=event.get('location', ''),
                calendar_id=calendar_id,
                calendar_name=calendar_name,
                is_all_day=is_all_day,
                attendees=attendees,
                organizer=organizer,
                status=event.get('status', 'confirmed')
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse event: {e}")
            return None
    
    async def get_calendar_summary(self) -> CalendarSummary:
        """Get a summary of calendar events for dashboard display."""
        events = await self.get_events()
        
        today = datetime.now().date()
        today_events = [e for e in events if e.start_time.date() == today]
        upcoming_events = [e for e in events if e.start_time.date() > today][:5]  # Next 5 events
        
        # Find next event
        next_event = None
        for event in events:
            if event.is_upcoming:
                next_event = event
                break
        
        return CalendarSummary(
            today_events=today_events,
            upcoming_events=upcoming_events,
            next_event=next_event,
            total_events=len(events),
            last_updated=datetime.now()
        )
    
    async def get_status(self) -> CalendarStatus:
        """Get calendar service status."""
        return CalendarStatus(
            authenticated=self.service is not None,
            calendars_count=len(self.config.calendar_ids),
            last_sync=self.last_sync,
            next_sync=self.last_sync + timedelta(minutes=30) if self.last_sync else None,
            error_message=self.error_message,
            api_calls_today=self.api_calls_today,
            quota_remaining=1000 - self.api_calls_today  # Google Calendar free quota
        )
    
    def get_config(self) -> CalendarConfig:
        """Get current calendar configuration."""
        return self.config
    
    def update_config(self, new_config: CalendarConfig) -> None:
        """Update calendar configuration."""
        self.config = new_config
        self.config_manager.save_config(new_config)
        
        # Re-authenticate if needed
        self.service = None
        self._authenticate()
        
        logger.info("Calendar configuration updated")