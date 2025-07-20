from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class WeatherCondition(BaseModel):
    """Weather condition details."""
    main: str  # e.g., "Clear", "Rain", "Clouds"
    description: str  # e.g., "clear sky", "light rain"
    icon: str  # Weather icon code

class Temperature(BaseModel):
    """Temperature information."""
    current: float
    feels_like: float
    min: float
    max: float
    unit: str = "°C"

class WeatherResponse(BaseModel):
    """Current weather response model."""
    location: str
    timestamp: datetime
    temperature: Temperature
    condition: WeatherCondition
    humidity: int  # Percentage
    pressure: float  # hPa
    wind_speed: float  # m/s
    wind_direction: int  # degrees
    visibility: Optional[float] = None  # km
    uv_index: Optional[float] = None

class ForecastDay(BaseModel):
    """Single day forecast."""
    date: str
    temperature_high: float
    temperature_low: float
    condition: WeatherCondition
    precipitation_chance: int  # Percentage
    humidity: int
    wind_speed: float

class WeatherConfig(BaseModel):
    """Weather service configuration."""
    api_key: Optional[str] = None
    location: str = "London,UK"  # Default location
    units: str = "metric"  # metric, imperial, standard
    update_interval: int = 300  # seconds (5 minutes)
    provider: str = "openweathermap"  # weather service provider

class WeatherAlert(BaseModel):
    """Weather alert/warning."""
    title: str
    description: str
    severity: str  # minor, moderate, severe, extreme
    start_time: datetime
    end_time: datetime
    areas: List[str]

class WeatherStatus(BaseModel):
    """Weather service status."""
    service_active: bool
    last_update: Optional[datetime] = None
    next_update: Optional[datetime] = None
    api_calls_today: int
    api_limit: Optional[int] = None
    error_count: int
    last_error: Optional[str] = None