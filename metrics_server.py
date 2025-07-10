"""
Prometheus metrics server for Grafana integration
"""

import asyncio
import logging
from aiohttp import web
from prometheus_client import Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict, Any

logger = logging.getLogger('metrics-server')

class MetricsServer:
    def __init__(self, port: int = 8081):
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        
        # Define all Prometheus metrics
        self.setup_metrics()
        logger.info(f"Metrics server initialized on port {port}")
    
    def setup_metrics(self):
        """Setup all Prometheus metrics"""
        # Network metrics
        self.block_height = Gauge('penumbra_block_height', 'Current block height')
        self.current_epoch = Gauge('penumbra_current_epoch', 'Current epoch')
        self.network_uptime = Gauge('penumbra_network_uptime_percentage', 'Network uptime percentage')
        
        # TVL metrics
        self.tvl_total = Gauge('penumbra_tvl_total_usd', 'Total Value Locked in USD')
        self.tvl_dex = Gauge('penumbra_tvl_dex_usd', 'DEX TVL in USD')
        self.tvl_staking = Gauge('penumbra_tvl_staking_usd', 'Staking TVL in USD')
        
        # Trading metrics
        self.trading_pairs_count = Gauge('penumbra_trading_pairs_count', 'Number of active trading pairs')
        self.trading_volume_24h = Gauge('penumbra_trading_volume_24h_usd', '24h trading volume in USD')
        
        # Transaction metrics
        self.transactions_24h = Gauge('penumbra_transactions_24h_total', 'Total transactions in 24h')
        self.transactions_per_second = Gauge('penumbra_transactions_per_second', 'Transactions per second')
        self.transactions_per_minute = Gauge('penumbra_transactions_per_minute', 'Transactions per minute')
        
        # LQT metrics
        self.lqt_participants_total = Gauge('penumbra_lqt_participants_total', 'Total LQT participants')
        self.lqt_participants_24h = Gauge('penumbra_lqt_participants_24h', 'Active LQT participants in 24h')
        self.lqt_volume_24h = Gauge('penumbra_lqt_volume_24h_usd', 'LQT volume in 24h USD')
        
        # Staking metrics
        self.active_validators = Gauge('penumbra_active_validators', 'Number of active validators')
        self.total_staked_um = Gauge('penumbra_total_staked_um', 'Total staked UM')
        self.total_staked_usd = Gauge('penumbra_total_staked_usd', 'Total staked value in USD')
        
        # Address metrics
        self.active_addresses_daily = Gauge('penumbra_active_addresses_daily', 'Active addresses daily')
        self.active_addresses_weekly = Gauge('penumbra_active_addresses_weekly', 'Active addresses weekly')
        
        # Bot health metrics
        self.bot_uptime_hours = Gauge('penumbra_bot_uptime_hours', 'Bot uptime in hours')
        self.bot_errors_24h = Counter('penumbra_bot_errors_24h_total', 'Bot errors in 24h')
        self.bot_last_update = Gauge('penumbra_bot_last_update_timestamp', 'Last update timestamp')
        
        # Data source health
        self.data_source_healthy = Gauge('penumbra_data_source_healthy', 'Data source health status', ['source'])
    
    def update_metrics(self, data: Dict[str, Any]):
        """Update all metrics with new data"""
        try:
            # Network metrics
            self.block_height.set(data['network']['block_height'])
            self.current_epoch.set(data['network']['current_epoch'])
            self.network_uptime.set(data['network']['network_uptime_percentage'])
            
            # TVL metrics
            self.tvl_total.set(data['tvl']['total_usd'])
            self.tvl_dex.set(data['tvl']['dex_usd'])
            self.tvl_staking.set(data['tvl']['staking_usd'])
            
            # Trading metrics
            self.trading_pairs_count.set(data['trading']['active_pairs_count'])
            self.trading_volume_24h.set(data['trading']['total_volume_24h_usd'])
            
            # Transaction metrics
            self.transactions_24h.set(data['transactions']['total_24h'])
            self.transactions_per_second.set(data['transactions']['per_second'])
            self.transactions_per_minute.set(data['transactions']['per_minute'])
            
            # LQT metrics
            self.lqt_participants_total.set(data['lqt']['total_participants'])
            self.lqt_participants_24h.set(data['lqt']['active_participants_24h'])
            self.lqt_volume_24h.set(data['lqt']['volume_24h_usd'])
            
            # Staking metrics
            self.active_validators.set(data['staking']['active_validators'])
            self.total_staked_um.set(data['staking']['total_staked_um'])
            self.total_staked_usd.set(data['staking']['total_staked_usd'])
            
            # Address metrics
            self.active_addresses_daily.set(data['addresses']['active_daily'])
            self.active_addresses_weekly.set(data['addresses']['active_weekly'])
            
            # Bot health metrics
            self.bot_uptime_hours.set(data['bot_health']['uptime_hours'])
            
            # Data source health
            for source_name, source_data in data['data_sources'].items():
                self.data_source_healthy.labels(source=source_name).set(1 if source_data['healthy'] else 0)
            
            # Update timestamp
            import time
            self.bot_last_update.set(time.time())
            
            logger.debug("Metrics updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
    
    async def metrics_handler(self, request):
        """Handle /metrics endpoint"""
        try:
            metrics_output = generate_latest()
            return web.Response(body=metrics_output, headers={'Content-Type': CONTENT_TYPE_LATEST})
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return web.Response(text="Error generating metrics", status=500)
    
    async def health_handler(self, request):
        """Handle /health endpoint"""
        return web.json_response({"status": "healthy", "service": "penumbra-analytics"})
    
    async def start(self):
        """Start the metrics server"""
        try:
            self.app = web.Application()
            self.app.router.add_get('/metrics', self.metrics_handler)
            self.app.router.add_get('/health', self.health_handler)
            
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            
            logger.info(f"Metrics server started on http://0.0.0.0:{self.port}")
            logger.info(f"  GET /metrics - Prometheus metrics")
            logger.info(f"  GET /health - Health check")
            
        except Exception as e:
            logger.error(f"Error starting metrics server: {e}")
            raise
    
    async def stop(self):
        """Stop the metrics server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Metrics server stopped")
