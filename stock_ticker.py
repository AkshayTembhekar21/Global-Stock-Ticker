import json
import urllib.request
import boto3
import os
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Cache secret so we don't fetch it on every invocation
cached_api_key = None

def get_api_key() -> str:
    """
    Get the Finnhub API key from AWS Secrets Manager or environment variable.
    Falls back to environment variable for local development.
    """
    global cached_api_key
    if cached_api_key:
        return cached_api_key
    
    # Check if running locally with direct API key
    local_api_key = os.environ.get("FINNHUB_API_KEY")
    if local_api_key:
        cached_api_key = local_api_key
        return cached_api_key
    
    # Try to get from AWS Secrets Manager
    try:
        secret_name = os.environ.get("SECRET_NAME", "prod/finnhub/api_key")
        region_name = os.environ.get("AWS_REGION", "us-east-1")

        # Create Secrets Manager client
        client = boto3.client("secretsmanager", region_name=region_name)

        # Retrieve secret
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(get_secret_value_response["SecretString"])
        
        cached_api_key = secret_dict["FINNHUB_API_KEY"]
        return cached_api_key
    except Exception as e:
        raise Exception(f"Failed to retrieve API key: {str(e)}")

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    Get stock quote data from Finnhub API.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing stock quote data
    """
    api_key = get_api_key()
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    try:
        # Use requests for better error handling and local development
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "symbol": symbol,
            "current_price": data.get("c"),
            "change": data.get("d"),
            "change_percent": data.get("dp"),
            "high_price": data.get("h"),
            "low_price": data.get("l"),
            "open_price": data.get("o"),
            "previous_close": data.get("pc"),
            "quote_data": data
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse API response: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event object
        context: Lambda context object
    
    Returns:
        Dict with statusCode and body
    """
    try:
        symbol = event.get("symbol", "AAPL")
        quote_data = get_stock_quote(symbol)
        
        return {
            "statusCode": 200,
            "body": json.dumps(quote_data)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def main():
    """
    Main function for local execution.
    """
    import sys
    
    # Get symbol from command line argument or use default
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    
    try:
        print(f"Fetching stock quote for {symbol}...")
        quote_data = get_stock_quote(symbol)
        
        print(f"\nStock Quote for {symbol}:")
        print(f"Current Price: ${quote_data['current_price']:.2f}")
        print(f"Change: ${quote_data['change']:.2f} ({quote_data['change_percent']:.2f}%)")
        print(f"High: ${quote_data['high_price']:.2f}")
        print(f"Low: ${quote_data['low_price']:.2f}")
        print(f"Open: ${quote_data['open_price']:.2f}")
        print(f"Previous Close: ${quote_data['previous_close']:.2f}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 