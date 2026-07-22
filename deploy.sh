#!/bin/bash
set -e

# ============================================================
# Telegram Verification Bot - Linux VPS Deployment Script
# ============================================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="telegram-verification-bot"

info "==========================================="
info "  Bot deployment starting..."
info "==========================================="

# 1. System packages
info "Updating system packages..."
sudo apt update -y
sudo apt install -y python3 python3-pip python3-venv git

# 2. Create virtual environment
info "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 3. Install requirements
info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

# 4. Check config
info "Checking configuration..."
cd "$PROJECT_DIR"
python3 -c "
from config import BOT_TOKEN, OWNER_ID
print(f'  Bot token: {BOT_TOKEN[:10]}...')
print(f'  Owner ID: {OWNER_ID}')
print('  Configuration OK')
"

# 5. Create data directory
mkdir -p "$PROJECT_DIR/data"
info "Data directory created"

# 6. Create systemd service
info "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Verification Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$VENV_DIR/bin
ExecStart=$VENV_DIR/bin/python3 $PROJECT_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 7. Enable and start service
info "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

# 8. Check status
sleep 3
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    info "==========================================="
    info "  Bot successfully deployed and running!"
    info "  Service: $SERVICE_NAME"
    info ""
    info "  Commands:"
    info "  sudo systemctl status $SERVICE_NAME"
    info "  sudo systemctl restart $SERVICE_NAME"
    info "  sudo systemctl stop $SERVICE_NAME"
    info "  sudo journalctl -u $SERVICE_NAME -f"
    info "==========================================="
else
    warn "Service is not running. Checking logs..."
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 20
fi
