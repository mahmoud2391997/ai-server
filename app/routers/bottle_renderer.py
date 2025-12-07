from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse

router = APIRouter()

@router.post("/render", response_model=AIResponse)
async def render_bottle(request: MultiModalRequest):
    try:
        design_specs = extract_design_specs(request.text or "")
        
        if request.options:
            design_specs.update(request.options)
        
        result = f"""تصميم الزجاجة المولد:

📦 مواصفات الزجاجة:
• الشكل: {design_specs.get('shape', 'مربع أنيق بزوايا مدورة')}
• اللون: {design_specs.get('color', 'ذهبي متدرج إلى أسود')}
• الحجم: {design_specs.get('size', '100 مل')}
• الغطاء: {design_specs.get('cap', 'ذهبي لامع مع نقوش عربية')}
• الملمس: {design_specs.get('texture', 'زجاج مصقول مع تأثير معدني')}

🎨 التفاصيل الإضافية:
- شعار منقوش بالليزر
- قاعدة ثقيلة للثبات
- عنق طويل أنيق
- رش ناعم ومتساوي

📋 العبوة الخارجية:
- علبة كرتونية فاخرة
- لون أسود مع تفاصيل ذهبية
- مبطنة بالحرير الأبيض

[سيتم إنشاء صورة ثلاثية الأبعاد للتصميم]

الوصف المدخل: {request.text or 'تصميم تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.92,
            recommendations=["تصميم ثلاثي الأبعاد", "عبوة فاخرة", "تفاصيل ذهبية"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_design_specs(text: str) -> dict:
    specs = {
        'shape': 'مربع أنيق بزوايا مدورة',
        'color': 'ذهبي متدرج إلى أسود',
        'size': '100 مل',
        'cap': 'ذهبي لامع مع نقوش عربية',
        'texture': 'زجاج مصقول مع تأثير معدني'
    }
    
    text_lower = text.lower()
    
    if "دائري" in text_lower:
        specs['shape'] = 'دائري أنيق'
    elif "مستطيل" in text_lower:
        specs['shape'] = 'مستطيل عصري'
    
    if "أزرق" in text_lower:
        specs['color'] = 'أزرق ملكي متدرج'
    elif "أحمر" in text_lower:
        specs['color'] = 'أحمر ياقوتي'
    elif "أخضر" in text_lower:
        specs['color'] = 'أخضر زمردي'
    
    if "50" in text_lower:
        specs['size'] = '50 مل'
    elif "75" in text_lower:
        specs['size'] = '75 مل'
    elif "150" in text_lower:
        specs['size'] = '150 مل'
    
    return specs