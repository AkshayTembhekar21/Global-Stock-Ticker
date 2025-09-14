#!/usr/bin/env python3
"""
Specific Load Test for Stock Ticker API
API URL: https://q12h96ifp0.execute-api.us-east-1.amazonaws.com/PROD/quote/LLY

Test Requirements:
1. 2000 concurrent requests in a second
2. 200 requests with 200ms delay between API calls
"""

import random
import time
from locust import HttpUser, task, between
import json

class StockAPILoadTest(HttpUser):
    """Load test for the specific Stock Ticker API endpoint"""
    
    # The specific API endpoint you want to test
    host = "https://q12h96ifp0.execute-api.us-east-1.amazonaws.com"
    
    # 200ms delay between requests as specified
    wait_time = between(0.2, 0.2)
    
    def on_start(self):
        """Called when a user starts"""
        print(f"🚀 Starting load test for user")
    
    @task
    def test_llm_stock_quote(self):
        """Test the specific LLY endpoint"""
        endpoint = "/PROD/quote/LLY"
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "current_price" in data and data["current_price"] is not None:
                        response.success()
                        # Log successful response
                        print(f"✅ LLY: ${data['current_price']} (Change: {data.get('quote_data', {}).get('d', 'N/A')})")
                    else:
                        response.failure("Invalid response format - missing current_price")
                except json.JSONDecodeError as e:
                    response.failure(f"Invalid JSON response: {str(e)}")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def test_other_stocks(self):
        """Test other stock symbols occasionally"""
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        symbol = random.choice(symbols)
        endpoint = f"/PROD/quote/{symbol}"
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "current_price" in data and data["current_price"] is not None:
                        response.success()
                        print(f"✅ {symbol}: ${data['current_price']}")
                    else:
                        response.failure(f"Invalid response format for {symbol}")
                except json.JSONDecodeError:
                    response.failure(f"Invalid JSON response for {symbol}")
            else:
                response.failure(f"HTTP {response.status_code} for {symbol}")

class BurstLoadUser(StockAPILoadTest):
    """User class for burst testing (2000 concurrent requests)"""
    wait_time = between(0.001, 0.01)  # Very fast requests for burst testing

class SustainedLoadUser(StockAPILoadTest):
    """User class for sustained load testing (200 users with 200ms delay)"""
    wait_time = between(0.2, 0.2)  # Fixed 200ms delay

if __name__ == "__main__":
    print("🌍 Stock Ticker API - Specific Load Test")
    print("=" * 50)
    print("API Endpoint: https://q12h96ifp0.execute-api.us-east-1.amazonaws.com/PROD/quote/LLY")
    print("\nTest Scenarios:")
    print("1. Burst Test: 2000 concurrent requests")
    print("2. Sustained Test: 200 users with 200ms delay")
    print("\nCommands to run:")
    print("\n🚀 Burst Test (2000 concurrent):")
    print("locust -f stock_api_load_test.py --users 2000 --spawn-rate 2000 --run-time 30s")
    print("\n⏱️ Sustained Test (200 users, 200ms delay):")
    print("locust -f stock_api_load_test.py --users 200 --spawn-rate 20 --run-time 5m")
    print("\n🌐 Web UI (Interactive):")
    print("locust -f stock_api_load_test.py --web-host 0.0.0.0 --web-port 8089")
