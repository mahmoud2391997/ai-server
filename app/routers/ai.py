import os
import json
import random
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from supabase import create_client, Client

# Initialize FastAPI app
app = FastAPI()

# Initialize Supabase client (set your SUPABASE_URL and SUPABASE_KEY env vars)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check Gemini API key env var
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error("FATAL: GEMINI_API_KEY environment variable is not set.")
    # You can optionally raise an error here or handle gracefully in route

# JSON Schema for validation reference (for documentation, not enforced here)
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

# Prompt templates dictionary
def default_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a perfume expert. Analyze the following query and generate a brief, friendly analysis '
            f'followed by a JSON object of search terms for a perfume database. The user\'s query is: "{text}"')

def ai_nose_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    weather_desc = context.get("weather", {}).get("description") if context else "not available"
    return (f'You are AI Nose™, a master perfumer. A user is looking for a scent. Their query is: "{text}". '
            f'The current weather is: {weather_desc}. '
            'Analyze their request in context and generate a brief, elegant analysis. Then, create a JSON object with ideal search keywords based on ingredients, mood, and style.')

def mood_advisor_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a mood and scent psychologist. A user has described their mood: "{text}". '
            'Analyze their mood and suggest the types of scents that would complement or enhance it. '
            'Then, generate a JSON object with specific \'mood_tag\' keywords to search for.')

def skin_analyzer_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a skin and perfume longevity expert. A user has provided an image of their skin and this description: "{text}". '
            'Analyze the image and text to determine the skin type (e.g., oily, dry, normal). '
            'Explain how this skin type affects perfume longevity and recommend the best perfume characteristics (e.g., \'citrus\', \'woody\', \'light\', \'long-lasting\'). '
            'Finally, generate a JSON object with search keywords for ingredients and styles suitable for this skin type.')

def occasion_detector_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are an event planning and etiquette expert specializing in fragrances. A user is planning for an occasion: "{text}". '
            'Analyze the occasion and suggest the most appropriate fragrance profile. '
            'Then, create a JSON object with \'occasion_tag\' and \'style_tag\' keywords for the search.')

def style_matcher_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a fashion and fragrance stylist. A user has described their clothing style: "{text}". '
            'Analyze the style and recommend a congruent scent family. '
            'Then, generate a JSON object with \'style_tag\' keywords that match this fashion identity.')

def personality_map_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a personality profiler who uses scent to define character. A user describes themselves as: "{text}". '
            'Create a short, insightful personality analysis based on their words. '
            'Then, generate a JSON object with \'mood_tag\' and \'style_tag\' keywords that reflect this personality.')

def gift_selector_prompt(text: Optional[str], context: Optional[Dict[str, Any]] = None) -> str:
    return (f'You are a thoughtful gift-giving assistant. A user wants to buy a perfume for someone. Their request is: "{text}". '
            'Analyze the relationship, recipient, and occasion to suggest the perfect scent profile for the gift. '
            'Then, generate a JSON object with appropriate search keywords.')

feature_prompts = {
    "default": default_prompt,
    "ai-nose": ai_nose_prompt,
    "mood-advisor": mood_advisor_prompt,
    "skin-analyzer": skin_analyzer_prompt,
    "occasion-detector": occasion_detector_prompt,
    "style-matcher": style_matcher_prompt,
    "personality-map": personality_map_prompt,
    "gift-selector": gift_selector_prompt,
}

# Allowed features
PERFUME_SEARCH_FEATURES = {
    "ai-nose", "mood-advisor", "skin-analyzer", "occasion-detector",
    "style-matcher", "personality-map", "gift-selector"
}

# Pydantic models for request and response
class AIRequest(BaseModel):
    feature: str
    text: Optional[str] = None
    image_data: Optional[str] = None  # base64 string
    context: Optional[Dict[str, Any]] = None

# Dummy AI model call simulation (replace with real Gemini AI client integration)
async def generate_ai_content(prompt: str, image_base64: Optional[str] = None) -> str:
    """
    This function should call the Gemini API or other AI service asynchronously,
    sending the prompt and optionally the image data, then return the raw text response.
    Here it is mocked for demonstration.
    """
    # MOCK: For real use, call the Gemini API with prompt and optional image, get response text.
    # Simulate a JSON response as string:
    fake_response = json.dumps({
        "analysis": "This is a simulated analysis based on the prompt.",
        "searchKeywords": {
            "moods": ["calm", "fresh"],
            "styles": ["casual"],
            "occasions": ["daytime"],
            "ingredients": ["citrus", "jasmine"]
        }
    })
    return fake_response

async def get_analysis_and_keywords(feature: str, text: Optional[str], image_base64: Optional[str], context: Optional[Dict[str, Any]]):
    prompt_builder = feature_prompts.get(feature, feature_prompts["default"])
    prompt_text = prompt_builder(text, context)
    prompt = (
        f"{prompt_text}\n\nIMPORTANT: Respond with ONLY a valid JSON object adhering to the following schema. "
        f"Do not use markdown.\nSchema: {json.dumps(json_schema)}\n"
    )

    raw_text = await generate_ai_content(prompt, image_base64)
    # Clean the AI response if needed (e.g., remove markdown codeblocks)
    json_string = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(json_string)
        return parsed["analysis"], parsed["searchKeywords"]
    except Exception as e:
        logging.error("AI JSON Parsing Error: %s", e)
        logging.error("Raw AI Response: %s", raw_text)
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response. Raw output: {raw_text}")

async def search_perfumes_in_db(keywords: Dict[str, Any]):
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
    # Call Supabase RPC function 'search_perfumes' with params
    response = supabase.rpc("search_perfumes", params).execute()
    if response.error:
        logging.error("Supabase error: %s", response.error)
        raise HTTPException(status_code=500, detail="Database query error")
    return response.data

@app.post("/api/perfume-search")
async def perfume_search(req: AIRequest):
    if not GEMINI_API_KEY:
        return JSONResponse(
            status_code=500,
            content={"message": "Server is missing AI configuration: GEMINI_API_KEY is not set."}
        )

    feature = req.feature
    text = req.text
    image_data = req.image_data
    context = req.context

    if feature not in PERFUME_SEARCH_FEATURES:
        return JSONResponse(
            status_code=404,
            content={"message": f"Feature '{feature}' is not implemented."}
        )

    if not text and not image_data:
        return JSONResponse(
            status_code=400,
            content={"message": "Text or image input is required for this feature."}
        )

    analysis, search_keywords = await get_analysis_and_keywords(feature, text, image_data, context)
    perfumes = await search_perfumes_in_db(search_keywords)

    if not perfumes:
        return {
            "analysis": f"{analysis}\n\nUnfortunately, we couldn't find any perfumes that perfectly match these criteria right now.",
            "recommendations": []
        }

    recommendations = []
    for p in perfumes:
        rec = dict(p)
        rec["reason"] = "An excellent match based on your query."
        rec["compatibility_score"] = random.randint(85, 98)
        recommendations.append(rec)

    return {
        "analysis": analysis,
        "recommendations": recommendations,
    }