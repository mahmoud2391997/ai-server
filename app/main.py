import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ai_nose, mood_advisor, skin_analyzer, occasion_detector, style_matcher, longevity_meter, perfume_memory, personality_map, gift_selector, description_generator, bottle_renderer, price_optimizer

app = FastAPI(title="Aura AI Server", version="1.0.0")

# CORS middleware - Allow all origins for Vercel deployment
# You can restrict this by setting ALLOWED_ORIGINS environment variable
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    allowed_origins = allowed_origins_env.split(",")
else:
    # Default to localhost for development
    allowed_origins = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"]
    # In production (Vercel), if no ALLOWED_ORIGINS is set, allow all origins
    # Note: When using allow_credentials=True, we can't use ["*"], so we'll allow all by not restricting
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        # For Vercel, allow all origins by using a wildcard pattern
        # But we need to set allow_credentials=False when using wildcard
        allowed_origins = ["*"]

# Set credentials based on whether we're using wildcard
use_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=use_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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

@app.get("/")
async def root():
    return {"message": "Aura AI Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}