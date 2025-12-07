#!/usr/bin/env python3
import asyncio
from app.services.database import supabase
import uuid

async def populate_sample_data():
    """Populate database with sample perfume data"""
    
    # Sample perfumes data
    perfumes_data = [
        {
            "name": "عطر الحمضيات المنعش",
            "brand": "أورا",
            "gender": "Unisex",
            "concentration": "EDT",
            "price": 299.00,
            "ml_size": 100,
            "description_llm": "عطر منعش مثالي للصيف والأجواء الحارة"
        },
        {
            "name": "عطر النعناع والليمون",
            "brand": "أورا",
            "gender": "Unisex", 
            "concentration": "EDT",
            "price": 249.00,
            "ml_size": 100,
            "description_llm": "يعطي إحساس بالنشاط والحيوية"
        },
        {
            "name": "عطر الأكوا المارين",
            "brand": "أورا",
            "gender": "Male",
            "concentration": "EDT", 
            "price": 199.00,
            "ml_size": 100,
            "description_llm": "رائحة بحرية منعشة تناسب الطقس المعتدل"
        },
        {
            "name": "عود الملكي الفاخر",
            "brand": "أورا",
            "gender": "Unisex",
            "concentration": "EDP",
            "price": 450.00,
            "ml_size": 100,
            "description_llm": "عطر شرقي فاخر بنفحات العود الأصيل"
        },
        {
            "name": "ورد الطائف الأصيل",
            "brand": "أورا", 
            "gender": "Female",
            "concentration": "EDP",
            "price": 350.00,
            "ml_size": 100,
            "description_llm": "عطر نسائي راقي برائحة الورد الطائفي"
        }
    ]
    
    try:
        # Insert perfumes
        result = supabase.from_('perfumes').insert(perfumes_data).execute()
        perfume_ids = [item['perfume_id'] for item in result.data]
        
        # Sample AI attributes for each perfume
        ai_attributes_data = [
            {
                "perfume_id": perfume_ids[0],
                "mood_tag": "نشيط",
                "occasion_tag": "يومي",
                "style_tag": "عصري",
                "longevity_score": 6,
                "sillage_score": 7,
                "skin_compatibility": "جميع أنواع البشرة"
            },
            {
                "perfume_id": perfume_ids[1], 
                "mood_tag": "نشيط",
                "occasion_tag": "يومي",
                "style_tag": "رياضي",
                "longevity_score": 5,
                "sillage_score": 6,
                "skin_compatibility": "البشرة الدهنية"
            },
            {
                "perfume_id": perfume_ids[2],
                "mood_tag": "هادئ",
                "occasion_tag": "عمل", 
                "style_tag": "كلاسيكي",
                "longevity_score": 7,
                "sillage_score": 6,
                "skin_compatibility": "جميع أنواع البشرة"
            },
            {
                "perfume_id": perfume_ids[3],
                "mood_tag": "واثق",
                "occasion_tag": "حفلة",
                "style_tag": "فاخر",
                "longevity_score": 9,
                "sillage_score": 9,
                "skin_compatibility": "البشرة الجافة"
            },
            {
                "perfume_id": perfume_ids[4],
                "mood_tag": "رومانسي", 
                "occasion_tag": "موعد",
                "style_tag": "أنثوي",
                "longevity_score": 8,
                "sillage_score": 7,
                "skin_compatibility": "جميع أنواع البشرة"
            }
        ]
        
        # Insert AI attributes
        supabase.from_('ai_attributes').insert(ai_attributes_data).execute()
        
        print("✅ Database populated successfully!")
        print(f"Added {len(perfumes_data)} perfumes with AI attributes")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")

if __name__ == "__main__":
    asyncio.run(populate_sample_data())