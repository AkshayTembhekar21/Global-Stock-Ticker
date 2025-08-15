import json
import urllib.request
import urllib.error
import boto3
import os
import time
import random

cached_api_key = None

def get_api_key():
    global cached_api_key
    if cached_api_key:
        return cached_api_key

    env_key = os.environ.get("FINNHUB_API_KEY")
    if env_key:
        cached_api_key = env_key
        return cached_api_key

    secret_name = os.environ.get("SECRET_NAME", "prod/finnhub/api_key")
    region_name = os.environ.get("AWS_REGION", "us-east-1")

    client = boto3.client("secretsmanager", region_name=region_name)
    resp = client.get_secret_value(SecretId=secret_name)
    secret_dict = json.loads(resp["SecretString"])
    cached_api_key = secret_dict["FINNHUB_API_KEY"]
    return cached_api_key

def _extract_symbol(event):
    if not isinstance(event, dict):
        return "AAPL"
    # direct invoke: {"symbol":"AAPL"}
    if "symbol" in event and isinstance(event["symbol"], str) and event["symbol"]:
        return event["symbol"]
    # API Gateway (HTTP API) proxy event
    q = event.get("queryStringParameters") or {}
    if isinstance(q, dict) and q.get("symbol"):
        return q["symbol"]
    return "AAPL"

def _call_finnhub(url, attempts=3, timeout=3):
    # simple retry with jitter for transient errors
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "quote-svc/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status >= 400:
                    raise urllib.error.HTTPError(url, response.status, "bad status", response.headers, None)
                return json.loads(response.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            if i == attempts - 1:
                raise
            time.sleep((2 ** i) * 0.2 + random.random() * 0.2)

def get_cors_headers(origin):
    # SECURE CORS - Only allow specific domains
    allowed_origins = [
        "https://yourdomain.com",  # Replace with your actual domain
        "https://app.yourdomain.com",  # Replace with your actual domain
        "http://localhost:3000",  # For local development
        "http://localhost:8080"   # For local development
    ]
    
    if origin in allowed_origins:
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600"
        }
    else:
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "null"  # Block unauthorized origins
        }

def lambda_handler(event, context):
    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        origin = event.get("headers", {}).get("origin", "")
        return {
            "statusCode": 200,
            "headers": get_cors_headers(origin),
            "body": ""
        }
    
    try:
        api_key = get_api_key()
        symbol = _extract_symbol(event)
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        data = _call_finnhub(url)

        body = {
            "symbol": symbol,
            "current_price": data.get("c"),
            "quote_data": data
        }
        
        # Get origin for CORS headers
        origin = event.get("headers", {}).get("origin", "")
        
        return {
            "statusCode": 200,
            "headers": get_cors_headers(origin),
            "body": json.dumps(body)
        }
    except Exception as e:
        # Get origin for CORS headers
        origin = event.get("headers", {}).get("origin", "")
        
        return {
            "statusCode": 500,
            "headers": get_cors_headers(origin),
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    # local test
    os.environ["FINNHUB_API_KEY"] = os.environ.get("FINNHUB_API_KEY", "PUT_YOUR_KEY_WHEN_TESTING_LOCALLY")
    print(lambda_handler({"symbol": "AAPL"}, None)) 