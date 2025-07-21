import os
import json
import logging
from typing import Optional
from .models import PhotoConfig

logger = logging.getLogger(__name__)

class PhotoConfigManager:
    """Manages photo service configuration."""
    
    def __init__(self, config_file: str = "photos_config.json"):
        self.config_file = config_file
        self.config_path = os.path.join(os.path.dirname(__file__), config_file)
    
    def load_config(self) -> PhotoConfig:
        """Load photo configuration from file or environment."""
        config_data = {}
        
        # Try to load from config file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                logger.info(f"Loaded photo config from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load photo config file: {e}")
        
        # Override with environment variables if available
        env_config = {
            "photos_directory": os.getenv("PHOTOS_DIRECTORY", 
                                        config_data.get("photos_directory", "/home/davidpm/Pictures")),
            "thumbnails_directory": os.getenv("THUMBNAILS_DIRECTORY", 
                                             config_data.get("thumbnails_directory", "/home/davidpm/Pictures/thumbnails")),
            "slideshow_interval": int(os.getenv("SLIDESHOW_INTERVAL", 
                                              config_data.get("slideshow_interval", 10))),
            "max_photo_size": int(os.getenv("MAX_PHOTO_SIZE", 
                                          config_data.get("max_photo_size", 10 * 1024 * 1024))),
            "auto_scan": os.getenv("AUTO_SCAN", "true").lower() == "true",
            "scan_interval": int(os.getenv("SCAN_INTERVAL", 
                                         config_data.get("scan_interval", 3600))),
            "show_metadata": os.getenv("SHOW_METADATA", "true").lower() == "true",
            "shuffle_slideshow": os.getenv("SHUFFLE_SLIDESHOW", "true").lower() == "true"
        }
        
        # Merge configs (env variables take precedence)
        for key, value in env_config.items():
            if value is not None:
                config_data[key] = value
        
        # Set defaults for lists and tuples if not present
        if "allowed_formats" not in config_data:
            config_data["allowed_formats"] = ["JPEG", "JPG", "PNG", "GIF", "BMP"]
        
        if "thumbnail_size" not in config_data:
            config_data["thumbnail_size"] = (200, 200)
        
        return PhotoConfig(**config_data)
    
    def save_config(self, config: PhotoConfig) -> None:
        """Save photo configuration to file."""
        try:
            config_dict = config.dict()
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved photo config to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save photo config file: {e}")
    
    def get_directory_info(self) -> dict:
        """Get information about photo directories."""
        config = self.load_config()
        
        return {
            "photos_directory": {
                "path": config.photos_directory,
                "exists": os.path.exists(config.photos_directory),
                "writable": os.access(config.photos_directory, os.W_OK) if os.path.exists(config.photos_directory) else False
            },
            "thumbnails_directory": {
                "path": config.thumbnails_directory,
                "exists": os.path.exists(config.thumbnails_directory),
                "writable": os.access(config.thumbnails_directory, os.W_OK) if os.path.exists(config.thumbnails_directory) else False
            }
        }