from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def select_gift(request: MultiModalRequest):
    try:
        recipient = "والدتك"
        occasion = "عيد الأم"
        relationship = "أم حبيبة"
        
        if request.text:
            recipient, occasion, relationship = extract_gift_info(request.text)
        
        if request.options:
            recipient = request.options.get('recipient', recipient)
            occasion = request.options.get('occasion', occasion)
            relationship = request.options.get('relationship', relationship)
        
        # Get gender-appropriate recommendations
        gender = 'Female' if any(word in recipient.lower() for word in ['أم', 'زوجة', 'أخت', 'بنت']) else None
        recommendations = await get_perfume_recommendations(gender=gender, limit=2)
        
        result = f"""مستشار الهدايا:

المتلقي: {recipient}
المناسبة: {occasion}
العلاقة: {relationship}

العطور المقترحة:

1. ورد الطائف الأصيل 🌹
   - رائحة كلاسيكية تحبها الأمهات
   - رمز للحب والاحترام
   - ثبات ممتاز

2. الياسمين الملكي 🌸
   - رائحة أنثوية راقية
   - مناسبة للاستخدام اليومي
   - تذكرها بجمال الطبيعة

رسالة مقترحة للهدية:
'إلى أغلى إنسان في حياتي، عطر يليق بجمال روحك وطيبة قلبك'

تفاصيل الهدية: {request.text or 'تحليل تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.94,
            recommendations=["ورد الطائف الأصيل", "الياسمين الملكي", "العود النسائي"],
            perfume_suggestions=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_gift_info(text: str) -> tuple:
    text_lower = text.lower()
    
    recipient = "والدتك"
    occasion = "مناسبة خاصة"
    relationship = "شخص عزيز"
    
    # Extract recipient
    if any(word in text_lower for word in ['أم', 'والدة', 'ماما']):
        recipient = "والدتك"
    elif any(word in text_lower for word in ['زوجة', 'زوجتي']):
        recipient = "زوجتك"
    elif any(word in text_lower for word in ['أخت', 'أختي']):
        recipient = "أختك"
    
    # Extract occasion
    if any(word in text_lower for word in ['عيد الأم', 'يوم الأم']):
        occasion = "عيد الأم"
    elif any(word in text_lower for word in ['عيد ميلاد', 'ميلاد']):
        occasion = "عيد ميلاد"
    elif any(word in text_lower for word in ['زفاف', 'عرس']):
        occasion = "زفاف"
    
    return recipient, occasion, relationship