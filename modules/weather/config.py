import os
import json
import logging
from typing import Optional
from .models import WeatherConfig

logger = logging.getLogger(__name__)

class WeatherConfigManager:
    """Manages weather service configuration."""
    
    def __init__(self, config_file: str = "weather_config.json"):
        self.config_file = config_file
        self.config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    def load_config(self) -> WeatherConfig:
        """Load weather configuration from file or environment."""
        config_data = {}
        
        # Try to load from config file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded weather config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}")
        
        # Override with environment variables if available
        env_config = {
            "api_key": os.getenv("OPENWEATHER_API_KEY"),
            "location": os.getenv("WEATHER_LOCATION", config_data.get("location", "London,UK")),
            "units": os.getenv("WEATHER_UNITS", config_data.get("units", "metric")),
            "update_interval": int(os.getenv("WEATHER_UPDATE_INTERVAL", 
                                          config_data.get("update_interval", 300))),
            "provider": os.getenv("WEATHER_PROVIDER", config_data.get("provider", "openweathermap"))
        }
        
        # Merge configs (env variables take precedence)
        for key, value in env_config.items():
            if value is not None:
                config_data[key] = value
        
        return WeatherConfig(**config_data)
    
    def save_config(self, config: WeatherConfig) -> None:
        """Save weather configuration to file."""
        try:
            # Don't save API key to file for security
            config_dict = config.dict()
            if "api_key" in config_dict:
                del config_dict["api_key"]
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved weather config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")
    
    def get_api_key_status(self) -> dict:
        """Check API key configuration status."""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        return {
            "configured": api_key is not None,
            "source": "environment" if api_key else "none",
            "masked_key": f"{api_key[:8]}..." if api_key else None
        }