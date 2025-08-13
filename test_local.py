#!/usr/bin/env python3
"""
Local test script for the Lambda function.
This tests the exact same code that will run on AWS Lambda.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from lambda_function import lambda_handler

def test_lambda_function():
    """Test the lambda function with different scenarios."""
    print("🧪 Testing Lambda Function Locally")
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
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Invalid symbol
    print("\n📋 Test 3: Invalid symbol")
    test_event = {"symbol": "INVALID_SYMBOL_12345"}
    try:
        result = lambda_handler(test_event, None)
        print(f"✅ Status Code: {result['statusCode']}")
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
        else:
            print(f"   Error: {result['body']}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    # Check if API key is set
    if not os.environ.get("FINNHUB_API_KEY"):
        print("❌ FINNHUB_API_KEY not set in environment")
        print("Please set your API key:")
        print("export FINNHUB_API_KEY=your_api_key_here")
        print("Or create a .env file with your API key")
        exit(1)
    
    test_lambda_function() 