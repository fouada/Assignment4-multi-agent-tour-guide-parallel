#!/bin/bash
# ============================================================================
# Multi-Agent Tour Guide - Setup Script
# ============================================================================
# This script sets up the project with UV
# Usage: ./scripts/setup.sh
# ============================================================================

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🗺️  Multi-Agent Tour Guide - Setup                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if UV is installed
echo "📦 Checking for UV..."
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    echo -e "${GREEN}✅ UV installed!${NC}"
else
    echo -e "${GREEN}✅ UV already installed: $(uv --version)${NC}"
fi

echo ""

# Sync dependencies
echo "📦 Syncing dependencies..."
uv sync --extra dev

echo ""
echo -e "${GREEN}✅ Dependencies synced!${NC}"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found.${NC}"
    echo "   Creating from template..."
    
    cat > .env << 'EOF'
# Multi-Agent Tour Guide - Environment Variables
# Add your API keys below

# Required for LLM-powered agents
OPENAI_API_KEY=

# Optional for real APIs
GOOGLE_MAPS_API_KEY=
YOUTUBE_API_KEY=
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
EOF
    
    echo -e "${GREEN}✅ Created .env file. Please add your API keys!${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Add your API keys to .env"
echo "  2. Run: ${YELLOW}make run${NC} to start the demo"
echo "  3. Run: ${YELLOW}make test${NC} to run tests"
echo ""
echo "Useful commands:"
echo "  ${YELLOW}make help${NC}      - Show all available commands"
echo "  ${YELLOW}make run${NC}       - Run demo"
echo "  ${YELLOW}make dev${NC}       - Sync dev dependencies"
echo "  ${YELLOW}make test${NC}      - Run tests"
echo "  ${YELLOW}make lint${NC}      - Check code quality"
echo ""

