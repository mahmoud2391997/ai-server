from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def match_style(request: MultiModalRequest):
    try:
        style = None
        
        if request.text:
            style = extract_style(request.text)
        
        if request.image_data:
            style = await analyze_style_image(request.image_data)
        
        if request.options and request.options.get('style'):
            style = request.options['style']
        
        style = style or 'كلاسيكي'
        
        recommendations = await get_perfume_recommendations(limit=3)
        
        result = f"""تحليل الأسلوب: {style}

العطور المتناسقة مع أسلوبك:
• العطور الخشبية الفاخرة
• الروائح الكلاسيكية الخالدة
• العطور ذات الطابع الرسمي

توصيات محددة:
- عود كمبودي فاخر
- صندل هندي أصيل
- عنبر ملكي

الأسلوب الموصوف: {request.text or 'تم تحليله من الصورة'}"""
        
        return AIResponse(
            result=result,
            confidence=0.85,
            recommendations=["عود كمبودي فاخر", "صندل هندي أصيل", "عنبر ملكي"],
            perfume_suggestions=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_style(text: str) -> str:
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['كلاسيكي', 'رسمي', 'أنيق']):
        return 'كلاسيكي'
    elif any(word in text_lower for word in ['عصري', 'حديث', 'موضة']):
        return 'عصري'
    elif any(word in text_lower for word in ['رياضي', 'كاجوال', 'مريح']):
        return 'رياضي'
    
    return 'كلاسيكي'

async def analyze_style_image(image_data: str) -> str:
    # Placeholder for image style analysis
    return 'كلاسيكي'