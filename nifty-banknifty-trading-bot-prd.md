# Product Requirements Document: AI-Driven Nifty/BankNifty Options Trading Bot

## Executive Summary

### Project Overview
An autonomous, AI-powered options trading system focused exclusively on Nifty and Bank Nifty options, designed for a single user (consulting manager) who cannot actively monitor markets during work hours. The system leverages serverless architecture with zero infrastructure costs, multi-source intelligence gathering, and Telegram-based control interface.

### Key Objectives
1. **Fully Autonomous Trading**: Execute trades without manual intervention during market hours
2. **Intelligent Decision Making**: Combine technical analysis, YouTube insights, and educational content
3. **Risk-Balanced Approach**: 60% conservative strategies, 40% aggressive strategies
4. **Zero Infrastructure Cost**: Utilize free-tier cloud services exclusively
5. **Mobile-First Control**: Complete system control via Telegram bot

### Success Metrics
- System uptime: >99.5% during market hours
- Risk-adjusted returns: Sharpe ratio >1.0
- Maximum drawdown: <10% of capital
- Alert accuracy: <5 non-critical notifications per day
- Strategy win rate: >55% for conservative, >45% for aggressive

---

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Telegram Bot                           │   │
│  │  Commands | Notifications | Reports | Emergency Controls  │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│                     SERVERLESS LAYER                            │
│  ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   GitHub     │───▶│  AWS Lambda │───▶│  API Gateway    │  │
│  │   Actions    │    │  Functions  │    │   (Optional)    │  │
│  └──────────────┘    └─────────────┘    └─────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│                    INTELLIGENCE LAYER                           │
│  ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   YouTube    │    │   Zerodha   │    │  Multi-TF       │  │
│  │   Analyzer   │    │   Varsity   │    │  Analysis       │  │
│  └──────────────┘    └─────────────┘    └─────────────────┘  │
│  ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │     Blog     │    │   Reddit    │    │  ML Models      │  │
│  │   Scraper    │    │  Sentiment  │    │  (LSTM/RF)      │  │
│  └──────────────┘    └─────────────┘    └─────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│                    EXECUTION LAYER                              │
│  ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │ Kite Connect │    │    Risk     │    │   Position      │  │
│  │     API      │    │  Manager    │    │   Tracker       │  │
│  └──────────────┘    └─────────────┘    └─────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
┌────────────────────────────┼───────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌──────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   Supabase   │    │     S3      │    │   CloudWatch    │  │
│  │   Database   │    │   Storage   │    │     Logs        │  │
│  └──────────────┘    └─────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Runtime**: Python 3.9+
- **Scheduler**: GitHub Actions (2000 min/month free)
- **Compute**: AWS Lambda (1M requests/month free)
- **Database**: Supabase PostgreSQL (500MB free)
- **Bot Platform**: Telegram Bot API (Railway hosting - $5 credit)
- **Trading API**: Zerodha Kite Connect (₹500/month)
- **ML Framework**: scikit-learn, TensorFlow Lite
- **Monitoring**: CloudWatch, UptimeRobot (free tiers)

---

## Functional Requirements

### 1. Trading Instruments Scope
```python
INSTRUMENTS = {
    'NIFTY': {
        'index': 'NIFTY 50',
        'trading_symbol': 'NIFTY',
        'lot_size': 50,
        'strike_interval': 50,
        'weekly_expiry': 'Thursday',
        'monthly_expiry': 'Last Thursday'
    },
    'BANKNIFTY': {
        'index': 'NIFTY BANK',
        'trading_symbol': 'BANKNIFTY',
        'lot_size': 25,
        'strike_interval': 100,
        'weekly_expiry': 'Wednesday',
        'monthly_expiry': 'Last Thursday'
    }
}
```

### 2. Strategy Distribution (60:40 Conservative:Aggressive)

