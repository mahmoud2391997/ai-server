from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class AIAttributes(BaseModel):
    perfume_id: UUID
    mood_tag: str
    occasion_tag: str
    style_tag: str
    longevity_score: int = Field(..., ge=1, le=10)
    sillage_score: int = Field(..., ge=1, le=10)
    skin_compatibility: str
    created_at: Optional[str] = None


class AIAttributesCreate(BaseModel):
    perfume_id: UUID
    mood_tag: str
    occasion_tag: str
    style_tag: str
    longevity_score: int = Field(..., ge=1, le=10)
    sillage_score: int = Field(..., ge=1, le=10)
    skin_compatibility: str


class AIAttributesUpdate(BaseModel):
    mood_tag: Optional[str] = None
    occasion_tag: Optional[str] = None
    style_tag: Optional[str] = None
    longevity_score: Optional[int] = Field(None, ge=1, le=10)
    sillage_score: Optional[int] = Field(None, ge=1, le=10)
    skin_compatibility: Optional[str] = None


@router.post("/ai-attributes", response_model=AIAttributes)
async def create_ai_attributes(ai_attributes: AIAttributesCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("ai_attributes").insert(ai_attributes.dict()).execute()
        if result.data:
            return AIAttributes(**result.data[0])
        else:
            raise HTTPException(
                status_code=400, detail="Could not create AI attributes"
            )
    except Exception as e:
        logger.exception(f"Error creating AI attributes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create AI attributes: {str(e)}"
        )


@router.get("/ai-attributes", response_model=List[AIAttributes])
async def get_ai_attributes():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("ai_attributes").select("*").execute()
        return [AIAttributes(**attrs) for attrs in result.data]
    except Exception as e:
        logger.exception(f"Error fetching AI attributes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch AI attributes: {str(e)}"
        )


@router.get("/ai-attributes/{perfume_id}", response_model=AIAttributes)
async def get_ai_attribute(perfume_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ai_attributes")
            .select("*")
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return AIAttributes(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="AI attributes not found")
    except Exception as e:
        logger.exception(f"Error fetching AI attributes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch AI attributes: {str(e)}"
        )


@router.put("/ai-attributes/{perfume_id}", response_model=AIAttributes)
async def update_ai_attributes(perfume_id: UUID, ai_attributes: AIAttributesUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ai_attributes")
            .update(ai_attributes.dict(exclude_unset=True))
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return AIAttributes(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="AI attributes not found")
    except Exception as e:
        logger.exception(f"Error updating AI attributes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update AI attributes: {str(e)}"
        )


@router.delete("/ai-attributes/{perfume_id}", response_model=dict)
async def delete_ai_attributes(perfume_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ai_attributes")
            .delete()
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return {"message": "AI attributes deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="AI attributes not found")
    except Exception as e:
        logger.exception(f"Error deleting AI attributes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete AI attributes: {str(e)}"
        )
