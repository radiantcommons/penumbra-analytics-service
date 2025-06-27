"""
Configuration for Penumbra Analytics Service
"""

import os
from typing import Optional

class Config:
    """Configuration class for the service"""
    
    def __init__(self):
        # Penumbra endpoints
        self.PENUMBRA_RPC_ENDPOINT = os.getenv('PENUMBRA_RPC_ENDPOINT', 'https://rpc-penumbra.radiantcommons.com')
        self.PENUMBRA_GRPC_ENDPOINT = os.getenv('PENUMBRA_GRPC_ENDPOINT', 'https://penumbra-1.radiantcommons.com')
        self.PENUMBRA_INDEXER_ENDPOINT = os.getenv('PENUMBRA_INDEXER_ENDPOINT')
        self.PENUMBRA_INDEXER_CA_CERT = os.getenv('PENUMBRA_INDEXER_CA_CERT')
        
        # Discord
        self.DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
        
        # API Server
        self.API_PORT = int(os.getenv('API_PORT', '8080'))
        self.METRICS_PORT = int(os.getenv('METRICS_PORT', '8081'))
        
        # Service configuration
        self.UPDATE_INTERVAL_SECONDS = int(os.getenv('UPDATE_INTERVAL_SECONDS', '30'))
        self.DISCORD_INTERVAL_HOURS = float(os.getenv('DISCORD_INTERVAL_HOURS', '3'))
        
        # Validate required config
        self._validate()
    
    def _validate(self):
        """Validate required configuration"""
        required_fields = [
            ('PENUMBRA_RPC_ENDPOINT', self.PENUMBRA_RPC_ENDPOINT),
            ('DISCORD_WEBHOOK_URL', self.DISCORD_WEBHOOK_URL),
        ]
        
        missing = [field for field, value in required_fields if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print(f"✅ Configuration loaded:")
        print(f"   RPC: {self.PENUMBRA_RPC_ENDPOINT}")
        print(f"   gRPC: {self.PENUMBRA_GRPC_ENDPOINT}")
        print(f"   Indexer: {'✅ Set' if self.PENUMBRA_INDEXER_ENDPOINT else '❌ Not set (will use fallbacks)'}")
        print(f"   Indexer CA Cert: {'✅ Set' if self.PENUMBRA_INDEXER_CA_CERT else '❌ Not set'}")
        print(f"   Discord: {'✅ Set' if self.DISCORD_WEBHOOK_URL else '❌ Not set'}")
        print(f"   Update interval: {self.UPDATE_INTERVAL_SECONDS}s")
        print(f"   Discord interval: {self.DISCORD_INTERVAL_HOURS}h")
        print(f"   Metrics port: {self.METRICS_PORT}")
