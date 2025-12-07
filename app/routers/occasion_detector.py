from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def detect_occasion(request: MultiModalRequest):
    try:
        occasion = None
        
        if request.text:
            occasion = extract_occasion(request.text)
        
        if request.options and request.options.get('occasion'):
            occasion = request.options['occasion']
        
        occasion = occasion or 'عام'
        
        recommendations = await get_perfume_recommendations(occasion=occasion, limit=3)
        
        result = f"""المناسبة المكتشفة: {occasion}

العطور المقترحة:
• عطور كلاسيكية وأنيقة
• روائح خفيفة غير مزعجة
• تجنب العطور القوية أو الحلوة

أمثلة مناسبة:
- الخشب الأبيض
- اللافندر الهادئ
- الأكوا الكلاسيكي

المناسبة المذكورة: {request.text or 'غير محددة'}"""
        
        return AIResponse(
            result=result,
            confidence=0.89,
            recommendations=["الخشب الأبيض", "اللافندر الهادئ", "الأكوا الكلاسيكي"],
            perfume_suggestions=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_occasion(text: str) -> str:
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['عمل', 'مكتب', 'اجتماع']):
        return 'عمل'
    elif any(word in text_lower for word in ['حفلة', 'احتفال', 'عيد']):
        return 'حفلة'
    elif any(word in text_lower for word in ['زفاف', 'عرس']):
        return 'زفاف'
    elif any(word in text_lower for word in ['موعد', 'لقاء']):
        return 'موعد'
    
    return 'عام'