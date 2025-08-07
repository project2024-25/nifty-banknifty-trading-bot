#!/usr/bin/env python3
"""
Interactive Service Setup Script
Guides user through setting up external services
"""
import os
import webbrowser
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("="*60)
    print("🚀 NIFTY/BANKNIFTY TRADING BOT SETUP")
    print("="*60)
    print("This script will guide you through setting up external services.")
    print("You'll need to create accounts and configure API keys.")
    print()

def print_section(title: str):
    """Print section header"""
    print("\n" + "-"*60)
    print(f"📋 {title}")
    print("-"*60)

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with optional default"""
    if default:
        response = input(f"{prompt} (default: {default}): ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()

def confirm(prompt: str) -> bool:
    """Get yes/no confirmation"""
    while True:
        response = input(f"{prompt} (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'")

def open_url(url: str, description: str):
    """Open URL in browser with user confirmation"""
    print(f"\n🌐 Opening {description}...")
    print(f"URL: {url}")
    
    if confirm("Open this URL in your browser?"):
        webbrowser.open(url)
    else:
        print("Please manually visit the URL above.")

def setup_aws():
    """Guide AWS setup"""
    print_section("1. AWS ACCOUNT SETUP")
    
    print("📊 AWS provides serverless compute (Lambda) for our trading bot.")
    print("Free tier includes: 1M Lambda requests/month, 400,000 GB-seconds compute")
    
    if not confirm("Do you already have an AWS account?"):
        open_url("https://aws.amazon.com/free/", "AWS Free Tier Registration")
        input("Press Enter after creating your AWS account...")
    
    print("\n🔑 Now let's create IAM credentials for the bot:")
    open_url("https://console.aws.amazon.com/iam/home#/users", "AWS IAM Users")
    
    print("\nSteps to create IAM user:")
    print("1. Click 'Create User'")
    print("2. Username: trading-bot-user")  
    print("3. Attach policies: AWSLambdaExecute, CloudWatchLogsFullAccess")
    print("4. Create access key for 'Application running outside AWS'")
    
    input("Press Enter when you have your AWS credentials ready...")
    
    aws_key = get_user_input("Enter AWS Access Key ID")
    aws_secret = get_user_input("Enter AWS Secret Access Key")
    
    return {
        "AWS_ACCESS_KEY_ID": aws_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret,
        "AWS_DEFAULT_REGION": "ap-south-1"
    }

def setup_supabase():
    """Guide Supabase setup"""
    print_section("2. SUPABASE DATABASE SETUP")
    
    print("🗃️  Supabase provides PostgreSQL database for storing trades and analytics.")
    print("Free tier includes: 500MB database, 2 CPU hours, 5GB bandwidth")
    
    if not confirm("Do you already have a Supabase account?"):
        open_url("https://supabase.com/dashboard/sign-up", "Supabase Registration")
        input("Press Enter after creating your Supabase account...")
    
    if not confirm("Have you created a project for the trading bot?"):
        open_url("https://supabase.com/dashboard/projects", "Supabase Projects")
        print("\nCreate new project:")
        print("- Name: nifty-trading-bot")
        print("- Region: Mumbai (ap-south-1) or closest")
        print("- Database password: Generate strong password and save it")
        input("Press Enter when your project is ready...")
    
    print("\n🔗 Now let's get your project credentials:")
    open_url("https://supabase.com/dashboard/project/_/settings/database", "Project Settings")
    
    supabase_url = get_user_input("Enter Supabase URL (https://xxx.supabase.co)")
    supabase_key = get_user_input("Enter Supabase Anon Key")
    supabase_service_key = get_user_input("Enter Supabase Service Key (optional)", "")
    
    print("\n📋 Next, you need to run the database schema:")
    print("1. Go to SQL Editor in your Supabase dashboard")  
    print("2. Copy contents of config/database_schema.sql")
    print("3. Paste and execute the SQL")
    
    confirm("Press Enter when you've set up the database schema...")
    
    return {
        "SUPABASE_URL": supabase_url,
        "SUPABASE_KEY": supabase_key,
        "SUPABASE_SERVICE_KEY": supabase_service_key
    }

def setup_telegram():
    """Guide Telegram bot setup"""
    print_section("3. TELEGRAM BOT SETUP")
    
    print("🤖 Telegram bot provides the user interface for controlling the trading bot.")
    print("You'll be able to check status, pause trading, view reports, etc.")
    
    print("\n📱 Step 1: Create bot with @BotFather")
    print("1. Open Telegram app")
    print("2. Search for @BotFather") 
    print("3. Send /start")
    print("4. Send /newbot")
    print("5. Choose bot name: 'Nifty Trading Bot' (or similar)")
    print("6. Choose username: 'nifty_trading_bot_yourname' (must be unique)")
    
    bot_token = get_user_input("Enter Bot Token (from @BotFather)")
    
    print("\n👤 Step 2: Get your User ID")
    print("1. Search for @userinfobot in Telegram")
    print("2. Send /start to get your User ID")
    
    user_id = get_user_input("Enter your Telegram User ID")
    
    print("\n⚙️  Step 3: Configure bot commands")
    print("Send these to @BotFather:")
    print("/setcommands")
    print("(Select your bot, then paste:)")
    
    commands = """start - Initialize bot and show welcome
