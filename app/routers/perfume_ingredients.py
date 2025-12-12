from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class PerfumeIngredient(BaseModel):
    perfume_id: UUID
    ingredient_id: int
    stage: str


class PerfumeIngredientCreate(BaseModel):
    perfume_id: UUID
    ingredient_id: int
    stage: str


class PerfumeIngredientUpdate(BaseModel):
    stage: Optional[str] = None


@router.post("/perfume-ingredients", response_model=PerfumeIngredient)
async def create_perfume_ingredient(perf_ing: PerfumeIngredientCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("perfume_ingredients").insert(perf_ing.dict()).execute()
        if result.data:
            return PerfumeIngredient(**result.data[0])
        else:
            raise HTTPException(
                status_code=400, detail="Could not create perfume ingredient"
            )
    except Exception as e:
        logger.exception(f"Error creating perfume ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create perfume ingredient: {str(e)}"
        )


@router.get("/perfume-ingredients", response_model=List[PerfumeIngredient])
async def get_perfume_ingredients():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("perfume_ingredients").select("*").execute()
        return [PerfumeIngredient(**pi) for pi in result.data]
    except Exception as e:
        logger.exception(f"Error fetching perfume ingredients: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch perfume ingredients: {str(e)}"
        )


@router.get("/perfume-ingredients/{perfume_id}/{ingredient_id}", response_model=PerfumeIngredient)
async def get_perfume_ingredient(perfume_id: UUID, ingredient_id: int):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfume_ingredients")
            .select("*")
            .eq("perfume_id", str(perfume_id))
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return PerfumeIngredient(**result.data[0])
        else:
            raise HTTPException(
                status_code=404, detail="Perfume ingredient not found"
            )
    except Exception as e:
        logger.exception(f"Error fetching perfume ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch perfume ingredient: {str(e)}"
        )


@router.put("/perfume-ingredients/{perfume_id}/{ingredient_id}", response_model=PerfumeIngredient)
async def update_perfume_ingredient(
    perfume_id: UUID, ingredient_id: int, perf_ing: PerfumeIngredientUpdate
):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfume_ingredients")
            .update(perf_ing.dict(exclude_unset=True))
            .eq("perfume_id", str(perfume_id))
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return PerfumeIngredient(**result.data[0])
        else:
            raise HTTPException(
                status_code=404, detail="Perfume ingredient not found"
            )
    except Exception as e:
        logger.exception(f"Error updating perfume ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update perfume ingredient: {str(e)}"
        )


@router.delete("/perfume-ingredients/{perfume_id}/{ingredient_id}", response_model=dict)
async def delete_perfume_ingredient(perfume_id: UUID, ingredient_id: int):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("perfume_ingredients")
            .delete()
            .eq("perfume_id", str(perfume_id))
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return {"message": "Perfume ingredient deleted successfully"}
        else:
            raise HTTPException(
                status_code=404, detail="Perfume ingredient not found"
            )
    except Exception as e:
        logger.exception(f"Error deleting perfume ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete perfume ingredient: {str(e)}"
        )
