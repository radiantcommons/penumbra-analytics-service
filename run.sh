#!/bin/bash
# Penumbra Analytics Service Launcher

echo "🚀 Starting Penumbra Analytics Service..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Missing .env file"
    echo "📝 Copy .env.example to .env and configure:"
    echo "   cp .env.example .env"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check Python dependencies
if ! python -c "import aiohttp, prometheus_client, psycopg2" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt && sleep 1
fi

# Load environment variables and check required ones
export $(grep -v '^#' .env | xargs)

if [ -z "$PENUMBRA_RPC_ENDPOINT" ] || [ -z "$DISCORD_WEBHOOK_URL" ]; then
    echo "❌ Missing required environment variables"
    echo "   Set PENUMBRA_RPC_ENDPOINT and DISCORD_WEBHOOK_URL in .env"
    exit 1
fi

echo "✅ Configuration loaded"
echo "   RPC: $PENUMBRA_RPC_ENDPOINT"
echo "   Discord: $(echo $DISCORD_WEBHOOK_URL | cut -c1-30)..."
echo "   Indexer: ${PENUMBRA_INDEXER_ENDPOINT:-"Not set (using fallbacks)"}"
echo ""

# Start the service
echo "🔥 Starting service..."
python main.py
