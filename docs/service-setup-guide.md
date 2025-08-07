# Service Setup Guide

This guide will walk you through setting up all external services required for the Nifty/BankNifty Trading Bot.

## 🎯 Overview

We need to set up the following services:
1. ✅ **AWS Account** - Lambda functions and cloud services
2. ✅ **Supabase** - Database for storing trades and analytics
3. ✅ **Telegram Bot** - User interface and notifications
4. ✅ **Railway/Render** - Bot hosting (optional for Telegram bot)
5. ✅ **GitHub** - Repository and CI/CD

---

## 1. 🌩️ AWS Account Setup

### Step 1: Create AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process (requires credit card but won't be charged for free tier)
4. Choose **Basic Support Plan (Free)**

### Step 2: Configure Free Tier Services
Free tier limits (12 months):
- **Lambda**: 1M requests/month, 400,000 GB-seconds compute time
- **CloudWatch**: 10 custom metrics, 1M API requests
- **API Gateway**: 1M REST API calls (optional for our use)

### Step 3: Create IAM User for Bot
1. Go to **IAM > Users** in AWS Console
2. Click **Create User**
3. Username: `trading-bot-user`
4. Attach policies:
   - `AWSLambdaExecute`
   - `CloudWatchLogsFullAccess`
   - `AmazonS3ReadOnlyAccess` (for storing ML models later)

