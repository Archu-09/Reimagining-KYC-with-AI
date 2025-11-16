#!/usr/bin/env python3
"""
Test script to simulate the exact request that the frontend makes
This helps debug the JSON parsing issue
"""

import requests
import json

# Test the verification endpoint
def test_verification():
    url = "http://localhost:8000/api/verify"
    
    # Prepare files (same as frontend would send)
    files = {
        'id_image': ('id_demo.jpg', open('/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend/id_demo.jpg', 'rb'), 'image/jpeg'),
        'selfie': ('selfie_demo.jpg', open('/Users/aryadav/Downloads/Reimagining-KYC-with-AI/backend/selfie_demo.jpg', 'rb'), 'image/jpeg')
    }
    
    data = {
        'document_type': 'passport',
        'liveness_attestation': json.dumps({
            'method': 'advanced',
            'confidence': 0.95,
            'timestamp': '2025-11-16T20:55:00Z'
        })
    }
    
    print("🚀 Sending POST request to", url)
    print("📁 Files:", list(files.keys()))
    print("📝 Data:", data)
    
    try:
        response = requests.post(url, files=files, data=data)
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📋 Response Headers:")
        for k, v in response.headers.items():
            print(f"   {k}: {v}")
        
        print(f"\n📄 Raw Response Text ({len(response.text)} chars):")
        print(response.text[:500] + ("..." if len(response.text) > 500 else ""))
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"\n✅ JSON Parsed Successfully:")
                print(json.dumps(json_data, indent=2)[:500] + "...")
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON Parse Error: {e}")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    finally:
        # Close files
        for file_tuple in files.values():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

if __name__ == "__main__":
    test_verification()
