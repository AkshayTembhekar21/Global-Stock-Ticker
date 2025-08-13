#!/usr/bin/env python3
"""
Deployment script for AWS Lambda function.
This script packages the application and deploys it to AWS Lambda.
"""

import os
import sys
import zipfile
import shutil
import subprocess
import argparse
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and handle errors."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        if check:
            sys.exit(1)
        return e

def check_aws_cli():
    """Check if AWS CLI is installed and configured."""
    result = run_command("aws --version", check=False)
    if result.returncode != 0:
        print("❌ AWS CLI is not installed or not in PATH")
        print("Please install AWS CLI: https://aws.amazon.com/cli/")
        sys.exit(1)
    
    result = run_command("aws sts get-caller-identity", check=False)
    if result.returncode != 0:
        print("❌ AWS CLI is not configured")
        print("Please run: aws configure")
        sys.exit(1)
    
    print("✅ AWS CLI is configured")
    return True

def create_package():
    """Create deployment package."""
    print("📦 Creating deployment package...")
    
    # Clean up previous package
    package_dir = Path("package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir()
    
    # Install dependencies
    print("Installing dependencies...")
    run_command(f"pip install -r requirements.txt -t {package_dir}")
    
    # Copy source files
    print("Copying source files...")
    shutil.copy("stock_ticker_simple.py", package_dir)
    shutil.copy("lambda_function.py", package_dir)
    
    # Create zip file
    print("Creating zip file...")
    zip_path = Path("lambda_deployment.zip")
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Package created: {zip_path}")
    return zip_path

def deploy_lambda(function_name, role_arn, runtime="python3.9", region="us-east-1"):
    """Deploy Lambda function."""
    print(f"🚀 Deploying Lambda function: {function_name}")
    
    zip_path = Path("lambda_deployment.zip")
    if not zip_path.exists():
        print("❌ Deployment package not found. Run with --package-only first.")
        sys.exit(1)
    
    # Check if function exists
    result = run_command(f"aws lambda get-function --function-name {function_name} --region {region}", check=False)
    
    if result.returncode == 0:
        # Function exists, update it
        print("Updating existing function...")
        run_command(f"aws lambda update-function-code --function-name {function_name} --zip-file fileb://{zip_path} --region {region}")
        run_command(f"aws lambda update-function-configuration --function-name {function_name} --runtime {runtime} --region {region}")
    else:
        # Function doesn't exist, create it
        print("Creating new function...")
        run_command(f"aws lambda create-function --function-name {function_name} --runtime {runtime} --role {role_arn} --handler lambda_function.lambda_handler --zip-file fileb://{zip_path} --region {region}")
    
    print(f"✅ Lambda function '{function_name}' deployed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Deploy Stock Ticker to AWS Lambda")
    parser.add_argument("--package-only", action="store_true", help="Only create package, don't deploy")
    parser.add_argument("--function-name", default="stock-ticker", help="Lambda function name")
    parser.add_argument("--role-arn", required=True, help="IAM role ARN for Lambda execution")
    parser.add_argument("--runtime", default="python3.9", help="Python runtime version")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    
    args = parser.parse_args()
    
    print("🌍 Global Stock Ticker - Lambda Deployment")
    print("=" * 50)
    
    # Check prerequisites
    check_aws_cli()
    
    # Create package
    package_path = create_package()
    
    if args.package_only:
        print("📦 Package created successfully. Use --deploy to deploy to Lambda.")
        return
    
    # Deploy to Lambda
    deploy_lambda(args.function_name, args.role_arn, args.runtime, args.region)
    
    print("\n🎉 Deployment completed successfully!")
    print(f"Function: {args.function_name}")
    print(f"Region: {args.region}")
    print(f"Runtime: {args.runtime}")
    print("\nYou can now test your function:")
    print(f"aws lambda invoke --function-name {args.function_name} --payload '{{\"symbol\":\"AAPL\"}}' --region {args.region} response.json")

if __name__ == "__main__":
    main() 