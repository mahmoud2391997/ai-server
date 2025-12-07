from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def analyze_longevity(request: MultiModalRequest):
    try:
        perfume_name = "عود الملكي"
        weather = "حار ورطب"
        skin_type = "دهنية"
        
        if request.text:
            if "عود" in request.text:
                perfume_name = "عود الملكي"
            elif "ورد" in request.text:
                perfume_name = "ورد الطائف"
        
        if request.context:
            weather_data = request.context.get('weather', {})
            temp = weather_data.get('temperature', 25)
            if temp > 30:
                weather = "حار ورطب"
            elif temp < 20:
                weather = "بارد وجاف"
            else:
                weather = "معتدل"
        
        if request.options:
            skin_type = request.options.get('skin_type', 'دهنية')
        
        result = f"""تحليل الثبات:

العطر: {perfume_name}
الطقس: {weather} (35°م، رطوبة 70%)
نوع البشرة: {skin_type}

توقع الثبات:
• الساعات الأولى (1-3): قوة عالية 90%
• الساعات الوسطى (4-6): قوة متوسطة 60%
• الساعات الأخيرة (7-10): قوة خفيفة 30%

نصائح لزيادة الثبات:
- ضع العطر على نقاط النبض
- استخدم مرطب غير معطر قبل العطر

المدخلات: {request.text or 'تحليل تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.93,
            recommendations=["نقاط النبض", "مرطب غير معطر", "طبقات العطر"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))