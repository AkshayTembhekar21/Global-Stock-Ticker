import json
import urllib.request
import boto3
import os
import requests
from dotenv import load_dotenv

# Load environment variables for local development
load_dotenv()

# Cache secret so we don't fetch it on every invocation
cached_api_key = None

def get_api_key():
    """Get the Finnhub API key from AWS Secrets Manager or environment variable."""
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

def main(symbol="AAPL"):
    """Main function to get stock quote data."""
    api_key = get_api_key()
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse API response: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error: {str(e)}")

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        # Get symbol from event or default to AAPL
        symbol = event.get("symbol", "AAPL") if isinstance(event, dict) else "AAPL"
        data = main(symbol)
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "symbol": symbol,
                "current_price": data["c"],
                "change": data.get("d"),
                "change_percent": data.get("dp"),
                "high_price": data.get("h"),
                "low_price": data.get("l"),
                "open_price": data.get("o"),
                "previous_close": data.get("pc"),
                "quote_data": data
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    # Running locally
    print("🌍 Global Stock Ticker - Local Execution")
    print("=" * 40)
    
    try:
        test_symbol = input("Enter stock symbol (default AAPL): ") or "AAPL"
        print(f"\n📈 Fetching data for {test_symbol}...")
        
        result = main(test_symbol)
        
        print(f"\n✅ Stock Quote for {test_symbol}:")
        print(f"Current Price: ${result['c']:.2f}")
        if 'd' in result:
            print(f"Change: ${result['d']:.2f} ({result.get('dp', 0):.2f}%)")
        if 'h' in result:
            print(f"High: ${result['h']:.2f}")
        if 'l' in result:
            print(f"Low: ${result['l']:.2f}")
        if 'o' in result:
            print(f"Open: ${result['o']:.2f}")
        if 'pc' in result:
            print(f"Previous Close: ${result['pc']:.2f}")
        
        print(f"\n📊 Full Quote Data:")
        print(json.dumps({
            "symbol": test_symbol,
            "current_price": result["c"],
            "quote_data": result
        }, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure you have FINNHUB_API_KEY in your .env file")
        print("2. Or ensure AWS credentials are configured for Secrets Manager")
        print("3. Check your internet connection") 