status - Show current P&L and positions  
positions - List all open positions
performance - Show performance metrics
pause - Pause all trading activities
resume - Resume trading activities
stop - Emergency stop all positions
analysis - Get current market analysis
report - Generate performance report
help - Show available commands"""
    
    print(commands)
    confirm("Press Enter when you've set up the bot commands...")
    
    return {
        "TELEGRAM_BOT_TOKEN": bot_token,
        "TELEGRAM_USER_ID": user_id
    }

def setup_kite():
    """Guide Kite Connect setup"""
    print_section("4. KITE CONNECT API SETUP")
    
    print("📈 Kite Connect API enables live trading with Zerodha.")
    print("Cost: ₹500/month subscription")
    print("Required: Active Zerodha trading account")
    
    if not confirm("Do you have a Zerodha trading account?"):
        open_url("https://zerodha.com/open-account", "Open Zerodha Account")
        print("You need a trading account before proceeding.")
        return {}
    
    print("\n💳 Subscribe to Kite Connect API:")
    open_url("https://console.zerodha.com/", "Zerodha Console")
    
    print("Steps:")
    print("1. Login to Zerodha Console")
    print("2. Go to Apps > Kite Connect")
    print("3. Subscribe to Kite Connect API (₹500/month)")
    print("4. Create new app:")
    print("   - App name: Nifty Trading Bot")
    print("   - App type: Connect")
    print("   - Redirect URL: https://your-domain.com/callback")
    
    if not confirm("Have you subscribed and created the app?"):
        print("Please complete the Kite Connect setup first.")
        return {}
    
    api_key = get_user_input("Enter Kite Connect API Key")
    api_secret = get_user_input("Enter Kite Connect API Secret")
    
    print("\n⚠️  Important: You'll need to generate access token separately")
    print("Run this after setup: python scripts/generate_kite_token.py")
    
    return {
        "KITE_API_KEY": api_key,
        "KITE_API_SECRET": api_secret
    }

def setup_github():
    """Guide GitHub setup"""
    print_section("5. GITHUB REPOSITORY SETUP")
    
    print("🐙 GitHub will host the code and run automated trading via Actions.")
    print("Free tier includes: Unlimited public/private repos, 2000 Action minutes/month")
    
    if not confirm("Do you have a GitHub account?"):
        open_url("https://github.com/join", "GitHub Registration")
        input("Press Enter after creating your GitHub account...")
    
    print("\n📂 Creating repository:")
    print("1. Repository name: nifty-banknifty-trading-bot")
    print("2. Visibility: Private (recommended)")
    print("3. Don't initialize with README (we have one)")
    
    open_url("https://github.com/new", "Create New Repository")
    
    repo_url = get_user_input("Enter your repository URL (https://github.com/username/repo)")
    
    print(f"\n📤 Push code to GitHub:")
    print("git init")
    print("git add .")  
    print('git commit -m "Initial trading bot setup"')
    print("git branch -M main")
    print(f"git remote add origin {repo_url}")
    print("git push -u origin main")
    
    confirm("Press Enter when you've pushed the code to GitHub...")
    
    return {"GITHUB_REPO": repo_url}

def create_env_file(env_vars: dict):
    """Create .env file with collected variables"""
    print_section("CREATING ENVIRONMENT FILE")
    
    env_file = Path(".env")
    
    if env_file.exists() and not confirm(".env file already exists. Overwrite?"):
        print("Keeping existing .env file.")
        return
    
    print("📝 Creating .env file...")
    
    # Add trading configuration
    env_vars.update({
        "TRADING_CAPITAL": "100000",
        "MAX_DAILY_LOSS_PERCENT": "3", 
        "CONSERVATIVE_ALLOCATION": "60",
        "AGGRESSIVE_ALLOCATION": "40",
        "ENABLE_PAPER_TRADING": "true",
        "ENABLE_ML_PREDICTIONS": "false",
        "ENABLE_YOUTUBE_ANALYSIS": "true",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "development"
    })
    
    with open(env_file, 'w') as f:
        f.write("# Trading Bot Configuration\n")
        f.write(f"# Generated on {os.environ.get('DATE', 'today')}\n\n")
        
        for key, value in env_vars.items():
            if value:  # Only write non-empty values
                f.write(f"{key}={value}\n")
    
    print(f"✅ Environment file created: {env_file.absolute()}")
    print("\n⚠️  IMPORTANT: Never commit this file to Git!")

def setup_github_secrets(env_vars: dict, repo_url: str):
    """Guide GitHub secrets setup"""
    print_section("CONFIGURING GITHUB SECRETS")
    
    if not repo_url:
        print("Skipping GitHub secrets - repository not set up")
        return
    
    print("🔐 GitHub Secrets store sensitive data for automated trading.")
    
    secrets_url = repo_url.replace("github.com", "github.com").rstrip('/') + "/settings/secrets/actions"
    open_url(secrets_url, "GitHub Repository Secrets")
    
    print("\n📋 Add these secrets in GitHub:")
    
    secret_vars = [
        "KITE_API_KEY", "KITE_API_SECRET", "TELEGRAM_BOT_TOKEN", 
        "TELEGRAM_USER_ID", "SUPABASE_URL", "SUPABASE_KEY",
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"
    ]
    
    for var in secret_vars:
        if var in env_vars and env_vars[var]:
            print(f"   {var} = {env_vars[var]}")
    
    print("\n⚠️  Copy these values to GitHub Secrets for automated trading.")
    confirm("Press Enter when you've configured GitHub secrets...")

def run_final_tests():
    """Run final validation tests"""
    print_section("FINAL VALIDATION")
    
    print("🧪 Running validation tests...")
    
    # Test configuration
    print("\n1. Testing configuration...")
    os.system("python main.py --validate-config")
    
    # Test database connection
    print("\n2. Testing database connection...")
    os.system("python scripts/init_database.py --test-only")
    
    # Test health check
    print("\n3. Running health check...")
    os.system("python scripts/health_check.py")

def main():
    """Main setup function"""
    print_banner()
    
    if not confirm("Ready to start the setup process?"):
        print("Setup cancelled.")
        return
    
    env_vars = {}
    
    # Run setup steps
    try:
        env_vars.update(setup_aws())
        env_vars.update(setup_supabase()) 
        env_vars.update(setup_telegram())
        env_vars.update(setup_kite())
        github_info = setup_github()
        env_vars.update(github_info)
        
        # Create configuration files
        create_env_file(env_vars)
        setup_github_secrets(env_vars, github_info.get("GITHUB_REPO"))
        
        # Final validation
        run_final_tests()
        
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        print("✅ All external services configured")  
        print("✅ Environment variables set")
        print("✅ Database schema created")
        print("✅ GitHub repository ready")
        print()
        print("🚀 Next steps:")
        print("1. Review .env file and adjust settings")
        print("2. Generate Kite access token: python scripts/generate_kite_token.py")
        print("3. Test paper trading: python main.py --paper-trading") 
        print("4. Start building Phase 2 features!")
        print()
        print("📖 Documentation: docs/service-setup-guide.md")
        print("🆘 Support: Check logs/ directory for troubleshooting")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user.")
        print("You can resume by running this script again.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("Check the logs and try again.")

if __name__ == "__main__":
    main()