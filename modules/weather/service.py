import asyncio
import aiohttp
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .models import WeatherResponse, WeatherConfig, WeatherCondition, Temperature, WeatherStatus
from .config import WeatherConfigManager

logger = logging.getLogger(__name__)

class WeatherService:
    """Weather service for fetching and managing weather data."""
    
    def __init__(self):
        self.config_manager = WeatherConfigManager()
        self.config = self.config_manager.load_config()
        self.last_update: Optional[datetime] = None
        self.cached_weather: Optional[WeatherResponse] = None
        self.api_calls_today = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        
    async def get_current_weather(self) -> WeatherResponse:
        """Get current weather data with caching."""
        try:
            # Check if cached data is still fresh
            if self._is_cache_valid():
                logger.info("Returning cached weather data")
                return self.cached_weather
            
            # Fetch fresh weather data
            weather_data = await self._fetch_weather_data()
            
            # Cache the result
            self.cached_weather = weather_data
            self.last_update = datetime.now()
            self.api_calls_today += 1
            
            logger.info(f"Fetched fresh weather data for {weather_data.location}")
            return weather_data
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Failed to get weather data: {e}")
            
            # Return cached data if available, even if stale
            if self.cached_weather:
                logger.warning("Returning stale cached weather data due to error")
                
    async def get_forecast(self, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast data."""
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            # Use specific coordinates for Medford, NJ to avoid confusion with Medford, OR
            params = {
                'lat': 39.9009,
                'lon': -74.8234,
                'appid': self.config.api_key,
                'units': self.config.units,
                'cnt': min(days * 8, 40)  # 8 forecasts per day (3-hour intervals), max 40
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 401:
                        raise ValueError("Invalid API key")
                    elif response.status == 404:
                        raise ValueError(f"Location '{self.config.location}' not found")
                    elif response.status != 200:
                        raise ValueError(f"Forecast API request failed with status {response.status}")
                    
                    data = await response.json()
                    return self._parse_forecast_data(data)
                    
        except Exception as e:
            logger.error(f"Failed to get forecast data: {e}")
            return {"error": str(e), "forecasts": []}
    
    def _parse_forecast_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse OpenWeatherMap forecast API response."""
        try:
            forecasts = []
            daily_forecasts = {}
            
            for item in data["list"]:
                # Parse each 3-hour forecast item
                dt = datetime.fromtimestamp(item["dt"])
                date_key = dt.strftime("%Y-%m-%d")
                
                forecast_item = {
                    "datetime": dt.isoformat(),
                    "date": date_key,
                    "time": dt.strftime("%H:%M"),
                    "temperature": round(item["main"]["temp"], 1),
                    "feels_like": round(item["main"]["feels_like"], 1),
                    "humidity": item["main"]["humidity"],
                    "condition": item["weather"][0]["main"],
                    "description": item["weather"][0]["description"].title(),
                    "icon": item["weather"][0]["icon"],
                    "wind_speed": item.get("wind", {}).get("speed", 0),
                    "precipitation": item.get("rain", {}).get("3h", 0) + item.get("snow", {}).get("3h", 0)
                }
                
                forecasts.append(forecast_item)
                
                # Group by day for daily summaries
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = {
                        "date": date_key,
                        "day_name": dt.strftime("%A"),
                        "temps": [],
                        "conditions": [],
                        "precipitation": 0,
                        "humidity": []
                    }
                
                daily_forecasts[date_key]["temps"].append(item["main"]["temp"])
                daily_forecasts[date_key]["conditions"].append(item["weather"][0]["main"])
                daily_forecasts[date_key]["precipitation"] += forecast_item["precipitation"]
                daily_forecasts[date_key]["humidity"].append(item["main"]["humidity"])
            
            # Calculate daily summaries
            daily_summaries = []
            for date_key, day_data in daily_forecasts.items():
                daily_summary = {
                    "date": date_key,
                    "day_name": day_data["day_name"],
                    "temp_min": round(min(day_data["temps"]), 1),
                    "temp_max": round(max(day_data["temps"]), 1),
                    "condition": max(set(day_data["conditions"]), key=day_data["conditions"].count),
                    "precipitation": round(day_data["precipitation"], 1),
                    "avg_humidity": round(sum(day_data["humidity"]) / len(day_data["humidity"]), 1)
                }
                daily_summaries.append(daily_summary)
            
            return {
                "location": f"{data['city']['name']}, {data['city']['country']}",
                "hourly_forecasts": forecasts,
                "daily_summaries": daily_summaries[:5],  # Limit to 5 days
                "updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to parse forecast data: {e}")
            return {"error": str(e), "forecasts": []}
    
    async def _fetch_weather_data(self) -> WeatherResponse:
        """Fetch weather data from OpenWeatherMap API."""
        if not self.config.api_key:
            raise ValueError("OpenWeatherMap API key not configured")
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        # Use specific coordinates for Medford, NJ to avoid confusion with Medford, OR
        params = {
            "lat": 39.9009,
            "lon": -74.8234,
            "appid": self.config.api_key,
            "units": self.config.units
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 401:
                    raise ValueError("Invalid API key")
                elif response.status == 404:
                    raise ValueError(f"Location '{self.config.location}' not found")
                elif response.status != 200:
                    raise ValueError(f"API request failed with status {response.status}")
                
                data = await response.json()
                return self._parse_weather_data(data)
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> WeatherResponse:
        """Parse OpenWeatherMap API response into WeatherResponse model."""
        try:
            # Extract temperature data
            temp_data = data["main"]
            temperature = Temperature(
                current=round(temp_data["temp"], 1),
                feels_like=round(temp_data["feels_like"], 1),
                min=round(temp_data["temp_min"], 1),
                max=round(temp_data["temp_max"], 1),
                unit="F" if self.config.units == "imperial" else "C"
            )
            
            # Extract weather condition
            weather_info = data["weather"][0]
            condition = WeatherCondition(
                main=weather_info["main"],
                description=weather_info["description"].title(),
                icon=weather_info["icon"]
            )
            
            # Extract other data
            wind_data = data.get("wind", {})
            
            return WeatherResponse(
                location=f"{data['name']}, {data['sys']['country']}",
                timestamp=datetime.now(),
                temperature=temperature,
                condition=condition,
                humidity=temp_data["humidity"],
                pressure=temp_data["pressure"],
                wind_speed=round(wind_data.get("speed", 0), 1),
                wind_direction=wind_data.get("deg", 0),
                visibility=round(data.get("visibility", 0) / 1000, 1),  # Convert m to km
                uv_index=None  # Would need separate UV API call
            )
            
        except KeyError as e:
            raise ValueError(f"Unexpected API response format: missing {e}")
    
    def _get_fallback_weather(self) -> WeatherResponse:
        """Return fallback weather data when API is unavailable."""
        return WeatherResponse(
            location=self.config.location,
            timestamp=datetime.now(),
            temperature=Temperature(
                current=20.0,
                feels_like=20.0,
                min=15.0,
                max=25.0
            ),
            condition=WeatherCondition(
                main="Unknown",
                description="Weather data unavailable",
                icon="01d"
            ),
            humidity=50,
            pressure=1013.25,
            wind_speed=0.0,
            wind_direction=0
        )
    
    def _is_cache_valid(self) -> bool:
        """Check if cached weather data is still valid."""
        if not self.cached_weather or not self.last_update:
            return False
        
        cache_age = datetime.now() - self.last_update
        return cache_age.total_seconds() < self.config.update_interval
    
    
    def get_config(self) -> WeatherConfig:
        """Get current weather configuration."""
        return self.config
    
    def update_config(self, new_config: WeatherConfig) -> None:
        """Update weather configuration."""
        self.config = new_config
        self.config_manager.save_config(new_config)
        
        # Clear cache to force refresh with new settings
        self.cached_weather = None
        self.last_update = None
        
        logger.info("Weather configuration updated")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get weather service status."""
        next_update = None
        if self.last_update:
            next_update = self.last_update + timedelta(seconds=self.config.update_interval)
        
        return {
            "service_active": True,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "next_update": next_update.isoformat() if next_update else None,
            "api_calls_today": self.api_calls_today,
            "api_limit": 1000,  # OpenWeatherMap free tier
            "error_count": self.error_count,
            "last_error": self.last_error,
            "cache_valid": self._is_cache_valid(),
            "location": self.config.location,
            "update_interval": self.config.update_interval
        }