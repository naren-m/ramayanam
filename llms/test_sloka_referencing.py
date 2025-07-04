#!/usr/bin/env python3
"""
Test enhanced sloka referencing in the RAG system
"""

import requests
import json
import sys
import time

def test_api_endpoint(url, method="GET", data=None):
    """Test an API endpoint"""
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def main():
    """Test the enhanced referencing system"""
    print("🧪 Testing Enhanced Sloka Referencing")
    print("=" * 50)
    
    base_url = "http://192.168.68.73:8000"
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    health = test_api_endpoint(f"{base_url}/health")
    if health:
        print(f"✅ System Status: {health['status']}")
        print(f"✅ Ollama Available: {health['ollama_available']}")
        print(f"✅ Corpus Loaded: {health['corpus_loaded']}")
    else:
        print("❌ Health check failed")
        return
    
    # Test 2: Get specific sloka by reference
    print("\n2. Testing Sloka Reference Lookup...")
    sloka_ref = {"reference": "BalaKanda.1.1"}
    sloka_result = test_api_endpoint(f"{base_url}/sloka", "POST", sloka_ref)
    
    if sloka_result and sloka_result['found']:
        sloka = sloka_result['sloka']
        print(f"✅ Found sloka: {sloka['kanda']}.{sloka['sarga']}.{sloka['sloka_number']}")
        print(f"   Sanskrit: {sloka['sanskrit_text'][:100]}...")
        print(f"   Translation: {sloka['translation'][:100] if sloka['translation'] else 'Not available'}...")
    else:
        print("❌ Sloka reference lookup failed")
    
    # Test 3: Search with enhanced context
    print("\n3. Testing Enhanced Search...")
    search_data = {"query": "Who is Rama?", "top_k": 3}
    search_result = test_api_endpoint(f"{base_url}/search", "POST", search_data)
    
    if search_result:
        print(f"✅ Found {search_result['total_results']} relevant slokas")
        for i, result in enumerate(search_result['results'][:2], 1):
            ref = f"{result['kanda']}.{result['sarga']}.{result['sloka_number']}"
            print(f"   {i}. Reference: {ref}")
            print(f"      Sanskrit: {result['sanskrit_text'][:80]}...")
    else:
        print("❌ Search failed")
    
    # Test 4: Generate response with references
    print("\n4. Testing Enhanced Response Generation...")
    generate_data = {"query": "What are Rama's qualities as described in the Ramayanam?", "top_k": 3}
    generate_result = test_api_endpoint(f"{base_url}/generate", "POST", generate_data)
    
    if generate_result:
        print("✅ Generated response with references:")
        print("-" * 60)
        print(generate_result['response'])
        print("-" * 60)
        print(f"Model used: {generate_result['model_used']}")
        
        # Check if response contains sloka references
        response_text = generate_result['response']
        if "Reference:" in response_text or "BalaKanda" in response_text or "AyodhyaKanda" in response_text:
            print("✅ Response contains sloka references!")
        else:
            print("⚠️  Response may not contain clear sloka references")
            
    else:
        print("❌ Response generation failed")
    
    # Test 5: Chat with enhanced referencing
    print("\n5. Testing Enhanced Chat...")
    chat_data = {
        "messages": [
            {"role": "user", "content": "Tell me about Hanuman's devotion to Rama. Please include specific sloka references."}
        ]
    }
    
    chat_result = test_api_endpoint(f"{base_url}/chat", "POST", chat_data)
    
    if chat_result:
        print("✅ Chat response with references:")
        print("-" * 60)
        print(chat_result['response'])
        print("-" * 60)
        
        # Check for references in chat
        response_text = chat_result['response']
        if "Reference:" in response_text or any(kanda in response_text for kanda in ["BalaKanda", "AyodhyaKanda", "AranyaKanda", "KishkindaKanda", "SundaraKanda", "YuddhaKanda"]):
            print("✅ Chat response contains sloka references!")
        else:
            print("⚠️  Chat response may not contain clear sloka references")
    else:
        print("❌ Chat failed")
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

if __name__ == "__main__":
    main()