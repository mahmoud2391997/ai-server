from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from app.services.database import get_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Order(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    customer_name: str
    customer_email: str
    shipping_address: str
    total_amount: float
    status: Optional[str] = "pending"
    created_at: Optional[str] = None
    city: str
    customer_phone: str
    postal_code: str
    payment_method: str


class OrderCreate(BaseModel):
    user_id: Optional[UUID] = None
    customer_name: str
    customer_email: str
    shipping_address: str
    total_amount: float
    status: Optional[str] = "pending"
    city: str
    customer_phone: str
    postal_code: str
    payment_method: str


class OrderUpdate(BaseModel):
    user_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = None
    city: Optional[str] = None
    customer_phone: Optional[str] = None
    postal_code: Optional[str] = None
    payment_method: Optional[str] = None


@router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    try:
        supabase = get_supabase_client()
        result = supabase.from_("orders").insert(order.dict()).execute()
        if result.data:
            return Order(**result.data[0])
        else:
            raise HTTPException(status_code=400, detail="Could not create order")
    except Exception as e:
        logger.exception(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")


@router.get("/orders", response_model=List[Order])
async def get_orders():
    try:
        supabase = get_supabase_client()
        result = supabase.from_("orders").select("*").execute()
        return [Order(**order) for order in result.data]
    except Exception as e:
        logger.exception(f"Error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("orders").select("*").eq("id", str(order_id)).execute()
        )
        if result.data:
            return Order(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.exception(f"Error fetching order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")


@router.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: UUID, order: OrderUpdate):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("orders")
            .update(order.dict(exclude_unset=True))
            .eq("id", str(order_id))
            .execute()
        )
        if result.data:
            return Order(**result.data[0])
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.exception(f"Error updating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@router.delete("/orders/{order_id}", response_model=dict)
async def delete_order(order_id: UUID):
    try:
        supabase = get_supabase_client()
        result = (
            supabase.from_("orders").delete().eq("id", str(order_id)).execute()
        )
        if result.data:
            return {"message": "Order deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        logger.exception(f"Error deleting order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete order: {str(e)}")
