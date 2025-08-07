-- Nifty/BankNifty Trading Bot Database Schema
-- Supabase PostgreSQL Database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trades table - stores all executed trades
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_time TIMESTAMP WITH TIME ZONE,
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    trade_type VARCHAR(10) NOT NULL, -- BUY/SELL
    order_type VARCHAR(10) NOT NULL, -- MARKET/LIMIT/SL/SL-M
    pnl DECIMAL(10,2) DEFAULT 0,
    commission DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OPEN', -- OPEN/CLOSED/PARTIAL
    trade_category VARCHAR(20) NOT NULL, -- CONSERVATIVE/AGGRESSIVE
    paper_trade BOOLEAN DEFAULT true,
    notes TEXT,
    kite_order_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Positions table - tracks current open positions
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    unrealized_pnl DECIMAL(10,2) DEFAULT 0,
    strategy VARCHAR(50) NOT NULL,
    trade_category VARCHAR(20) NOT NULL,
    paper_trade BOOLEAN DEFAULT true,
    stop_loss DECIMAL(10,2),
    target_price DECIMAL(10,2),
    kite_order_id VARCHAR(50),
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_symbol_strategy UNIQUE(symbol, strategy, paper_trade)
);

-- Signals table - stores all generated trading signals
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL, -- youtube/technical/ml/combined
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(30) NOT NULL, -- BUY/SELL/IRON_CONDOR/STRADDLE etc
    confidence DECIMAL(3,2) CHECK (confidence >= 0 AND confidence <= 1),
    strategy VARCHAR(50) NOT NULL,
    entry_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    quantity INTEGER,
    metadata JSONB, -- Store additional signal data
    executed BOOLEAN DEFAULT false,
    execution_time TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market intelligence table - stores scraped/analyzed market data
CREATE TABLE IF NOT EXISTS market_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(50) NOT NULL, -- youtube/varsity/reddit/news
    content_type VARCHAR(50) NOT NULL, -- video/article/post/analysis
    title TEXT,
    content TEXT,
    extracted_data JSONB, -- Structured extracted information
    sentiment_score DECIMAL(3,2), -- -1 to 1 sentiment
    processed BOOLEAN DEFAULT FALSE,
    relevance_score DECIMAL(3,2), -- 0 to 1 relevance
    symbols TEXT[], -- Array of relevant symbols
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- System logs table - application logs and events
CREATE TABLE IF NOT EXISTS system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(10) NOT NULL, -- INFO/DEBUG/WARNING/ERROR/CRITICAL
    message TEXT NOT NULL,
    module VARCHAR(100),
    function_name VARCHAR(100),
    line_number INTEGER,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table - daily/weekly/monthly performance
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    period_type VARCHAR(10) NOT NULL, -- daily/weekly/monthly
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(12,2) DEFAULT 0,
    conservative_pnl DECIMAL(12,2) DEFAULT 0,
    aggressive_pnl DECIMAL(12,2) DEFAULT 0,
    max_drawdown DECIMAL(10,2) DEFAULT 0,
    sharpe_ratio DECIMAL(6,4),
    win_rate DECIMAL(5,4),
    profit_factor DECIMAL(6,4),
    largest_win DECIMAL(10,2) DEFAULT 0,
    largest_loss DECIMAL(10,2) DEFAULT 0,
    paper_trade BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_date_period_paper UNIQUE(date, period_type, paper_trade)
);

-- Risk events table - track risk management events
CREATE TABLE IF NOT EXISTS risk_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(30) NOT NULL, -- LIMIT_EXCEEDED/STOP_TRIGGERED/EMERGENCY_STOP
    severity VARCHAR(10) NOT NULL, -- LOW/MEDIUM/HIGH/CRITICAL
    description TEXT NOT NULL,
    current_value DECIMAL(10,2),
    limit_value DECIMAL(10,2),
    action_taken VARCHAR(100),
    trade_id UUID REFERENCES trades(id),
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User sessions table - track system usage
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_type VARCHAR(20) NOT NULL, -- telegram/api/system
    user_id VARCHAR(50),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    commands_executed INTEGER DEFAULT 0,
    trades_executed INTEGER DEFAULT 0,
    metadata JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trades_symbol_date ON trades(symbol, entry_time);
