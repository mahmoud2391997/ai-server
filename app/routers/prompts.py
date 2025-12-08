from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional

router = APIRouter()

# Simple in-memory prompt catalog keyed by feature name
PROMPTS: Dict[str, List[str]] = {
    "ai-nose": [
        "حلل المكونات العطرية واقترح مزيجاً متوازناً.",
        "اعطني تقييم السِياج والثبات لعطر شرقي فاخر."
    ],
    "mood-advisor": [
        "اقترح عطراً يرفع المعنويات في يوم عمل طويل.",
        "ما العطر الأنسب لمزاج هادئ قبل النوم؟"
    ],
    "skin-analyzer": [
        "ما أفضل تركيز لعطر يناسب بشرة دهنية وحساسة؟"
    ],
    "occasion-detector": [
        "اقترح عطراً لحفل مسائي رسمي.",
        "ما العطر الأنسب لاجتماع عمل صباحي؟"
    ],
    "style-matcher": [
        "طابق عطراً مع أسلوب كلاسيكي وألوان محايدة.",
        "ما العطر الأنسب لأسلوب رياضي عصري؟"
    ],
    "longevity-meter": [
        "قدّر مدة الثبات لعطر زهري في طقس حار رطب."
    ],
    "perfume-memory": [
        "أعد صياغة ذكريات عطرية مرتبطة بالورد الدمشقي."
    ],
    "personality-map": [
        "اربط سمات شخصية منفتحة على التجارب بعطور حمضية."
    ],
    "gift-selector": [
        "اختر عطراً هدية لشخص يحب الروائح الخشبية."
    ],
    "description-generator": [
        "أنشئ وصفاً تسويقياً لعطر جلدي فاخر بلمسة فانيلا."
    ],
    "bottle-renderer": [
        "صف تصميم زجاجة عطر مستوحى من الطراز الأندلسي."
    ],
    "price-optimizer": [
        "اقترح تسعيراً ديناميكياً لعطر محدود الإصدار."
    ],
}


@router.get("/prompts")
async def get_prompts(feature: Optional[str] = None):
    """
    Return sample prompts. If feature is provided, return prompts for that feature.
    """
    if feature:
        key = feature.strip()
        if key not in PROMPTS:
            raise HTTPException(status_code=404, detail="Feature not found")
        return {"feature": key, "prompts": PROMPTS[key]}

    # If no feature provided, return catalog
    return {"features": list(PROMPTS.keys()), "prompts": PROMPTS}

