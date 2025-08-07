# 🚀 PHASE 1 SERVICE SETUP CHECKLIST

Follow this checklist to set up all external services for your trading bot.

## ✅ COMPLETED
- [x] Python virtual environment 
- [x] Project structure and dependencies
- [x] Configuration management system
- [x] Database schema design
- [x] Logging infrastructure
- [x] GitHub Actions workflow
- [x] Setup scripts and documentation

## 🔄 REMAINING TASKS

### 1. 🌩️ AWS ACCOUNT SETUP
- [ ] **Create AWS Account**
  - Go to: https://aws.amazon.com/free/
  - Sign up for free tier (requires credit card but won't charge)
  - Choose Basic Support Plan (Free)

- [ ] **Create IAM User**
  - Go to: AWS Console > IAM > Users
  - Create user: `trading-bot-user`
  - Attach policies: `AWSLambdaExecute`, `CloudWatchLogsFullAccess`
  - Generate access key for "Application running outside AWS"
  - **Save Access Key ID and Secret Access Key**

### 2. 🗃️ SUPABASE DATABASE SETUP
- [ ] **Create Supabase Account**
  - Go to: https://supabase.com/dashboard/sign-up
  - Sign up with GitHub (recommended)

- [ ] **Create Project**
  - Project name: `nifty-trading-bot`
  - Region: Mumbai (ap-south-1) or closest
  - Database password: Generate strong password and SAVE IT
  - Wait for project creation (2-3 minutes)

- [ ] **Get Project Credentials**
  - Go to: Settings > Database
  - Copy: Project URL (`https://xxx.supabase.co`)
  - Copy: Anon key (`eyJ...`)
  - Copy: Service role key (`eyJ...`)

- [ ] **Set Up Database Schema**
  - Go to: SQL Editor in Supabase dashboard
  - Copy contents of: `config/database_schema.sql`
  - Paste and click "Run"
  - Verify tables created in Table Editor

### 3. 🤖 TELEGRAM BOT SETUP
- [ ] **Create Bot with @BotFather**
  - Open Telegram app
  - Search for `@BotFather`
  - Send `/start`
  - Send `/newbot`
  - Bot name: "Nifty Trading Bot" (or your choice)
  - Bot username: `nifty_trading_bot_yourname` (must be unique)
  - **Save Bot Token**: `1234567890:ABCDEF...`

- [ ] **Get Your User ID**
  - Search for `@userinfobot` in Telegram
  - Send `/start`
  - **Save User ID**: `123456789`

- [ ] **Configure Bot Commands**
  - Send to @BotFather: `/setcommands`
  - Select your bot
  - Paste these commands:
```
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

### 4. 📈 KITE CONNECT API (Optional - for live trading)
- [ ] **Subscribe to Kite Connect**
  - Go to: https://console.zerodha.com/
  - Navigate to: Apps > Kite Connect
  - Subscribe to Kite Connect API (₹500/month)

- [ ] **Create App**
  - Click "Create new app"
  - App name: "Nifty Trading Bot"
  - App type: Connect
  - Redirect URL: `https://your-domain.com/callback`
  - **Save API Key and Secret**

### 5. 🐙 GITHUB SETUP
- [ ] **Create Repository**
  - Go to: https://github.com/new
  - Repository name: `nifty-banknifty-trading-bot`
  - Visibility: Private (recommended)
  - Don't initialize with README

- [ ] **Push Code to GitHub**
```bash
git init
git add .
git commit -m "Initial trading bot setup"
git branch -M main
git remote add origin https://github.com/yourusername/nifty-banknifty-trading-bot.git
git push -u origin main
```

- [ ] **Configure GitHub Secrets**
  - Go to: Repository > Settings > Secrets and variables > Actions
  - Add these secrets:
```
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_user_id
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
TRADING_CAPITAL=100000
MAX_DAILY_LOSS_PERCENT=3
ENABLE_PAPER_TRADING=true
```

## 🔧 CONFIGURATION

### Create .env File
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Required Environment Variables:
```
# Trading API (Optional for paper trading)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_telegram_user_id

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key

# AWS (Optional initially)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Trading Configuration
TRADING_CAPITAL=100000
MAX_DAILY_LOSS_PERCENT=3
ENABLE_PAPER_TRADING=true
```

## 🧪 TESTING & VALIDATION

### Test Configuration:
```bash
python main.py --validate-config
```

### Test Database Connection:
```bash
python scripts/init_database.py --test-only
```

### Run Health Check:
```bash
python scripts/health_check.py
```

### Test Paper Trading:
```bash
python main.py --paper-trading
```

## ⚠️ IMPORTANT SECURITY NOTES

1. **NEVER commit .env file to Git** (it's in .gitignore)
2. **Use strong passwords** for all accounts
3. **Enable 2FA** on AWS, GitHub, and Supabase
4. **Keep API keys secure** and rotate them regularly
5. **Start with paper trading** before using real money

## 💰 COST SUMMARY

### Free Services (Monthly):
- AWS Lambda: ₹0 (within free tier)
- Supabase: ₹0 (500MB limit)
- GitHub: ₹0 (private repositories)
- Telegram: ₹0

### Paid Services:
- Kite Connect API: ₹500/month (only for live trading)

**Total Cost**: ₹0-500/month depending on live trading needs

## 🎯 SUCCESS CRITERIA

When setup is complete, you should be able to:
- [x] Configuration validation passes
- [x] Database connection successful
- [x] Telegram bot responds to /start
- [x] Health check shows all systems OK
- [x] Paper trading mode runs without errors

## 🚀 NEXT STEPS AFTER SETUP

1. **Complete Phase 1**: Update task tracker
2. **Start Phase 2**: Implement core trading strategies
3. **Test thoroughly**: Run paper trading for at least 1 week
4. **Go live**: Deploy with small capital once confident

---

## 🆘 NEED HELP?

- Check logs in `logs/` directory
- Review `docs/service-setup-guide.md` for detailed instructions
- Run `python scripts/health_check.py` to diagnose issues
- All setup is designed for FREE TIER usage initially

Good luck! 🚀📈