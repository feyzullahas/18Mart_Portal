import httpx
from typing import Optional
import time
import asyncio

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Çanakkale koordinatları
    CANAKKALE_LAT = 40.1553
    CANAKKALE_LON = 26.4142
    
    def __init__(self):
        self._cache = None
        self._cache_time = 0
        self.CACHE_TTL = 1800  # 30 dakika
        self._lock = asyncio.Lock()
    
    async def _fetch_weather(self, days: int = 7) -> Optional[dict]:
        now = time.time()
        
        async with self._lock:
            if self._cache and (now - self._cache_time < self.CACHE_TTL):
                return self._cache
                
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self.BASE_URL,
                        params={
                            "latitude": self.CANAKKALE_LAT,
                            "longitude": self.CANAKKALE_LON,
                            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weathercode,wind_speed_10m,precipitation",
                            "hourly": "temperature_2m,weathercode,precipitation_probability,apparent_temperature",
                            "daily": "temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,weathercode,precipitation_probability_max",
                            "timezone": "Europe/Istanbul",
                            "forecast_days": days
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    self._cache = data
                    self._cache_time = time.time()
                    return data
            except Exception as e:
                print(f"Hava durumu hatası: {e}")
                return self._cache
    
    async def get_current_weather(self) -> Optional[dict]:
        """Çanakkale için güncel hava durumunu getirir"""
        data = await self._fetch_weather()
        if data and "current" in data:
            return {"current": data["current"]}
        return None
    
    async def get_forecast(self, days: int = 7) -> Optional[dict]:
        """Çanakkale için hava durumu tahmini getirir"""
        # Always fetch max needed (7 days) for simplicity since the frontend defaults to 7.
        data = await self._fetch_weather(days)
        if data and "hourly" in data and "daily" in data:
            return {"hourly": data["hourly"], "daily": data["daily"]}
        return None

weather_service = WeatherService()
