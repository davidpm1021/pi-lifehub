"""
Configuration manager for Google Calendar integration.
"""

import os
import json
import logging
from typing import Optional
from .models import CalendarConfig

logger = logging.getLogger(__name__)


class CalendarConfigManager:
    """Manages Google Calendar service configuration."""
    
    def __init__(self, config_file: str = "calendar_config.json"):
        self.config_file = config_file
        self.config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    def load_config(self) -> CalendarConfig:
        """Load calendar configuration from file or environment."""
        config_data = {}
        
        # Try to load from config file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded calendar config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load calendar config file: {e}")
        
        # Override with environment variables if available
        env_config = {
            "credentials_file": os.getenv("GOOGLE_CREDENTIALS_FILE", 
                                        config_data.get("credentials_file", "credentials.json")),
            "token_file": os.getenv("GOOGLE_TOKEN_FILE", 
                                   config_data.get("token_file", "token.json")),
            "calendar_ids": os.getenv("GOOGLE_CALENDAR_IDS", "").split(",") if os.getenv("GOOGLE_CALENDAR_IDS") else config_data.get("calendar_ids", ["primary"]),
            "max_events": int(os.getenv("CALENDAR_MAX_EVENTS", 
                                      config_data.get("max_events", 10))),
            "days_ahead": int(os.getenv("CALENDAR_DAYS_AHEAD", 
                                      config_data.get("days_ahead", 7))),
            "timezone": os.getenv("CALENDAR_TIMEZONE", 
                                config_data.get("timezone", "America/New_York"))
        }
        
        # Filter out None values and empty strings
        env_config = {k: v for k, v in env_config.items() if v not in [None, "", []]}
        
        # Merge configs (env variables take precedence)
        for key, value in env_config.items():
            if value is not None:
                config_data[key] = value
        
        # Set default scopes if not present
        if "scopes" not in config_data:
            config_data["scopes"] = ["https://www.googleapis.com/auth/calendar.readonly"]
        
        return CalendarConfig(**config_data)
    
    def save_config(self, config: CalendarConfig) -> None:
        """Save calendar configuration to file."""
        try:
            config_dict = config.dict()
            
            # Don't save sensitive file paths to config
            sensitive_keys = ["credentials_file", "token_file"]
            for key in sensitive_keys:
                if key in config_dict:
                    del config_dict[key]
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved calendar config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save calendar config file: {e}")
    
    def get_credentials_status(self) -> dict:
        """Check Google Calendar credentials status."""
        config = self.load_config()
        credentials_path = os.path.join(os.path.dirname(__file__), config.credentials_file)
        token_path = os.path.join(os.path.dirname(__file__), config.token_file)
        
        return {
            "credentials_file": {
                "path": credentials_path,
                "exists": os.path.exists(credentials_path),
                "readable": os.access(credentials_path, os.R_OK) if os.path.exists(credentials_path) else False
            },
            "token_file": {
                "path": token_path,
                "exists": os.path.exists(token_path),
                "readable": os.access(token_path, os.R_OK) if os.path.exists(token_path) else False
            },
            "config_valid": all([
                os.path.exists(credentials_path),
                len(config.scopes) > 0,
                len(config.calendar_ids) > 0
            ])
        }