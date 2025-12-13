import json
import logging
import re
from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIAnalysisResponse, PerfumeRecommendation
from app.services.database import get_perfume_recommendations, save_ai_interaction

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_ai_nose(request: MultiModalRequest):
    try:
        logger.info("AI Nose request received", extra={"request": request.model_dump()})

        # Normalize context/options in case the client sent JSON as string
        context_data = request.context
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
        
        # Get weather/location/time context
        weather_context = ""
        location_context = ""
        time_context = ""
        if context_data:
            weather = context_data.get('weather')
            location = context_data.get('location')
            if isinstance(location, str):
                try:
                    location = json.loads(location)
                except Exception:
                    location = {}

            time_str = context_data.get('time')

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
        
        # Generate analysis text
        analysis = f"""بناءً على تحليل الأنف الإلكتروني AI Nose™:

النص المدخل: {request.text or 'لا يوجد نص'}
{weather_context}
{location_context}
{time_context}

تحليل المزاج: {mood or 'غير محدد'}
المناسبة: {occasion or 'غير محددة'}

إليك أفضل 3 عطور مخصصة لك:"""

        # Save interaction for learning
        if request.user_id:
            await save_ai_interaction(
                request.user_id,
                'ai_nose',
                {
                    'text': request.text,
                    'options': request.options,
                    'context': request.context
                },
                {
                    'mood': mood,
                    'occasion': occasion,
                    'recommendations': [r.dict() for r in recommendations]
                }
            )
        
        return AIAnalysisResponse(
            analysis=analysis,
            recommendations=recommendations,
            confidence=0.92,
            metadata={
                'detected_mood': mood,
                'detected_occasion': occasion,
                'weather_context': weather_context,
                'location_context': location_context,
                'time_context': time_context
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
