import json
import logging
import re
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIAnalysisResponse, PerfumeRecommendation
from app.services.database import get_perfume_recommendations, save_ai_interaction

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_location_from_coordinates(latitude: float, longitude: float) -> Dict[str, str]:
    """Get city and country name from coordinates using reverse geocoding"""
    try:
        # Try using OpenWeather's reverse geocoding API (free, no key needed for basic usage)
        # Or use Nominatim (OpenStreetMap) which is free and doesn't require API key
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "accept-language": "ar,en"
        }
        
        response = requests.get(url, params=params, timeout=5, headers={
            "User-Agent": "Aura-AI-Server/1.0"
        })
        
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            
            # Try to get city name in Arabic or English
            city = (
                address.get("city") or 
                address.get("town") or 
                address.get("village") or 
                address.get("municipality") or
                address.get("county") or
                "غير محدد"
            )
            
            country = address.get("country", "غير محدد")
            country_code = address.get("country_code", "").upper()
            
            return {
                "city": city,
                "country": country,
                "country_code": country_code
            }
    except Exception as e:
        logger.warning(f"Reverse geocoding failed: {e}")
    
    # Fallback: return coordinates only
    return {
        "city": f"خط العرض {latitude:.4f}",
        "country": f"خط الطول {longitude:.4f}",
        "country_code": ""
    }

