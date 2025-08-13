"""
Configuration module for Global Stock Ticker.
Manages environment-specific settings and configurations.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # AWS Configuration
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    SECRET_NAME = os.environ.get("SECRET_NAME", "prod/finnhub/api_key")
    
    # API Configuration
    FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
    API_TIMEOUT = int(os.environ.get("API_TIMEOUT", "10"))
    
    # Environment
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "local")
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    
    # Cache settings
    CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))  # 5 minutes
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() in ["prod", "production"]
    
    @classmethod
    def is_local(cls) -> bool:
        """Check if running locally."""
        return cls.ENVIRONMENT.lower() in ["local", "dev", "development"]
    
    @classmethod
    def get_api_key_source(cls) -> str:
        """Get the source of the API key."""
        if cls.FINNHUB_API_KEY:
            return "environment"
        elif cls.is_production():
            return "aws_secrets_manager"
        else:
            return "not_configured"
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status."""
        status = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "environment": cls.ENVIRONMENT,
            "api_key_source": cls.get_api_key_source()
        }
        
        # Check required configurations
        if not cls.FINNHUB_API_KEY and cls.is_local():
            status["warnings"].append("FINNHUB_API_KEY not set for local development")
        
        if cls.is_production() and not cls.SECRET_NAME:
            status["errors"].append("SECRET_NAME must be set for production")
            status["valid"] = False
        
        # Check AWS configuration
        if cls.is_production():
            if not cls.AWS_REGION:
                status["errors"].append("AWS_REGION must be set for production")
                status["valid"] = False
        
        return status

def print_config_status():
    """Print current configuration status."""
    print("🔧 Configuration Status")
    print("=" * 40)
    
    status = Config.validate()
    
    print(f"Environment: {status['environment']}")
    print(f"API Key Source: {status['api_key_source']}")
    print(f"Valid: {'✅ Yes' if status['valid'] else '❌ No'}")
    
    if status['errors']:
        print("\n❌ Errors:")
        for error in status['errors']:
            print(f"   - {error}")
    
    if status['warnings']:
        print("\n⚠️  Warnings:")
        for warning in status['warnings']:
            print(f"   - {warning}")
    
    if status['valid']:
        print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Configuration has errors. Please fix them before proceeding.")

if __name__ == "__main__":
    print_config_status() 