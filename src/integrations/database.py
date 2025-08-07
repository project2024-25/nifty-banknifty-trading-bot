"""
Database Integration
Handles all database operations using Supabase
"""
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from supabase import create_client, Client
from decimal import Decimal

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.config = get_config()
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.client = create_client(
                self.config.supabase_url,
                self.config.supabase_key
            )
            logger.info("Database connection initialized")
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    def _ensure_connected(self):
        """Ensure database is connected"""
        if not self.client:
            raise Exception("Database not initialized. Call initialize() first.")
    
    # Trades Operations
    async def create_trade(self, trade_data: Dict[str, Any]) -> str:
        """Create a new trade record"""
        self._ensure_connected()
        
        try:
            result = self.client.table('trades').insert(trade_data).execute()
            trade_id = result.data[0]['id']
            
            logger.info(f"Trade created successfully", 
                       trade_id=trade_id,
                       symbol=trade_data.get('symbol'),
                       strategy=trade_data.get('strategy'))
            
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to create trade: {e}", trade_data=trade_data)
            raise
    
    async def update_trade(self, trade_id: str, update_data: Dict[str, Any]) -> bool:
        """Update existing trade record"""
        self._ensure_connected()
        
        try:
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('trades').update(update_data).eq('id', trade_id).execute()
            
            logger.info(f"Trade updated successfully", trade_id=trade_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update trade: {e}", 
                        trade_id=trade_id, 
                        update_data=update_data)
            return False
    
    async def get_open_trades(self, paper_trade: bool = True) -> List[Dict[str, Any]]:
        """Get all open trades"""
        self._ensure_connected()
        
        try:
            result = self.client.table('trades').select("*").eq('status', 'OPEN').eq('paper_trade', paper_trade).execute()
            
            logger.debug(f"Retrieved {len(result.data)} open trades")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get open trades: {e}")
            return []
    
    # Positions Operations
    async def upsert_position(self, position_data: Dict[str, Any]) -> bool:
        """Create or update position"""
        self._ensure_connected()
        
        try:
            result = self.client.table('positions').upsert(position_data).execute()
            
            logger.info("Position updated successfully",
                       symbol=position_data.get('symbol'),
                       strategy=position_data.get('strategy'))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert position: {e}", position_data=position_data)
            return False
    
    async def get_active_positions(self, paper_trade: bool = True) -> List[Dict[str, Any]]:
        """Get all active positions"""
        self._ensure_connected()
        
        try:
            result = self.client.from_('active_positions').select("*").eq('paper_trade', paper_trade).execute()
            
            logger.debug(f"Retrieved {len(result.data)} active positions")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get active positions: {e}")
            return []
    
    async def close_position(self, symbol: str, strategy: str, paper_trade: bool = True) -> bool:
        """Close a position by setting quantity to 0"""
        self._ensure_connected()
        
        try:
            update_data = {
                'quantity': 0,
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.client.table('positions').update(update_data).eq('symbol', symbol).eq('strategy', strategy).eq('paper_trade', paper_trade).execute()
            
            logger.info(f"Position closed", symbol=symbol, strategy=strategy)
            return True
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}", symbol=symbol, strategy=strategy)
            return False
    
    # Signals Operations
    async def create_signal(self, signal_data: Dict[str, Any]) -> str:
        """Create a new signal record"""
        self._ensure_connected()
        
        try:
            result = self.client.table('signals').insert(signal_data).execute()
            signal_id = result.data[0]['id']
            
            logger.info("Signal created successfully",
                       signal_id=signal_id,
                       symbol=signal_data.get('symbol'),
                       signal_type=signal_data.get('signal_type'),
                       confidence=signal_data.get('confidence'))
            
            return signal_id
            
        except Exception as e:
            logger.error(f"Failed to create signal: {e}", signal_data=signal_data)
            raise
    
    async def mark_signal_executed(self, signal_id: str, execution_time: datetime = None) -> bool:
        """Mark signal as executed"""
        self._ensure_connected()
        
        try:
            update_data = {
                'executed': True,
                'execution_time': (execution_time or datetime.now()).isoformat()
            }
            
            result = self.client.table('signals').update(update_data).eq('id', signal_id).execute()
            
            logger.info("Signal marked as executed", signal_id=signal_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark signal as executed: {e}", signal_id=signal_id)
            return False
    
    async def get_pending_signals(self) -> List[Dict[str, Any]]:
        """Get all pending (unexecuted) signals"""
        self._ensure_connected()
        
        try:
            result = self.client.table('signals').select("*").eq('executed', False).execute()
            
            logger.debug(f"Retrieved {len(result.data)} pending signals")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get pending signals: {e}")
            return []
    
    # Market Intelligence Operations
    async def store_intelligence(self, intelligence_data: Dict[str, Any]) -> str:
        """Store market intelligence data"""
        self._ensure_connected()
        
        try:
            result = self.client.table('market_intelligence').insert(intelligence_data).execute()
            intel_id = result.data[0]['id']
            
            logger.info("Intelligence data stored",
                       intel_id=intel_id,
                       source=intelligence_data.get('source'),
                       content_type=intelligence_data.get('content_type'))
            
            return intel_id
            
        except Exception as e:
            logger.error(f"Failed to store intelligence: {e}", intelligence_data=intelligence_data)
            raise
    
    # Performance Metrics Operations
    async def update_daily_metrics(self, date_val: date, metrics: Dict[str, Any], paper_trade: bool = True) -> bool:
        """Update daily performance metrics"""
        self._ensure_connected()
        
        try:
            metrics.update({
                'date': date_val.isoformat(),
                'period_type': 'daily',
                'paper_trade': paper_trade
            })
            
            result = self.client.table('performance_metrics').upsert(metrics).execute()
            
            logger.info("Daily metrics updated", date=date_val, paper_trade=paper_trade)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}", date=date_val, metrics=metrics)
            return False
    
    async def get_daily_pnl(self, days: int = 30, paper_trade: bool = True) -> List[Dict[str, Any]]:
        """Get daily P&L summary"""
        self._ensure_connected()
        
        try:
            result = self.client.from_('daily_pnl').select("*").eq('paper_trade', paper_trade).limit(days).execute()
            
            logger.debug(f"Retrieved {len(result.data)} days of P&L data")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get daily P&L: {e}")
            return []
    
    # Risk Events Operations
    async def log_risk_event(self, event_data: Dict[str, Any]) -> str:
        """Log a risk management event"""
        self._ensure_connected()
        
        try:
            result = self.client.table('risk_events').insert(event_data).execute()
            event_id = result.data[0]['id']
            
            logger.warning("Risk event logged",
                          event_id=event_id,
                          event_type=event_data.get('event_type'),
                          severity=event_data.get('severity'))
            
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to log risk event: {e}", event_data=event_data)
            raise
    
    async def get_unresolved_risk_events(self) -> List[Dict[str, Any]]:
        """Get all unresolved risk events"""
        self._ensure_connected()
        
        try:
            result = self.client.table('risk_events').select("*").eq('resolved', False).execute()
            
            logger.debug(f"Retrieved {len(result.data)} unresolved risk events")
            return result.data
            
        except Exception as e:
            logger.error(f"Failed to get unresolved risk events: {e}")
            return []
    
    # System Logs Operations
    async def log_system_event(self, log_data: Dict[str, Any]) -> bool:
        """Log system event to database"""
        self._ensure_connected()
        
        try:
            result = self.client.table('system_logs').insert(log_data).execute()
            return True
            
        except Exception as e:
            # Don't log this error to avoid recursion
            print(f"Failed to log system event: {e}")
            return False
    
    # Analytics and Reports
    async def calculate_performance_metrics(self, start_date: date, end_date: date, paper_trade: bool = True) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics for a period"""
        self._ensure_connected()
        
        try:
            # Get all closed trades in the period
            trades_result = self.client.table('trades').select("*").eq('status', 'CLOSED').eq('paper_trade', paper_trade).gte('entry_time', start_date.isoformat()).lte('entry_time', end_date.isoformat()).execute()
            
            trades = trades_result.data
            
            if not trades:
                return {
                    'total_trades': 0,
                    'total_pnl': 0,
                    'win_rate': 0,
                    'profit_factor': 0,
                    'sharpe_ratio': 0,
                    'max_drawdown': 0
                }
            
            # Calculate metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if float(t['pnl']) > 0])
            losing_trades = total_trades - winning_trades
            
            total_pnl = sum(float(t['pnl']) for t in trades)
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            gross_profit = sum(float(t['pnl']) for t in trades if float(t['pnl']) > 0)
            gross_loss = abs(sum(float(t['pnl']) for t in trades if float(t['pnl']) < 0))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Calculate max drawdown
            cumulative_pnl = 0
            peak = 0
            max_drawdown = 0
            
            for trade in sorted(trades, key=lambda x: x['entry_time']):
                cumulative_pnl += float(trade['pnl'])
                if cumulative_pnl > peak:
                    peak = cumulative_pnl
                drawdown = (peak - cumulative_pnl) / peak if peak > 0 else 0
                max_drawdown = max(max_drawdown, drawdown)
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'avg_trade_pnl': total_pnl / total_trades,
                'largest_win': max((float(t['pnl']) for t in trades), default=0),
                'largest_loss': min((float(t['pnl']) for t in trades), default=0)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()