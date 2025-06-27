#!/usr/bin/env python3
"""
Penumbra Analytics Service - Lightweight Bot
Collects data from Penumbra RPC + Pindexer, sends Discord updates, exposes Grafana metrics
"""

import os
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from data_collector import PenumbraDataCollector
from discord_notifier import DiscordNotifier
from metrics_server import MetricsServer
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('penumbra-analytics')

class PenumbraAnalyticsService:
    def __init__(self):
        self.config = Config()
        self.data_collector = PenumbraDataCollector(
            rpc_endpoint=self.config.PENUMBRA_RPC_ENDPOINT,
            indexer_endpoint=self.config.PENUMBRA_INDEXER_ENDPOINT,
            indexer_ca_cert=self.config.PENUMBRA_INDEXER_CA_CERT
        )
        self.discord_notifier = DiscordNotifier(self.config.DISCORD_WEBHOOK_URL)
        self.metrics_server = MetricsServer(port=self.config.METRICS_PORT)
        
        self.last_discord_message = datetime.now() - timedelta(hours=4)  # Send first message immediately
        self.update_interval = self.config.UPDATE_INTERVAL_SECONDS
        self.discord_interval_hours = self.config.DISCORD_INTERVAL_HOURS
        
        logger.info("Penumbra Analytics Service initialized")
    
    async def collect_and_update_data(self) -> Dict[str, Any]:
        """Collect all data and update metrics"""
        try:
            # Collect data from all sources
            data = await self.data_collector.collect_all_data()
            
            # Update Prometheus metrics
            self.metrics_server.update_metrics(data)
            
            logger.info(f"Data updated - Epoch: {data['network']['current_epoch']}, "
                       f"Height: {data['network']['block_height']}, "
                       f"TVL: ${data['tvl']['total_usd']:,.0f}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting data: {e}")
            return None
    
    def should_send_discord_message(self) -> bool:
        """Check if it's time to send Discord message"""
        now = datetime.now()
        time_since_last = now - self.last_discord_message
        return time_since_last.total_seconds() >= (self.discord_interval_hours * 3600)
    
    async def send_discord_update(self, data: Dict[str, Any]):
        """Send Discord status update"""
        try:
            message = self.format_discord_message(data)
            await self.discord_notifier.send_message(message)
            self.last_discord_message = datetime.now()
            logger.info("Discord update sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
    
    def format_discord_message(self, data: Dict[str, Any]) -> str:
        """Format data into Discord message"""
        network = data['network']
        trading = data['trading']
        lqt = data['lqt']
        tvl = data['tvl']
        transactions = data['transactions']
        privacy = data['privacy']
        
        # Calculate next update time
        next_update = datetime.now() + timedelta(hours=self.discord_interval_hours)
        
        message = f"""🌟 **Penumbra Network Status Update**

📊 **Network Health**
• Current Epoch: **{network['current_epoch']}**
• Block Height: **{network['block_height']:,}**
• Network Uptime: **{network['network_uptime_percentage']:.1f}%**

💰 **Total Value Locked (TVL)**
• Total TVL: **${tvl['dex_usd']:,.0f}**
• DEX TVL: **${tvl['dex_usd']:,.0f} USDC**
• Staking TVL: **{data['staking']['total_staked_um']:,.0f} UM**

🔄 **Trading Activity**
• Active Trading Pairs: **{trading['active_pairs_count']}**
• 24h Volume: **${trading['total_volume_24h_usd']:,.0f} USDC**
• Top 3 Pairs:
{self.format_top_pairs(trading['top_pairs'])}

🏆 **LQT Tournament**
• Total Participants: **{lqt['total_participants']:,}**
• Active (24h): **{lqt['active_participants_24h']}**
• 24h Volume: **${lqt['volume_24h_usd']:,.0f}**

⚡ **Network Activity**
• Transactions (24h): **{transactions['total_24h']}**
• Tx Rate: **{transactions['per_minute']}/min**

🔒 **Privacy (MVAS)**
• MVAS Adoption: **{privacy['mvas_percentage']:.1f}%**
• Private Volume (24h): **${privacy['mvas_volume_24h_usd']:,.0f}**

⏰ **Next Update:** {next_update.strftime('%H:%M UTC')} ({self.discord_interval_hours}h)

*Data powered by Penumbra RPC & Pindexer*"""
        
        return message
    
    def format_top_pairs(self, top_pairs) -> str:
        """Format top trading pairs for Discord message"""
        if not top_pairs:
            return "  • No trading pairs available"
        
        formatted_pairs = []
        for i, pair in enumerate(top_pairs[:3]):  # Top 3 pairs
            # Clean up pair name - try to extract meaningful symbols
            pair_name = pair.get('name', 'Unknown')
            if len(pair_name) > 20:  # If it's a long hex string
                pair_name = f"Pair #{i+1}"  # Fallback to generic name
            
            volume = pair.get('volume', '0 USDC')
            formatted_pairs.append(f"  • **{pair_name}**: {volume}")
        
        return '\n'.join(formatted_pairs)
    
    async def run(self):
        """Main service loop"""
        logger.info("Starting Penumbra Analytics Service...")
        
        # Start metrics server
        await self.metrics_server.start()
        
        try:
            while True:
                # Collect and update data
                data = await self.collect_and_update_data()
                
                if data:
                    # Send Discord message if it's time
                    if self.should_send_discord_message():
                        await self.send_discord_update(data)
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
        except Exception as e:
            logger.error(f"Service error: {e}")
        finally:
            await self.metrics_server.stop()

if __name__ == "__main__":
    service = PenumbraAnalyticsService()
    asyncio.run(service.run())
