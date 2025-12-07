from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfume_recommendations
import base64
from PIL import Image
import io

router = APIRouter()

@router.post("/analyze", response_model=AIResponse)
async def analyze_skin(request: MultiModalRequest):
    try:
        skin_type = None
        analysis_source = ""
        
        # Process image input
        if request.image_data:
            skin_type = await analyze_skin_image(request.image_data)
            analysis_source = "تحليل صورة اليد: تم تحليل نوع البشرة من الصورة"
        
        # Process text description
        if request.text:
            text_skin_type = analyze_skin_text(request.text)
            if text_skin_type:
                skin_type = text_skin_type
                analysis_source = f"الوصف المدخل: {request.text}"
        
        # Use options if provided
        if request.options and request.options.get('skin_type'):
            skin_type = request.options['skin_type']
            analysis_source = f"نوع البشرة المحدد: {skin_type}"
        
        skin_type = skin_type or 'دهنية'
        
        # Get perfume recommendations
        recommendations = await get_perfume_recommendations(skin_type=skin_type, limit=3)
        
        result = f"""تحليل البشرة: بشرة {skin_type}

العطور المناسبة:
• العطور الخفيفة والمنعشة
• تركيزات EDT بدلاً من EDP
• تجنب العطور الثقيلة والزيتية

مدة الثبات المتوقعة: 6-8 ساعات
أفضل أوقات الاستخدام: الصباح والظهيرة

{analysis_source}"""
        
        return AIResponse(
            result=result,
            confidence=0.91,
            recommendations=["العطور الخفيفة", "تركيزات EDT", "الروائح المنعشة"],
            perfume_suggestions=recommendations,
            metadata={'detected_skin_type': skin_type, 'source': analysis_source}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def analyze_skin_image(image_data: str) -> str:
    """Analyze skin type from image"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Placeholder for actual image analysis
        # In real implementation, you would:
        # 1. Use CNN model to analyze skin texture
        # 2. Detect oiliness, dryness, etc.
        # 3. Return skin type classification
        
        # Simple placeholder logic based on image properties
        width, height = image.size
        if width > 1000:  # High resolution might indicate detailed skin analysis
            return 'جافة'
        else:
            return 'دهنية'
            
    except Exception as e:
        print(f"Image analysis error: {e}")
        return 'دهنية'

def analyze_skin_text(text: str) -> str:
    """Analyze skin type from text description"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['دهنية', 'زيتية', 'لامعة']):
        return 'دهنية'
    elif any(word in text_lower for word in ['جافة', 'خشنة', 'متشققة']):
        return 'جافة'
    elif any(word in text_lower for word in ['حساسة', 'تتهيج', 'حكة']):
        return 'حساسة'
    elif any(word in text_lower for word in ['مختلطة', 'منطقة دهنية']):
        return 'مختلطة'
    
    return None