#!/usr/bin/env python3
"""
Demo script for the Global Stock Ticker.
This script demonstrates how to use the stock ticker functionality.
"""

import json
import time
from stock_ticker import get_stock_quote, lambda_handler

def demo_local_execution():
    """Demonstrate local execution of stock ticker."""
    print("🔍 Local Execution Demo")
    print("=" * 40)
    
    # List of popular stocks to demo
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    for symbol in symbols:
        try:
            print(f"\n📈 Fetching data for {symbol}...")
            quote_data = get_stock_quote(symbol)
            
            print(f"   Current Price: ${quote_data['current_price']:.2f}")
            print(f"   Change: ${quote_data['change']:.2f} ({quote_data['change_percent']:.2f}%)")
            print(f"   High: ${quote_data['high_price']:.2f}")
            print(f"   Low: ${quote_data['low_price']:.2f}")
            print(f"   Open: ${quote_data['open_price']:.2f}")
            print(f"   Previous Close: ${quote_data['previous_close']:.2f}")
            
            # Add a small delay to avoid hitting API rate limits
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Error fetching {symbol}: {str(e)}")

def demo_lambda_handler():
    """Demonstrate Lambda handler functionality."""
    print("\n\n🚀 Lambda Handler Demo")
    print("=" * 40)
    
    # Test different event scenarios
    test_events = [
        {"symbol": "AAPL"},
        {"symbol": "MSFT"},
        {},  # No symbol - should default to AAPL
        {"symbol": "INVALID_SYMBOL"}  # Should cause an error
    ]
    
    for i, event in enumerate(test_events, 1):
        print(f"\n📋 Test {i}: Event = {json.dumps(event)}")
        
        try:
            result = lambda_handler(event, None)
            print(f"   Status Code: {result['statusCode']}")
            
            if result['statusCode'] == 200:
                body = json.loads(result['body'])
                print(f"   Symbol: {body['symbol']}")
                print(f"   Current Price: ${body['current_price']:.2f}")
            else:
                body = json.loads(result['body'])
                print(f"   Error: {body.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n\n⚠️  Error Handling Demo")
    print("=" * 40)
    
    # Test with invalid symbol
    try:
        print("Testing with invalid symbol 'INVALID_SYMBOL'...")
        quote_data = get_stock_quote("INVALID_SYMBOL")
        print(f"Unexpected success: {quote_data}")
    except Exception as e:
        print(f"✅ Properly caught error: {str(e)}")
    
    # Test with empty symbol
    try:
        print("\nTesting with empty symbol...")
        quote_data = get_stock_quote("")
        print(f"Unexpected success: {quote_data}")
    except Exception as e:
        print(f"✅ Properly caught error: {str(e)}")

def main():
    """Main demo function."""
    print("🌍 Global Stock Ticker - Demo")
    print("=" * 50)
    print("This demo showcases the stock ticker functionality")
    print("Make sure you have set up your FINNHUB_API_KEY in .env file")
    print("=" * 50)
    
    try:
        # Run demos
        demo_local_execution()
        demo_lambda_handler()
        demo_error_handling()
        
        print("\n\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Test with your own stock symbols")
        print("2. Deploy to AWS Lambda using deploy.py")
        print("3. Integrate with your applications")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {str(e)}")
        print("Make sure you have:")
        print("1. Created a .env file with FINNHUB_API_KEY")
        print("2. Installed dependencies: pip install -r requirements.txt")
        print("3. Valid Finnhub API key")

if __name__ == "__main__":
    main() 