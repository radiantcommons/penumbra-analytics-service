"""
Discord notification sender
"""

import aiohttp
import ssl
import logging
from typing import Dict, Any

logger = logging.getLogger('discord-notifier')

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        logger.info("Discord notifier initialized")
    
    async def send_message(self, message: str, title: str = "Penumbra Network Update"):
        """Send message to Discord"""
        try:
            # Create Discord embed
            embed = {
                "title": title,
                "description": message,
                "color": 0x7447FF,  # Penumbra purple
                "timestamp": None,  # Discord will use current time
                "footer": {
                    "text": "Penumbra Analytics Service"
                }
            }
            
            payload = {
                "embeds": [embed]
            }
            
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload, ssl=ssl_context) as resp:
                    if resp.status == 204:
                        logger.info("Discord message sent successfully")
                    else:
                        logger.error(f"Discord error: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error sending Discord message: {e}")
            raise
