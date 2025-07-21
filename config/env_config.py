"""
Environment Configuration Management
Secure handling of environment variables and sensitive configuration
"""
import os
from pathlib import Path
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class EnvConfig:
    """
    Secure environment configuration manager.
    Loads from .env file and provides type-safe access to environment variables.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize with optional custom .env file path"""
        self.env_file = env_file or self._find_env_file()
        self._load_dotenv()
        
    def _find_env_file(self) -> Optional[str]:
        """Find .env file in project directory"""
        project_root = Path(__file__).parent.parent
        env_path = project_root / '.env'
        return str(env_path) if env_path.exists() else None
    
    def _load_dotenv(self):
        """Load environment variables from .env file"""
        if self.env_file and Path(self.env_file).exists():
            try:
                from dotenv import load_dotenv
                load_dotenv(self.env_file)
                logger.info(f"Loaded environment from {self.env_file}")
            except ImportError:
                logger.warning("python-dotenv not installed, using system environment only")
            except Exception as e:
                logger.error(f"Error loading .env file: {e}")
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get environment variable with optional default and required validation
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Raise error if not found and no default
            
        Returns:
            Environment variable value or default
            
        Raises:
            ValueError: If required=True and variable not found
        """
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"Required environment variable '{key}' not found")
            
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = self.get(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable"""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: list = None, separator: str = ',') -> list:
        """Get list environment variable (comma-separated by default)"""
        if default is None:
            default = []
        value = self.get(key)
        if not value:
            return default
        return [item.strip() for item in value.split(separator) if item.strip()]

# Global configuration instance
config = EnvConfig()

# Application Configuration
class Config:
    """Application configuration using environment variables"""
    
    # Google OAuth
    GOOGLE_CLIENT_ID = config.get('GOOGLE_CLIENT_ID', required=True)
    GOOGLE_CLIENT_SECRET = config.get('GOOGLE_CLIENT_SECRET', required=True)
    GOOGLE_REDIRECT_URI = config.get('GOOGLE_REDIRECT_URI', 'http://localhost:8001/auth/callback')
    
    # Server Settings
    SERVER_HOST = config.get('SERVER_HOST', 'localhost')
    SERVER_PORT = config.get_int('SERVER_PORT', 8001)
    DEBUG_MODE = config.get_bool('DEBUG_MODE', False)
    
    # Database
    DATABASE_URL = config.get('DATABASE_URL', 'sqlite:///lifehub.db')
    DATABASE_ECHO = config.get_bool('DATABASE_ECHO', False)
    
    # Security
    SECRET_KEY = config.get('SECRET_KEY', required=True)
    SESSION_TIMEOUT = config.get_int('SESSION_TIMEOUT', 3600)
    
    # CORS and Security
    CORS_ORIGINS = config.get_list('CORS_ORIGINS', ['http://localhost:8001'])
    ALLOWED_HOSTS = config.get_list('ALLOWED_HOSTS', ['localhost'])
    
    # Logging
    LOG_LEVEL = config.get('LOG_LEVEL', 'INFO')
    LOG_FILE = config.get('LOG_FILE', 'logs/lifehub.log')
    LOG_MAX_SIZE = config.get_int('LOG_MAX_SIZE', 10485760)  # 10MB
    LOG_BACKUP_COUNT = config.get_int('LOG_BACKUP_COUNT', 5)
    
    # Pi-specific
    KIOSK_MODE = config.get_bool('KIOSK_MODE', True)
    DISPLAY_BRIGHTNESS = config.get_int('DISPLAY_BRIGHTNESS', 80)
    SCREEN_TIMEOUT = config.get_int('SCREEN_TIMEOUT', 300)
    
    @classmethod
    def validate(cls) -> Dict[str, str]:
        """
        Validate required configuration.
        Returns dict of missing/invalid settings.
        """
        errors = {}
        
        if not cls.GOOGLE_CLIENT_ID or cls.GOOGLE_CLIENT_ID == 'your_client_id_here.apps.googleusercontent.com':
            errors['GOOGLE_CLIENT_ID'] = 'Missing or default value'
            
        if not cls.GOOGLE_CLIENT_SECRET or cls.GOOGLE_CLIENT_SECRET == 'your_client_secret_here':
            errors['GOOGLE_CLIENT_SECRET'] = 'Missing or default value'
            
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'your_very_long_random_secret_key_here':
            errors['SECRET_KEY'] = 'Missing or default value'
            
        return errors
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.DEBUG_MODE or config.get_bool('RELOAD_ON_CHANGE', False)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return not cls.is_development()

def get_oauth_config() -> Dict[str, str]:
    """
    Get OAuth configuration for Google Calendar API.
    Returns dict that can be used with google-auth-oauthlib.
    """
    return {
        "web": {
            "client_id": Config.GOOGLE_CLIENT_ID,
            "client_secret": Config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
        }
    }

def create_secret_key() -> str:
    """Generate a secure random secret key"""
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits + "\!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(64))

if __name__ == "__main__":
    # Validation and setup assistance
    print("Pi Life Hub Configuration Validator")
    print("=" * 50)
    
    errors = Config.validate()
    if errors:
        print("❌ Configuration Errors:")
        for key, error in errors.items():
            print(f"  {key}: {error}")
        print("\nPlease update your .env file with valid values.")
        print("Use .env.example as a template.")
    else:
        print("✅ Configuration is valid\!")
        
    print(f"\nMode: {'Development' if Config.is_development() else 'Production'}")
    print(f"Server: {Config.SERVER_HOST}:{Config.SERVER_PORT}")
    print(f"Database: {Config.DATABASE_URL}")
EOF < /dev/null
