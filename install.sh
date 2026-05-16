#!/usr/bin/env bash
# Kermes one-line installer
# curl -fsSL https://raw.githubusercontent.com/bbbirkan/2026-kermes/main/install.sh | bash

set -e

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}"
cat << 'EOF'
  _  __
 | |/ / ___ _ __ _ __ ___   ___  ___
 | ' / / _ \ '__| '_ ` _ \ / _ \/ __|
 | . \|  __/ |  | | | | | |  __/\__ \
 |_|\_\___|_|  |_| |_| |_|\___||___/
EOF
echo -e "${NC}"
echo "Installing Kermes — token-smart AI agents"
echo ""

# Python check
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found. Install Python 3.10+ first."
    exit 1
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python $PY_VERSION detected"

# Install
pip install --quiet --upgrade kermes-agent 2>/dev/null || {
    echo "pip install failed, trying from source..."
    git clone --depth 1 https://github.com/bbbirkan/2026-kermes.git /tmp/kermes-install
    pip install --quiet /tmp/kermes-install
    rm -rf /tmp/kermes-install
}

# Init config
echo ""
echo "Initializing config..."
kermes init

echo ""
echo -e "${YELLOW}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit ~/.kermes/config.yaml and set your api_key"
echo "  2. kermes chat      — start chatting"
echo "  3. kermes ask 'hi'  — single query"
echo ""
echo "Get an OpenRouter key (supports all models): https://openrouter.ai"
