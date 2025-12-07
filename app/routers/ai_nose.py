from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIAnalysisResponse, PerfumeRecommendation
from app.services.database import get_perfume_recommendations, save_ai_interaction
import json
import re

router = APIRouter()

@router.post("/analyze", response_model=AIAnalysisResponse)
async def analyze_ai_nose(request: MultiModalRequest):
    try:
        # Extract context from text and options
        mood = extract_mood(request.text) if request.text else None
        occasion = extract_occasion(request.text) if request.text else None
        
        # Use options if provided
        if request.options:
            mood = request.options.get('mood', mood)
            occasion = request.options.get('occasion', occasion)
            gender = request.options.get('gender')
            skin_type = request.options.get('skin_type')
        
        # Get weather/location context
        weather_context = ""
        if request.context:
            weather = request.context.get('weather')
            if weather:
                weather_context = f"الطقس: {weather.get('description', '')}, درجة الحرارة: {weather.get('temperature', '')}°م"
        
        # Get recommendations from database
        recommendations = await get_perfume_recommendations(
            mood=mood,
            occasion=occasion,
            skin_type=request.options.get('skin_type') if request.options else None,
            gender=request.options.get('gender') if request.options else None,
            limit=3
        )
        
        # Generate analysis text
        analysis = f"""بناءً على تحليل الأنف الإلكتروني AI Nose™:

النص المدخل: {request.text or 'لا يوجد نص'}
{weather_context}

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
                'weather_context': weather_context
            }
        )
        
    except Exception as e:
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