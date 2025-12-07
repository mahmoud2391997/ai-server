from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_customer_profile, get_perfume_recommendations

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def analyze_perfume_memory(request: MultiModalRequest):
    try:
        preferences = []
        patterns = []
        
        # Get customer profile if user_id provided
        if request.user_id:
            profile = await get_customer_profile(request.user_id)
            if profile and profile.get('personality_map'):
                preferences = profile['personality_map'].get('preferences', [])
        
        # Extract preferences from text
        if request.text:
            text_preferences = extract_preferences(request.text)
            preferences.extend(text_preferences)
        
        # Default preferences if none found
        if not preferences:
            preferences = ["العود الكمبودي", "الورد الطائفي", "الياسمين الهندي"]
        
        recommendations = await get_perfume_recommendations(limit=3)
        
        result = f"""تحليل ذاكرة العطر:

العطور المفضلة سابقاً:
• {preferences[0] if len(preferences) > 0 else 'العود الكمبودي'} ⭐⭐⭐⭐⭐
• {preferences[1] if len(preferences) > 1 else 'الورد الطائفي'} ⭐⭐⭐⭐
• {preferences[2] if len(preferences) > 2 else 'الياسمين الهندي'} ⭐⭐⭐

الأنماط المكتشفة:
- تفضيل للروائح الشرقية
- حب للعطور الثقيلة والدافئة
- تجنب الحمضيات القوية

التوصيات الجديدة بناءً على ذاكرتك:
1. عود الهند الأصيل
2. العنبر الأحمر
3. المسك الأبيض

التفضيلات المذكورة: {request.text or 'تحليل الملف الشخصي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.88,
            recommendations=["عود الهند الأصيل", "العنبر الأحمر", "المسك الأبيض"],
            perfume_suggestions=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_preferences(text: str) -> list:
    preferences = []
    text_lower = text.lower()
    
    if "عود" in text_lower:
        preferences.append("العود الكمبودي")
    if "ورد" in text_lower:
        preferences.append("الورد الطائفي")
    if "ياسمين" in text_lower:
        preferences.append("الياسمين الهندي")
    if "عنبر" in text_lower:
        preferences.append("العنبر الذهبي")
    if "مسك" in text_lower:
        preferences.append("المسك الأبيض")
    
    return preferences