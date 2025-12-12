from fastapi import APIRouter, HTTPException
from app.services.database import get_supabase_client

router = APIRouter()

@router.get("/all-tables")
async def get_all_tables():
    """
    Fetches all data from all tables in the database.
    """
    try:
        supabase = get_supabase_client()
        table_names = [
            "ai_attributes",
            "customers",
            "ingredients",
            "order_items",
            "orders",
            "perfume_ingredients",
            "perfumes",
            "users",
        ]
        
        all_tables_data = {}
        for table_name in table_names:
            result = supabase.from_(table_name).select("*").execute()
            all_tables_data[table_name] = result.data

        return all_tables_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch data: {str(e)}"
        )