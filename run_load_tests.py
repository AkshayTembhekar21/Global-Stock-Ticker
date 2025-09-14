#!/usr/bin/env python3
"""
Load Test Runner for Stock Ticker API
Provides easy commands to run different load test scenarios
"""

import subprocess
import sys
import time
import argparse

def run_command(command, description):
    """Run a command and display results"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run load tests for Stock Ticker API")
    parser.add_argument("--test", choices=["burst", "sustained", "web"], 
                       default="web", help="Type of test to run")
    parser.add_argument("--users", type=int, default=2000, help="Number of users")
    parser.add_argument("--spawn-rate", type=int, default=100, help="Spawn rate")
    parser.add_argument("--run-time", default="2m", help="Run time (e.g., 2m, 30s)")
    
    args = parser.parse_args()
    
    print("🌍 Stock Ticker API - Load Test Runner")
    print("=" * 50)
    print(f"API: https://q12h96ifp0.execute-api.us-east-1.amazonaws.com/PROD/quote/LLY")
    
    if args.test == "burst":
        # Burst test: 2000 concurrent requests
        command = f"locust -f stock_api_load_test.py --users 2000 --spawn-rate 2000 --run-time 30s --headless"
        run_command(command, "Burst Load Test (2000 concurrent requests)")
        
    elif args.test == "sustained":
        # Sustained test: 200 users with 200ms delay
        command = f"locust -f stock_api_load_test.py --users 200 --spawn-rate 20 --run-time 5m --headless"
        run_command(command, "Sustained Load Test (200 users, 200ms delay)")
        
    elif args.test == "web":
        # Web UI mode
        command = f"locust -f stock_api_load_test.py --web-host 0.0.0.0 --web-port 8089"
        print(f"\n🌐 Starting Locust Web UI...")
        print(f"Open your browser and go to: http://localhost:8089")
        print(f"Press Ctrl+C to stop the web server")
        print(f"\nCommand: {command}")
        print(f"{'='*60}")
        
        try:
            subprocess.run(command, shell=True)
        except KeyboardInterrupt:
            print("\n🛑 Web UI stopped by user")

if __name__ == "__main__":
    main()