async def fetch_weather_from_coordinates(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch weather, location, and time data from coordinates"""
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        # Get location from coordinates using reverse geocoding
        location_info = await get_location_from_coordinates(latitude, longitude)
        
        if not api_key:
            logger.warning("OPENWEATHER_API_KEY not set, using mock weather data")
            return {
                "weather": {
                    "description": "معتدل",
                    "temperature": 25,
                    "humidity": 60,
                    "condition": "clear"
                },
                "location": {
                    "city": location_info["city"],
                    "country": location_info["country"],
                    "country_code": location_info.get("country_code", ""),
                    "latitude": latitude,
                    "longitude": longitude
                },
                "time": datetime.now().strftime("%I:%M %p"),
                "isRealData": False
            }
        
        # Call OpenWeather API
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
            "lang": "ar"
        }
        
        response = requests.get(
            url,
            params=params,
            timeout=10,
            proxies={"http": None, "https": None}
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract weather information
        weather_main = data.get("weather", [{}])[0]
        main_data = data.get("main", {})
        location_data = data.get("sys", {})
        
        # Get location from coordinates using reverse geocoding (more accurate)
        location_info = await get_location_from_coordinates(latitude, longitude)
        city_name = location_info.get("city", data.get("name", ""))
        country_name = location_info.get("country", "")
        country_code = location_info.get("country_code", location_data.get("country", ""))
        
        # Map weather conditions to Arabic
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
        
        return {
            "weather": {
                "description": condition_ar,
                "temperature": round(main_data.get("temp", 25)),
                "feels_like": round(main_data.get("feels_like", 25)),
                "humidity": main_data.get("humidity", 60),
                "condition": weather_condition,
                "wind_speed": data.get("wind", {}).get("speed", 0)
            },
            "location": {
                "city": city_name or location_info.get("city", "غير محدد"),
                "country": country_name or location_info.get("country", country_code),
                "country_code": country_code or location_info.get("country_code", ""),
                "latitude": latitude,
                "longitude": longitude
            },
            "time": datetime.now().strftime("%I:%M %p"),
            "isRealData": True
        }
        
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        # Get location from coordinates even if weather fails
        location_info = await get_location_from_coordinates(latitude, longitude)
        
        # Return fallback data with actual location
        return {
            "weather": {
                "description": "غير محدد",
                "temperature": 25,
                "humidity": 60,
                "condition": "unknown"
            },
            "location": {
                "city": location_info.get("city", "غير محدد"),
                "country": location_info.get("country", ""),
                "country_code": location_info.get("country_code", ""),
                "latitude": latitude,
                "longitude": longitude
            },
            "time": datetime.now().strftime("%I:%M %p"),
            "isRealData": False,
            "error": str(e)
        }

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_ai_nose(request: MultiModalRequest):
    try:
        logger.info("AI Nose request received", extra={"request": request.model_dump()})

        # Normalize context/options in case the client sent JSON as string
        context_data = request.context or {}
        if isinstance(context_data, str):
            try:
                context_data = json.loads(context_data)
            except Exception:
                context_data = {}

        options_data = request.options
        if isinstance(options_data, str):
            try:
                options_data = json.loads(options_data)
            except Exception:
                options_data = None

        # Extract context from text and options
        mood = extract_mood(request.text) if request.text else None
        occasion = extract_occasion(request.text) if request.text else None
        
        # Use options if provided
        if options_data:
            mood = options_data.get('mood', mood)
            occasion = options_data.get('occasion', occasion)
            gender = options_data.get('gender')
            skin_type = options_data.get('skin_type')
        
        # Auto-fetch weather/location/time if coordinates provided but weather not
        location = context_data.get('location', {})
        if isinstance(location, str):
            try:
                location = json.loads(location)
            except Exception:
                location = {}
        
        weather = context_data.get('weather')
        latitude = location.get('latitude') if isinstance(location, dict) else None
        longitude = location.get('longitude') if isinstance(location, dict) else None
        
        # If coordinates provided but weather not, fetch it automatically
        if (latitude is not None and longitude is not None) and not weather:
            logger.info(f"Auto-fetching weather for coordinates: {latitude}, {longitude}")
            weather_data = await fetch_weather_from_coordinates(latitude, longitude)
            context_data['weather'] = weather_data['weather']
            context_data['location'] = weather_data['location']
            context_data['time'] = weather_data['time']
            weather = weather_data['weather']
            location = weather_data['location']
            time_str = weather_data['time']
        else:
            weather = context_data.get('weather')
            location = context_data.get('location')
            time_str = context_data.get('time')
        
        # Build context strings for analysis
        weather_context = ""
        location_context = ""
        time_context = ""
        
        if weather and isinstance(weather, dict):
            weather_context = f"الطقس: {weather.get('description', 'غير محدد')}, درجة الحرارة: {weather.get('temperature', 'غير محددة')}°م"
        
        if location and isinstance(location, dict):
            city = location.get('city')
            country = location.get('country')
            if city or country:
                location_context = f"الموقع: {city or ''}{', ' if city and country else ''}{country or ''}".strip()
        
        if time_str:
            time_context = f"الوقت: {time_str}"
        
        # Get recommendations from database
        recommendations = await get_perfume_recommendations(
            mood=mood,
            occasion=occasion,
            skin_type=options_data.get('skin_type') if options_data else None,
            gender=options_data.get('gender') if options_data else None,
            limit=3
        )
        
        # Ensure all recommendations have perfume_id
        for rec in recommendations:
            if not rec.perfume_id:
                logger.warning(f"Recommendation missing perfume_id: {rec.name}")
        
        # Generate analysis text
        analysis = f"""بناءً على تحليل الأنف الإلكتروني AI Nose™:

النص المدخل: {request.text or 'لا يوجد نص'}
{weather_context}
{location_context}
{time_context}

تحليل المزاج: {mood or 'غير محدد'}
المناسبة: {occasion or 'غير محددة'}

إليك أفضل {len(recommendations)} عطور مخصصة لك:"""

        # Save interaction for learning
        if request.user_id:
            await save_ai_interaction(
                request.user_id,
                'ai_nose',
                {
                    'text': request.text,
                    'options': request.options,
                    'context': context_data
                },
                {
                    'mood': mood,
                    'occasion': occasion,
                    'weather': weather,
                    'location': location,
                    'time': time_str,
                    'recommendations': [
                        {
                            'perfume_id': r.perfume_id,
                            'name': r.name,
                            'brand': r.brand,
                            'compatibility_score': r.compatibility_score
                        } for r in recommendations
                    ]
                }
            )
        
        return AIAnalysisResponse(
            analysis=analysis,
            recommendations=recommendations,
            confidence=0.92,
            metadata={
                'detected_mood': mood,
                'detected_occasion': occasion,
                'weather': weather,
                'location': location,
                'time': time_str,
                'weather_context': weather_context,
                'location_context': location_context,
                'time_context': time_context,
                'recommendations_count': len(recommendations),
                'recommendations_with_ids': [r.perfume_id for r in recommendations if r.perfume_id]
            }
        )
        
    except Exception as e:
        logger.exception("AI Nose processing failed", extra={"request": request.model_dump()})
        raise HTTPException(status_code=500, detail=str(e))

def extract_mood(text: str) -> str:
    """Extract mood from text using simple keyword matching"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    mood_keywords = {
        'نشيط': ['منعش', 'نشيط', 'حيوي', 'طاقة', 'متحمس', 'fresh', 'energetic'],
        'هادئ': ['هادئ', 'مسترخي', 'مريح', 'هدوء', 'بارد'],
        'واثق': ['واثق', 'قوي', 'مؤثر', 'قائد', 'confident'],
        'رومانسي': ['رومانسي', 'حب', 'موعد', 'عاطفي', 'أمسية خاصة'],
        'سعيد': ['سعيد', 'فرح', 'مبسوط', 'مرح', 'adventurous']
    }
    
    for mood, keywords in mood_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood
    
    return 'متوازن'

def extract_occasion(text: str) -> str:
    """Extract occasion from text using simple keyword matching"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    occasion_keywords = {
        'يومي': ['صيف', 'يومي', 'عادي', 'بيت', 'منزل', 'منعش'],
        'عمل': ['عمل', 'مكتب', 'اجتماع', 'مقابلة'],
        'موعد': ['موعد', 'لقاء', 'خروج', 'أمسية خاصة', 'رومانسي'],
        'حفلة': ['حفلة', 'احتفال', 'مناسبة', 'عيد'],
        'زفاف': ['زفاف', 'عرس', 'زواج']
    }
    
    for occasion, keywords in occasion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return occasion
    
    return 'عام'
