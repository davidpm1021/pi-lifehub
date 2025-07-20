"""
API routes for Google Calendar integration.
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from .service import CalendarService
from .models import CalendarEvent, CalendarSummary, CalendarStatus, CalendarConfig

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/calendar", tags=["calendar"])

# Initialize calendar service
calendar_service = CalendarService()


@router.get("/events", response_model=List[CalendarEvent])
async def get_calendar_events(
    days_ahead: int = Query(default=7, ge=1, le=30, description="Number of days ahead to fetch events")
):
    """Get calendar events for the specified number of days ahead."""
    try:
        events = await calendar_service.get_events(days_ahead=days_ahead)
        return events
    except Exception as e:
        logger.error(f"Failed to get calendar events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get calendar events: {str(e)}")


@router.get("/summary", response_model=CalendarSummary)
async def get_calendar_summary():
    """Get a summary of calendar events for dashboard display."""
    try:
        summary = await calendar_service.get_calendar_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get calendar summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get calendar summary: {str(e)}")


@router.get("/today", response_model=List[CalendarEvent])
async def get_today_events():
    """Get today's calendar events."""
    try:
        events = await calendar_service.get_events(days_ahead=1)
        today = datetime.now().date()
        today_events = [e for e in events if e.start_time.date() == today]
        return today_events
    except Exception as e:
        logger.error(f"Failed to get today's events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get today's events: {str(e)}")


@router.get("/next", response_model=CalendarEvent)
async def get_next_event():
    """Get the next upcoming calendar event."""
    try:
        events = await calendar_service.get_events(days_ahead=7)
        for event in events:
            if event.is_upcoming:
                return event
        raise HTTPException(status_code=404, detail="No upcoming events found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get next event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get next event: {str(e)}")


@router.get("/status", response_model=CalendarStatus)
async def get_calendar_status():
    """Get calendar service status."""
    try:
        status = await calendar_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get calendar status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get calendar status: {str(e)}")


@router.get("/config", response_model=CalendarConfig)
async def get_calendar_config():
    """Get current calendar configuration."""
    try:
        config = calendar_service.get_config()
        return config
    except Exception as e:
        logger.error(f"Failed to get calendar config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get calendar config: {str(e)}")


@router.post("/sync")
async def sync_calendar():
    """Force a calendar sync."""
    try:
        events = await calendar_service.get_events()
        return {
            "status": "success",
            "events_count": len(events),
            "message": f"Successfully synced {len(events)} events",
            "last_sync": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to sync calendar: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync calendar: {str(e)}")


@router.get("/auth/url")
async def get_auth_url():
    """Get Google Calendar authentication URL for manual setup."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        import os
        
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        if not os.path.exists(credentials_path):
            raise HTTPException(status_code=404, detail="Credentials file not found")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, calendar_service.config.scopes)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        auth_url, _ = flow.authorization_url(prompt='consent')
        
        return {
            "auth_url": auth_url,
            "instructions": "1. Open this URL in your browser\n2. Sign in and grant permissions\n3. Copy the authorization code\n4. Use /api/calendar/auth/token endpoint with the code"
        }
    except Exception as e:
        logger.error(f"Failed to generate auth URL: {e}")
        raise HTTPException(status_code=500, detail=f"Auth URL generation error: {str(e)}")


@router.post("/auth/token")
async def complete_auth(code: str):
    """Complete authentication with authorization code."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        import os
        
        credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
        token_path = os.path.join(os.path.dirname(__file__), "token.json")
        
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, calendar_service.config.scopes)
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        # Update service
        calendar_service._authenticate()
        
        return {
            "status": "success",
            "message": "Successfully authenticated with Google Calendar",
            "authenticated": True
        }
    except Exception as e:
        logger.error(f"Failed to complete authentication: {e}")
        raise HTTPException(status_code=500, detail=f"Token exchange error: {str(e)}")


@router.post("/authenticate")
async def authenticate_calendar():
    """Re-authenticate with Google Calendar API."""
    try:
        success = calendar_service._authenticate()
        if success:
            return {
                "status": "success",
                "message": "Successfully authenticated with Google Calendar",
                "authenticated": True
            }
        else:
            raise HTTPException(status_code=401, detail="Failed to authenticate with Google Calendar")
    except Exception as e:
        logger.error(f"Failed to authenticate calendar: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


# Health check endpoint
@router.get("/health")
async def calendar_health_check():
    """Health check for calendar service."""
    try:
        status = await calendar_service.get_status()
        
        health_status = "healthy"
        if not status.authenticated:
            health_status = "authentication_required"
        elif status.error_message:
            health_status = "error"
        
        return {
            "service": "calendar",
            "status": health_status,
            "authenticated": status.authenticated,
            "calendars_count": status.calendars_count,
            "api_calls_today": status.api_calls_today,
            "last_sync": status.last_sync.isoformat() if status.last_sync else None,
            "error": status.error_message
        }
    except Exception as e:
        logger.error(f"Calendar health check failed: {e}")
        return {
            "service": "calendar",
            "status": "unhealthy",
            "error": str(e)
        }