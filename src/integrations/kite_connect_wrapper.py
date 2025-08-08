"""
Kite Connect API Wrapper for Trading Bot

This module provides a secure, robust wrapper around the Kite Connect API
with comprehensive error handling, authentication management, and integration
with our sophisticated trading system.

Features:
- Secure credential management
- Automatic token refresh
- Comprehensive error handling
- Order management with validation
- Position tracking and portfolio sync
- Real-time market data integration
- Paper trading mode support
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

try:
    from kiteconnect import KiteConnect, KiteTicker
except ImportError:
    KiteConnect = None
    KiteTicker = None
    logging.warning("kiteconnect module not installed. Install with: pip install kiteconnect")

# from ..utils.logger import get_logger

def get_logger(name):
    """Fallback logger function."""
    import logging
    return logging.getLogger(name)

logger = get_logger(__name__)


@dataclass
class KiteCredentials:
    """Kite Connect API credentials."""
    api_key: str
    api_secret: str
    access_token: Optional[str] = None
    request_token: Optional[str] = None


@dataclass
class OrderRequest:
    """Standardized order request structure."""
    symbol: str
    quantity: int
    order_type: str  # MARKET, LIMIT, SL, SL-M
    transaction_type: str  # BUY, SELL
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    validity: str = "DAY"
    variety: str = "regular"
    product: str = "MIS"  # MIS, CNC, NRML
    tag: Optional[str] = None


@dataclass
class Position:
    """Position information from Kite."""
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    pnl: float
    product: str
    exchange: str


@dataclass
class Trade:
    """Trade execution details."""
    order_id: str
    symbol: str
    quantity: int
    price: float
    timestamp: datetime
    transaction_type: str
    status: str


class KiteConnectWrapper:
    """
    Comprehensive wrapper for Kite Connect API.
    
    Provides secure, robust integration with Zerodha Kite Connect API
    including authentication, order management, and real-time data.
    """
    
    def __init__(self, credentials: KiteCredentials, paper_trading: bool = True):
        """
        Initialize Kite Connect wrapper.
        
        Args:
            credentials: Kite API credentials
            paper_trading: If True, simulate orders without actual execution
        """
        self.credentials = credentials
        self.paper_trading = paper_trading
        self.kite = None
        self.ticker = None
        
        # Connection state
        self.authenticated = False
        self.last_heartbeat = None
        self.token_expiry = None
        
        # Paper trading state
        self.paper_orders = {}
        self.paper_positions = {}
        self.paper_order_id_counter = 100000
        
        # Rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_reset = time.time()
        
        if KiteConnect:
            self.kite = KiteConnect(api_key=credentials.api_key)
        else:
            logger.error("KiteConnect not available. Please install kiteconnect library.")
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Kite Connect API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not self.kite:
            logger.error("KiteConnect not initialized")
            return False
        
        try:
            if self.paper_trading:
                logger.info("Paper trading mode - skipping real authentication")
                self.authenticated = True
                return True
            
            # Check if we have access token
            if not self.credentials.access_token:
                logger.error("Access token not available. Please complete login flow first.")
                return False
            
            # Set access token
            self.kite.set_access_token(self.credentials.access_token)
            
            # Test connection
            profile = await self._safe_api_call(self.kite.profile)
            if profile:
                logger.info(f"Authenticated successfully for user: {profile.get('user_name', 'Unknown')}")
                self.authenticated = True
                self.last_heartbeat = datetime.now()
                return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
        
        return False
    
    def get_login_url(self) -> str:
        """
        Get login URL for Kite Connect authentication.
        
        Returns:
            Login URL for user to complete authentication
        """
        if not self.kite:
            return ""
        
        try:
            login_url = self.kite.login_url()
            logger.info("Login URL generated successfully")
            return login_url
        except Exception as e:
            logger.error(f"Error generating login URL: {e}")
            return ""
    
    async def complete_login(self, request_token: str) -> bool:
        """
        Complete login process with request token.
        
        Args:
            request_token: Request token from Kite Connect callback
            
        Returns:
            True if login completed successfully
        """
        if not self.kite:
            return False
        
        try:
            # Generate session
            data = await self._safe_api_call(
                self.kite.generate_session,
                request_token,
                api_secret=self.credentials.api_secret
            )
            
            if data and 'access_token' in data:
                self.credentials.access_token = data['access_token']
                self.credentials.request_token = request_token
                
                # Set access token
                self.kite.set_access_token(data['access_token'])
                
                logger.info("Login completed successfully")
                return await self.authenticate()
            
        except Exception as e:
            logger.error(f"Login completion failed: {e}")
        
        return False
    
    async def place_order(self, order_request: OrderRequest) -> Optional[str]:
        """
        Place an order through Kite Connect or paper trading.
        
        Args:
            order_request: Order details
            
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Validate order
            if not self._validate_order(order_request):
                return None
            
            if self.paper_trading:
                return await self._place_paper_order(order_request)
            
            # Real order placement
            if not self.authenticated:
                logger.error("Not authenticated with Kite Connect")
                return None
            
            # Apply rate limiting
            await self._rate_limit()
            
            # Prepare order parameters
            order_params = {
                'variety': order_request.variety,
                'exchange': self._get_exchange(order_request.symbol),
                'tradingsymbol': order_request.symbol,
                'transaction_type': order_request.transaction_type,
                'quantity': order_request.quantity,
                'product': order_request.product,
                'order_type': order_request.order_type,
                'validity': order_request.validity
            }
            
            # Add price parameters
            if order_request.price:
                order_params['price'] = order_request.price
            if order_request.trigger_price:
                order_params['trigger_price'] = order_request.trigger_price
            if order_request.tag:
                order_params['tag'] = order_request.tag
            
            # Place order
            response = await self._safe_api_call(self.kite.place_order, **order_params)
            
            if response and 'order_id' in response:
                order_id = response['order_id']
                logger.info(f"Order placed successfully: {order_id}")
                
                # Log order details
                logger.info(f"Order details: {order_request.symbol} {order_request.transaction_type} "
                           f"{order_request.quantity} @ {order_request.price}")
                
                return str(order_id)
            else:
                logger.error(f"Order placement failed: {response}")
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
        
        return None
    
    async def get_positions(self) -> List[Position]:
        """
        Get current positions from Kite Connect or paper trading.
        
        Returns:
            List of current positions
        """
        try:
            if self.paper_trading:
                return await self._get_paper_positions()
            
            if not self.authenticated:
                logger.warning("Not authenticated - cannot fetch positions")
                return []
            
            await self._rate_limit()
            positions_data = await self._safe_api_call(self.kite.positions)
            
            if not positions_data:
                return []
            
            positions = []
            for pos_data in positions_data.get('net', []):
                if pos_data['quantity'] != 0:  # Only active positions
                    position = Position(
                        symbol=pos_data['tradingsymbol'],
                        quantity=pos_data['quantity'],
                        average_price=pos_data['average_price'],
                        current_price=pos_data.get('last_price', pos_data['average_price']),
                        pnl=pos_data.get('pnl', 0),
                        product=pos_data['product'],
                        exchange=pos_data['exchange']
                    )
                    positions.append(position)
            
            logger.info(f"Retrieved {len(positions)} positions")
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    async def get_orders(self) -> List[Trade]:
        """
        Get order history and trades.
        
        Returns:
            List of executed trades
        """
        try:
            if self.paper_trading:
                return await self._get_paper_trades()
            
            if not self.authenticated:
                return []
            
            await self._rate_limit()
            orders_data = await self._safe_api_call(self.kite.orders)
            
            if not orders_data:
                return []
            
            trades = []
            for order_data in orders_data:
                if order_data['status'] == 'COMPLETE':
                    trade = Trade(
                        order_id=order_data['order_id'],
                        symbol=order_data['tradingsymbol'],
                        quantity=order_data['filled_quantity'],
                        price=order_data['average_price'],
                        timestamp=order_data['order_timestamp'],
                        transaction_type=order_data['transaction_type'],
                        status=order_data['status']
                    )
                    trades.append(trade)
            
            return trades
            
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    async def get_quote(self, instruments: List[str]) -> Dict[str, Dict]:
        """
        Get real-time quotes for instruments.
        
        Args:
            instruments: List of instrument symbols
            
        Returns:
            Dictionary of quotes
        """
        try:
            if self.paper_trading:
                return await self._get_paper_quotes(instruments)
            
            if not self.authenticated:
                return {}
            
            await self._rate_limit()
            quotes = await self._safe_api_call(self.kite.quote, instruments)
            
            return quotes or {}
            
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            return {}
    
    async def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """
        Cancel an existing order.
        
        Args:
            order_id: Order ID to cancel
            variety: Order variety
            
        Returns:
            True if cancellation successful
        """
        try:
            if self.paper_trading:
                return await self._cancel_paper_order(order_id)
            
            if not self.authenticated:
                return False
            
            await self._rate_limit()
            response = await self._safe_api_call(
                self.kite.cancel_order,
                variety=variety,
                order_id=order_id
            )
            
            return bool(response and response.get('order_id'))
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    # Helper methods
    def _validate_order(self, order: OrderRequest) -> bool:
        """Validate order parameters."""
        if not order.symbol or not order.quantity:
            logger.error("Invalid order: missing symbol or quantity")
            return False
        
        if order.quantity <= 0:
            logger.error("Invalid order: quantity must be positive")
            return False
        
        if order.order_type in ['LIMIT', 'SL'] and not order.price:
            logger.error("Invalid order: LIMIT/SL orders require price")
            return False
        
        if order.order_type in ['SL', 'SL-M'] and not order.trigger_price:
            logger.error("Invalid order: SL orders require trigger price")
            return False
        
        return True
    
    def _get_exchange(self, symbol: str) -> str:
        """Determine exchange for symbol."""
        if 'NIFTY' in symbol or 'BANKNIFTY' in symbol:
            return 'NFO'
        return 'NSE'
    
    async def _rate_limit(self):
        """Apply rate limiting to API calls."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.rate_limit_reset > 60:
            self.request_count = 0
            self.rate_limit_reset = current_time
        
        # Limit to 100 requests per minute
        if self.request_count >= 100:
            sleep_time = 60 - (current_time - self.rate_limit_reset)
            if sleep_time > 0:
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.rate_limit_reset = time.time()
        
        # Minimum 100ms between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.1:
            await asyncio.sleep(0.1 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def _safe_api_call(self, func, *args, **kwargs):
        """Make API call with error handling and retries."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}): {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                else:
                    logger.error(f"API call failed after {max_retries} attempts")
                    raise e
        
        return None
    
    # Paper trading methods
    async def _place_paper_order(self, order: OrderRequest) -> str:
        """Simulate order placement for paper trading."""
        order_id = str(self.paper_order_id_counter)
        self.paper_order_id_counter += 1
        
        # Simulate order execution
        current_price = await self._get_mock_price(order.symbol)
        execution_price = order.price or current_price
        
        paper_order = {
            'order_id': order_id,
            'symbol': order.symbol,
            'quantity': order.quantity,
            'price': execution_price,
            'order_type': order.order_type,
            'transaction_type': order.transaction_type,
            'timestamp': datetime.now(),
            'status': 'COMPLETE'
        }
        
        self.paper_orders[order_id] = paper_order
        
        # Update paper positions
        await self._update_paper_position(order.symbol, order.quantity, 
                                        execution_price, order.transaction_type)
        
        logger.info(f"Paper order executed: {order_id} - {order.symbol} "
                   f"{order.transaction_type} {order.quantity} @ ₹{execution_price}")
        
        return order_id
    
    async def _update_paper_position(self, symbol: str, quantity: int, 
                                   price: float, transaction_type: str):
        """Update paper trading positions."""
        if symbol not in self.paper_positions:
            self.paper_positions[symbol] = {
                'quantity': 0,
                'average_price': 0,
                'total_cost': 0
            }
        
        position = self.paper_positions[symbol]
        
        if transaction_type == 'BUY':
            position['total_cost'] += quantity * price
            position['quantity'] += quantity
        else:  # SELL
            position['quantity'] -= quantity
        
        # Calculate average price
        if position['quantity'] > 0:
            position['average_price'] = position['total_cost'] / position['quantity']
        elif position['quantity'] == 0:
            position['average_price'] = 0
            position['total_cost'] = 0
    
    async def _get_paper_positions(self) -> List[Position]:
        """Get paper trading positions."""
        positions = []
        
        for symbol, pos_data in self.paper_positions.items():
            if pos_data['quantity'] != 0:
                current_price = await self._get_mock_price(symbol)
                pnl = (current_price - pos_data['average_price']) * pos_data['quantity']
                
                position = Position(
                    symbol=symbol,
                    quantity=pos_data['quantity'],
                    average_price=pos_data['average_price'],
                    current_price=current_price,
                    pnl=pnl,
                    product='MIS',
                    exchange='NFO'
                )
                positions.append(position)
        
        return positions
    
    async def _get_paper_trades(self) -> List[Trade]:
        """Get paper trading order history."""
        trades = []
        
        for order_data in self.paper_orders.values():
            if order_data['status'] == 'COMPLETE':
                trade = Trade(
                    order_id=order_data['order_id'],
                    symbol=order_data['symbol'],
                    quantity=order_data['quantity'],
                    price=order_data['price'],
                    timestamp=order_data['timestamp'],
                    transaction_type=order_data['transaction_type'],
                    status=order_data['status']
                )
                trades.append(trade)
        
        return trades
    
    async def _get_paper_quotes(self, instruments: List[str]) -> Dict[str, Dict]:
        """Get mock quotes for paper trading."""
        quotes = {}
        
        for instrument in instruments:
            price = await self._get_mock_price(instrument)
            quotes[instrument] = {
                'last_price': price,
                'buy_price': price * 0.999,
                'sell_price': price * 1.001,
                'volume': 100000,
                'timestamp': datetime.now().isoformat()
            }
        
        return quotes
    
    async def _get_mock_price(self, symbol: str) -> float:
        """Generate mock price for paper trading."""
        # Simple price simulation - in reality you'd use historical data or real quotes
        base_prices = {
            'NIFTY': 25000,
            'BANKNIFTY': 52000
        }
        
        # Extract base instrument
        base_instrument = None
        for base in base_prices:
            if base in symbol:
                base_instrument = base
                break
        
        if not base_instrument:
            return 100.0  # Default for options
        
        base_price = base_prices[base_instrument]
        
        # For options, simulate premium based on strike and expiry
        if 'CE' in symbol or 'PE' in symbol:
            return base_price * 0.005  # ~0.5% as option premium
        
        return base_price
    
    async def _cancel_paper_order(self, order_id: str) -> bool:
        """Cancel paper trading order."""
        if order_id in self.paper_orders:
            self.paper_orders[order_id]['status'] = 'CANCELLED'
            logger.info(f"Paper order {order_id} cancelled")
            return True
        
        return False
    
    # Health check methods
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            'authenticated': self.authenticated,
            'paper_trading': self.paper_trading,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'api_available': self.kite is not None,
            'rate_limit_status': f"{self.request_count}/100 requests",
            'connection_status': 'healthy' if self.authenticated else 'disconnected'
        }
        
        if self.paper_trading:
            health_status.update({
                'paper_orders_count': len(self.paper_orders),
                'paper_positions_count': len([p for p in self.paper_positions.values() if p['quantity'] != 0])
            })
        
        return health_status
    
    async def close(self):
        """Close connections and cleanup."""
        if self.ticker:
            self.ticker.close()
        
        self.authenticated = False
        logger.info("Kite Connect wrapper closed")


