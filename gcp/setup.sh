#!/bin/bash
# Niskala - VPS Setup Script
# Run this once on fresh Ubuntu VPS

set -e

echo "=========================================="
echo "   Niskala VPS Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo bash setup.sh${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}[1/8] Updating system...${NC}"
apt-get update && apt-get upgrade -y

# Install Docker
echo -e "${YELLOW}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}Docker installed${NC}"
else
    echo -e "${GREEN}Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "${YELLOW}[3/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
    echo -e "${GREEN}Docker Compose installed${NC}"
else
    echo -e "${GREEN}Docker Compose already installed${NC}"
fi

# Setup firewall
echo -e "${YELLOW}[4/8] Configuring firewall...${NC}"
apt-get install -y ufw
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
echo -e "${GREEN}Firewall configured${NC}"

# Install useful tools
echo -e "${YELLOW}[5/8] Installing utilities...${NC}"
apt-get install -y curl wget git htop tmux nano

# Create app directory
echo -e "${YELLOW}[6/8] Creating directories...${NC}"
mkdir -p /opt/niskala
mkdir -p /opt/niskala/backups
mkdir -p /var/log/niskala

# Setup automatic updates
echo -e "${YELLOW}[7/8] Configuring auto-updates...${NC}"
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Setup log rotation
echo -e "${YELLOW}[8/8] Configuring log rotation...${NC}"
cat > /etc/logrotate.d/niskala << 'EOF'
/var/log/niskala/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker kill --signal=USR1 niskala-nginx 2>/dev/null || true
    endscript
}
EOF

echo ""
echo "=========================================="
echo -e "${GREEN}   Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Clone Niskala: cd /opt/niskala && git clone https://github.com/niskala/niskala.git ."
echo "  2. Configure: cp gcp/.env.example .env && nano .env"
echo "  3. Deploy: chmod +x gcp/deploy.sh && ./gcp/deploy.sh"
echo ""
