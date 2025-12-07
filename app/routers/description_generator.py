from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse

router = APIRouter()

@router.post("/generate", response_model=AIResponse)
async def generate_description(request: MultiModalRequest):
    try:
        perfume_name = extract_perfume_name(request.text or "عود الملكي الفاخر")
        ingredients = extract_ingredients(request.text or "")
        
        if request.options:
            perfume_name = request.options.get('name', perfume_name)
            ingredients = request.options.get('ingredients', ingredients)
        
        result = f"""وصف العطر المولد:

🌟 {perfume_name} 🌟

الوصف العربي:
رحلة عطرية ملكية تبدأ بنفحات العود الكمبودي الأصيل، تتوسطها زهور الياسمين الهندي، وتختتم بدفء العنبر والمسك الأبيض. عطر يحكي قصة الفخامة والأصالة.

English Description:
A royal olfactory journey that begins with authentic Cambodian oud, embraced by Indian jasmine flowers, and concludes with the warmth of amber and white musk. A fragrance that tells the story of luxury and authenticity.

المكونات:
• المقدمة: {ingredients.get('top', 'عود كمبودي، هيل')}
• القلب: {ingredients.get('heart', 'ياسمين، ورد طائفي')}
• القاعدة: {ingredients.get('base', 'عنبر، مسك أبيض')}

المدخلات: {request.text or 'وصف تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.96,
            recommendations=["وصف إبداعي", "ترجمة احترافية", "تفاصيل المكونات"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_perfume_name(text: str) -> str:
    # Extract perfume name from text or use default
    if "عود" in text.lower():
        return "عود الملكي الفاخر"
    elif "ورد" in text.lower():
        return "ورد الطائف الأصيل"
    elif "ياسمين" in text.lower():
        return "ياسمين الليل الساحر"
    
    return "عود الملكي الفاخر"

def extract_ingredients(text: str) -> dict:
    ingredients = {
        'top': 'عود كمبودي، هيل',
        'heart': 'ياسمين، ورد طائفي',
        'base': 'عنبر، مسك أبيض'
    }
    
    text_lower = text.lower()
    
    if "حمضيات" in text_lower:
        ingredients['top'] = 'برغموت، ليمون، جريب فروت'
    if "زهور" in text_lower:
        ingredients['heart'] = 'ورد، ياسمين، زنبق'
    if "خشب" in text_lower:
        ingredients['base'] = 'صندل، أرز، عود'
    
    return ingredients