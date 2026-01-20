"""
Orchestration Service

Glue layer that connects Binance consumer, C++ indicator engine,
and FastAPI server. Manages the data flow pipeline.

Responsibilities:
- Initialize and coordinate all components
- Handle trade data from consumer and route to engine
- Trigger periodic database snapshots
- Manage application lifecycle
"""

# TODO: Implement orchestration logic
# - Component initialization
# - Trade data pipeline (consumer → engine)
# - Periodic snapshot persistence
# - Graceful startup/shutdown
# - Error handling and recovery



from app.services.indicators import IndicatorService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class OrchestrationService:
    """Coordinates between Binance consumer and indicator engine."""
    
    def __init__(self):
        self.indicator_service = IndicatorService(
            vwap_window=settings.max_trade_window,
            rsi_period = settings.rsi_period
        )
        
        logger.info("OrchestrationService initialized.")
        
    async def handle_trade(self, trade_data:dict):
        """Process incoming trade data from Binance consumer."""
        try:
            
            #Add to indicator engine
            self.indicator_service.add_trade(trade_data)
            
        except Exception as e:
            logger.error("Error processing trade data: %s", e)
    
    def get_indicators(self, symbol: str):
        """Get indicators for a specific symbol."""
        
        return self.indicator_service.get_indicators(symbol)
            
            