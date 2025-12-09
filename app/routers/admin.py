from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from app.services.database import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter()

class CustomerResponse(BaseModel):
    customer_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class CustomersListResponse(BaseModel):
    customers: List[CustomerResponse]
    total: int
    page: int
    limit: int
    total_pages: int

@router.get("/customers", response_model=CustomersListResponse)
async def get_customers(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)")
):
    """
    Get paginated list of customers.
    
    Args:
        page: Page number (starts from 1)
        limit: Number of items per page (max 100)
        
    Returns:
        Paginated list of customers with metadata
    """
    try:
        supabase = get_supabase_client()
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        count_result = supabase.from_('customers').select('*', count='exact').execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Get paginated customers
        result = supabase.from_('customers')\
            .select('*')\
            .order('created_at', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        customers = []
        if result.data:
            for customer in result.data:
                customers.append(CustomerResponse(
                    customer_id=str(customer.get('customer_id', '')),
                    name=customer.get('name'),
                    email=customer.get('email'),
                    phone=customer.get('phone'),
                    created_at=customer.get('created_at'),
                    preferences=customer.get('preferences')
                ))
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        return CustomersListResponse(
            customers=customers,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.exception(f"Error fetching customers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch customers: {str(e)}"
        )

