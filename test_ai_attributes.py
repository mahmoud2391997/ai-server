
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_create_ai_attributes():
    perfume_id = str(uuid.uuid4())
    response = client.post("/ai-attributes", json={
        "perfume_id": perfume_id,
        "mood_tag": "Happy",
        "occasion_tag": "Casual",
        "style_tag": "Elegant",
        "longevity_score": 8,
        "sillage_score": 7,
        "skin_compatibility": "Normal"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["perfume_id"] == perfume_id
    assert data["mood_tag"] == "Happy"

def test_get_ai_attributes():
    response = client.get("/ai-attributes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_ai_attribute():
    perfume_id = str(uuid.uuid4())
    client.post("/ai-attributes", json={
        "perfume_id": perfume_id,
        "mood_tag": "Happy",
        "occasion_tag": "Casual",
        "style_tag": "Elegant",
        "longevity_score": 8,
        "sillage_score": 7,
        "skin_compatibility": "Normal"
    })
    response = client.get(f"/ai-attributes/{perfume_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["perfume_id"] == perfume_id

def test_update_ai_attributes():
    perfume_id = str(uuid.uuid4())
    client.post("/ai-attributes", json={
        "perfume_id": perfume_id,
        "mood_tag": "Happy",
        "occasion_tag": "Casual",
        "style_tag": "Elegant",
        "longevity_score": 8,
        "sillage_score": 7,
        "skin_compatibility": "Normal"
    })
    response = client.put(f"/ai-attributes/{perfume_id}", json={"mood_tag": "Excited"})
    assert response.status_code == 200
    data = response.json()
    assert data["mood_tag"] == "Excited"

def test_delete_ai_attributes():
    perfume_id = str(uuid.uuid4())
    client.post("/ai-attributes", json={
        "perfume_id": perfume_id,
        "mood_tag": "Happy",
        "occasion_tag": "Casual",
        "style_tag": "Elegant",
        "longevity_score": 8,
        "sillage_score": 7,
        "skin_compatibility": "Normal"
    })
    response = client.delete(f"/ai-attributes/{perfume_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI attributes deleted successfully"