#### Conservative Strategies (60% Capital Allocation)
```python
CONSERVATIVE_STRATEGIES = {
    'iron_condor': {
        'allocation': 25,
        'max_loss': 2,
        'target_profit': 1.5,
        'entry_conditions': {
            'vix_range': (12, 20),
            'trend': 'sideways',
            'time_to_expiry': (7, 30)
        }
    },
    'bull_put_spread': {
        'allocation': 20,
        'max_loss': 3,
        'target_profit': 2,
        'entry_conditions': {
            'trend': 'bullish',
            'support_nearby': True
        }
    },
    'bear_call_spread': {
        'allocation': 15,
        'max_loss': 3,
        'target_profit': 2,
        'entry_conditions': {
            'trend': 'bearish',
            'resistance_nearby': True
        }
    }
}
```

#### Aggressive Strategies (40% Capital Allocation)
```python
AGGRESSIVE_STRATEGIES = {
    'long_straddle': {
        'allocation': 15,
        'max_loss': 5,
        'target_profit': 10,
        'entry_conditions': {
            'event': 'high_impact',
            'vix': '<15 or >25'
        }
    },
    'directional_options': {
        'allocation': 15,
        'max_loss': 100,  # of premium
        'target_profit': 200,
        'entry_conditions': {
            'strong_trend': True,
            'momentum_confirmation': True
        }
    },
    'intraday_scalping': {
        'allocation': 10,
        'max_loss': 1,
        'target_profit': 0.5,
        'frequency': 'high'
    }
}
```

### 3. Multi-Source Signal Generator

#### 3.1 Multi-Timeframe Analysis
```python
class MultiTimeframeAnalyzer:
    def analyze(self):
        return {
            'monthly': {
                'trend': self.identify_major_trend(),
                'support_resistance': self.get_major_levels(),
                'indicators': ['EMA_20', 'EMA_50', 'EMA_200']
            },
            'weekly': {
                'trend': self.identify_intermediate_trend(),
                'divergences': self.check_divergences(),
                'indicators': ['RSI', 'MACD']
            },
            'daily': {
                'setup': self.identify_trade_setup(),
                'risk_zones': self.calculate_risk_zones(),
                'indicators': ['Bollinger', 'VWAP', 'ATR']
            },
            '60min': {
                'entry_zone': self.refine_entry_zone(),
                'indicators': ['Stochastic', 'Volume']
            },
            '15min': {
                'trigger': self.get_entry_trigger(),
                'indicators': ['MACD', 'RSI']
            },
            '5min': {
                'execution': self.precise_entry_exit(),
                'indicators': ['Price_Action', 'Volume_Spike']
            }
        }
```

#### 3.2 YouTube Intelligence Extractor
```python
class YouTubeIntelligence:
    channels = {
        'sensibull': {
            'channel_id': 'UC...',
            'schedule': '16:00',  # 4 PM daily
            'extract': ['nifty_levels', 'banknifty_levels', 'strategy_bias']
        },
        'trading_chanakya': {
            'channel_id': 'UC...',
            'extract': ['support_resistance', 'trend_analysis']
        },
        'pr_sundar': {
            'channel_id': 'UC...',
            'extract': ['option_chain_analysis', 'vix_interpretation']
        }
    }
    
    def extract_daily_insights(self):
        insights = {}
        for channel, config in self.channels.items():
            video = self.get_latest_video(config['channel_id'])
            insights[channel] = {
                'title_sentiment': self.analyze_title(video.title),
                'levels': self.extract_levels_from_description(video.description),
                'strategy': self.parse_strategy_recommendation(video)
            }
        return self.aggregate_insights(insights)
```

#### 3.3 Educational Content Integration
```python
class ZerodhaVarsityKnowledge:
    def update_knowledge_base(self):
        modules = {
            'options_basics': self.scrape_module(5),
            'options_strategies': self.scrape_module(6),
            'volatility': self.scrape_module(10)
        }
        
        # Extract trading rules and guidelines
        self.trading_rules = self.extract_rules(modules)
        self.strategy_guidelines = self.extract_guidelines(modules)
        
    def apply_knowledge_to_signal(self, signal):
        # Validate signal against Varsity principles
        if self.violates_rules(signal):
            return None
        return self.enhance_with_guidelines(signal)
```

### 4. AI/ML Components

