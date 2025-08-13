#!/usr/bin/env python3
"""
Test script for the stock ticker functionality.
This script tests the core functions without making actual API calls.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from stock_ticker import get_api_key, get_stock_quote, lambda_handler

class TestStockTicker(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear any cached API key
        import stock_ticker
        stock_ticker.cached_api_key = None
        
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'FINNHUB_API_KEY': 'test_api_key_12345',
            'AWS_REGION': 'us-east-1',
            'SECRET_NAME': 'test/finnhub/api_key'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_get_api_key_local(self):
        """Test getting API key from environment variable."""
        api_key = get_api_key()
        self.assertEqual(api_key, 'test_api_key_12345')
    
    @patch('boto3.client')
    def test_get_api_key_aws(self, mock_boto_client):
        """Test getting API key from AWS Secrets Manager."""
        # Clear environment variable to force AWS lookup
        with patch.dict(os.environ, {}, clear=True):
            # Mock AWS Secrets Manager response
            mock_client = MagicMock()
            mock_response = {
                'SecretString': json.dumps({'FINNHUB_API_KEY': 'aws_api_key_67890'})
            }
            mock_client.get_secret_value.return_value = mock_response
            mock_boto_client.return_value = mock_client
            
            api_key = get_api_key()
            self.assertEqual(api_key, 'aws_api_key_67890')
    
    @patch('requests.get')
    def test_get_stock_quote_success(self, mock_get):
        """Test successful stock quote retrieval."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'c': 150.25,  # current price
            'd': 2.50,    # change
            'dp': 1.69,   # change percent
            'h': 152.00,  # high
            'l': 148.75,  # low
            'o': 149.50,  # open
            'pc': 147.75  # previous close
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        quote_data = get_stock_quote('AAPL')
        
        self.assertEqual(quote_data['symbol'], 'AAPL')
        self.assertEqual(quote_data['current_price'], 150.25)
        self.assertEqual(quote_data['change'], 2.50)
        self.assertEqual(quote_data['change_percent'], 1.69)
        self.assertEqual(quote_data['high_price'], 152.00)
        self.assertEqual(quote_data['low_price'], 148.75)
        self.assertEqual(quote_data['open_price'], 149.50)
        self.assertEqual(quote_data['previous_close'], 147.75)
    
    @patch('requests.get')
    def test_get_stock_quote_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = Exception("API request failed")
        
        with self.assertRaises(Exception) as context:
            get_stock_quote('INVALID')
        
        self.assertIn("API request failed", str(context.exception))
    
    def test_lambda_handler_success(self):
        """Test successful Lambda handler execution."""
        with patch('stock_ticker.get_stock_quote') as mock_get_quote:
            mock_get_quote.return_value = {
                'symbol': 'AAPL',
                'current_price': 150.25,
                'change': 2.50,
                'change_percent': 1.69
            }
            
            event = {'symbol': 'AAPL'}
            result = lambda_handler(event, None)
            
            self.assertEqual(result['statusCode'], 200)
            body = json.loads(result['body'])
            self.assertEqual(body['symbol'], 'AAPL')
            self.assertEqual(body['current_price'], 150.25)
    
    def test_lambda_handler_default_symbol(self):
        """Test Lambda handler with default symbol."""
        with patch('stock_ticker.get_stock_quote') as mock_get_quote:
            mock_get_quote.return_value = {
                'symbol': 'AAPL',
                'current_price': 150.25
            }
            
            event = {}  # No symbol provided
            result = lambda_handler(event, None)
            
            self.assertEqual(result['statusCode'], 200)
            body = json.loads(result['body'])
            self.assertEqual(body['symbol'], 'AAPL')
    
    def test_lambda_handler_error(self):
        """Test Lambda handler error handling."""
        with patch('stock_ticker.get_stock_quote') as mock_get_quote:
            mock_get_quote.side_effect = Exception("Test error")
            
            event = {'symbol': 'INVALID'}
            result = lambda_handler(event, None)
            
            self.assertEqual(result['statusCode'], 500)
            body = json.loads(result['body'])
            self.assertIn('error', body)
            self.assertIn('Test error', body['error'])

def run_tests():
    """Run the test suite."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockTicker)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("Running Stock Ticker Tests...")
    print("=" * 50)
    
    exit_code = run_tests()
    
    print("=" * 50)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    sys.exit(exit_code) 