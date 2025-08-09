-- Trading Bot Database Schema for Supabase
-- This script creates all necessary tables for the sophisticated trading system

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. TRADES TABLE - Core trade tracking
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    strategy VARCHAR(100) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(12,4),
    exit_price DECIMAL(12,4),
    entry_time TIMESTAMPTZ NOT NULL,
    exit_time TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
    pnl DECIMAL(12,4) DEFAULT 0,
    commission DECIMAL(12,4) DEFAULT 0,
    paper_trade BOOLEAN DEFAULT true,
    market_regime VARCHAR(50),
    confidence_score DECIMAL(3,2),
    risk_score DECIMAL(3,2),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. POSITIONS TABLE - Current position tracking
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    strategy VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    avg_price DECIMAL(12,4),
    current_price DECIMAL(12,4),
    unrealized_pnl DECIMAL(12,4) DEFAULT 0,
    paper_trade BOOLEAN DEFAULT true,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Composite unique constraint
    UNIQUE(symbol, strategy, paper_trade)
);

-- 3. SIGNALS TABLE - Trading signal tracking
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(50) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('BUY', 'SELL', 'HOLD')),
    confidence DECIMAL(3,2) NOT NULL,
    strategy VARCHAR(100) NOT NULL,
    market_regime VARCHAR(50),
    regime_confidence DECIMAL(3,2),
    price_target DECIMAL(12,4),
    stop_loss DECIMAL(12,4),
    executed BOOLEAN DEFAULT false,
    execution_time TIMESTAMPTZ,
    signal_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. MARKET_INTELLIGENCE TABLE - Market analysis data
CREATE TABLE market_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(100) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    symbol VARCHAR(50),
    regime VARCHAR(50),
    confidence DECIMAL(3,2),
    volatility_regime VARCHAR(20),
    trend_strength DECIMAL(3,2),
    momentum_score DECIMAL(3,2),
    support_resistance JSONB,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. PERFORMANCE_METRICS TABLE - Daily/periodic performance tracking
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL DEFAULT 'daily' CHECK (period_type IN ('daily', 'weekly', 'monthly')),
    paper_trade BOOLEAN DEFAULT true,
    total_pnl DECIMAL(12,4) DEFAULT 0,
    unrealized_pnl DECIMAL(12,4) DEFAULT 0,
    realized_pnl DECIMAL(12,4) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0,
    profit_factor DECIMAL(8,4) DEFAULT 0,
    max_drawdown DECIMAL(5,4) DEFAULT 0,
    sharpe_ratio DECIMAL(6,4) DEFAULT 0,
    portfolio_value DECIMAL(15,4),
    risk_utilization DECIMAL(3,2) DEFAULT 0,
    active_strategies JSONB,
    regime_distribution JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint for date-period-paper_trade combination
    UNIQUE(date, period_type, paper_trade)
);

-- 6. RISK_EVENTS TABLE - Risk management events
CREATE TABLE risk_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    symbol VARCHAR(50),
    strategy VARCHAR(100),
    description TEXT NOT NULL,
    risk_metric VARCHAR(50),
    current_value DECIMAL(12,4),
    threshold_value DECIMAL(12,4),
    action_taken VARCHAR(200),
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    paper_trade BOOLEAN DEFAULT true,
    event_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. SYSTEM_LOGS TABLE - System event logging
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level VARCHAR(20) NOT NULL CHECK (level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    source VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    execution_id VARCHAR(100),
    function_name VARCHAR(100),
    error_details TEXT,
    context_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. STRATEGY_PERFORMANCE TABLE - Strategy-specific performance tracking
CREATE TABLE strategy_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    strategy_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    paper_trade BOOLEAN DEFAULT true,
    trades_count INTEGER DEFAULT 0,
    total_pnl DECIMAL(12,4) DEFAULT 0,
    win_rate DECIMAL(5,4) DEFAULT 0,
    avg_trade_duration INTERVAL,
    max_drawdown DECIMAL(5,4) DEFAULT 0,
    profit_factor DECIMAL(8,4) DEFAULT 0,
    regime_performance JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(strategy_name, date, paper_trade)
);

-- VIEWS FOR EASY ACCESS

-- Active Positions View
CREATE VIEW active_positions AS
SELECT 
    p.*,
    COALESCE(p.unrealized_pnl, 0) as current_pnl,
    CASE 
        WHEN p.quantity > 0 THEN 'LONG'
        WHEN p.quantity < 0 THEN 'SHORT'
        ELSE 'FLAT'
    END as position_type
FROM positions p 
WHERE p.quantity != 0;

-- Daily P&L View
CREATE VIEW daily_pnl AS
SELECT 
    date,
    paper_trade,
    total_pnl,
    realized_pnl,
    unrealized_pnl,
    total_trades,
    win_rate,
    portfolio_value,
    risk_utilization,
    created_at
FROM performance_metrics 
WHERE period_type = 'daily'
ORDER BY date DESC;

-- Recent Trades View
CREATE VIEW recent_trades AS
SELECT 
    t.*,
    CASE 
        WHEN t.pnl > 0 THEN 'WIN'
        WHEN t.pnl < 0 THEN 'LOSS'
        ELSE 'BREAK_EVEN'
    END as trade_outcome,
    EXTRACT(EPOCH FROM (t.exit_time - t.entry_time))/3600 as trade_duration_hours
FROM trades t 
WHERE t.status = 'CLOSED'
ORDER BY t.exit_time DESC;

-- Market Intelligence Summary View
CREATE VIEW market_intelligence_summary AS
SELECT 
    symbol,
    regime,
    confidence,
    volatility_regime,
    trend_strength,
    momentum_score,
    created_at,
    ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY created_at DESC) as rn
FROM market_intelligence
WHERE created_at > NOW() - INTERVAL '1 day';

-- INDEXES for performance
CREATE INDEX idx_trades_symbol_status ON trades(symbol, status);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);
CREATE INDEX idx_trades_paper_trade ON trades(paper_trade);
CREATE INDEX idx_positions_symbol_strategy ON positions(symbol, strategy);
CREATE INDEX idx_signals_executed ON signals(executed);
CREATE INDEX idx_signals_created_at ON signals(created_at);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(date);
CREATE INDEX idx_risk_events_resolved ON risk_events(resolved);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_market_intelligence_symbol ON market_intelligence(symbol, created_at);

-- TRIGGERS for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trades_updated_at 
    BEFORE UPDATE ON trades 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at 
    BEFORE UPDATE ON positions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - Optional but recommended
-- ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE market_intelligence ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE risk_events ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE strategy_performance ENABLE ROW LEVEL SECURITY;

-- Sample data for testing (optional)
INSERT INTO performance_metrics (date, paper_trade, total_pnl, total_trades, portfolio_value) 
VALUES (CURRENT_DATE, true, 0, 0, 1000000);

COMMENT ON TABLE trades IS 'Core trading records with full trade lifecycle';
COMMENT ON TABLE positions IS 'Current position tracking with real-time P&L';
COMMENT ON TABLE signals IS 'Trading signals generated by the intelligence system';
COMMENT ON TABLE market_intelligence IS 'Market regime and analysis data';
COMMENT ON TABLE performance_metrics IS 'Daily and periodic performance tracking';
COMMENT ON TABLE risk_events IS 'Risk management events and alerts';
COMMENT ON TABLE system_logs IS 'System-wide logging and audit trail';
COMMENT ON TABLE strategy_performance IS 'Strategy-specific performance analytics';