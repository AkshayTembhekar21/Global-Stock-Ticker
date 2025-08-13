# 🚀 Complete Setup Instructions for CI/CD Pipeline

## What We've Created

1. **`.github/workflows/deploy.yml`** - GitHub Actions CI/CD pipeline
2. **`lambda_function.py`** - Your Lambda function code
3. **`requirements.txt`** - Local development dependencies
4. **`env.example`** - Environment variables template
5. **`test_local.py`** - Local testing script

## Step-by-Step Setup

### Step 1: Set Up GitHub Secrets

Go to your GitHub repository: https://github.com/AkshayTembhekar21/Global-Stock-Ticker

1. Click on **Settings** tab
2. Click on **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these 3 secrets:

**Secret 1:**
- Name: `AWS_ACCESS_KEY_ID`
- Value: `AKIAZ4PGZQWRO7RWCW45`

**Secret 2:**
- Name: `AWS_SECRET_ACCESS_KEY`
- Value: `[Your AWS Secret Access Key]`

**Secret 3:**
- Name: `FINNHUB_API_KEY`
- Value: `d2d6jn1r01qjem5jb400d2d6jn1r01qjem5jb40g`

### Step 2: Set Up Local Environment

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create .env file:**
   ```bash
   cp env.example .env
   # Edit .env and add your API key
   ```

3. **Test locally:**
   ```bash
   python test_local.py
   ```

### Step 3: Push Code to GitHub

1. **Add all files:**
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline and Lambda function"
   git push origin main
   ```

2. **Check GitHub Actions:**
   - Go to **Actions** tab in your repository
   - You should see the deployment workflow running

## How the CI/CD Pipeline Works

### What Happens on Every Commit:

1. **Checkout Code** - Downloads your latest code
2. **Setup Python 3.13** - Matches your Lambda runtime
3. **Install boto3** - For AWS SDK functionality
4. **Test Locally** - Runs your code to ensure it works
5. **Create Package** - Zips code + dependencies
6. **Deploy to Lambda** - Updates your GetStockPrice function

### Automatic Deployment:

- **Every push to main branch** triggers deployment
- **Tests run first** - only deploys if tests pass
- **Updates your Lambda function** automatically
- **Uses your exact configuration** (GetStockPrice, us-east-1)

## Testing Your Setup

### Local Testing:
```bash
python test_local.py
```

### Lambda Testing:
After deployment, test your function URL:
```
https://4vfidwlwzb7l6lms24ufgphjoe0ylkjd.lambda-url.us-east-1.on.aws/
```

## Troubleshooting

### If GitHub Actions Fail:
1. Check **Actions** tab for error details
2. Verify all 3 secrets are set correctly
3. Ensure your AWS credentials have proper permissions

### If Local Testing Fails:
1. Check your `.env` file has the correct API key
2. Verify boto3 is installed: `pip install boto3`
3. Check your internet connection

## What You Get

✅ **Automatic deployment** on every code commit
✅ **Local testing** before deployment
✅ **Exact match** with your Lambda configuration
✅ **Zero manual deployment** needed
✅ **Professional CI/CD pipeline**

## Next Steps

1. Set up the GitHub secrets
2. Test locally with `python test_local.py`
3. Push code to GitHub
4. Watch the automatic deployment happen!

Your Lambda function will automatically update every time you commit code. No more manual deployments! 