#### 4.1 Model Architecture
```python
class TradingMLModels:
    def __init__(self):
        self.models = {
            'trend_predictor': self.load_lstm_model(),
            'volatility_forecaster': self.load_prophet_model(),
            'pattern_recognizer': self.load_random_forest(),
            'sentiment_analyzer': self.load_bert_lite()
        }
    
    def ensemble_prediction(self, market_data):
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(market_data)
        
        # Weighted ensemble
        weights = {'trend': 0.3, 'volatility': 0.25, 'pattern': 0.25, 'sentiment': 0.2}
        return self.weighted_average(predictions, weights)
```

#### 4.2 Feature Engineering
```python
FEATURES = {
    'price_based': [
        'returns_1d', 'returns_5d', 'returns_20d',
        'volatility_realized', 'volatility_garch',
        'price_momentum', 'mean_reversion_score'
    ],
    'technical': [
        'rsi', 'macd_signal', 'bollinger_position',
        'atr_normalized', 'adx', 'volume_ratio'
    ],
    'options_specific': [
        'put_call_ratio', 'max_pain', 'open_interest_change',
        'implied_volatility_rank', 'iv_percentile',
        'gamma_exposure', 'options_flow'
    ],
    'sentiment': [
        'youtube_sentiment', 'reddit_sentiment',
        'fear_greed_index', 'vix_level'
    ]
}
```

### 5. Risk Management System

```python
class RiskManager:
    def __init__(self):
        self.limits = {
            'max_daily_loss': 0.03,  # 3% of capital
            'max_position_size': 0.10,  # 10% per position
            'max_open_positions': 5,
            'max_aggressive_exposure': 0.40,  # 40% in aggressive
            'min_capital_buffer': 0.20  # Keep 20% cash
        }
    
    def validate_trade(self, trade):
        checks = [
            self.check_daily_loss(),
            self.check_position_sizing(trade),
            self.check_strategy_allocation(trade),
            self.check_correlation_risk(),
            self.check_margin_requirements(trade)
        ]
        return all(checks), self.get_rejection_reason()
    
    def emergency_protocols(self):
        if self.daily_loss > 0.03:
            self.close_all_positions()
            self.pause_trading_until_tomorrow()
            self.send_emergency_alert()
```

### 6. Telegram Bot Interface

#### 6.1 Command Structure
```python
TELEGRAM_COMMANDS = {
    # Status Commands
    '/start': 'Initialize bot and show welcome message',
    '/status': 'Show current P&L, positions, and system health',
    '/positions': 'List all open positions with details',
    '/performance': 'Show today/week/month performance metrics',
    
    # Control Commands
    '/pause': 'Pause all trading activities',
    '/resume': 'Resume trading activities',
    '/stop': 'Stop and close all positions (emergency)',
    '/risk': 'Adjust risk level (low/medium/high)',
    
    # Strategy Commands
    '/strategies': 'Show active strategies and allocations',
    '/enable': 'Enable specific strategy',
    '/disable': 'Disable specific strategy',
    
    # Analysis Commands
    '/analysis': 'Get current market analysis',
    '/signals': 'Show pending trade signals',
    '/youtube': 'Latest YouTube insights summary',
    
    # Reporting Commands
    '/report': 'Generate detailed performance report',
    '/logs': 'Show recent trade logs',
    '/errors': 'Show system errors/warnings'
}
```

#### 6.2 Notification Templates
```python
NOTIFICATIONS = {
    'trade_executed': """
🎯 Trade Executed
━━━━━━━━━━━━━━━━
Symbol: {symbol}
Strategy: {strategy}
Type: {order_type}
Entry: ₹{entry_price}
Quantity: {quantity}
Target: ₹{target} ({profit_percent}%)
Stop Loss: ₹{stop_loss} ({loss_percent}%)
━━━━━━━━━━━━━━━━
    """,
    
    'daily_summary': """
📊 Daily Summary - {date}
━━━━━━━━━━━━━━━━
📈 P&L: ₹{pnl:+,.2f} ({pnl_percent:+.2f}%)
🎯 Trades: {total_trades} ({winning}/{losing})
💰 Capital Used: {capital_used}%
🏆 Best Trade: ₹{best_trade:+,.2f}
😞 Worst Trade: ₹{worst_trade:+,.2f}
━━━━━━━━━━━━━━━━
Conservative: {conservative_pnl:+,.2f}
Aggressive: {aggressive_pnl:+,.2f}
━━━━━━━━━━━━━━━━
    """
}
```

