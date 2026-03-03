import httpx
from typing import Optional

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Çanakkale koordinatları
    CANAKKALE_LAT = 40.1553
    CANAKKALE_LON = 26.4142
    
    async def get_current_weather(self) -> Optional[dict]:
        """Çanakkale için güncel hava durumunu getirir"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "latitude": self.CANAKKALE_LAT,
                        "longitude": self.CANAKKALE_LON,
                        "current_weather": "true",
                        "timezone": "Europe/Istanbul"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Hava durumu hatası: {e}")
            return None
    
    async def get_forecast(self, days: int = 5) -> Optional[dict]:
        """Çanakkale için hava durumu tahmini getirir"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "latitude": self.CANAKKALE_LAT,
                        "longitude": self.CANAKKALE_LON,
                        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                        "timezone": "Europe/Istanbul",
                        "forecast_days": days
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Tahmin hatası: {e}")
            return None

weather_service = WeatherService()
