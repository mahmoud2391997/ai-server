
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.ai_features import AiFeaturesMiddleware
from app.routers import api

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

# Include routers
app.include_router(api.router, prefix="/api", tags=["API"])


@app.get("/")
async def root():
    return {"message": "Aura AI Server is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