CREATE INDEX IF NOT EXISTS idx_trades_strategy ON trades(strategy);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_paper ON trades(paper_trade);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_strategy ON positions(strategy);
CREATE INDEX IF NOT EXISTS idx_positions_paper ON positions(paper_trade);

CREATE INDEX IF NOT EXISTS idx_signals_symbol_date ON signals(symbol, created_at);
CREATE INDEX IF NOT EXISTS idx_signals_executed ON signals(executed);
CREATE INDEX IF NOT EXISTS idx_signals_confidence ON signals(confidence);

CREATE INDEX IF NOT EXISTS idx_intelligence_source ON market_intelligence(source);
CREATE INDEX IF NOT EXISTS idx_intelligence_processed ON market_intelligence(processed);
CREATE INDEX IF NOT EXISTS idx_intelligence_date ON market_intelligence(created_at);

CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON system_logs(timestamp);

CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date);
CREATE INDEX IF NOT EXISTS idx_performance_paper ON performance_metrics(paper_trade);

CREATE INDEX IF NOT EXISTS idx_risk_events_type ON risk_events(event_type);
CREATE INDEX IF NOT EXISTS idx_risk_events_severity ON risk_events(severity);
CREATE INDEX IF NOT EXISTS idx_risk_events_resolved ON risk_events(resolved);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_trades_updated_at BEFORE UPDATE ON trades
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (Row Level Security) policies for multi-tenancy (if needed later)
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE signals ENABLE ROW LEVEL SECURITY;

-- Insert some initial data for testing
INSERT INTO performance_metrics (date, period_type, paper_trade) 
VALUES (CURRENT_DATE, 'daily', true)
ON CONFLICT (date, period_type, paper_trade) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW active_positions AS
SELECT 
    p.*,
    t.entry_time,
    COALESCE(p.unrealized_pnl, 0) as current_pnl,
    CASE 
        WHEN p.current_price > 0 THEN 
            ((p.current_price - p.entry_price) / p.entry_price * 100)
        ELSE 0 
    END as pnl_percentage
FROM positions p
LEFT JOIN trades t ON p.symbol = t.symbol AND p.strategy = t.strategy
WHERE p.quantity != 0;

CREATE OR REPLACE VIEW daily_pnl AS
SELECT 
    DATE(entry_time) as trade_date,
    strategy,
    trade_category,
    paper_trade,
    COUNT(*) as trade_count,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    MAX(pnl) as max_profit,
    MIN(pnl) as max_loss
FROM trades 
WHERE status = 'CLOSED'
GROUP BY DATE(entry_time), strategy, trade_category, paper_trade
ORDER BY trade_date DESC;

-- Function to calculate Sharpe ratio
CREATE OR REPLACE FUNCTION calculate_sharpe_ratio(
    start_date DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    end_date DATE DEFAULT CURRENT_DATE,
    risk_free_rate DECIMAL DEFAULT 0.06
) 
RETURNS DECIMAL AS $$
DECLARE
    avg_return DECIMAL;
    return_stddev DECIMAL;
    sharpe DECIMAL;
BEGIN
    SELECT 
        AVG(daily_return),
        STDDEV(daily_return)
    INTO avg_return, return_stddev
    FROM (
        SELECT 
            DATE(entry_time) as trade_date,
            SUM(pnl) as daily_return
        FROM trades 
        WHERE DATE(entry_time) BETWEEN start_date AND end_date
        AND status = 'CLOSED'
        GROUP BY DATE(entry_time)
    ) daily_returns;
    
    IF return_stddev > 0 THEN
        sharpe := (avg_return * 252 - risk_free_rate) / (return_stddev * SQRT(252));
    ELSE
        sharpe := 0;
    END IF;
    
    RETURN sharpe;
END;
$$ LANGUAGE plpgsql;