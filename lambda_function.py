import json
import urllib.request
import boto3
import os

# Cache secret so we don't fetch it on every invocation
cached_api_key = None

def get_api_key():
    global cached_api_key
    if cached_api_key:
        return cached_api_key
    
    # First, try to get API key from environment variable (for local testing)
    local_api_key = os.environ.get("FINNHUB_API_KEY")
    if local_api_key:
        cached_api_key = local_api_key
        return cached_api_key
    
    # If no environment variable, try AWS Secrets Manager (for Lambda execution)
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

def lambda_handler(event, context):
    api_key = get_api_key()
    symbol = event.get("symbol", "AAPL")
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "symbol": symbol,
                "current_price": data["c"],
                "quote_data": data
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

# For local testing
if __name__ == "__main__":
    # Test locally
    print("Testing stock ticker locally...")
    
    # Set a test event
    test_event = {"symbol": "AAPL"}
    
    # Call lambda handler
    result = lambda_handler(test_event, None)
    
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {result['body']}") 