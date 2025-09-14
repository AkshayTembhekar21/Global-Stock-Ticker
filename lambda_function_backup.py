import json
import boto3
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError
import requests
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Circuit breaker for Finnhub API calls
finnhub_breaker = CircuitBreaker(
    fail_max=5,           # Open circuit after 5 failures
    reset_timeout=60,      # Wait 60 seconds before trying again
    exclude=[RequestException]  # Exclude these exceptions from counting as failures
)

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
    
    # API Gateway REST API with path parameters: /quote/{symbol}
    if "pathParameters" in event and event["pathParameters"]:
        symbol = event["pathParameters"].get("symbol")
        if symbol:
            return symbol
    
    # API Gateway with query parameters: /quote?symbol=TSLA
    q = event.get("queryStringParameters") or {}
    if isinstance(q, dict) and q.get("symbol"):
        return q["symbol"]
    
    return "AAPL"

@finnhub_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RequestException, Timeout))
)
def _call_finnhub(url, timeout=5):
    """Call Finnhub API with automatic retries and circuit breaker protection."""
    response = requests.get(
        url, 
        timeout=timeout,
        headers={"User-Agent": "quote-svc/1.0"}
    )
    response.raise_for_status()  # Raises HTTPError for bad status codes
    return response.json()

def get_cors_headers(origin):
    # OPEN CORS - Allow all origins for now (development/testing)
    # TODO: Restrict to specific domains in production
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin if origin else "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600"
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
        
        try:
            data = _call_finnhub(url)
        except CircuitBreakerError:
            # Circuit is open - return cached data or error
            return {
                "statusCode": 503,
                "headers": get_cors_headers(event.get("headers", {}).get("origin", "")),
                "body": json.dumps({
                    "error": "Service temporarily unavailable - circuit breaker open",
                    "symbol": symbol
                })
            }

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