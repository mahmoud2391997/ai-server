
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.ai_features import AiFeaturesMiddleware
from app.routers import (
    api,
    ai_nose,
    mood_advisor,
    skin_analyzer,
    occasion_detector,
    style_matcher,
    longevity_meter,
    perfume_memory,
    personality_map,
    gift_selector,
    description_generator,
    bottle_renderer,
    price_optimizer,
    tts,
    weather,
    ai_attributes,
    customers,
    database,
    ingredients,
    order_items,
    orders,
    perfume_ingredients,
    perfumes,
    prompts,
    admin
)

app = FastAPI(title="Aura AI Server", version="1.0.0")

# Add middlewares
app.add_middleware(AiFeaturesMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - AI Features
app.include_router(api.router, prefix="/api", tags=["API"])
app.include_router(ai_nose.router, prefix="/api/ai-nose", tags=["AI Nose"])
app.include_router(mood_advisor.router, prefix="/api/mood-advisor", tags=["Mood Advisor"])
app.include_router(skin_analyzer.router, prefix="/api/skin-analyzer", tags=["Skin Analyzer"])
app.include_router(occasion_detector.router, prefix="/api/occasion-detector", tags=["Occasion Detector"])
app.include_router(style_matcher.router, prefix="/api/style-matcher", tags=["Style Matcher"])
app.include_router(longevity_meter.router, prefix="/api/longevity-meter", tags=["Longevity Meter"])
app.include_router(perfume_memory.router, prefix="/api/perfume-memory", tags=["Perfume Memory"])
app.include_router(personality_map.router, prefix="/api/personality-map", tags=["Personality Map"])
app.include_router(gift_selector.router, prefix="/api/gift-selector", tags=["Gift Selector"])
app.include_router(description_generator.router, prefix="/api/description-generator", tags=["Description Generator"])
app.include_router(bottle_renderer.router, prefix="/api/bottle-renderer", tags=["Bottle Renderer"])
app.include_router(price_optimizer.router, prefix="/api/price-optimizer", tags=["Price Optimizer"])
app.include_router(tts.router, prefix="/api/tts", tags=["Text-to-Speech"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])

# Include routers - Data Management
app.include_router(ai_attributes.router, prefix="/api/ai-attributes", tags=["AI Attributes"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(database.router, prefix="/api/database", tags=["Database"])
app.include_router(ingredients.router, prefix="/api/ingredients", tags=["Ingredients"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["Order Items"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(perfume_ingredients.router, prefix="/api/perfume-ingredients", tags=["Perfume Ingredients"])
app.include_router(perfumes.router, prefix="/api/perfumes", tags=["Perfumes"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["Prompts"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {"message": "Aura AI Server is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

