from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from enum import Enum
import uuid

class MultiModalRequest(BaseModel):
    text: Optional[str] = None
    image_data: Optional[str] = None  # base64 encoded
    audio_data: Optional[str] = None  # base64 encoded
    options: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None  # weather, location, time

class PerfumeRecommendation(BaseModel):
    perfume_id: str
    name: str
    brand: str
    compatibility_score: float
    reason: str
    price: float
    mood_tag: Optional[str] = None
    occasion_tag: Optional[str] = None
    style_tag: Optional[str] = None
    longevity_score: Optional[int] = None
    sillage_score: Optional[int] = None
    skin_compatibility: Optional[str] = None

class AIAnalysisResponse(BaseModel):
    analysis: str
    recommendations: List[PerfumeRecommendation]
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class AIResponse(BaseModel):
    result: str
    confidence: Optional[float] = None
    recommendations: Optional[List[str]] = None
    perfume_suggestions: Optional[List[PerfumeRecommendation]] = None
    metadata: Optional[Dict[str, Any]] = None

class CustomerProfile(BaseModel):
    customer_id: str
    email: str
    skin_type: Optional[str] = None
    personality_map: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class PerfumeData(BaseModel):
    perfume_id: str
    name: str
    brand: str
    gender: str
    concentration: str
    price: float
    mood_tag: str
    occasion_tag: str
    style_tag: str
    longevity_score: int
    sillage_score: int
    skin_compatibility: str
    ingredients: Optional[List[Dict[str, str]]] = None

class SkinType(str, Enum):
    oily = "Oily"
    dry = "Dry"
    neutral = "Neutral"

class Gender(str, Enum):
    male = "Male"
    female = "Female"
    unisex = "Unisex"

class Concentration(str, Enum):
    edc = "EDC"
    edt = "EDT"
    edp = "EDP"
    parfum = "Parfum"
    extrait = "Extrait"