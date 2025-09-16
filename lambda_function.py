import json
import boto3
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError
import requests
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        logger.info(" Using cached API key (first 8 chars): %s", cached_api_key[:8] + "..." if cached_api_key else "None")
        return cached_api_key

    env_key = os.environ.get("FINNHUB_API_KEY")
    if env_key:
        logger.info(" Found API key in environment variable (first 8 chars): %s", env_key[:8] + "...")
        cached_api_key = env_key
        return cached_api_key

    secret_name = os.environ.get("SECRET_NAME", "prod/finnhub/api_key")
    region_name = os.environ.get("AWS_REGION", "us-east-1")
    
    logger.info(" Secrets Manager config - Secret: %s, Region: %s", secret_name, region_name)

    try:
        client = boto3.client("secretsmanager", region_name=region_name)
        
        resp = client.get_secret_value(SecretId=secret_name)
        
        secret_dict = json.loads(resp["SecretString"])
        cached_api_key = secret_dict["FINNHUB_API_KEY"]
        
        logger.info(" Successfully retrieved API key from Secrets Manager (first 8 chars): %s", cached_api_key[:8] + "...")
        return cached_api_key
        
    except Exception as e:
        logger.error(" Failed to retrieve API key from Secrets Manager: %s", str(e))
        raise

def _extract_symbol(event):
    logger.info("Incoming Event : %s", event)
    
    if not isinstance(event, dict):
        logger.warning(" Event is not a dictionary, using default symbol AAPL")
        return "AAPL"
    
    # direct invoke: {"symbol":"AAPL"}
    if "symbol" in event and isinstance(event["symbol"], str) and event["symbol"]:
        logger.info(" Found symbol in direct event: %s", event["symbol"])
        return event["symbol"]
    
    # API Gateway REST API with path parameters: /quote/{symbol}
    if "pathParameters" in event and event["pathParameters"]:
        symbol = event["pathParameters"].get("symbol")
        if symbol:
            logger.info(" Found symbol in pathParameters: %s", symbol)
            return symbol
        else:
            logger.info(" pathParameters exists but no symbol found: %s", event["pathParameters"])
    else:
        logger.info(" No pathParameters in event")
    
    # API Gateway with query parameters: /quote?symbol=TSLA
    q = event.get("queryStringParameters") or {}
    if isinstance(q, dict) and q.get("symbol"):
        logger.info(" Found symbol in queryStringParameters: %s", q.get("symbol"))
        return q["symbol"]
    else:
        logger.info(" No symbol in queryStringParameters: %s", q)
    
    logger.info(" No symbol found, using default: AAPL")
    return "AAPL"

@finnhub_breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RequestException, Timeout))
)
def _call_finnhub(url, timeout=5):
    """Call Finnhub API with automatic retries and circuit breaker protection."""
    logger.info(" Making request to Finnhub API")
    logger.info(" URL (masked): %s", url.replace(url.split('token=')[1] if 'token=' in url else '', '***MASKED***'))
    logger.info(" Timeout: %s seconds", timeout)
    
    try:
        response = requests.get(
            url, 
            timeout=timeout,
            headers={"User-Agent": "quote-svc/1.0"}
        )
        
        logger.info(" Response status code: %s", response.status_code)
        logger.info(" Response headers: %s", dict(response.headers))
        
        response.raise_for_status()  # Raises HTTPError for bad status codes
        
        data = response.json()
        logger.info(" Successfully received data from Finnhub API")
        logger.info(" Response data keys: %s", list(data.keys()) if isinstance(data, dict) else "Not a dict")
        
        return data
        
    except Timeout as e:
        logger.error(" Request timeout after %s seconds: %s", timeout, str(e))
        raise
    except RequestException as e:
        logger.error(" Request failed: %s", str(e))
        raise
    except Exception as e:
        logger.error(" Unexpected error in _call_finnhub: %s", str(e))
        raise

def get_cors_headers(origin):
    logger.info(" Setting up CORS headers for origin: %s", origin if origin else "None")
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": origin if origin else "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600"
    }
    logger.info(" CORS headers: %s", headers)
    return headers

def lambda_handler(event, context):
    logger.info(" Lambda function started")
    logger.info(" Event: %s", json.dumps(event, default=str)[:500] + "..." if len(str(event)) > 500 else json.dumps(event, default=str))
    logger.info(" Context: %s", str(context)[:200] + "..." if context and len(str(context)) > 200 else str(context))
    
    # Handle preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        logger.info(" Handling OPTIONS preflight request")
        origin = event.get("headers", {}).get("origin", "")
        logger.info(" Origin for OPTIONS: %s", origin)
        
        response = {
            "statusCode": 200,
            "headers": get_cors_headers(origin),
            "body": ""
        }
        logger.info(" OPTIONS response: %s", response)
        return response
    
    try:
        api_key = get_api_key()
        
        symbol = _extract_symbol(event)
        logger.info(" Using symbol: %s", symbol)
        
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        logger.info(" Constructed Finnhub URL (masked): %s", url.replace(api_key, "***MASKED***"))
        
        try:
            data = _call_finnhub(url)
            logger.info(" Successfully received data from Finnhub")
            
        except CircuitBreakerError as e:
            logger.error(" Circuit breaker is OPEN - Finnhub service unavailable")
            logger.error(" Circuit breaker error: %s", str(e))
            
            # Circuit is open - return cached data or error
            response = {
                "statusCode": 503,
                "headers": get_cors_headers(event.get("headers", {}).get("origin", "")),
                "body": json.dumps({
                    "error": "Service temporarily unavailable - circuit breaker open",
                    "symbol": symbol
                })
            }
            logger.info(" Returning 503 response: %s", response)
            return response

        body = {
            "symbol": symbol,
            "current_price": data.get("c"),
            "quote_data": data
        }
        logger.info(" Response body: %s", json.dumps(body, default=str))
        
        # Get origin for CORS headers
        origin = event.get("headers", {}).get("origin", "")
        logger.info(" Origin for response: %s", origin)
        
        response = {
            "statusCode": 200,
            "headers": get_cors_headers(origin),
            "body": json.dumps(body)
        }
        
        logger.info(" Successfully processed request")
        return response
        
    except Exception as e:
        logger.error(" Unexpected error in lambda_handler: %s", str(e))
        logger.error(" Error type: %s", type(e).__name__)
        logger.error(" Full error details: %s", str(e))
        
        # Get origin for CORS headers
        origin = event.get("headers", {}).get("origin", "")
        
        response = {
            "statusCode": 500,
            "headers": get_cors_headers(origin),
            "body": json.dumps({"error": str(e)})
        }
        
        logger.error(" Returning 500 error response: %s", response)
        return response

if __name__ == "__main__":
    # local test
    logger.info(" Running local test")
    os.environ["FINNHUB_API_KEY"] = os.environ.get("FINNHUB_API_KEY", "PUT_YOUR_KEY_WHEN_TESTING_LOCALLY")
    result = lambda_handler({"symbol": "AAPL"}, None)
    print(" Local test result:", result)
