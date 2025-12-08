import logging
import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

class WeatherRequest(BaseModel):
    latitude: float
    longitude: float

class WeatherResponse(BaseModel):
    weather: dict
    location: dict
    time: str
    isRealData: Optional[bool] = True
    error: Optional[str] = None

@router.post("/get-weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest):
    """
    Get weather data from OpenWeather API based on latitude and longitude.
    Also returns location information and current time.
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            logger.warning("⚠️ OPENWEATHER_API_KEY not set! Using mock data.")
            logger.warning("To get real weather data:")
            logger.warning("1. Get API key from https://openweathermap.org/api")
            logger.warning("2. Create .env file in ai-server directory")
            logger.warning("3. Add: OPENWEATHER_API_KEY=your_api_key_here")
            logger.warning("4. Restart the server")
            # Return mock data if API key is not set, with flag indicating it's mock data
            return WeatherResponse(
                weather={
                    "description": "معتدل",
                    "temperature": 25,
                    "humidity": 60,
                    "condition": "clear"
                },
                location={
                    "city": "الرياض",
                    "country": "السعودية",
                    "latitude": request.latitude,
                    "longitude": request.longitude
                },
                time=get_current_time(),
                isRealData=False,
                error="OPENWEATHER_API_KEY not configured"
            )
        
        # Call OpenWeather API
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": request.latitude,
            "lon": request.longitude,
            "appid": api_key,
            "units": "metric",  # Use metric units (Celsius)
            "lang": "ar"  # Arabic language
        }
        
        logger.info(f"Calling OpenWeather API for lat={request.latitude}, lon={request.longitude}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched weather data for {data.get('name', 'unknown location')}")
        
        # Extract weather information
        weather_main = data.get("weather", [{}])[0]
        main_data = data.get("main", {})
        location_data = data.get("sys", {})
        
        # Get city name (try Arabic name if available, otherwise English)
        city_name = data.get("name", "غير محدد")
        country_code = location_data.get("country", "")
        
        # Map weather conditions to Arabic descriptions
        weather_condition = weather_main.get("main", "").lower()
        condition_map = {
            "clear": "صافي",
            "clouds": "غائم",
            "rain": "ممطر",
            "drizzle": "رذاذ",
            "thunderstorm": "عاصفة رعدية",
            "snow": "ثلجي",
            "mist": "ضباب",
            "fog": "ضباب",
            "haze": "ضباب خفيف"
        }
        condition_ar = condition_map.get(weather_condition, weather_main.get("description", "غير محدد"))
        
        weather_info = {
            "description": condition_ar,
            "temperature": round(main_data.get("temp", 25)),
            "feels_like": round(main_data.get("feels_like", 25)),
            "humidity": main_data.get("humidity", 60),
            "condition": weather_condition,
            "wind_speed": data.get("wind", {}).get("speed", 0)
        }
        
        # Get location information
        location_info = {
            "city": city_name,
            "country": country_code,
            "latitude": request.latitude,
            "longitude": request.longitude
        }
        
        return WeatherResponse(
            weather=weather_info,
            location=location_info,
            time=get_current_time(),
            isRealData=True
        )
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        logger.error(f"Error calling OpenWeather API: {error_msg}")
        # Return fallback data on API error, marked as mock
        return WeatherResponse(
            weather={
                "description": "غير محدد",
                "temperature": 25,
                "humidity": 60,
                "condition": "unknown"
            },
            location={
                "city": "غير محدد",
                "country": "",
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            time=get_current_time(),
            isRealData=False,
            error=f"API Error: {error_msg}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in weather endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

def get_current_time():
    """Get current time in Arabic format"""
    from datetime import datetime
    now = datetime.now()
    # Format: HH:MM AM/PM
    return now.strftime("%I:%M %p")

