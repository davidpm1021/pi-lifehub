from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from .service import WeatherService
from .models import WeatherResponse, WeatherConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/weather", tags=["weather"])

# Initialize weather service
weather_service = WeatherService()

@router.get("/current", response_model=WeatherResponse)
async def get_current_weather() -> WeatherResponse:
    """Get current weather data."""
    try:
        weather_data = await weather_service.get_current_weather()
        return weather_data
    except Exception as e:
        logger.error(f"Failed to get current weather: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")

@router.get("/forecast")
async def get_weather_forecast(days: int = 3) -> Dict[str, Any]:
    """Get weather forecast for upcoming days."""
    try:
        forecast_data = await weather_service.get_forecast(days)
        return forecast_data
    except Exception as e:
        logger.error(f"Failed to get weather forecast: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch forecast data")

@router.get("/config")
async def get_weather_config() -> WeatherConfig:
    """Get current weather configuration."""
    return weather_service.get_config()

@router.post("/config")
async def update_weather_config(config: WeatherConfig) -> Dict[str, str]:
    """Update weather configuration."""
    try:
        weather_service.update_config(config)
        return {"status": "success", "message": "Weather configuration updated"}
    except Exception as e:
        logger.error(f"Failed to update weather config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@router.get("/status")
async def get_weather_status() -> Dict[str, Any]:
    """Get weather service status and health."""
    try:
        status = await weather_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get weather status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weather status")