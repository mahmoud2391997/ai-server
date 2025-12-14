import requests
import uuid

perfume_id = str(uuid.uuid4())
data = {
    "perfume_id": perfume_id,
    "mood_tag": "Happy",
    "occasion_tag": "Casual",
    "style_tag": "Elegant",
    "longevity_score": 8,
    "sillage_score": 7,
    "skin_compatibility": "Normal"
}

response = requests.post("http://127.0.0.1:8000/ai-attributes", json=data)

print(response.status_code)
print(response.json())