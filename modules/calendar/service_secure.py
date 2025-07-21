"""
Secure Google Calendar Service
Uses environment variables and secure token management
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.env_config import get_oauth_config, Config

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class SecureCalendarService:
    """Secure Google Calendar service with environment-based configuration"""
    
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.service = None
        self.token_file = self._get_token_file_path()
        
    def _get_token_file_path(self) -> Path:
        """Get secure path for token storage"""
        # Store tokens in a secure location
        token_dir = Path.home() / '.config' / 'lifehub'
        token_dir.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions
        os.chmod(str(token_dir), 0o700)
        
        return token_dir / 'calendar_token.json'
    
    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from secure token file"""
        if not self.token_file.exists():
            return None
            
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                
            credentials = Credentials.from_authorized_user_info(
                token_data, SCOPES
            )
            
            logger.info("Loaded existing credentials")
            return credentials
            
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return None
    
    def _save_credentials(self, credentials: Credentials):
        """Save credentials to secure token file"""
        try:
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
                
            # Set restrictive permissions
            os.chmod(str(self.token_file), 0o600)
            
            logger.info("Saved credentials securely")
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
            raise
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Try to load existing credentials
            self.credentials = self._load_credentials()
            
            # Check if credentials are valid and refresh if needed
            if self.credentials:
                if self.credentials.expired and self.credentials.refresh_token:
                    logger.info("Refreshing expired credentials")
                    self.credentials.refresh(Request())
                    self._save_credentials(self.credentials)
                elif not self.credentials.valid:
                    logger.warning("Credentials are invalid")
                    self.credentials = None
            
            # If no valid credentials, start OAuth flow
            if not self.credentials:
                logger.info("Starting OAuth authentication flow")
                oauth_config = get_oauth_config()
                
                flow = InstalledAppFlow.from_client_config(
                    oauth_config, SCOPES
                )
                
                # For headless environments, use device flow
                if Config.KIOSK_MODE:
                    self.credentials = flow.run_device_flow()
                else:
                    self.credentials = flow.run_local_server(
                        port=Config.SERVER_PORT + 1
                    )
                
                self._save_credentials(self.credentials)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Calendar service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_upcoming_events(self, max_results: int = 10) -> list:
        """
        Get upcoming calendar events
        
        Args:
            max_results: Maximum number of events to return
            
        Returns:
            List of calendar events
        """
        if not self.service:
            raise RuntimeError("Service not authenticated. Call authenticate() first.")
        
        try:
            # Get current time in RFC3339 format
            now = datetime.utcnow().isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} upcoming events")
            return events
            
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health and authentication status
        
        Returns:
            Health status dictionary
        """
        status = {
            'authenticated': False,
            'credentials_valid': False,
            'service_available': False,
            'last_check': datetime.now().isoformat()
        }
        
        try:
            if self.credentials:
                status['authenticated'] = True
                status['credentials_valid'] = self.credentials.valid
                
                if self.service:
                    # Try a simple API call
                    self.service.calendarList().list(maxResults=1).execute()
                    status['service_available'] = True
                    
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            status['error'] = str(e)
        
        return status

# Global service instance
calendar_service = SecureCalendarService()

def get_calendar_service() -> SecureCalendarService:
    """Get the global calendar service instance"""
    return calendar_service

if __name__ == "__main__":
    # Test the service
    service = SecureCalendarService()
    
    print("Testing Calendar Service Authentication...")
    if service.authenticate():
        print("✅ Authentication successful\!")
        
        print("\nHealth Check:")
        health = service.health_check()
        for key, value in health.items():
            print(f"  {key}: {value}")
            
        print("\nFetching upcoming events...")
        events = service.get_upcoming_events(5)
        print(f"Found {len(events)} upcoming events")
        
    else:
        print("❌ Authentication failed\!")
EOF < /dev/null
