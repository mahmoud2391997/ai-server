#!/usr/bin/env python3
"""
Test script for AI Attributes range query endpoint

This script tests querying ai_attributes table using:
- geo_range (box): (35,45),(30,40)
- temp_range (numrange): [20,35)
- datetime_range (tsrange): ["2024-01-01 14:00:00","2024-01-01 22:00:00")
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_range_query():
    """Test the range query endpoint"""
    
    # Test 1: Query with all three ranges
    print("=" * 60)
    print("Test 1: Query with geo_range, temp_range, and datetime_range")
    print("=" * 60)
    
    payload = {
        "geo_range": "(35,45),(30,40)",
        "temp_range": "[20,35)",
        "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/ai-attributes/query-by-ranges",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # Test 2: Query with point coordinates (check if point is within geo_range)
    print("=" * 60)
    print("Test 2: Query with point coordinates (32.5, 42.5)")
    print("=" * 60)
    
    payload2 = {
        "point_latitude": 32.5,
        "point_longitude": 42.5,
        "temp_range": "[20,35)",
        "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
    }
    
    response2 = requests.post(
        f"{BASE_URL}/api/ai-attributes/query-by-ranges",
        json=payload2,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2, ensure_ascii=False)}")
    print()
    
    # Test 3: Query with temperature value
    print("=" * 60)
    print("Test 3: Query with temperature value (25)")
    print("=" * 60)
    
    payload3 = {
        "geo_range": "(35,45),(30,40)",
        "temperature": 25,
        "datetime_range": "[\"2024-01-01 14:00:00\",\"2024-01-01 22:00:00\")"
    }
    
    response3 = requests.post(
        f"{BASE_URL}/api/ai-attributes/query-by-ranges",
        json=payload3,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response3.status_code}")
    print(f"Response: {json.dumps(response3.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    try:
        test_range_query()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

