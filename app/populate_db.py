
import asyncio
from supabase import create_client, Client
import os

# --- Database Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xroixqfaaqelcitaubfx.supabase.co")
# Important: Replace with your REAL Supabase service role key
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "<YOUR_REAL_SUPABASE_SERVICE_ROLE_KEY>")

# --- Perfume Test Data (All Arabic) ---
perfumes = [
    {"perfume_id": "p001", "name": "العنبر الدافئ", "brand": "متجر الدرعي للعطور", "gender": "للجنسين", "concentration": "EDP", "price": 150, "ml_size": 100, "description_llm": "عطر دافئ وجذاب من العنبر يناسب الأمسيات الخاصة."},
    {"perfume_id": "p002", "name": "انتعاش الحمضيات", "brand": "روائح من الخليج", "gender": "رجالي", "concentration": "EDT", "price": 80, "ml_size": 75, "description_llm": "رائحة حمضيات منعشة وحيوية للارتداء اليومي."},
    {"perfume_id": "p003", "name": "بتلة الورد", "brand": "البيت العطري", "gender": "نسائي", "concentration": "Parfum", "price": 250, "ml_size": 50, "description_llm": "عطر ورد أنيق ورومانسي للمناسبات الخاصة."},
    {"perfume_id": "p004", "name": "نسيم المحيط", "brand": "روائح من الخليج", "gender": "للجنسين", "concentration": "EDC", "price": 60, "ml_size": 125, "description_llm": "عطر مائي خفيف ومثالي لأيام الصيف الحارة."},
    {"perfume_id": "p005", "name": "العود المتبل", "brand": "كنوز العود", "gender": "رجالي", "concentration": "EDP", "price": 200, "ml_size": 100, "description_llm": "مزيج غني ومعقد من العود والتوابل الشرقية."},
    {"perfume_id": "p006", "name": "الفانيليا الحلوة", "brand": "البيت العطري", "gender": "نسائي", "concentration": "EDT", "price": 95, "ml_size": 100, "description_llm": "عطر فانيليا حلو ومريح يبعث على الدفء."},
    {"perfume_id": "p007", "name": "الجلد العصري", "brand": "متجر الدرعي للعطور", "gender": "رجالي", "concentration": "EDP", "price": 180, "ml_size": 90, "description_llm": "رائحة جلدية متطورة للرجل العصري والأنيق."},
    {"perfume_id": "p008", "name": "حلم الغاردينيا", "brand": "البيت العطري", "gender": "نسائي", "concentration": "Parfum", "price": 280, "ml_size": 50, "description_llm": "عطر غاردينيا فاخر ومترف للمرأة الجذابة."},
    {"perfume_id": "p009", "name": "ليالي عربية", "brand": "كنوز العود", "gender": "للجنسين", "concentration": "EDP", "price": 220, "ml_size": 100, "description_llm": "عطر شرقي غامض يجمع بين البخور والمسك."},
    {"perfume_id": "p010", "name": "همسة الصحراء", "brand": "روائح من الخليج", "gender": "للجنسين", "concentration": "EDT", "price": 110, "ml_size": 80, "description_llm": "عطر ترابي خشبي مستوحى من هدوء الصحراء."},
    {"perfume_id": "p011", "name": "حديقة الياسمين", "brand": "البيت العطري", "gender": "نسائي", "concentration": "EDP", "price": 160, "ml_size": 90, "description_llm": "رائحة ياسمين ناعمة وأنثوية تشعرك بالهدوء."},
    {"perfume_id": "p012", "name": "مسك أبيض", "brand": "متجر الدرعي للعطور", "gender": "للجنسين", "concentration": "Parfum", "price": 300, "ml_size": 50, "description_llm": "مسك أبيض نقي وفاخر يمنحك شعوراً بالنظافة."}
]

# --- AI Attributes Test Data (All Arabic) ---
ai_attributes = [
    {"perfume_id": "p001", "mood_tag": "واثق", "occasion_tag": "عمل", "style_tag": "كلاسيكي", "longevity_score": 85, "sillage_score": 70, "skin_compatibility": "عادية, جافة"},
    {"perfume_id": "p002", "mood_tag": "نشيط", "occasion_tag": "يومي", "style_tag": "رياضي", "longevity_score": 60, "sillage_score": 75, "skin_compatibility": "دهنية, عادية"},
    {"perfume_id": "p003", "mood_tag": "رومانسي", "occasion_tag": "موعد", "style_tag": "فاخر", "longevity_score": 90, "sillage_score": 80, "skin_compatibility": "جميع الأنواع"},
    {"perfume_id": "p004", "mood_tag": "هادئ", "occasion_tag": "يومي", "style_tag": "عصري", "longevity_score": 50, "sillage_score": 60, "skin_compatibility": "حساسة, دهنية"},
    {"perfume_id": "p005", "mood_tag": "واثق", "occasion_tag": "حفلة", "style_tag": "فاخر", "longevity_score": 95, "sillage_score": 90, "skin_compatibility": "عادية, جافة"},
    {"perfume_id": "p006", "mood_tag": "سعيد", "occasion_tag": "يومي", "style_tag": "كلاسيكي", "longevity_score": 70, "sillage_score": 65, "skin_compatibility": "جميع الأنواع"},
    {"perfume_id": "p007", "mood_tag": "واثق", "occasion_tag": "عمل", "style_tag": "عصري", "longevity_score": 88, "sillage_score": 78, "skin_compatibility": "عادية, دهنية"},
    {"perfume_id": "p008", "mood_tag": "رومانسي", "occasion_tag": "زفاف", "style_tag": "فاخر", "longevity_score": 92, "sillage_score": 85, "skin_compatibility": "حساسة, جافة"},
    {"perfume_id": "p009", "mood_tag": "غامض", "occasion_tag": "أمسية", "style_tag": "شرقي", "longevity_score": 93, "sillage_score": 88, "skin_compatibility": "عادية, جافة"},
    {"perfume_id": "p010", "mood_tag": "هادئ", "occasion_tag": "استرخاء", "style_tag": "طبيعي", "longevity_score": 75, "sillage_score": 65, "skin_compatibility": "جميع الأنواع"},
    {"perfume_id": "p011", "mood_tag": "سعيد", "occasion_tag": "يومي", "style_tag": "أنثوي", "longevity_score": 80, "sillage_score": 70, "skin_compatibility": "عادية, حساسة"},
    {"perfume_id": "p012", "mood_tag": "نظيف", "occasion_tag": "رسمي", "style_tag": "أنيق", "longevity_score": 95, "sillage_score": 90, "skin_compatibility": "جميع الأنواع"}
]

# --- Main function to populate the database ---
async def populate_database():
    """Connects to Supabase and populates the perfumes and ai_attributes tables."""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Starting database population with Arabic data...")

    # Upsert Perfumes
    print(f"Upserting {len(perfumes)} perfumes...")
    perfume_response = supabase.table("perfumes").upsert(perfumes, on_conflict="perfume_id").execute()
    if perfume_response.data:
        print("Perfumes upserted successfully.")
    else:
        print(f"Error upserting perfumes: {perfume_response}")

    # Upsert AI Attributes
    print(f"Upserting {len(ai_attributes)} AI attributes...")
    ai_attributes_response = supabase.table("ai_attributes").upsert(ai_attributes, on_conflict="perfume_id").execute()
    if ai_attributes_response.data:
        print("AI attributes upserted successfully.")
    else:
        print(f"Error upserting AI attributes: {ai_attributes_response}")

    print("Database population complete.")

# --- Run the population script ---
if __name__ == "__main__":
    asyncio.run(populate_database())
