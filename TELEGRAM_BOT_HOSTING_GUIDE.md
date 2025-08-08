# Telegram Bot 24/7 Hosting Guide

## 🤖 Deploy Your Trading Bot for 24/7 Mobile Control

This guide shows you how to deploy your Telegram bot to cloud hosting platforms for continuous operation.

---

## 🎯 Overview

Your Telegram bot will run 24/7 in the cloud, providing:
- **Mobile Control Interface**: Full trading control from your phone
- **Real-time Notifications**: Instant trade alerts and market updates  
- **Emergency Controls**: Stop trading from anywhere
- **Portfolio Monitoring**: Live P&L and position tracking
- **Health Monitoring**: System status and uptime tracking

---

## 🏆 Option A: Railway Deployment (Recommended)

Railway offers excellent free tier and simple deployment.

### A.1 Railway Setup

**Step 1: Create Railway Account**
- Visit: **https://railway.app/**
- Sign up with GitHub account (recommended)
- Connect your GitHub repository

**Step 2: Create New Project**
- Click **"New Project"**
- Select **"Deploy from GitHub repo"**
- Choose your `nifty-banknifty-trading-bot` repository
- Railway will auto-detect Python and start deployment

### A.2 Environment Variables Configuration

In Railway dashboard → **Variables** tab, add:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=7589521488:AAGuI6d0o9EU7gFsfJqjfd7mea-3_bL3Xt8
TELEGRAM_USER_ID=8247070289

# Kite Connect Configuration  
KITE_API_KEY=ww96hwow1ydw6g4z
KITE_API_SECRET=hkscdwvtca0njznyjco5w0suvnnso7xm
KITE_ACCESS_TOKEN=YrBs9DkakokyP2hsFrhlUU3YxpUxp170

# Database Configuration
SUPABASE_URL=https://zndhtinssqalzshzpwny.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpuZGh0aW5zc3FhbHpzaHpwd255Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ1NjgwNDcsImV4cCI6MjA3MDE0NDA0N30.J5pzZYlnIkgbSP2YnNjJOxs_ukpHXBskFFGHcqhoYVc

# Trading Configuration
ENABLE_PAPER_TRADING=true
ENVIRONMENT=production
PORT=8000
```

### A.3 Deployment Settings

Railway will automatically:
- ✅ **Detect Python**: Uses `requirements.txt`
- ✅ **Install Dependencies**: All packages installed automatically
- ✅ **Start Command**: Uses `telegram_bot_server.py`
- ✅ **Health Checks**: Monitors `/health` endpoint
- ✅ **Auto Restart**: Restarts on failures
- ✅ **Logs**: Real-time log streaming

### A.4 Domain & Access
- **Custom Domain**: `your-bot.up.railway.app`
- **Health Check**: `https://your-bot.up.railway.app/health`
- **Status Page**: `https://your-bot.up.railway.app/status`

---

## 🌟 Option B: Render Deployment (Alternative)

Render is another excellent free hosting option.

### B.1 Render Setup

**Step 1: Create Render Account**
- Visit: **https://render.com/**
- Sign up with GitHub account
- Connect your repository

**Step 2: Create Web Service**
- Click **"New +"** → **"Web Service"**
- Connect GitHub repository
- Configure deployment:
  ```
  Name: nifty-banknifty-trading-bot
  Environment: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: python telegram_bot_server.py
  ```

### B.2 Environment Variables

In Render dashboard → **Environment** tab, add the same variables as Railway.

### B.3 Service Configuration

```yaml
# render.yaml (optional)
services:
  - type: web
    name: trading-bot-telegram
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python telegram_bot_server.py"
    plan: free
    healthCheckPath: "/health"
    envVars:
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_USER_ID  
        sync: false
      - key: KITE_API_KEY
        sync: false
```

---

## 💰 Free Tier Comparison

### Railway Free Tier:
```
✅ 512MB RAM
✅ 1GB Storage  
✅ 500 hours/month execution time
✅ Custom domain included
✅ Auto-restart on failures
✅ Real-time logs
✅ GitHub integration

Cost: $0/month (free tier)
Upgrade: $5/month for unlimited
```

### Render Free Tier:
```
✅ 512MB RAM
✅ 750 hours/month execution time
✅ Auto-deploy from GitHub
✅ SSL certificates
✅ Health checks
✅ Log streaming

Cost: $0/month (free tier)
Upgrade: $7/month for always-on
```

**Recommendation**: Railway for better uptime and features.

---

## 🚀 Step-by-Step Deployment (Railway)

### Step 1: Prepare Repository
```bash
cd "D:\Omkar\Algo trading bot\algo_bot_2025"

# Ensure all files are committed
git add .
git commit -m "🤖 Add Telegram bot server for 24/7 hosting"
git push origin main
```

### Step 2: Deploy to Railway
1. Go to **https://railway.app/**
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway starts automatic deployment

### Step 3: Configure Environment Variables
1. Click on your deployed service
2. Go to **"Variables"** tab
3. Add all environment variables from above
4. Click **"Deploy"** to restart with new variables

### Step 4: Verify Deployment
1. Check **"Deployments"** tab for success
2. Visit health endpoint: `https://your-app.up.railway.app/health`
3. Check logs in **"Observability"** tab
4. Test Telegram bot commands

---

## ✅ Deployment Verification

