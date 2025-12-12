from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class OrderItem(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    order_id: Optional[UUID] = None
    perfume_id: str
    perfume_name: str
    perfume_brand: str
    price: float
    quantity: int
    created_at: Optional[str] = None


class OrderItemCreate(BaseModel):
    order_id: Optional[UUID] = None
    perfume_id: str
    perfume_name: str
    perfume_brand: str
    price: float
    quantity: int


class OrderItemUpdate(BaseModel):
    order_id: Optional[UUID] = None
    perfume_id: Optional[str] = None
    perfume_name: Optional[str] = None
    perfume_brand: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None


@router.post("/order-items", response_model=OrderItem)
async def create_order_item(order_item: OrderItemCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("order_items").insert(order_item.dict()).execute()
        if result.data:
            return OrderItem(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Could not create order item")
    except Exception as e:
        logger.exception(f"Error creating order item: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create order item: {str(e)}"
        )


@router.get("/order-items", response_model=List[OrderItem])
async def get_order_items():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("order_items").select("*").execute()
        return [OrderItem(**item) for item in result.data]
    except Exception as e:
        logger.exception(f"Error fetching order items: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch order items: {str(e)}"
        )


@router.get("/order-items/{item_id}", response_model=OrderItem)
async def get_order_item(item_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("order_items")
            .select("*")
            .eq("id", str(item_id))
            .execute()
        )
        if result.data:
            return OrderItem(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Order item not found")
    except Exception as e:
        logger.exception(f"Error fetching order item: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch order item: {str(e)}"
        )


@router.put("/order-items/{item_id}", response_model=OrderItem)
async def update_order_item(item_id: UUID, order_item: OrderItemUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("order_items")
            .update(order_item.dict(exclude_unset=True))
            .eq("id", str(item_id))
            .execute()
        )
        if result.data:
            return OrderItem(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Order item not found")
    except Exception as e:
        logger.exception(f"Error updating order item: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update order item: {str(e)}"
        )


@router.delete("/order-items/{item_id}", response_model=dict)
async def delete_order_item(item_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("order_items")
            .delete()
            .eq("id", str(item_id))
            .execute()
        )
        if result.data:
            return {"message": "Order item deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Order item not found")
    except Exception as e:
        logger.exception(f"Error deleting order item: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete order item: {str(e)}"
        )