### 7. Data Models

#### 7.1 Database Schema (Supabase)
```sql
-- Trades table
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    trade_type VARCHAR(10) NOT NULL, -- BUY/SELL
    pnl DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Positions table
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    unrealized_pnl DECIMAL(10,2),
    strategy VARCHAR(50),
    opened_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Signals table
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL, -- youtube/technical/ml
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market intelligence table
CREATE TABLE market_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL,
    content_type VARCHAR(50),
    extracted_data JSONB,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 8. Scheduling and Automation

#### 8.1 GitHub Actions Workflow
```yaml
name: Trading Bot Scheduler

on:
  schedule:
    # Pre-market analysis (7:00 AM IST)
    - cron: '30 1 * * 1-5'
    
    # Market hours - every 5 minutes (9:15 AM - 3:30 PM IST)
    - cron: '*/5 3-10 * * 1-5'
    
    # YouTube analysis (4:00 PM IST)
    - cron: '30 10 * * 1-5'
    
    # Daily report (5:00 PM IST)
    - cron: '30 11 * * 1-5'

jobs:
  execute:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Determine action
        id: action
        run: |
          HOUR=$(TZ=Asia/Kolkata date +%H)
          if [ $HOUR -eq 7 ]; then
            echo "ACTION=pre_market" >> $GITHUB_OUTPUT
          elif [ $HOUR -ge 9 ] && [ $HOUR -lt 16 ]; then
            echo "ACTION=trading" >> $GITHUB_OUTPUT
          elif [ $HOUR -eq 16 ]; then
            echo "ACTION=youtube_analysis" >> $GITHUB_OUTPUT
          else
            echo "ACTION=report" >> $GITHUB_OUTPUT
          fi
      
      - name: Trigger Lambda
        env:
          LAMBDA_URL: ${{ secrets.LAMBDA_FUNCTION_URL }}
          API_KEY: ${{ secrets.API_KEY }}
        run: |
          curl -X POST $LAMBDA_URL \
            -H "x-api-key: $API_KEY" \
            -d '{"action": "${{ steps.action.outputs.ACTION }}"}'
```

### 9. Lambda Functions

#### 9.1 Main Trading Function
```python
import json
import os
from datetime import datetime
import boto3

