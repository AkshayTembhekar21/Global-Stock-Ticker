#!/usr/bin/env python3
"""
Load Test Script for Global Stock Ticker API
Tests the API endpoint: https://q12h96ifp0.execute-api.us-east-1.amazonaws.com/DEV/quote/LLY

Test Scenarios:
1. High Concurrency Test: 2000 concurrent users
2. Sustained Load Test: 200 users with 200ms delay between requests
"""

import random
import time
from locust import HttpUser, task, between
import json

class StockTickerUser(HttpUser):
    """Locust user class for testing the Stock Ticker API"""
    
    # Base URL for the API
    host = "https://q12h96ifp0.execute-api.us-east-1.amazonaws.com"
    
    # Wait time between tasks (200ms = 0.2 seconds)
    wait_time = between(0.2, 0.2)  # Fixed 200ms delay
    
    # List of stock symbols to test
    stock_symbols = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", 
        "LLY", "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL",
        "ADBE", "CRM", "INTC", "CMCSA", "PFE", "TMO", "ABT", "COST", "PEP",
        "ABBV", "ACN", "DHR", "VZ", "NKE", "TXN", "QCOM", "NEE", "HON"
    ]
    
    def on_start(self):
        """Called when a user starts"""
        print(f"🚀 Starting load test for user")
    
    @task(3)
    def test_stock_quote_with_symbol(self):
        """Test API with specific stock symbol (75% of requests)"""
        symbol = random.choice(self.stock_symbols)
        endpoint = f"/DEV/quote/{symbol}"
        
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
    
    @task(1)
    def test_stock_quote_default(self):
        """Test API with default symbol (25% of requests)"""
        endpoint = "/DEV/quote/AAPL"  # Default symbol
        
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "current_price" in data and data["current_price"] is not None:
                        response.success()
                        print(f"✅ AAPL (default): ${data['current_price']}")
                    else:
                        response.failure("Invalid response format for default symbol")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response for default symbol")
            else:
                response.failure(f"HTTP {response.status_code} for default symbol")
    
    @task(1)
    def test_cors_preflight(self):
        """Test CORS preflight OPTIONS request"""
        symbol = random.choice(self.stock_symbols)
        endpoint = f"/DEV/quote/{symbol}"
        
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        with self.client.options(endpoint, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                print(f"✅ CORS preflight successful for {symbol}")
            else:
                response.failure(f"CORS preflight failed with {response.status_code}")

class HighConcurrencyUser(StockTickerUser):
    """User class for high concurrency testing (2000 users)"""
    wait_time = between(0.1, 0.5)  # Faster requests for high concurrency

class SustainedLoadUser(StockTickerUser):
    """User class for sustained load testing (200 users with 200ms delay)"""
    wait_time = between(0.2, 0.2)  # Fixed 200ms delay as requested

# Configuration for different test scenarios
class LoadTestConfig:
    """Configuration class for different load test scenarios"""
    
    @staticmethod
    def get_high_concurrency_config():
        """Configuration for 2000 concurrent users test"""
        return {
            "users": 2000,
            "spawn_rate": 100,  # Spawn 100 users per second
            "run_time": "2m",   # Run for 2 minutes
            "user_class": HighConcurrencyUser
        }
    
    @staticmethod
    def get_sustained_load_config():
        """Configuration for 200 users with 200ms delay test"""
        return {
            "users": 200,
            "spawn_rate": 20,   # Spawn 20 users per second
            "run_time": "5m",   # Run for 5 minutes
            "user_class": SustainedLoadUser
        }

if __name__ == "__main__":
    print("🌍 Global Stock Ticker - Load Test Script")
    print("=" * 50)
    print("Available test scenarios:")
    print("1. High Concurrency: 2000 users")
    print("2. Sustained Load: 200 users with 200ms delay")
    print("\nTo run the tests, use:")
    print("locust -f load_test.py --users 2000 --spawn-rate 100 --run-time 2m")
    print("locust -f load_test.py --users 200 --spawn-rate 20 --run-time 5m")
    print("\nOr run with web UI:")
    print("locust -f load_test.py --web-host 0.0.0.0 --web-port 8089")
