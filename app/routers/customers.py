from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Any, Dict
from uuid import UUID, uuid4
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Customer(BaseModel):
    customer_id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    skin_type: Optional[str] = None
    personality_map: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


class CustomerCreate(BaseModel):
    email: EmailStr
    skin_type: Optional[str] = None
    personality_map: Optional[Dict[str, Any]] = None


class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    skin_type: Optional[str] = None
    personality_map: Optional[Dict[str, Any]] = None


@router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("customers").insert(customer.dict()).execute()
        if result.data:
            return Customer(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Could not create customer")
    except Exception as e:
        logger.exception(f"Error creating customer: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create customer: {str(e)}"
        )


@router.get("/customers", response_model=List[Customer])
async def get_customers():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("customers").select("*").execute()
        return [Customer(**customer) for customer in result.data]
    except Exception as e:
        logger.exception(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch customers: {str(e)}"
        )


@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("customers")
            .select("*")
            .eq("customer_id", str(customer_id))
            .execute()
        )
        if result.data:
            return Customer(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.exception(f"Error fetching customer: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch customer: {str(e)}"
        )


@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: UUID, customer: CustomerUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("customers")
            .update(customer.dict(exclude_unset=True))
            .eq("customer_id", str(customer_id))
            .execute()
        )
        if result.data:
            return Customer(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.exception(f"Error updating customer: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update customer: {str(e)}"
        )


@router.delete("/customers/{customer_id}", response_model=dict)
async def delete_customer(customer_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("customers")
            .delete()
            .eq("customer_id", str(customer_id))
            .execute()
        )
        if result.data:
            return {"message": "Customer deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Customer not found")
    except Exception as e:
        logger.exception(f"Error deleting customer: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete customer: {str(e)}"
        )
