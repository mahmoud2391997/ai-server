#!/usr/bin/env python3
"""
Test TTS endpoint and capture detailed logs
"""
import requests
import json
import sys

def test_tts():
    url = "http://localhost:8000/api/tts/text-to-voice"
    payload = {"text": "مرحبا هذا اختبار"}
    
    print("=" * 60)
    print("Testing TTS Endpoint")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("-" * 60)
        
        if response.status_code == 200:
            print(f"SUCCESS: Received audio file ({len(response.content)} bytes)")
            print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        else:
            print("ERROR Response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
        
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out after 30 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to server: {e}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_tts()