def lambda_handler(event, context):
    action = event.get('action', 'trading')
    
    try:
        if action == 'pre_market':
            result = pre_market_analysis()
        elif action == 'trading':
            result = execute_trading_cycle()
        elif action == 'youtube_analysis':
            result = analyze_youtube_content()
        elif action == 'report':
            result = generate_daily_report()
        else:
            result = {'error': 'Unknown action'}
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        send_error_notification(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def execute_trading_cycle():
    # 1. Check if market is open
    if not is_market_open():
        return {'status': 'Market closed'}
    
    # 2. Fetch latest market data
    market_data = fetch_market_data()
    
    # 3. Run multi-timeframe analysis
    technical_signals = multi_timeframe_analysis(market_data)
    
    # 4. Get AI predictions
    ml_predictions = get_ml_predictions(market_data)
    
    # 5. Combine all signals
    final_signals = combine_signals(technical_signals, ml_predictions)
    
    # 6. Apply risk management
    validated_signals = risk_manager.validate_signals(final_signals)
    
    # 7. Execute trades
    executed_trades = execute_trades(validated_signals)
    
    # 8. Update database and notify
    update_database(executed_trades)
    notify_user(executed_trades)
    
    return {'trades_executed': len(executed_trades)}
```

### 10. Performance Monitoring

#### 10.1 Key Metrics
```python
PERFORMANCE_METRICS = {
    'financial': [
        'total_pnl',
        'win_rate',
        'profit_factor',
        'sharpe_ratio',
        'max_drawdown',
        'average_trade_pnl'
    ],
    'operational': [
        'system_uptime',
        'api_response_time',
        'signal_accuracy',
        'execution_slippage'
    ],
    'strategy_specific': {
        'conservative': ['win_rate', 'average_return', 'risk_adjusted_return'],
        'aggressive': ['hit_rate', 'risk_reward_ratio', 'recovery_time']
    }
}
```

---

## Non-Functional Requirements

### 1. Performance Requirements
- **Latency**: <1 second for signal generation
- **Execution Speed**: <500ms for order placement
- **Data Processing**: Handle 1000 ticks/second
- **Concurrent Operations**: Support 10 parallel strategy executions

### 2. Reliability Requirements
- **Uptime**: 99.5% during market hours
- **Error Recovery**: Automatic retry with exponential backoff
- **Data Integrity**: Transaction-based updates with rollback
- **Failover**: Fallback to manual alerts if system fails

### 3. Security Requirements
- **API Keys**: Stored in environment variables/secrets
- **Telegram Bot**: Whitelist single user ID only
- **Database**: SSL encryption for all connections
- **Audit Trail**: Log all trades and system actions

### 4. Scalability Considerations
- **Current**: Single user, 2 instruments
- **Future**: Extensible to multiple instruments
- **Architecture**: Serverless scales automatically
- **Database**: Partitioning ready for growth

---

## Deployment Strategy

### Phase 1: Infrastructure Setup (Week 1)
1. AWS account with Lambda setup
2. GitHub repository with Actions
3. Supabase database provisioning
4. Telegram bot creation
5. Railway/Render account for bot hosting

### Phase 2: Core Development (Week 2-3)
1. Kite Connect integration
2. Basic trading strategies
3. Risk management system
4. Telegram bot commands
5. Database models

### Phase 3: Intelligence Layer (Week 4)
1. YouTube data extraction
2. Multi-timeframe analysis
3. ML model training
4. Signal aggregation logic

### Phase 4: Testing (Week 5)
1. Paper trading mode
2. Backtesting framework
3. Performance monitoring
4. Error handling

### Phase 5: Production (Week 6)
1. Live deployment with small capital
2. Daily monitoring and adjustments
3. Performance tracking
4. Iterative improvements

---

## Cost Analysis

### Monthly Costs
```
Infrastructure (Free Tier):
- AWS Lambda: ₹0
- GitHub Actions: ₹0
- Supabase: ₹0
- Railway/Render: ₹0
- Monitoring: ₹0

Paid Services:
- Kite Connect API: ₹500
- Domain (optional): ₹100
- Total: ₹500-600/month
```

---

## Success Criteria

### Month 1
- System deployed and running
- 95% uptime achieved
- Paper trading profitable

### Month 3
- Live trading with positive returns
- <5% maximum drawdown
- All strategies tested

### Month 6
- Consistent profitability
- Sharpe ratio >1.0
- Ready for capital scaling

---

## Appendix

### A. Error Codes
```python
ERROR_CODES = {
    'E001': 'Market data unavailable',
    'E002': 'Order placement failed',
    'E003': 'Risk limit exceeded',
    'E004': 'Strategy error',
    'E005': 'Database connection failed'
}
```

### B. Configuration Templates
```python
# config.py
TRADING_CONFIG = {
    'capital': 100000,
    'risk_per_trade': 0.02,
    'max_positions': 5,
    'trading_hours': '09:30-15:00',
    'instruments': ['NIFTY', 'BANKNIFTY']
}
```

### C. Sample Telegram Interaction
```
User: /status
Bot: 📊 Trading Status
     ━━━━━━━━━━━━━━━
     💰 Capital: ₹98,500
     📈 Day P&L: +₹1,250 (+1.27%)
     📍 Positions: 3 open
     🎯 Active: Iron Condor, Bull Put Spread
     ⚡ Risk: Medium
     
User: /pause
Bot: ⏸️ Trading paused. Use /resume to continue.

User: /positions
Bot: 📍 Open Positions:
     1. NIFTY 24500 CE SELL
        Entry: ₹125 | Current: ₹118
        P&L: +₹350 (+5.6%)
     
     2. BANKNIFTY 52000 PE SELL
        Entry: ₹85 | Current: ₹92
        P&L: -₹175 (-8.2%)
```

---

This PRD provides comprehensive specifications for building an autonomous Nifty/BankNifty options trading system optimized for a single user with limited monitoring capability during work hours.