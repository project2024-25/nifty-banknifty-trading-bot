# AWS Lambda Deployment Guide

## 🚀 Complete Guide for AWS Lambda Setup & Deployment

### 📋 Prerequisites
- AWS Account (free tier available)
- GitHub account with repository access
- Your Kite Connect and Telegram credentials

---

## 🏗️ Step 1: AWS Account Setup

### 1.1 Create AWS Account
- Visit: **https://aws.amazon.com/**
- Click "Create AWS Account"
- Fill in account details and credit card (for verification)
- **Note**: Free tier covers your trading bot completely!

### 1.2 AWS Free Tier Resources
Your trading bot will use:
```
✅ AWS Lambda: 1M requests/month FREE (you'll use ~50,000)
✅ CloudWatch Logs: 5GB storage FREE
✅ Parameter Store: 10,000 parameters FREE
✅ CloudWatch Alarms: 10 alarms FREE
✅ Estimated monthly cost: $0.00 (within free tier)
```

### 1.3 Create IAM User for Deployment
1. Go to **AWS Console** → **IAM** → **Users**
2. Click **"Create User"**
3. User name: `trading-bot-deployer`
4. Select **"Programmatic access"**
5. Attach policies:
   - `AWSLambdaFullAccess`
   - `CloudWatchFullAccess`
   - `AmazonSSMFullAccess`
   - `IAMFullAccess` (for deployment only)

6. **Save the Access Key ID and Secret Access Key** - you'll need these!

---

## 🔐 Step 2: GitHub Secrets Configuration

### 2.1 Add AWS Credentials to GitHub
Go to your GitHub repository → **Settings** → **Secrets and Variables** → **Actions**

Add these **Repository Secrets**:

```
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here

KITE_API_KEY=ww96hwow1ydw6g4z
KITE_API_SECRET=hkscdwvtca0njznyjco5w0suvnnso7xm
KITE_ACCESS_TOKEN=YrBs9DkakokyP2hsFrhlUU3YxpUxp170

TELEGRAM_BOT_TOKEN=7589521488:AAGuI6d0o9EU7gFsfJqjfd7mea-3_bL3Xt8
TELEGRAM_USER_ID=8247070289

SUPABASE_URL=https://zndhtinssqalzshzpwny.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpuZGh0aW5zc3FhbHpzaHpwd255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjgwNDcsImV4cCI6MjA3MDE0NDA0N30.J5pzZYlnIkgbSP2YnNjJOxs_ukpHXBskFFGHcqhoYVc
```

### 2.2 Security Best Practices
- ✅ **Never commit secrets to code**
- ✅ **All secrets stored in GitHub encrypted secrets**
- ✅ **AWS Parameter Store for additional security layer**
- ✅ **IAM roles with minimal permissions**

---

## 🛠️ Step 3: Local Development Setup

### 3.1 Install Serverless Framework
```bash
# Install Node.js (if not already installed)
# Download from: https://nodejs.org/

# Install Serverless Framework globally
npm install -g serverless@3

# Verify installation
serverless --version
```

### 3.2 Install Required Plugins
```bash
cd "D:\Omkar\Algo trading bot\algo_bot_2025"

# Initialize package.json if not exists
npm init -y

# Install serverless plugins
npm install serverless-python-requirements
npm install serverless-plugin-aws-alerts
```

### 3.3 Configure AWS CLI (Optional)
```bash
# Install AWS CLI
pip install awscli

# Configure with your credentials
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret] 
# Default region: ap-south-1
# Default output format: json
```

---

## 🚀 Step 4: Deployment Process

### 4.1 Manual Deployment (First Time)
```bash
cd "D:\Omkar\Algo trading bot\algo_bot_2025"

# Deploy to dev stage
serverless deploy --stage dev --region ap-south-1

# Deploy to production (when ready)
serverless deploy --stage prod --region ap-south-1
```

### 4.2 Automated Deployment via GitHub Actions
Once you commit and push to main branch:

1. **Automatic trigger** when you push to main
2. **Tests run** to validate code
3. **Secrets deployed** to AWS Parameter Store
4. **Lambda functions deployed** with all dependencies
5. **Functions tested** automatically
6. **Notifications sent** via Telegram

### 4.3 Deployment Architecture
```
GitHub Push → GitHub Actions → AWS Lambda Deployment

Functions Created:
├── mainTrading (every 5 min during market hours)
├── preMarketAnalysis (9:00 AM IST daily)  
├── postMarketReporting (4:30 PM IST daily)
└── youtubeAnalysis (4:00 PM IST daily)
```

---

## ⏰ Step 5: Scheduled Execution

### 5.1 Market Hours Schedule
```yaml
Main Trading Function:
  - Runs: Every 5 minutes
  - Time: 9:15 AM - 3:30 PM IST (Monday-Friday)
  - Action: Market analysis, signal generation, trade execution

Pre-Market Analysis:
  - Runs: 9:00 AM IST (Monday-Friday)
  - Action: Daily preparation, strategy setup

Post-Market Reporting:
  - Runs: 4:30 PM IST (Monday-Friday) 
  - Action: Performance analysis, daily summary

YouTube Analysis:
  - Runs: 4:00 PM IST (Monday-Friday)
  - Action: Content analysis, sentiment extraction
```

### 5.2 Manual Triggering
You can also trigger functions manually:
- **AWS Console** → **Lambda** → **Test**
- **API Gateway** endpoints (if configured)
- **Your Telegram bot** commands

---

## 📊 Step 6: Monitoring & Alerting

### 6.1 CloudWatch Monitoring
Automatic monitoring includes:
- ✅ **Function execution success/failure**
- ✅ **Execution duration and memory usage**
- ✅ **Error rates and throttling**
- ✅ **Custom trading metrics**

