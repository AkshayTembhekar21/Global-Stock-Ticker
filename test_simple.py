#!/usr/bin/env python3
"""
Simple test script for the simplified stock ticker.
Tests the main functionality without complex mocking.
"""

import json
from stock_ticker_simple import main, lambda_handler

def test_main_function():
    """Test the main function with a valid symbol."""
    print("🧪 Testing main function...")
    try:
        result = main("AAPL")
        print("✅ Main function test passed!")
        print(f"   Symbol: AAPL")
        print(f"   Current Price: ${result.get('c', 'N/A')}")
        print(f"   Change: ${result.get('d', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Main function test failed: {e}")
        return False

def test_lambda_handler():
    """Test the lambda handler function."""
    print("\n🧪 Testing lambda handler...")
    
    # Test with symbol
    try:
        event = {"symbol": "MSFT"}
        result = lambda_handler(event, None)
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print("✅ Lambda handler test passed!")
            print(f"   Status: {result['statusCode']}")
            print(f"   Symbol: {body['symbol']}")
            print(f"   Current Price: ${body['current_price']}")
        else:
            print(f"❌ Lambda handler returned error status: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Lambda handler test failed: {e}")
        return False
    
    # Test with default symbol
    try:
        event = {}
        result = lambda_handler(event, None)
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print("✅ Lambda handler default symbol test passed!")
            print(f"   Default Symbol: {body['symbol']}")
        else:
            print(f"❌ Lambda handler default symbol test failed: {result['statusCode']}")
            return False
            
    except Exception as e:
        print(f"❌ Lambda handler default symbol test failed: {e}")
        return False
    
    return True

def test_error_handling():
    """Test error handling with invalid symbol."""
    print("\n🧪 Testing error handling...")
    
    try:
        # This should raise an exception
        result = main("INVALID_SYMBOL_12345")
        print("❌ Error handling test failed - should have raised an exception")
        return False
    except Exception as e:
        print("✅ Error handling test passed!")
        print(f"   Caught expected error: {e}")
        return True

def main_test():
    """Run all tests."""
    print("🧪 Simple Stock Ticker Tests")
    print("=" * 40)
    
    tests = [
        ("Main Function", test_main_function),
        ("Lambda Handler", test_lambda_handler),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main_test()
    exit(0 if success else 1) 