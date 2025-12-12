
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Perfume(BaseModel):
    perfume_id: UUID = Field(default_factory=uuid4)
    name: str
    brand: str
    gender: str
    concentration: str
    year_released: Optional[int] = None
    price: float
    ml_size: Optional[int] = None
    description_llm: Optional[str] = None
    created_at: Optional[str] = None


class PerfumeCreate(BaseModel):
    name: str
    brand: str
    gender: str
    concentration: str
    year_released: Optional[int] = None
    price: float
    ml_size: Optional[int] = None
    description_llm: Optional[str] = None


class PerfumeUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    concentration: Optional[str] = None
    year_released: Optional[int] = None
    price: Optional[float] = None
    ml_size: Optional[int] = None
    description_llm: Optional[str] = None


@router.post("/perfumes", response_model=Perfume)
async def create_perfume(perfume: PerfumeCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("perfumes").insert(perfume.dict()).execute()
        if result.data:
            return Perfume(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Could not create perfume")
    except Exception as e:
        logger.exception(f"Error creating perfume: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create perfume: {str(e)}"
        )


@router.get("/perfumes", response_model=List[Perfume])
async def get_perfumes():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("perfumes").select("*").execute()
        return [Perfume(**perfume) for perfume in result.data]
    except Exception as e:
        logger.exception(f"Error fetching perfumes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch perfumes: {str(e)}"
        )


@router.get("/perfumes/{perfume_id}", response_model=Perfume)
async def get_perfume(perfume_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfumes")
            .select("*")
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return Perfume(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Perfume not found")
    except Exception as e:
        logger.exception(f"Error fetching perfume: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch perfume: {str(e)}"
        )


@router.put("/perfumes/{perfume_id}", response_model=Perfume)
async def update_perfume(perfume_id: UUID, perfume: PerfumeUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfumes")
            .update(perfume.dict(exclude_unset=True))
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return Perfume(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Perfume not found")
    except Exception as e:
        logger.exception(f"Error updating perfume: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update perfume: {str(e)}"
        )


@router.delete("/perfumes/{perfume_id}", response_model=dict)
async def delete_perfume(perfume_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfumes")
            .delete()
            .eq("perfume_id", str(perfume_id))
            .execute()
        )
        if result.data:
            return {"message": "Perfume deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Perfume not found")
    except Exception as e:
        logger.exception(f"Error deleting perfume: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete perfume: {str(e)}"
        )
