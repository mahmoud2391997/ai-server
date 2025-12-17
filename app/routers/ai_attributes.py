from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
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


class RangeQueryRequest(BaseModel):
    """Request model for range-based queries"""
    geo_range: Optional[str] = Field(None, description="Box range: (x1,y1),(x2,y2) e.g., (35,45),(30,40)")
    temp_range: Optional[str] = Field(None, description="Temperature range: [min,max) or (min,max) e.g., [20,35)")
    datetime_range: Optional[str] = Field(None, description="DateTime range: [start,end) e.g., [\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")")
    point_latitude: Optional[float] = Field(None, description="Point latitude to check if within geo_range")
    point_longitude: Optional[float] = Field(None, description="Point longitude to check if within geo_range")
    temperature: Optional[float] = Field(None, description="Temperature value to check if within temp_range")
    datetime: Optional[str] = Field(None, description="DateTime value to check if within datetime_range")


@router.post("/query-by-ranges", response_model=List[Dict[str, Any]])
async def query_ai_attributes_by_ranges(request: RangeQueryRequest):
    """
    Query AI attributes using PostgreSQL range types:
    - geo_range (box): Geographic bounding box
    - temp_range (numrange): Temperature range
    - datetime_range (tsrange): DateTime range
    
    You can either:
    1. Provide ranges to find all records that have overlapping ranges
    2. Provide point values (latitude, longitude, temperature, datetime) to find records where the point is within the range
    """
    try:
        supabase = get_supabase_client()
        
        # Build SQL query for range matching
        # Since Supabase PostgREST doesn't directly support range operators,
        # we'll use RPC function or raw SQL
        
        query_parts = []
        params = {}
        param_count = 0
        
        # Build WHERE conditions
        conditions = []
        
        # Geo range query - check if point is within box or if boxes overlap
        if request.point_latitude is not None and request.point_longitude is not None:
            # Check if point is contained in geo_range box
            conditions.append(f"geo_range @> box(point(${param_count + 1}, ${param_count + 2}))")
            params[f"param_{param_count + 1}"] = request.point_longitude
            params[f"param_{param_count + 2}"] = request.point_latitude
            param_count += 2
        elif request.geo_range:
            # Check if geo_range overlaps with provided box
            # Format: (35,45),(30,40) -> box '((35,45),(30,40))'
            conditions.append(f"geo_range && box '({request.geo_range})'")
        
        # Temperature range query
        if request.temperature is not None:
            # Check if temperature is contained in temp_range
            conditions.append(f"temp_range @> ${param_count + 1}::numeric")
            params[f"param_{param_count + 1}"] = request.temperature
            param_count += 1
        elif request.temp_range:
            # Check if temp_range overlaps with provided range
            # Format: [20,35) -> numrange '[20,35)'
            conditions.append(f"temp_range && numrange '{request.temp_range}'")
        
        # DateTime range query
        if request.datetime:
            # Check if datetime is contained in datetime_range
            conditions.append(f"datetime_range @> ${param_count + 1}::timestamp")
            params[f"param_{param_count + 1}"] = request.datetime
            param_count += 1
        elif request.datetime_range:
            # Check if datetime_range overlaps with provided range
            # Format: ["2024-01-01 14:00:00","2024-01-01 22:00:00") -> tsrange '["2024-01-01 14:00:00","2024-01-01 22:00:00")'
            # Remove quotes from the range string if present
            range_str = request.datetime_range.replace('"', "'")
            conditions.append(f"datetime_range && tsrange '{range_str}'")
        
        # Use RPC function for complex range queries
        # First, let's try a direct query approach using Supabase's RPC
        if conditions:
            # Build the SQL query
            sql_query = f"""
            SELECT 
                aa.*,
                p.name as perfume_name,
                p.brand as perfume_brand,
                p.price as perfume_price
            FROM ai_attributes aa
            JOIN perfumes p ON aa.perfume_id = p.perfume_id
            WHERE {' AND '.join(conditions)}
            """
            
            # Execute using RPC (we'll need to create an RPC function in the database)
            # For now, let's use a simpler approach with PostgREST filters
            # Note: Supabase PostgREST has limited support for range operators
            # We'll need to use a database function
            
            # Use RPC function for range queries
            rpc_params = {}
            if request.point_latitude is not None and request.point_longitude is not None:
                rpc_params['point_lat'] = request.point_latitude
                rpc_params['point_lon'] = request.point_longitude
            if request.geo_range:
                rpc_params['geo_box'] = request.geo_range
            if request.temperature is not None:
                rpc_params['temp_value'] = request.temperature
            if request.temp_range:
                rpc_params['temp_range_str'] = request.temp_range
            if request.datetime:
                rpc_params['dt_value'] = request.datetime
            if request.datetime_range:
                # Remove quotes and ensure proper format
                dt_range = request.datetime_range.replace('"', "'")
                rpc_params['dt_range_str'] = dt_range
            
            # Call RPC function
            try:
                result = supabase.rpc('query_ai_attributes_by_ranges', rpc_params).execute()
                if result.data:
                    logger.info(f"Found {len(result.data)} matching records")
                    return result.data
                else:
                    logger.info("No matching records found")
                    return []
            except Exception as rpc_error:
                error_msg = str(rpc_error)
                logger.error(f"RPC function error: {error_msg}")
                
                # If RPC function doesn't exist, try fallback: get all attributes
                if "function" in error_msg.lower() or "does not exist" in error_msg.lower():
                    logger.warning("RPC function not found, using fallback: returning all attributes")
                    # Fallback: return all attributes (can't filter by ranges without RPC)
                    result = supabase.from_("ai_attributes").select("*, perfumes(*)").execute()
                    if result.data:
                        logger.info(f"Fallback: Found {len(result.data)} total records")
                        return result.data
                    else:
                        return []
                else:
                    # If RPC function doesn't exist, provide helpful error message
                    raise HTTPException(
                        status_code=500,
                        detail=f"Range query function not available. Please run migration 002_add_range_query_function.sql. Error: {error_msg}"
                    )
        else:
            # No conditions, return all
            result = supabase.from_("ai_attributes").select("*, perfumes(*)").execute()
            return result.data if result.data else []
            
    except Exception as e:
        logger.exception(f"Error querying AI attributes by ranges: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to query AI attributes: {str(e)}"
        )
