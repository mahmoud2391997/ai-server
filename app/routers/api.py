from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
import os
from typing import Dict, Any

app = FastAPI()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://xroixqfaaqelcitaubfx.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhyb2l4cWZhYXFlbGNpdGF1YmZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQzMjk5ODQsImV4cCI6MjA3OTkwNTk4NH0.h_DYktyQrOiXSMl0TYqrgW6BtmxL4Fj2t64FHB6nB9w")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/perfumes/{perfume_id}")
async def get_perfume(perfume_id: str):
    """
    Get a specific perfume by ID
    
    Args:
        perfume_id (str): The ID of the perfume to retrieve
        
    Returns:
        Dict[Any]: The perfume data
        
    Raises:
        HTTPException: If perfume not found or error occurs
    """
    if not perfume_id:
        raise HTTPException(status_code=400, detail="Perfume ID is required")
    
    try:
        response = supabase.table("perfumes").select("*").eq("perfume_id", perfume_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Perfume not found")
            
        return response.data[0]
        
    except Exception as e:
        print(f"Error fetching perfume: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch perfume")