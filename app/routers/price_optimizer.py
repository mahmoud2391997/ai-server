from fastapi import APIRouter, HTTPException
from app.models.schemas import MultiModalRequest, AIResponse
from app.services.database import get_perfumes_with_ai_attributes

router = APIRouter()

@router.post("/optimize", response_model=AIResponse)
async def optimize_price(request: MultiModalRequest):
    try:
        product_name = extract_product_name(request.text or "عود الملكي الفاخر")
        current_price = 450
        
        if request.options:
            product_name = request.options.get('product', product_name)
            current_price = request.options.get('current_price', current_price)
        
        # Get market data (simplified)
        market_analysis = analyze_market(product_name, current_price)
        
        result = f"""تحليل موازن الأسعار:

📊 العطر: {product_name}

السعر الحالي: {current_price} ريال
السعر المقترح: {market_analysis['suggested_price']} ريال ({market_analysis['change_percent']})

📈 تحليل السوق:
• الطلب: {market_analysis['demand']}
• المخزون: {market_analysis['inventory']}
• الموسم: {market_analysis['season']}
• المنافسة: سعر متوسط {market_analysis['competitor_avg']} ريال

🎯 التوصيات:
1. {market_analysis['recommendation_1']}
2. {market_analysis['recommendation_2']}
3. {market_analysis['recommendation_3']}

⏰ أفضل وقت للتطبيق: خلال 48 ساعة
🔄 مراجعة الأسعار: كل أسبوع

المنتج المحلل: {request.text or 'تحليل تلقائي'}"""
        
        return AIResponse(
            result=result,
            confidence=0.89,
            recommendations=["خفض السعر 5.5%", "مراجعة أسبوعية", "مراقبة المنافسين"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_product_name(text: str) -> str:
    if "عود" in text.lower():
        return "عود الملكي الفاخر"
    elif "ورد" in text.lower():
        return "ورد الطائف الأصيل"
    
    return "عود الملكي الفاخر"

def analyze_market(product_name: str, current_price: float) -> dict:
    # Simplified market analysis
    suggested_price = current_price * 0.945  # 5.5% reduction
    change_percent = f"-{((current_price - suggested_price) / current_price * 100):.1f}%"
    
    return {
        'suggested_price': int(suggested_price),
        'change_percent': change_percent,
        'demand': 'مرتفع (85%)',
        'inventory': 'متوسط (60%)',
        'season': 'ذروة (شتاء)',
        'competitor_avg': current_price - 10,
        'recommendation_1': f'خفض السعر {int(current_price - suggested_price)} ريال لزيادة المبيعات',
        'recommendation_2': 'متوقع زيادة المبيعات بنسبة 15%',
        'recommendation_3': 'الربح المتوقع: +8% رغم انخفاض السعر'
    }