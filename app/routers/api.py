
import os
import json
import logging
import random
from typing import Optional, Any, Dict, List
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
# import google.generativeai as genai
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
# if not os.getenv('GEMINI_API_KEY'):
#     logger.error("FATAL: GEMINI_API_KEY environment variable is not set.")
# else:
#     genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Configure Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

router = APIRouter()

# model = genai.GenerativeModel('gemini-1.5-flash')
feature_prompts = {
    'default': lambda text, context=None: f'You are a perfume expert. Analyze the following query and generate a brief, friendly analysis followed by a JSON object of search terms for a perfume database. The user\'s query is: "{text}"',
    'ai-nose': lambda text, context=None: f'''You are AI Nose™, a master perfumer. A user is looking for a scent. Their query is: "{text}". 
   The current weather is: {context.get("weather", {}).get("description", "not available") if context else "not available"}.
   Analyze their request in context and generate a brief, elegant analysis. Then, create a JSON object with ideal search keywords based on ingredients, mood, and style.''',
    'mood-advisor': lambda text, context=None: f'''You are a mood and scent psychologist. A user has described their mood: "{text}". 
   Analyze their mood and suggest the types of scents that would complement or enhance it. 
   Then, generate a JSON object with specific 'mood_tag' keywords to search for.''',
    'skin-analyzer': lambda text, context=None: f'''You are a skin and perfume longevity expert. A user has provided an image of their skin and this description: "{text}".
   Analyze the image and text to determine the skin type (e.g., oily, dry, normal). 
   Explain how this skin type affects perfume longevity and recommend the best perfume characteristics (e.g., 'citrus', 'woody', 'light', 'long-lasting').
   Finally, generate a JSON object with search keywords for ingredients and styles suitable for this skin type.''',
    'occasion-detector': lambda text, context=None: f'''You are an event planning and etiquette expert specializing in fragrances. A user is planning for an occasion: "{text}".
   Analyze the occasion and suggest the most appropriate fragrance profile. 
   Then, create a JSON object with 'occasion_tag' and 'style_tag' keywords for the search.''',
    'style-matcher': lambda text, context=None: f'''You are a fashion and fragrance stylist. A user has described their clothing style: "{text}".
   Analyze the style and recommend a congruent scent family. 
   Then, generate a JSON object with 'style_tag' keywords that match this fashion identity.''',
    'personality-map': lambda text, context=None: f'''You are a personality profiler who uses scent to define character. A user describes themselves as: "{text}".
   Create a short, insightful personality analysis based on their words. 
   Then, generate a JSON object with 'mood_tag' and 'style_tag' keywords that reflect this personality.''',
    'gift-selector': lambda text, context=None: f'''You are a thoughtful gift-giving assistant. A user wants to buy a perfume for someone. Their request is: "{text}".
   Analyze the relationship, recipient, and occasion to suggest the perfect scent profile for the gift. 
   Then, generate a JSON object with appropriate search keywords.''',
}
json_schema = {
    "type": "object",
    "properties": {
        "analysis": {
            "type": "string",
            "description": "A brief, user-facing text that explains the reasoning for the perfume recommendations."
        },
        "searchKeywords": {
            "type": "object",
            "properties": {
                "moods": {"type": "array", "items": {"type": "string"}},
                "styles": {"type": "array", "items": {"type": "string"}},
                "occasions": {"type": "array", "items": {"type": "string"}},
                "ingredients": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["moods", "styles", "occasions", "ingredients"]
        }
    },
    "required": ["analysis", "searchKeywords"]
}
perfume_search_features = {
    'ai-nose', 'mood-advisor', 'skin-analyzer', 'occasion-detector', 
    'style-matcher', 'personality-map', 'gift-selector'
}

async def get_analysis_and_keywords(feature: str, text: Optional[str] = None, image_base64: Optional[str] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
    prompt_builder = feature_prompts.get(feature, feature_prompts['default'])
    prompt = f"{prompt_builder(text, context)}\n\n  IMPORTANT: Respond with ONLY a valid JSON object adhering to the following schema. Do not use markdown.\n  Schema: {json.dumps(json_schema)}\n  "

    content_parts = [prompt]
    if feature == 'skin-analyzer' and image_base64:
        content_parts.append({
            "mime_type": "image/jpeg",
            "data": image_base64
        })

    # response = model.generate_content(content_parts)
    # raw_text = response.text
    raw_text = '{"analysis": "This is a test analysis", "searchKeywords": {"moods": [], "styles": [], "occasions": [], "ingredients": []}}'
    json_string = raw_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"AI JSON Parsing Error: {e}")
        logger.error(f"Raw AI Response: {raw_text}")
        raise ValueError(f"Failed to parse a valid response from the AI. Raw output: {raw_text}")

async def search_perfumes_in_db(keywords: Dict[str, List[str]]) -> List[Dict]:
    params = {
        "primary_moods": [f"%{k}%" for k in keywords.get("moods", [])],
        "primary_styles": [f"%{k}%" for k in keywords.get("styles", [])],
        "primary_occasions": [f"%{k}%" for k in keywords.get("occasions", [])],
        "primary_ingredients": [f"%{k}%" for k in keywords.get("ingredients", [])],
        "fallback_moods": [],
        "fallback_styles": [],
        "fallback_occasions": [],
        "fallback_ingredients": [],
    }

    result = supabase.rpc('search_perfumes', params).execute()
    return result.data if result.data else []

class PerfumeSearchRequest(BaseModel):
    feature: str
    text: Optional[str] = None
    image_data: Optional[str] = None
    context: Optional[Dict] = None

@router.post("/perfume-search")
async def perfume_search(request: PerfumeSearchRequest):
    # if not os.getenv('GEMINI_API_KEY'):
    #     raise HTTPException(status_code=500, detail="Server is missing AI configuration: GEMINI_API_KEY is not set.")

    try:
        if request.feature in perfume_search_features:
            if not request.text and not request.image_data:
                raise HTTPException(status_code=400, detail="Text or image input is required for this feature.")

            analysis_data = await get_analysis_and_keywords(request.feature, request.text, request.image_data, request.context)
            analysis = analysis_data.get("analysis")
            search_keywords = analysis_data.get("searchKeywords")
            
            perfumes = await search_perfumes_in_db(search_keywords)

            if not perfumes:
                return {
                    "analysis": f"{analysis}\n\nUnfortunately, we couldn't find any perfumes that perfectly match these criteria right now.",
                    "recommendations": []
                }

            recommendations = [
                {
                    **p,
                    "reason": "An excellent match based on your query.",
                    "compatibility_score": random.randint(85, 98),
                }
                for p in perfumes
            ]

            return {"analysis": analysis, "recommendations": recommendations}

        raise HTTPException(status_code=404, detail=f"Feature '{request.feature}' is not implemented.")

    except ValueError as e:
        logger.error(f"Error in AI API route: {e}")
        raise HTTPException(status_code=500, detail=f"Server error during AI processing: {str(e)}")
    except Exception as e:
        logger.error(f"Error in AI API route: {e}")
        raise HTTPException(status_code=500, detail="Server error during AI processing.")
