from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def analyze_personality(request: MultiModalRequest):
    try:
        personality = analyze_personality_traits(request.text or "")
        
        if request.options and request.options.get('personality'):
            personality = request.options['personality']
        
        recommendations = await get_perfume_recommendations(limit=3)
        
        result = f"""خريطة الشخصية العطرية:

نوع الشخصية: {personality}

الخصائص:
• شخصية قوية ومؤثرة
• يحب التميز والظهور
• واثق من نفسه
• يقدر الجودة والفخامة

العطور المناسبة لشخصيتك:
- العطور الخشبية القوية
- الروائح الفاخرة والمميزة
- العطور ذات الحضور القوي

أمثلة:
• عود الملوك الفاخر
• العنبر الإمبراطوري
• الصندل الملكي

الوصف الشخصي: {request.text or 'تحليل تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.90,
            recommendations=["عود الملوك الفاخر", "العنبر الإمبراطوري", "الصندل الملكي"],
            perfume_suggestions=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_personality_traits(text: str) -> str:
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['قائد', 'قوي', 'مؤثر', 'واثق']):
        return 'القائد الواثق'
    elif any(word in text_lower for word in ['رومانسي', 'حب', 'عاطفي']):
        return 'الرومانسي الحالم'
    elif any(word in text_lower for word in ['عصري', 'حديث', 'موضة']):
        return 'العصري المبدع'
    elif any(word in text_lower for word in ['هادئ', 'مسالم', 'بسيط']):
        return 'الهادئ المتوازن'
    
    return 'القائد الواثق'