### Step 4: Get Access Keys
1. Click on the created user
2. Go to **Security credentials** tab
3. Click **Create access key**
4. Choose **Application running outside AWS**
5. **Save the Access Key ID and Secret Access Key** (you'll need these)

### ⚠️ Important Security Notes:
- Never commit AWS keys to GitHub
- Use environment variables only
- Enable MFA on your root account

---

## 2. 🗃️ Supabase Database Setup

### Step 1: Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click **Start your project**
3. Sign up with GitHub (recommended)

### Step 2: Create New Project
1. Click **New Project**
2. Project name: `nifty-trading-bot`
3. Database password: Generate a strong password and **save it**
4. Region: **Mumbai (ap-south-1)** or closest to you
5. Pricing plan: **Free tier** (500MB storage, 2 CPU hours)

### Step 3: Configure Database
1. Wait for project creation (2-3 minutes)
2. Go to **Settings > Database**
3. Note down:
   - **URL**: `https://your-project-ref.supabase.co`
   - **Anon key**: `eyJ...` (for client connections)
   - **Service role key**: `eyJ...` (for server/admin operations)

### Step 4: Run Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Copy contents of `config/database_schema.sql`
3. Paste and click **Run**
4. Verify tables are created in **Table Editor**

Expected tables:
- `trades` - All executed trades
- `positions` - Current open positions  
- `signals` - Generated trading signals
- `market_intelligence` - Scraped market data
- `performance_metrics` - Daily/weekly/monthly stats
- `risk_events` - Risk management events
- `system_logs` - Application logs
- `user_sessions` - User interaction tracking

---

## 3. 🤖 Telegram Bot Setup

### Step 1: Create Bot with BotFather
1. Open Telegram app
2. Search for `@BotFather`
3. Start conversation with `/start`
4. Create new bot: `/newbot`
5. Bot name: `Nifty Trading Bot` (or any name you like)
6. Bot username: `nifty_trading_bot_yourname` (must be unique)
7. **Save the Bot Token**: `1234567890:ABCDEF...`

### Step 2: Get Your User ID
1. Search for `@userinfobot` in Telegram
2. Start conversation
3. It will show your User ID: `123456789`
4. **Save this User ID** (only this user can control the bot)

### Step 3: Configure Bot Settings
Send these commands to @BotFather:
```
/setcommands
# Select your bot
# Paste these commands:

start - Initialize bot and show welcome
status - Show current P&L and positions
positions - List all open positions
performance - Show performance metrics
pause - Pause all trading activities
resume - Resume trading activities
stop - Emergency stop all positions
analysis - Get current market analysis
report - Generate performance report
help - Show available commands
```

### Step 4: Set Bot Description
```
/setdescription
# Select your bot
# Description:
Autonomous Nifty/BankNifty options trading bot. Manages positions, risk, and provides real-time trading updates.
```

---

## 4. 🚂 Railway Hosting Setup (Alternative: Render)

### Option A: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. **Free tier**: $5 credit (no credit card required initially)
4. Create new project: **Deploy from GitHub repo**
5. Connect your trading bot repository
6. Railway will auto-detect Python and deploy

### Option B: Render (Alternative)
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. **Free tier**: 750 hours/month
4. Create **Web Service** from GitHub repo
5. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python telegram_bot.py`

### Configuration
Both platforms support environment variables from dashboard.

---

## 5. 🐙 GitHub Repository Setup

### Step 1: Create Repository
1. Go to [github.com](https://github.com)
2. Click **New repository**
3. Name: `nifty-banknifty-trading-bot`
4. Description: "Autonomous options trading bot for Nifty and Bank Nifty"
5. Visibility: **Private** (recommended for trading bots)
6. Initialize with README: **No** (we already have one)

### Step 2: Push Code
```bash
# In your project directory
git init
git add .
git commit -m "Initial trading bot setup"
git branch -M main
git remote add origin https://github.com/yourusername/nifty-banknifty-trading-bot.git
git push -u origin main
```

### Step 3: Configure Secrets
Go to **Settings > Secrets and variables > Actions**

Add these secrets:
```
# Trading API
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCDEF...
TELEGRAM_USER_ID=123456789

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# AWS
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=ap-south-1

# Trading Config
TRADING_CAPITAL=100000
MAX_DAILY_LOSS_PERCENT=3
ENABLE_PAPER_TRADING=true
```

---

## 6. 📊 Kite Connect API Setup

### Step 1: Get Kite Connect Subscription
1. Log into [console.zerodha.com](https://console.zerodha.com)
2. Go to **Apps > Kite Connect**
3. Subscribe to **Kite Connect API** (₹500/month)

### Step 2: Create App
1. Click **Create new app**
2. App name: `Nifty Trading Bot`
3. App type: **Connect**
4. Redirect URL: `https://your-app-url.com/callback` (or localhost for testing)
5. **Save API Key and Secret**

### Step 3: Generate Access Token
```python
# Run this once to get access token
from kiteconnect import KiteConnect

api_key = "your_api_key"
api_secret = "your_api_secret"

kite = KiteConnect(api_key=api_key)
print("Login URL:", kite.login_url())

# Visit the URL, login, get request_token from redirect
request_token = "your_request_token"
data = kite.generate_session(request_token, api_secret=api_secret)
print("Access Token:", data["access_token"])
```

---

## 7. ✅ Verification Checklist

After setting up all services, verify:

- [ ] **AWS**: Can access Lambda console
- [ ] **Supabase**: Database tables created successfully
- [ ] **Telegram**: Bot responds to `/start` command  
- [ ] **GitHub**: Repository created with secrets configured
- [ ] **Kite Connect**: API subscription active, keys obtained
- [ ] **Environment**: `.env` file configured locally

### Test Commands:
```bash
# Test configuration
python main.py --validate-config

# Test database connection  
python scripts/init_database.py --test-only

# Test bot locally (in paper trading mode)
python main.py --paper-trading
```

---

## 🔒 Security Best Practices

1. **Never commit secrets** to Git
2. Use **environment variables** for all credentials
3. Enable **2FA** on all accounts
4. Use **least privilege** access for AWS IAM
5. Regularly **rotate API keys**
6. Monitor **unusual activity** in all services
7. Keep **backup** of all credentials in secure location

---

## 💰 Cost Estimation

### Free Tier Usage (Monthly):
- AWS Lambda: **₹0** (within limits)
- Supabase: **₹0** (500MB limit)
- GitHub: **₹0** (private repo)
- Railway: **₹0** ($5 credit covers small bot)

### Paid Services:
- Kite Connect API: **₹500/month**
- **Total**: ~₹500/month

### Scaling Costs:
If you exceed free tiers:
- AWS Lambda: ~₹20-100/month
- Supabase: ~₹800/month (Pro plan)
- Railway: ~₹400-800/month

---

## 🆘 Support & Troubleshooting

### Common Issues:
1. **"Configuration validation failed"**: Check `.env` file format
2. **"Database connection failed"**: Verify Supabase URL and keys
3. **"Bot not responding"**: Check Telegram bot token
4. **"AWS credentials error"**: Verify IAM user permissions

### Getting Help:
- Check the logs: `logs/trading_bot_YYYYMMDD.log`
- Run health check: `python scripts/health_check.py`
- Test individual components in isolation

---

## 🚀 Next Steps

Once all services are configured:

1. **Complete Phase 1**: Update task tracker
2. **Start Phase 2**: Implement trading strategies  
3. **Paper Trading**: Test with virtual money
4. **Go Live**: Deploy with real capital (start small!)

Good luck with your trading bot! 🚀📈