# Nifty/BankNifty Options Trading Bot

An autonomous, AI-powered options trading system focused exclusively on Nifty and Bank Nifty options. Built with serverless architecture using free-tier cloud services.

🚀 **Status: Production Ready - AWS Lambda & Railway Deployment Configured**

## Features

- **Fully Autonomous Trading**: Executes trades without manual intervention
- **Multi-Strategy Approach**: 60% conservative, 40% aggressive strategies
- **Risk Management**: Comprehensive risk controls and position sizing
- **Telegram Integration**: Complete control via Telegram bot
- **Multi-Source Intelligence**: Technical analysis + YouTube insights + ML predictions
- **Serverless Architecture**: Zero infrastructure costs using AWS Lambda
- **Paper Trading**: Safe testing environment before live deployment

## Quick Start

### Prerequisites

- Python 3.9+
- Git
- AWS Account (free tier)
- Telegram account
- Zerodha account with Kite Connect API

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd algo_bot_2025
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv trading_bot_env
   source trading_bot_env/Scripts/activate  # Windows
   # or
   source trading_bot_env/bin/activate      # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize database**
   ```bash
   python scripts/init_database.py
   ```

## Configuration

Key environment variables to set in `.env`:

```bash
# Trading API
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_USER_ID=your_telegram_user_id

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Trading Parameters
TRADING_CAPITAL=100000
MAX_DAILY_LOSS_PERCENT=3
ENABLE_PAPER_TRADING=true
```

## Project Structure

```
├── src/
│   ├── core/                 # Core trading logic
│   ├── strategies/           # Trading strategies
│   │   ├── conservative/     # Conservative strategies (60%)
│   │   └── aggressive/       # Aggressive strategies (40%)
│   ├── intelligence/         # AI/ML and analysis
│   ├── integrations/         # External API integrations
│   └── utils/               # Utilities and helpers
├── lambda_functions/        # AWS Lambda functions
├── tests/                   # Test suite
├── config/                  # Configuration files
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

## Strategies

### Conservative Strategies (60% allocation)
- **Iron Condor**: Range-bound market strategy
- **Bull Put Spread**: Bullish bias with limited risk
- **Bear Call Spread**: Bearish bias with limited risk

### Aggressive Strategies (40% allocation)
- **Long Straddle**: High volatility plays
- **Directional Options**: Strong trend following
- **Intraday Scalping**: Quick profit opportunities

## Usage

### Telegram Bot Commands

- `/status` - View current positions and P&L
- `/positions` - List all open positions
- `/pause` - Pause trading activities
- `/resume` - Resume trading activities
- `/stop` - Emergency stop (close all positions)
- `/report` - Generate performance report

### Running Locally

```bash
# Start in paper trading mode
python -m src.main --paper-trading

# Run backtesting
python -m src.backtesting.runner --strategy iron_condor --period 30d

# Health check
python scripts/health_check.py
```

## Deployment

The bot is designed to run on AWS Lambda with GitHub Actions for automation.

1. **Set up AWS credentials**
2. **Configure GitHub secrets**
3. **Deploy using GitHub Actions**

See [deployment documentation](docs/deployment.md) for detailed instructions.

## Risk Management

- Maximum daily loss: 3% of capital
- Position size limit: 10% per trade
- Maximum open positions: 5
- Capital allocation: 60% conservative, 40% aggressive
- Emergency stop mechanisms

## Monitoring

- **CloudWatch**: System metrics and logs
- **Telegram**: Real-time notifications
- **Daily Reports**: Performance summaries
- **Health Checks**: Automated system monitoring

## Testing

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/strategies/
pytest tests/integration/

# Run with coverage
pytest --cov=src --cov-report=html
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Security

- Never commit API keys or secrets
- Use environment variables for all credentials
- Enable 2FA on all accounts
- Regular security audits with `bandit`

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

This trading bot is for educational and research purposes only. Trading in options involves substantial risk and is not suitable for all investors. Past performance does not guarantee future results. The developers are not responsible for any financial losses.

## Support

- Check the [troubleshooting guide](docs/troubleshooting.md)
- Review the [FAQ](docs/faq.md)
- Open an issue for bugs or feature requests

---

**⚠️ Important**: Start with paper trading and thoroughly test all strategies before deploying with real capital.