import os
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from app.models.schemas import PerfumeData, PerfumeRecommendation

# Supabase configuration - use environment variables if available, otherwise fall back to defaults
SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://xroixqfaaqelcitaubfx.supabase.co"
)
SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhyb2l4cWZhYXFlbGNpdGF1YmZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQzMjk5ODQsImV4cCI6MjA3OTkwNTk4NH0.h_DYktyQrOiXSMl0TYqrgW6BtmxL4Fj2t64FHB6nB9w"
)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_perfumes_with_ai_attributes(filters: Optional[Dict[str, Any]] = None) -> List[PerfumeData]:
    """Get perfumes with AI attributes from database"""
    try:
        # Build the query to join perfumes with ai_attributes
        query = supabase.from_('perfumes').select(
            'perfume_id, name, brand, gender, concentration, price, ml_size, description_llm, '
            'ai_attributes(mood_tag, occasion_tag, style_tag, longevity_score, sillage_score, skin_compatibility)'
        )
        
        # Apply filters if provided
        if filters:
            if filters.get('mood_tag'):
                query = query.eq('ai_attributes.mood_tag', filters['mood_tag'])
            if filters.get('occasion_tag'):
                query = query.eq('ai_attributes.occasion_tag', filters['occasion_tag'])
            if filters.get('skin_compatibility'):
                query = query.ilike('ai_attributes.skin_compatibility', f"%{filters['skin_compatibility']}%")
            if filters.get('gender'):
                query = query.eq('gender', filters['gender'])
        
        result = query.execute()
        print(f"Database query result: {result.data}")
        
        perfumes = []
        for item in result.data:
            if item.get('ai_attributes'):
                ai_attr = item['ai_attributes']
                perfume = PerfumeData(
                    perfume_id=str(item['perfume_id']),
                    name=item['name'],
                    brand=item['brand'],
                    gender=item['gender'],
                    concentration=item['concentration'],
                    price=float(item['price']),
                    mood_tag=ai_attr['mood_tag'],
                    occasion_tag=ai_attr['occasion_tag'],
                    style_tag=ai_attr['style_tag'],
                    longevity_score=ai_attr['longevity_score'],
                    sillage_score=ai_attr['sillage_score'],
                    skin_compatibility=ai_attr['skin_compatibility'],
                    ingredients=[]
                )
                perfumes.append(perfume)
        
        return perfumes
    except Exception as e:
        print(f"Database error: {e}")
        return []

async def get_customer_profile(customer_id: str) -> Optional[Dict[str, Any]]:
    """Get customer profile from database"""
    try:
        result = supabase.from_('customers').select('*').eq('customer_id', customer_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None

async def save_ai_interaction(customer_id: str, feature: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
    """Save AI interaction for learning purposes"""
    try:
        interaction = {
            'customer_id': customer_id,
            'feature': feature,
            'input_data': input_data,
            'output_data': output_data,
            'created_at': 'now()'
        }
        # This would require an ai_interactions table
        # supabase.from_('ai_interactions').insert(interaction).execute()
        pass
    except Exception as e:
        print(f"Database error: {e}")

async def get_perfume_recommendations(
    mood: Optional[str] = None,
    occasion: Optional[str] = None,
    skin_type: Optional[str] = None,
    gender: Optional[str] = None,
    limit: int = 3
) -> List[PerfumeRecommendation]:
    """Get perfume recommendations based on criteria"""
    filters = {}
    
    # Map user input to database tags
    if mood:
        filters['mood_tag'] = mood
    if occasion:
        filters['occasion_tag'] = occasion
    if skin_type:
        filters['skin_compatibility'] = skin_type
    if gender:
        filters['gender'] = gender
    
    print(f"Searching with filters: {filters}")
    
    # Get perfumes from database
    perfumes = await get_perfumes_with_ai_attributes(filters)
    print(f"Found {len(perfumes)} perfumes")
    
    # If no exact matches, get all perfumes and score them
    if not perfumes:
        perfumes = await get_perfumes_with_ai_attributes()
        print(f"Fallback: Found {len(perfumes)} total perfumes")
    
    recommendations = []
    for i, perfume in enumerate(perfumes[:limit]):
        # Calculate compatibility score based on matches
        score = 95 - (i * 7)  # Decrease score for each position
        
        # Build reason based on what matched
        reason_parts = []
        if mood and perfume.mood_tag == mood:
            reason_parts.append(f"يناسب مزاجك {mood}")
        if occasion and perfume.occasion_tag == occasion:
            reason_parts.append(f"مثالي لـ{occasion}")
        
        reason = " و ".join(reason_parts) if reason_parts else f"يناسب تفضيلاتك العامة"
        
        rec = PerfumeRecommendation(
            perfume_id=perfume.perfume_id,
            name=perfume.name,
            brand=perfume.brand,
            compatibility_score=score,
            reason=reason,
            price=perfume.price,
            mood_tag=perfume.mood_tag,
            occasion_tag=perfume.occasion_tag,
            style_tag=perfume.style_tag,
            longevity_score=perfume.longevity_score,
            sillage_score=perfume.sillage_score,
            skin_compatibility=perfume.skin_compatibility
        )
        recommendations.append(rec)
    
    print(f"Returning {len(recommendations)} recommendations")
    return recommendations