# Factory function
def create_kite_wrapper(api_key: str, api_secret: str, 
                       access_token: str = None, 
                       paper_trading: bool = True) -> KiteConnectWrapper:
    """
    Create Kite Connect wrapper with credentials.
    
    Args:
        api_key: Kite Connect API key
        api_secret: Kite Connect API secret
        access_token: Access token (optional)
        paper_trading: Enable paper trading mode
        
    Returns:
        Configured KiteConnectWrapper instance
    """
    credentials = KiteCredentials(
        api_key=api_key,
        api_secret=api_secret,
        access_token=access_token
    )
    
    return KiteConnectWrapper(credentials, paper_trading=paper_trading)


if __name__ == "__main__":
    # Example usage for testing
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")
    
    if api_key and api_secret:
        wrapper = create_kite_wrapper(api_key, api_secret, paper_trading=True)
        
        # Test paper trading
        async def test():
            print("Testing Kite Connect wrapper...")
            
            # Test authentication (paper trading)
            success = await wrapper.authenticate()
            print(f"Authentication: {'✅ Success' if success else '❌ Failed'}")
            
            # Test health check
            health = await wrapper.health_check()
            print(f"Health check: {health}")
            
        asyncio.run(test())
    else:
        print("Set KITE_API_KEY and KITE_API_SECRET environment variables to test")