from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Ingredient(BaseModel):
    ingredient_id: int
    name: str
    category: Optional[str] = None
    created_at: Optional[str] = None


class IngredientCreate(BaseModel):
    name: str
    category: Optional[str] = None


class IngredientUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


@router.post("/ingredients", response_model=Ingredient)
async def create_ingredient(ingredient: IngredientCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("ingredients").insert(ingredient.dict()).execute()
        if result.data:
            return Ingredient(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Could not create ingredient")
    except Exception as e:
        logger.exception(f"Error creating ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create ingredient: {str(e)}"
        )


@router.get("/ingredients", response_model=List[Ingredient])
async def get_ingredients():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("ingredients").select("*").execute()
        return [Ingredient(**ingredient) for ingredient in result.data]
    except Exception as e:
        logger.exception(f"Error fetching ingredients: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch ingredients: {str(e)}"
        )


@router.get("/ingredients/{ingredient_id}", response_model=Ingredient)
async def get_ingredient(ingredient_id: int):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ingredients")
            .select("*")
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return Ingredient(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Ingredient not found")
    except Exception as e:
        logger.exception(f"Error fetching ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch ingredient: {str(e)}"
        )


@router.put("/ingredients/{ingredient_id}", response_model=Ingredient)
async def update_ingredient(ingredient_id: int, ingredient: IngredientUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ingredients")
            .update(ingredient.dict(exclude_unset=True))
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return Ingredient(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Ingredient not found")
    except Exception as e:
        logger.exception(f"Error updating ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update ingredient: {str(e)}"
        )


@router.delete("/ingredients/{ingredient_id}", response_model=dict)
async def delete_ingredient(ingredient_id: int):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("ingredients")
            .delete()
            .eq("ingredient_id", ingredient_id)
            .execute()
        )
        if result.data:
            return {"message": "Ingredient deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Ingredient not found")
    except Exception as e:
        logger.exception(f"Error deleting ingredient: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete ingredient: {str(e)}"
        )
