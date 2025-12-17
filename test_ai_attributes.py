import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app import app  # assuming your FastAPI app is in app.py or app/__init__.py

@pytest.mark.asyncio
async def test_perfume_search_endpoint():
    test_cases = [
        {
            "feature": "ai-nose",
            "text": "I want a fresh scent for summer days",
            "context": {"weather": {"description": "sunny"}},
        },
        {
            "feature": "mood-advisor",
            "text": "Feeling stressed and need relaxation",
        },
        {
            "feature": "skin-analyzer",
            "text": "My skin is oily and sensitive",
            "image_data": "base64imagestring==",
        },
        {
            "feature": "occasion-detector",
            "text": "Looking for a fragrance for a wedding",
        },
        {
            "feature": "style-matcher",
            "text": "I usually wear casual and sporty clothes",
        },
        {
            "feature": "personality-map",
            "text": "I am outgoing and love adventures",
        },
        {
            "feature": "gift-selector",
            "text": "Buying a gift for my mother’s birthday",
        },
    ]

    async with AsyncClient(app=app, base_url="http://test") as client:
        for case in test_cases:
            response = await client.post("/api/perfume-search", json=case)
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert "recommendations" in data
            assert isinstance(data["recommendations"], list)
            # Optionally check structure of first recommendation if exists
            if data["recommendations"]:
                rec = data["recommendations"][0]
                assert "reason" in rec
                assert "compatibility_score" in rec
                assert 85 <= rec["compatibility_score"] <= 98