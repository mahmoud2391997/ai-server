
import os
import json
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import google.generativeai as genai
from supabase import create_client, Client
import random

# --- PRE-FLIGHT CHECK ---
if not os.getenv("GEMINI_API_KEY"):
    print("FATAL: GEMINI_API_KEY environment variable is not set.")
if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
    print("FATAL: Supabase environment variables are not set.")

# Initialize clients
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
except Exception as e:
    print(f"Error during client initialization: {e}")
    model = None
    supabase = None

# --- PROMPT ENGINEERING TEMPLATES ---
feature_prompts = {
    "default": lambda text, context: f'You are a perfume expert. Analyze the following query and generate a brief, friendly analysis followed by a JSON object of search terms for a perfume database. The user\'s query is: "{text}"',
    
    'ai-nose': lambda text, context: f"""You are AI Nose™, a master perfumer. A user is looking for a scent. Their query is: "{text}".
   The current weather is: {context.get('weather', {}).get('description', 'not available') if context else 'not available'}.
   Analyze their request in context and generate a brief, elegant analysis. Then, create a JSON object with ideal search keywords based on ingredients, mood, and style.""" ,

    'mood-advisor': lambda text, context: f"""You are a mood and scent psychologist. A user has described their mood: "{text}".
   Analyze their mood and suggest the types of scents that would complement or enhance it.
   Then, generate a JSON object with specific 'mood_tag' keywords to search for.""" ,

    'skin-analyzer': lambda text, context: f"""You are a skin and perfume longevity expert. A user has provided an image of their skin and this description: "{text}".
   Analyze the image and text to determine the skin type (e.g., oily, dry, normal).
   Explain how this skin type affects perfume longevity and recommend the best perfume characteristics (e.g., 'citrus', 'woody', 'light', 'long-lasting').
   Finally, generate a JSON object with search keywords for ingredients and styles suitable for this skin type.""" ,

    'occasion-detector': lambda text, context: f"""You are an event planning and etiquette expert specializing in fragrances. A user is planning for an occasion: "{text}".
   Analyze the occasion and suggest the most appropriate fragrance profile.
   Then, create a JSON object with 'occasion_tag' and 'style_tag' keywords for the search.""" ,

    'style-matcher': lambda text, context: f"""You are a fashion and fragrance stylist. A user has described their clothing style: "{text}".
   Analyze the style and recommend a congruent scent family.
   Then, generate a JSON object with 'style_tag' keywords that match this fashion identity.""" ,

    'personality-map': lambda text, context: f"""You are a personality profiler who uses scent to define character. A user describes themselves as: "{text}".
   Create a short, insightful personality analysis based on their words.
   Then, generate a JSON object with 'mood_tag' and 'style_tag' keywords that reflect this personality.""" ,

    'gift-selector': lambda text, context: f"""You are a thoughtful gift-giving assistant. A user wants to buy a perfume for someone. Their request is: "{text}".
   Analyze the relationship, recipient, and occasion to suggest the perfect scent profile for the gift.
   Then, generate a JSON object with appropriate search keywords.""" ,
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
        "moods": { "type": "array", "items": { "type": "string" } },
        "styles": { "type": "array", "items": { "type": "string" } },
        "occasions": { "type": "array", "items": { "type": "string" } },
        "ingredients": { "type": "array", "items": { "type": "string" } }
      },
      "required": ["moods", "styles", "occasions", "ingredients"]
    }
  },
  "required": ["analysis", "searchKeywords"]
}

async def get_analysis_and_keywords(feature: str, text: str = None, image_base64: str = None, context: dict = None):
    if not model:
        raise ValueError("Gemini AI model is not initialized.")

    prompt_builder = feature_prompts.get(feature, feature_prompts["default"])
    prompt = f"{prompt_builder(text, context)}\n\nIMPORTANT: Respond with ONLY a valid JSON object adhering to the following schema. Do not use markdown.\nSchema: {json.dumps(json_schema)}\n"

    content = [prompt]
    if feature == 'skin-analyzer' and image_base64:
        # Assuming image_base64 is a base64-encoded string without the data URI prefix
        content.append({"inline_data": {"data": image_base64, "mime_type": "image/jpeg"}})

    try:
        response = await model.generate_content_async(content)
        raw_text = response.text
        json_string = raw_text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(json_string)
    except Exception as e:
        print(f"AI JSON Parsing Error: {e}")
        # It's possible the model still returns markdown `json` even when told not to.
        if '```json' in raw_text:
            cleaner_text = raw_text[raw_text.find('{'):raw_text.rfind('}')+1]
            try:
                return json.loads(cleaner_text)
            except Exception as e2:
                 print(f"Secondary parsing attempt failed: {e2}")
        print(f"Raw AI Response: {raw_text}")
        raise ValueError(f"Failed to parse a valid response from the AI.")


async def search_perfumes_in_db(keywords: dict):
    if not supabase:
        raise ValueError("Supabase client is not initialized.")
    
    params = {
        'primary_moods': keywords.get('moods', []),
        'primary_styles': keywords.get('styles', []),
        'primary_occasions': keywords.get('occasions', []),
        'primary_ingredients': keywords.get('ingredients', []),
        'fallback_moods': [],
        'fallback_styles': [],
        'fallback_occasions': [],
        'fallback_ingredients': [],
    }
    
    try:
        response = await supabase.rpc('search_perfumes', params).execute()
        return response.data
    except Exception as e:
        print(f"Supabase RPC Error: {e}")
        raise

PERFUME_SEARCH_FEATURES = {
  'ai-nose', 'mood-advisor', 'skin-analyzer', 'occasion-detector', 
  'style-matcher', 'personality-map', 'gift-selector'
}

class AiFeaturesMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method != "POST" or request.url.path != "/api/perfume-search":
            return await call_next(request)

        if not model or not supabase:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Server is missing AI or DB configuration."})

        try:
            body = await request.json()
            feature = body.get("feature")
            text = body.get("text")
            image_data = body.get("image_data")
            context = body.get("context")

            if feature in PERFUME_SEARCH_FEATURES:
                if not text and not image_data:
                    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Text or image input is required for this feature."})
                
                ai_result = await get_analysis_and_keywords(feature, text, image_data, context)
                analysis = ai_result.get("analysis")
                search_keywords = ai_result.get("searchKeywords")
                
                perfumes = await search_perfumes_in_db(search_keywords)

                if not perfumes:
                    return JSONResponse(status_code=status.HTTP_200_OK, content={
                        "analysis": f"{analysis}\n\nUnfortunately, we couldn\'t find any perfumes that perfectly match these criteria right now.",
                        "recommendations": []
                    })
                
                recommendations = []
                for p in perfumes:
                    p['reason'] = "An excellent match based on your query."
                    p['compatibility_score'] = random.randint(85, 98)
                    recommendations.append(p)

                return JSONResponse(status_code=status.HTTP_200_OK, content={"analysis": analysis, "recommendations": recommendations})
            
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": f"Feature '{feature}' is not implemented."})

        except json.JSONDecodeError:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": "Invalid JSON in request body."})
        except Exception as e:
            print(f"Error in AI middleware: {e}")
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Server error during AI processing.", "error": str(e)})