### 6.2 Alerting Setup
Alerts will be sent for:
- ❌ **Function errors or timeouts**
- ⚠️ **High memory usage**
- 🚨 **Trading system failures**
- 📈 **Performance anomalies**

### 6.3 Log Analysis
Access logs via:
- **AWS Console** → **CloudWatch** → **Log Groups**
- **Real-time streaming** for debugging
- **Structured JSON logs** for analysis

---

## 🧪 Step 7: Testing & Validation

### 7.1 Pre-Deployment Testing
```bash
# Test locally (paper trading mode)
cd "D:\Omkar\Algo trading bot\algo_bot_2025"
python lambda_functions/main_trading/lambda_function.py

# Validate serverless configuration
serverless deploy --noDeploy

# Run integration tests
python -m pytest tests/ -v
```

### 7.2 Post-Deployment Testing
```bash
# Test deployed function
aws lambda invoke \
  --function-name nifty-banknifty-trading-bot-dev-mainTrading \
  --payload '{"action": "test", "force_run": true}' \
  response.json

# Check response
cat response.json
```

### 7.3 Production Readiness Checklist
- [ ] Paper trading tested extensively
- [ ] All environment variables configured
- [ ] Monitoring and alerts enabled
- [ ] Error handling tested
- [ ] Performance metrics validated
- [ ] Telegram notifications working
- [ ] Emergency stop procedures tested

---

## 💰 Step 8: Cost Optimization

### 8.1 Current Costs (Free Tier)
```
Monthly AWS Costs:
├── Lambda Executions: $0.00 (within 1M free requests)
├── CloudWatch Logs: $0.00 (within 5GB free storage)
├── Parameter Store: $0.00 (within 10K free parameters)
├── Data Transfer: $0.00 (minimal usage)
└── Total AWS Cost: $0.00/month

Total System Costs:
├── AWS: $0.00/month
├── Kite Connect: ₹590/month  
├── GitHub: $0.00 (free tier)
└── Grand Total: ₹590/month (~$7.10)
```

### 8.2 Scaling Considerations
- **Free tier limits**: 1M Lambda requests/month
- **Your usage**: ~50,000 requests/month (well within limits)
- **Memory allocation**: 512MB (optimized for cost/performance)
- **Execution time**: <30 seconds average (within free tier)

---

## 🔄 Step 9: Continuous Deployment

### 9.1 Development Workflow
```
1. Code changes → Commit to GitHub
2. GitHub Actions → Automated testing
3. Tests pass → Deploy to dev stage  
4. Manual validation → Promote to prod
5. Monitor → Performance tracking
```

### 9.2 Version Management
- **Dev environment**: For testing new features
- **Prod environment**: For live trading
- **Blue/Green deployment**: Zero-downtime updates
- **Rollback capability**: Quick revert if issues

---

## 🆘 Step 10: Troubleshooting

### 10.1 Common Issues

**Deployment Fails:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify serverless config
serverless config credentials --provider aws --key YOUR_KEY --secret YOUR_SECRET
```

**Function Timeouts:**
- Increase timeout in `serverless.yml`
- Optimize code for faster execution
- Check external API response times

**Memory Issues:**
- Monitor CloudWatch metrics
- Increase memory allocation if needed
- Optimize data processing

**Permission Errors:**
- Check IAM roles and policies
- Verify Parameter Store permissions
- Review CloudWatch access rights

### 10.2 Debug Commands
```bash
# View function logs
serverless logs -f mainTrading -t

# Monitor function execution
aws logs tail /aws/lambda/nifty-banknifty-trading-bot-dev-mainTrading --follow

# Test function locally
serverless invoke local -f mainTrading -d '{"action": "test"}'
```

---

## ✅ Step 11: Deployment Checklist

### Pre-Deployment:
- [ ] AWS account created and configured
- [ ] IAM user with appropriate permissions
- [ ] GitHub secrets configured
- [ ] Serverless Framework installed
- [ ] All credentials validated

### Deployment:
- [ ] Code committed to GitHub main branch
- [ ] GitHub Actions pipeline successful
- [ ] Lambda functions deployed
- [ ] Environment variables set in Parameter Store
- [ ] Monitoring and alerts configured

### Post-Deployment:
- [ ] Functions tested manually
- [ ] Scheduled executions verified
- [ ] Telegram notifications working
- [ ] Paper trading mode active
- [ ] Performance metrics monitoring
- [ ] Emergency procedures documented

---

## 🎯 Expected Results

After successful deployment:

### ✅ **Autonomous Operation**
- Trading bot runs automatically during market hours
- No manual intervention required
- Intelligent strategy selection based on market regime
- Risk management integrated

### 📱 **Mobile Control**
- Full control via Telegram bot
- Real-time notifications
- Emergency stop capability
- Performance monitoring

### 📊 **Advanced Analytics**
- Multi-timeframe market analysis
- Strategy performance attribution
- Real-time P&L tracking
- Sophisticated risk metrics

### 💰 **Cost Efficiency**
- $0/month AWS costs (free tier)
- Only ₹590/month for Kite Connect
- Scalable architecture ready for growth

---

## 🎉 Success Indicators

Your deployment is successful when:
- ✅ Lambda functions execute without errors
- ✅ Scheduled triggers fire correctly
- ✅ Telegram bot responds with live data
- ✅ Paper trading generates realistic trades
- ✅ Monitoring dashboards show healthy metrics
- ✅ All alerts and notifications work properly

**CONGRATULATIONS!** Your sophisticated Nifty/BankNifty trading bot is now running autonomously in the cloud! 🚀