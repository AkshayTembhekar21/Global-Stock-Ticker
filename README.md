# Global Stock Ticker

A Python application that fetches real-time stock quotes from the Finnhub API. This project can run both locally for development and on AWS Lambda for production deployment.

## 🚀 Quick Start (Simplified Version)

For a quick start with the simplified approach (similar to ChatGPT's recommendation):

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your API key
cp env.example .env
# Edit .env and add your FINNHUB_API_KEY

# Run the simplified version
python stock_ticker_simple.py

# Test the lambda handler locally
python test_simple.py
```

## 📁 Project Structure

The project includes two main approaches:

### **Simplified Version** (Recommended for most users)
- **`stock_ticker_simple.py`** - Single file that handles both local and Lambda execution
- **`lambda_function.py`** - Lambda entry point for the simplified version
- **`test_simple.py`** - Simple tests for the simplified version

### **Comprehensive Version** (For advanced users)
- **`stock_ticker.py`** - Full-featured module with enhanced functionality
- **`test_stock_ticker.py`** - Comprehensive unit tests with mocking
- **`config.py`** - Configuration management
- **`demo.py`** - Feature demonstration script

## Features

- Real-time stock quote data from Finnhub API
- Support for any stock symbol (e.g., AAPL, MSFT, GOOGL)
- AWS Secrets Manager integration for secure API key storage
- Local development support with environment variables
- Comprehensive error handling and logging
- AWS Lambda ready
- **Two approaches**: Simplified single-file and comprehensive modular

## Prerequisites

- Python 3.8 or higher
- AWS CLI configured (for Lambda deployment)
- Finnhub API key
- AWS Secrets Manager access (for production)

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Global-Stock-Ticker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

## Configuration

### Local Development

Create a `.env` file with your configuration:

```bash
# For local development, you can set the API key directly
FINNHUB_API_KEY=your_api_key_here

# Or use AWS Secrets Manager
AWS_REGION=us-east-1
SECRET_NAME=prod/finnhub/api_key
```

### AWS Lambda

The Lambda function will automatically use AWS Secrets Manager to retrieve the API key. Ensure your Lambda execution role has the necessary permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:prod/finnhub/api_key*"
        }
    ]
}
```

## Usage

### Local Execution

#### Simplified Version (Recommended)
```bash
# Interactive mode - prompts for symbol
python stock_ticker_simple.py

# Or use the main function programmatically
python -c "
from stock_ticker_simple import main
result = main('AAPL')
print(f'AAPL: ${result[\"c\"]}')
"
```

#### Comprehensive Version
```bash
# Get quote for default symbol (AAPL)
python stock_ticker.py

# Get quote for specific symbol
python stock_ticker.py MSFT
python stock_ticker.py GOOGL

# Run demo
python demo.py
```

### AWS Lambda

Deploy to AWS Lambda using the `lambda_function.py` file. The function expects an event with an optional `symbol` parameter:

```json
{
    "symbol": "AAPL"
}
```

If no symbol is provided, it defaults to "AAPL".

## API Response Format

The API returns stock quote data in the following format:

```json
{
    "symbol": "AAPL",
    "current_price": 150.25,
    "change": 2.50,
    "change_percent": 1.69,
    "high_price": 152.00,
    "low_price": 148.75,
    "open_price": 149.50,
    "previous_close": 147.75,
    "quote_data": {
        "c": 150.25,
        "d": 2.50,
        "dp": 1.69,
        "h": 152.00,
        "l": 148.75,
        "o": 149.50,
        "pc": 147.75
    }
}
```

## Testing

### Simple Tests
```bash
# Test the simplified version
python test_simple.py
```

### Comprehensive Tests
```bash
# Run comprehensive unit tests
python test_stock_ticker.py
```

## Error Handling

The application includes comprehensive error handling for:
- API request failures
- Invalid API responses
- AWS Secrets Manager errors
- Network timeouts
- Invalid stock symbols

## Development

### Project Structure

```
Global-Stock-Ticker/
├── stock_ticker_simple.py    # Simplified version (recommended)
├── stock_ticker.py           # Comprehensive version
├── lambda_function.py        # Lambda entry point
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── test_simple.py           # Simple tests
├── test_stock_ticker.py     # Comprehensive tests
├── deploy.py                # Deployment script
├── demo.py                  # Feature demonstration
├── config.py                # Configuration management
├── README.md                # This file
└── .gitignore               # Git ignore file
```

## Deployment

### AWS Lambda

1. Create a deployment package:
```bash
python deploy.py --package-only
```

2. Deploy to AWS Lambda:
```bash
python deploy.py --role-arn YOUR_IAM_ROLE_ARN
```

Or use the deployment script:
```bash
python deploy.py --function-name stock-ticker --role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role
```

## Security

- API keys are stored securely in AWS Secrets Manager
- No hardcoded credentials in the code
- Environment-specific configuration
- Proper error handling to prevent information leakage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the error logs
- Verify your API key and permissions
- Ensure proper AWS configuration
- Check Finnhub API status

## Version Comparison

| Feature | Simplified | Comprehensive |
|---------|------------|---------------|
| **File Count** | 1 main file | Multiple modules |
| **Learning Curve** | Easy | Moderate |
| **Features** | Core functionality | Advanced features |
| **Testing** | Basic tests | Full unit tests |
| **Configuration** | Environment variables | Config management |
| **Best For** | Quick start, simple use | Production, enterprise |

**Recommendation**: Start with the simplified version (`stock_ticker_simple.py`) for most use cases. Use the comprehensive version when you need advanced features, better testing, or more modular architecture. 