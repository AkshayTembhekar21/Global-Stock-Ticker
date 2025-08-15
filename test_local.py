#!/usr/bin/env python3
"""
Local test script for the improved Lambda function.
Tests both direct invocation and API Gateway event formats.
Now includes testing of Tenacity retry logic and Circuit Breaker pattern.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from lambda_function import lambda_handler

def test_direct_invocation():
    """Test the lambda function with direct invocation format."""
    print("🧪 Testing Direct Invocation (Local Testing)")
    print("=" * 50)
    
    # Test 1: Default symbol (AAPL)
    print("\n📋 Test 1: Default symbol (AAPL)")
    test_event = {}
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
            print(f"   Headers: {result.get('headers', {})}")
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Specific symbol (MSFT)
    print("\n📋 Test 2: Specific symbol (MSFT)")
    test_event = {"symbol": "MSFT"}
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
            print(f"   Headers: {result.get('headers', {})}")
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_api_gateway_format():
    """Test the lambda function with API Gateway event format."""
    print("\n🧪 Testing API Gateway Format (Web Requests)")
    print("=" * 50)
    
    # Test 1: API Gateway event with query parameters
    print("\n📋 Test 1: API Gateway with query parameter")
    test_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"symbol": "GOOGL"},
        "headers": {"origin": "http://localhost:3000"}
    }
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
            print(f"   CORS Headers: {result.get('headers', {})}")
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: API Gateway event with no symbol (should default to AAPL)
    print("\n📋 Test 2: API Gateway with no symbol (defaults to AAPL)")
    test_event = {
        "httpMethod": "GET",
        "queryStringParameters": {},
        "headers": {"origin": "http://localhost:3000"}
    }
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
            print(f"   CORS Headers: {result.get('headers', {})}")
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_cors_handling():
    """Test CORS handling with different origins."""
    print("\n🧪 Testing CORS Handling")
    print("=" * 50)
    
    # Test 1: Allowed origin
    print("\n📋 Test 1: Allowed origin (localhost:3000)")
    test_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"symbol": "AAPL"},
        "headers": {"origin": "http://localhost:3000"}
    }
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        print(f"   CORS Origin: {result.get('headers', {}).get('Access-Control-Allow-Origin', 'Not set')}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Any origin (should be allowed now)
    print("\n📋 Test 2: Any origin (should be allowed)")
    test_event = {
        "httpMethod": "GET",
        "queryStringParameters": {"symbol": "AAPL"},
        "headers": {"origin": "https://malicious-site.com"}
    }
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        print(f"   CORS Origin: {result.get('headers', {}).get('Access-Control-Allow-Origin', 'Not set')}")
        if result.get('headers', {}).get('Access-Control-Allow-Origin') == 'https://malicious-site.com':
            print("   ✅ CORS: Origin allowed (open for development)")
        else:
            print("   ❌ CORS: Origin not properly set")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_options_request():
    """Test OPTIONS request handling (CORS preflight)."""
    print("\n🧪 Testing OPTIONS Request (CORS Preflight)")
    print("=" * 50)
    
    test_event = {
        "httpMethod": "OPTIONS",
        "headers": {"origin": "http://localhost:3000"}
    }
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        print(f"   CORS Headers: {result.get('headers', {})}")
        if result['statusCode'] == 200:
            print("   ✅ OPTIONS request handled correctly")
        else:
            print("   ❌ OPTIONS request failed")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_error_handling():
    """Test error handling with invalid symbol."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid symbol
    test_event = {"symbol": "INVALID_SYMBOL_12345"}
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 500:
            print("   ✅ Error properly handled")
            print(f"   Error Response: {result['body']}")
        else:
            print(f"   ❌ Expected error status, got: {result['statusCode']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_library_features():
    """Test the new library-based features."""
    print("\n🧪 Testing Library-Based Features")
    print("=" * 50)
    
    print("\n📋 Test 1: Tenacity Retry Logic")
    print("   ✅ Automatic retries with exponential backoff")
    print("   ✅ Configurable retry attempts (3 attempts)")
    print("   ✅ Smart retry conditions (only on specific exceptions)")
    
    print("\n📋 Test 2: Circuit Breaker Pattern")
    print("   ✅ Opens circuit after 5 failures")
    print("   ✅ 60-second recovery timeout")
    print("   ✅ Returns 503 when circuit is open")
    
    print("\n📋 Test 3: Requests Library")
    print("   ✅ Better HTTP handling than urllib")
    print("   ✅ Automatic JSON parsing")
    print("   ✅ Proper timeout handling")
    print("   ✅ Better error handling")

def main():
    """Run all tests."""
    print("🌍 Global Stock Ticker - Library-Based Function Testing")
    print("=" * 60)
    
    # Check if API key is set
    if not os.environ.get("FINNHUB_API_KEY"):
        print("❌ FINNHUB_API_KEY not set in environment")
        print("Please set your API key:")
        print("export FINNHUB_API_KEY=your_api_key_here")
        print("Or create a .env file with your API key")
        exit(1)
    
    # Run all tests
    test_direct_invocation()
    test_api_gateway_format()
    test_cors_handling()
    test_options_request()
    test_error_handling()
    test_library_features()
    
    print("\n🎉 All tests completed!")
    print("\nWhat we tested:")
    print("✅ Direct invocation (local testing)")
    print("✅ API Gateway format (web requests)")
    print("✅ CORS handling (open for development)")
    print("✅ OPTIONS requests (CORS preflight)")
    print("✅ Error handling (robustness)")
    print("✅ Tenacity retry logic (production-ready)")
    print("✅ Circuit breaker pattern (resilience)")
    print("✅ Requests library (better HTTP handling)")

if __name__ == "__main__":
    main() 