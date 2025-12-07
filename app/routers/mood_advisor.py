from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations
import base64
import io

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def analyze_mood(request: MultiModalRequest):
    try:
        mood = None
        analysis_source = ""
        
        # Process text input
        if request.text:
            mood = analyze_text_mood(request.text)
            analysis_source = f"النص المحلل: {request.text}"
        
        # Process audio input
        if request.audio_data:
            audio_mood = await analyze_audio_mood(request.audio_data)
            if audio_mood:
                mood = audio_mood
                analysis_source = "تحليل الصوت: تم تحليل نبرة الصوت والمشاعر"
        
        # Use options if provided
        if request.options and request.options.get('mood'):
            mood = request.options['mood']
            analysis_source = f"المزاج المحدد: {mood}"
        
        mood = mood or 'متوازن'
        
        # Get perfume recommendations
        recommendations = await get_perfume_recommendations(mood=mood, limit=3)
        
        result = f"""تحليل المزاج: {mood}

العطور المقترحة لتعزيز هذا المزاج:
• الحمضيات المنعشة
• النعناع والأوكالبتوس  
• الجريب فروت والليمون

هذه الروائح ستزيد من طاقتك الإيجابية وتحافظ على نشاطك طوال اليوم.

{analysis_source}"""
        
        return AIResponse(
            result=result,
            confidence=0.87,
            recommendations=["الحمضيات المنعشة", "النعناع والأوكالبتوس", "الجريب فروت والليمون"],
            perfume_suggestions=recommendations,
            metadata={'detected_mood': mood, 'source': analysis_source}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_text_mood(text: str) -> str:
    """Analyze mood from text"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['سعيد', 'فرح', 'مبسوط']):
        return 'سعيد'
    elif any(word in text_lower for word in ['حزين', 'زعلان', 'مكتئب']):
        return 'حزين'
    elif any(word in text_lower for word in ['غضبان', 'زعلان', 'متضايق']):
        return 'غاضب'
    elif any(word in text_lower for word in ['هادئ', 'مسترخي', 'مريح']):
        return 'هادئ'
    elif any(word in text_lower for word in ['متوتر', 'قلقان', 'خايف']):
        return 'متوتر'
    elif any(word in text_lower for word in ['نشيط', 'حيوي', 'متحمس']):
        return 'نشيط'
    
    return 'متوازن'

async def analyze_audio_mood(audio_data: str) -> str:
    """Analyze mood from audio (placeholder for actual implementation)"""
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        
        # Placeholder for actual audio analysis
        # In real implementation, you would:
        # 1. Convert audio to text using speech recognition
        # 2. Analyze tone and emotion from audio features
        # 3. Return detected mood
        
        return 'نشيط'  # Placeholder result
        
    except Exception as e:
        print(f"Audio analysis error: {e}")
        return None