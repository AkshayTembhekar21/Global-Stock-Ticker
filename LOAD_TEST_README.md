# Load Testing for Stock Ticker API

This directory contains load testing scripts for the Global Stock Ticker API using Locust.

## API Endpoint
- **URL**: https://q12h96ifp0.execute-api.us-east-1.amazonaws.com/DEV/quote/LLY
- **Method**: GET
- **Response**: JSON with stock quote data

## Test Scenarios

### 1. Burst Test (2000 Concurrent Requests)
- **Users**: 2000 concurrent users
- **Spawn Rate**: 2000 users per second
- **Duration**: 30 seconds
- **Purpose**: Test API's ability to handle sudden high load

### 2. Sustained Load Test (200 Users with 200ms Delay)
- **Users**: 200 concurrent users
- **Spawn Rate**: 20 users per second
- **Wait Time**: 200ms between requests
- **Duration**: 5 minutes
- **Purpose**: Test API's performance under sustained load

## Files

- `stock_api_load_test.py` - Main load test script
- `load_test.py` - General load test with multiple scenarios
- `run_load_tests.py` - Test runner script
- `locust.conf` - Locust configuration file
- `LOAD_TEST_README.md` - This documentation

## Quick Start

### 1. Install Dependencies
```bash
pip install locust
```

### 2. Run Tests

#### Option A: Using the Test Runner
```bash
# Burst test (2000 concurrent)
python run_load_tests.py --test burst

# Sustained test (200 users, 200ms delay)
python run_load_tests.py --test sustained

# Web UI (interactive)
python run_load_tests.py --test web
```

#### Option B: Direct Locust Commands
```bash
# Burst test
locust -f stock_api_load_test.py --users 2000 --spawn-rate 2000 --run-time 30s --headless

# Sustained test
locust -f stock_api_load_test.py --users 200 --spawn-rate 20 --run-time 5m --headless

# Web UI
locust -f stock_api_load_test.py --web-host 0.0.0.0 --web-port 8089
```

#### Option C: Using Configuration File
```bash
# Burst test
locust -f stock_api_load_test.py -c locust.conf --burst-test

# Sustained test
locust -f stock_api_load_test.py -c locust.conf --sustained-test

# Web UI
locust -f stock_api_load_test.py -c locust.conf --web-test
```

## Web UI

When running in web mode, open your browser and go to:
- **URL**: http://localhost:8089
- **Features**: 
  - Real-time statistics
  - Interactive test configuration
  - Live charts and graphs
  - Downloadable reports

## Expected Results

### Burst Test (2000 Concurrent)
- **Target**: Handle 2000 simultaneous requests
- **Success Criteria**: < 5% error rate, < 2s average response time
- **Expected Behavior**: API should handle the burst gracefully

### Sustained Test (200 Users, 200ms Delay)
- **Target**: 200 users making requests every 200ms
- **Success Criteria**: < 1% error rate, < 1s average response time
- **Expected Behavior**: Consistent performance over 5 minutes

## Monitoring

The tests will display:
- ✅ Successful requests with stock prices
- ❌ Failed requests with error details
- 📊 Real-time statistics
- 📈 Performance metrics

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Check if the API endpoint is accessible
   - Verify network connectivity

2. **High Error Rates**
   - API might be rate-limited
   - Reduce concurrent users
   - Increase wait time between requests

3. **Memory Issues**
   - Reduce number of users
   - Use headless mode for large tests

### Performance Tuning

- **For High Concurrency**: Use `BurstLoadUser` class
- **For Sustained Load**: Use `SustainedLoadUser` class
- **For Custom Scenarios**: Modify the user classes in the script

## API Response Format

```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "3600"
  },
  "body": "{\"symbol\": \"LLY\", \"current_price\": 234.07, \"quote_data\": {...}}"
}
```

## Notes

- The API supports CORS for web applications
- Default symbol is AAPL if no symbol is provided
- The API uses AWS Lambda with API Gateway
- Response times may vary based on AWS Lambda cold starts
