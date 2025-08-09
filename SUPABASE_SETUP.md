# Supabase Database Setup Guide

## 🎯 **Quick Setup (5 minutes)**

### **Step 1: Create Supabase Project**
1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/login with GitHub
3. Click **"New Project"**
4. Choose organization and enter:
   - **Project Name**: `trading-bot-db`
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to Mumbai (Singapore recommended)
5. Click **"Create new project"** (takes ~2 minutes)

### **Step 2: Get Database Credentials**
1. In your Supabase dashboard, go to **Settings → API**
2. Copy these values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **anon public key**: `eyJ0eXAiOiJKV1Q...` (long token)

### **Step 3: Run Database Schema**
1. In Supabase dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy entire contents of `supabase_schema.sql` into the editor
4. Click **"Run"** to create all tables and views
5. You should see: "Success. No rows returned"

### **Step 4: Configure Environment Variables**

Add these to your GitHub Secrets and local environment:

```bash
# GitHub Secrets (Settings → Secrets and variables → Actions)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJ0eXAiOiJKV1Q...your-anon-key

# Local .env file
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=eyJ0eXAiOiJKV1Q...your-anon-key
```

### **Step 5: Verify Setup**
1. In Supabase dashboard, go to **Table Editor**
2. You should see 8 tables created:
   - ✅ trades
   - ✅ positions  
   - ✅ signals
   - ✅ market_intelligence
   - ✅ performance_metrics
   - ✅ risk_events
   - ✅ system_logs
   - ✅ strategy_performance

## 🎨 **Database Schema Overview**

### **Core Tables:**

1. **`trades`** - Complete trade lifecycle tracking
   - Entry/exit prices, P&L, strategy, market regime
   - Paper vs live trading separation
   - Trade status (OPEN/CLOSED/CANCELLED)

2. **`positions`** - Real-time position tracking  
   - Current quantities, unrealized P&L
   - Strategy-specific position management
   - Automatic position updates

3. **`signals`** - Trading signal generation
   - Strategy signals with confidence scores
   - Market regime context
   - Execution tracking

4. **`market_intelligence`** - Market analysis storage
   - Regime detection results
   - Volatility analysis
   - Technical indicators

5. **`performance_metrics`** - Daily performance tracking
   - P&L, win rates, Sharpe ratio
   - Portfolio value tracking
   - Risk utilization metrics

6. **`risk_events`** - Risk management alerts
   - Risk threshold breaches
   - Automated risk responses
   - Event resolution tracking

### **Helpful Views:**

- **`active_positions`** - Current non-zero positions
- **`daily_pnl`** - Daily P&L summary
- **`recent_trades`** - Latest closed trades
- **`market_intelligence_summary`** - Latest market analysis

## 🚀 **Advanced Features Enabled:**

✅ **Full Trade Tracking** - Every trade logged with context  
✅ **Performance Analytics** - Sharpe ratio, drawdown, profit factor  
✅ **Risk Management** - Automated risk event logging  
✅ **Market Intelligence** - Regime detection and analysis storage  
✅ **Strategy Performance** - Individual strategy tracking  
✅ **Real-time Positions** - Live position and P&L tracking  
✅ **System Audit** - Complete system event logging  
✅ **Paper Trading** - Separate tracking for paper vs live trades  

## 📊 **Free Tier Limits:**

- **Database Size**: 500MB (sufficient for ~1M+ trades)
- **API Requests**: 50,000/month (more than enough)
- **Bandwidth**: 2GB/month  
- **Real-time Connections**: 200 concurrent
- **Auth Users**: 50,000

## 🔐 **Security Notes:**

- Database uses UUID primary keys for security
- Row Level Security (RLS) ready (commented out for simplicity)
- Environment variables keep credentials secure
- API keys have appropriate permissions

## 🛠️ **Next Steps After Setup:**

1. **Test Connection**: Deploy Lambda with database integration
2. **Enable Real Trading**: Switch `paper_trade=false` when ready
3. **Monitor Performance**: Use Supabase dashboard for real-time monitoring
4. **Scale Up**: Upgrade to Pro tier when you exceed free limits

Your sophisticated trading system is now ready with enterprise-grade database capabilities! 🎯