### 1. Health Check
Visit your app's health endpoint:
```json
{
  "status": "running",
  "timestamp": "2025-01-08T10:30:00Z",
  "bot_running": true,
  "environment": "production", 
  "kite_authenticated": true,
  "paper_trading": true
}
```

### 2. Telegram Bot Test
Send `/start` to your bot - you should receive:
```
🚀 Trading Bot Server Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ System Status
• Server: Online and Running
• Environment: Production
• Time: 2025-01-08 10:30:00

🔗 Connections  
• Kite Connect: ✅ Authenticated
• Telegram Bot: ✅ Active
• Mode: 📋 Paper Trading

Your sophisticated trading bot is accessible 24/7! 📱
```

### 3. Command Testing
Test these commands:
- `/status` - Should show portfolio data
- `/analysis` - Should show market analysis
- `/help` - Should show command list

---

## 🔧 Monitoring & Maintenance

### Health Monitoring
Your bot server includes automatic health monitoring:

**Health Endpoints:**
- `/health` - Simple health check (for Railway/Render)
- `/status` - Detailed system status
- `/` - Root endpoint with system info

**Automatic Features:**
- ✅ **Auto-restart** on failures
- ✅ **Health monitoring** every 30 seconds
- ✅ **Log rotation** to prevent disk full
- ✅ **Memory optimization** for long-running processes
- ✅ **Graceful shutdown** on deployment updates

### Log Monitoring
Access logs through:
- **Railway**: Dashboard → Observability → Logs
- **Render**: Dashboard → Logs tab
- **File**: `telegram_bot.log` (rotated automatically)

### Performance Monitoring
Monitor these metrics:
- **Response Time**: < 1 second for bot commands
- **Memory Usage**: Should stay under 256MB
- **Error Rate**: Should be < 1%
- **Uptime**: Target 99.9%

---

## 🚨 Troubleshooting

### Common Issues

**1. Bot Not Responding**
```bash
# Check health endpoint
curl https://your-app.up.railway.app/health

# Check logs for errors
# Look for authentication failures or API limits
```

**2. Environment Variables Not Loading**
- Verify all variables are set correctly
- Check for typos in variable names
- Restart the service after adding variables

**3. Memory/Resource Issues**
- Monitor memory usage in dashboard
- Consider upgrading to paid tier if needed
- Check for memory leaks in logs

**4. Telegram API Limits**
- Bot has built-in rate limiting
- Avoid sending too many messages quickly
- Check Telegram Bot API status

### Debug Commands
```bash
# Test health endpoint
curl https://your-app.up.railway.app/health

# Test status endpoint  
curl https://your-app.up.railway.app/status

# Check bot webhook (if using webhooks)
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

---

## 🔄 Updates & Maintenance

### Automatic Updates
Your bot will automatically update when you:
1. Push code changes to GitHub
2. Railway/Render detects changes
3. Automatic redeployment triggered
4. Bot restarts with new code

### Manual Updates
```bash
# Deploy specific branch
git push origin feature-branch

# Force redeploy in Railway/Render dashboard
# Click "Deploy Latest Commit"
```

### Backup & Recovery
- **Configuration**: Environment variables backed up
- **Logs**: Retained for 7 days on free tier
- **Code**: Always available in GitHub
- **Database**: Supabase handles backups automatically

---

## 🎯 Production Checklist

### Pre-Deployment:
- [ ] All environment variables configured
- [ ] GitHub repository up to date
- [ ] Health endpoints respond correctly
- [ ] Telegram bot commands tested locally
- [ ] Error handling tested

### Post-Deployment:
- [ ] Health check endpoint accessible
- [ ] Telegram bot responds to commands
- [ ] Real-time notifications working
- [ ] Kite Connect authentication successful
- [ ] Logs showing no errors
- [ ] Performance metrics within limits

### Monitoring Setup:
- [ ] Health check monitoring enabled
- [ ] Log aggregation configured
- [ ] Performance alerts set up
- [ ] Backup procedures documented
- [ ] Update procedures tested

---

## 🎉 Success Indicators

Your deployment is successful when:

### ✅ **24/7 Availability**
- Bot responds to commands anytime
- Health endpoints always accessible
- Automatic restarts working
- Uptime > 99%

### 📱 **Mobile Control**
- All Telegram commands working
- Real-time notifications received
- Emergency controls functional
- Portfolio data accurate

### 🔗 **System Integration**
- Kite Connect authenticated
- Database connections stable
- AWS Lambda integration working
- Performance within limits

---

## 💡 Pro Tips

### Performance Optimization:
- Use webhooks instead of polling for better performance
- Enable Redis caching for frequently accessed data
- Optimize database queries for faster responses
- Use CDN for static assets if any

### Security Best Practices:
- Never log sensitive data
- Rotate access tokens regularly
- Use environment variables for all secrets
- Enable 2FA on hosting accounts

### Cost Management:
- Monitor usage to stay within free tiers
- Optimize resource usage
- Consider paid plans for production
- Use multiple platforms for redundancy

---

**🎉 CONGRATULATIONS!**

Your Telegram bot is now running 24/7 in the cloud, providing complete mobile control over your sophisticated Nifty/BankNifty trading system!

**✅ What You Now Have:**
- 24/7 mobile access to trading controls
- Real-time portfolio monitoring
- Instant trade notifications  
- Emergency stop capabilities
- Professional-grade system monitoring
- Automatic failover and recovery

Your trading bot is now **FULLY AUTONOMOUS** and **REMOTELY CONTROLLABLE**! 🚀📱