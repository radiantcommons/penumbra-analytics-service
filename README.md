# Penumbra Analytics Service

A lightweight analytics service for the Penumbra network that:
- ✅ Collects essential blockchain data from Penumbra RPC
- ✅ Queries real trading data from Pindexer database (optional)
- ✅ Sends concise Discord updates every 3 hours
- ✅ Exposes clean Prometheus metrics for Grafana dashboards

## 🚀 Quick Start

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the service:**
```bash
./run.sh
# Or manually: source venv/bin/activate && python main.py
```

## ⚙️ Configuration

### Required Environment Variables
- `PENUMBRA_RPC_ENDPOINT` - Penumbra RPC endpoint
- `DISCORD_WEBHOOK_URL` - Discord webhook for notifications

### Optional Environment Variables
- `PENUMBRA_INDEXER_ENDPOINT` - PostgreSQL connection string for real trading data
- `UPDATE_INTERVAL_SECONDS` - How often to collect data (default: 30)
- `DISCORD_INTERVAL_HOURS` - Discord message frequency (default: 3)
- `METRICS_PORT` - Prometheus metrics port (default: 8081)

## 📊 Endpoints

### Prometheus Metrics (Grafana)
- `GET http://localhost:8081/metrics` - Prometheus metrics for Grafana
- `GET http://localhost:8081/health` - Health check

### Sample Metrics
```
penumbra_block_height
penumbra_current_epoch
penumbra_tvl_total_usd
penumbra_tvl_dex_usd
penumbra_trading_volume_24h_usd
penumbra_transactions_24h_total
penumbra_lqt_participants_total
penumbra_mvas_percentage
```

## 🎯 Features

### Discord Updates (Every 3 Hours)
- Network status (epoch, block height, uptime)
- TVL breakdown (total, DEX, staking)
- Trading activity (pairs, volume, top pair)
- LQT tournament stats
- Privacy metrics (MVAS)
- Transaction rates

### Real Data Integration
- **With Pindexer**: Real trading pairs, volumes, and participant counts
- **Without Pindexer**: Realistic fallback estimates with transparent labeling
- **Always**: Real network data from Penumbra RPC

### Grafana Compatibility
- Complete Prometheus metrics
- Compatible with existing dashboards
- Clean metric naming conventions
- Health monitoring included

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────┐
│ Penumbra RPC    │───▶│ Data         │───▶│ Discord     │
│ (Network Data)  │    │ Collector    │    │ Notifier    │
└─────────────────┘    │              │    └─────────────┘
                       │              │
┌─────────────────┐    │              │    ┌─────────────┐
│ Pindexer DB     │───▶│              │───▶│ Prometheus  │
│ (Trading Data)  │    │              │    │ Metrics     │
└─────────────────┘    └──────────────┘    └─────────────┘
```

## 📈 Data Sources

1. **Penumbra RPC** - Block height, epoch, network status
2. **Pindexer Database** (optional) - Trading pairs, volumes, real activity
3. **Fallback Estimates** - When real data unavailable, uses realistic estimates

## 🔍 Example Discord Message

```
🌟 Penumbra Network Status Update

📊 Network Health
• Current Epoch: 461
• Block Height: 5,287,931
• Network Uptime: 99.9%

💰 Total Value Locked (TVL)
• Total TVL: $158,226
• DEX TVL: $105,817
• Staking TVL: $52,409

🔄 Trading Activity
• Active Trading Pairs: 5
• 24h Volume: $4,233
• Top Pair: UM/USDC

🏆 LQT Tournament
• Total Participants: 1,024
• Active (24h): 25
• 24h Volume: $3,386

⚡ Network Activity
• Transactions (24h): 253
• Tx Rate: 0.2/min

🔒 Privacy (MVAS)
• MVAS Adoption: 15.5%
• Private Volume (24h): $656

⏰ Next Update: 21:30 UTC (3h)
```

## 🚀 Production Deployment

The service is designed to be lightweight and production-ready:
- Minimal dependencies
- Robust error handling
- Fallback data sources
- Health monitoring
- Configurable intervals
- Clean logging

Ready for Docker, Kubernetes, or direct deployment!
