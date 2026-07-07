#!/bin/bash
# Niskala - Deploy Script
# One-click deployment

set -e

echo "=========================================="
echo "   Niskala Deployment"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from template...${NC}"
    cp gcp/.env.example .env
    echo -e "${RED}Please edit .env with your settings:${NC}"
    echo "  nano .env"
    echo ""
    echo "Required settings:"
    echo "  DB_PASSWORD - Database password"
    echo "  SECRET_KEY  - API secret key"
    exit 1
fi

# Source environment
source .env

# Validate required variables
if [ -z "$DB_PASSWORD" ] || [ "$DB_PASSWORD" = "change_me_to_a_secure_password" ]; then
    echo -e "${RED}Error: Please set DB_PASSWORD in .env${NC}"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "change_me_to_a_random_secret_key" ]; then
    echo -e "${RED}Error: Please set SECRET_KEY in .env${NC}"
    exit 1
fi

# Build and start containers
echo -e "${YELLOW}[1/4] Building containers...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

echo -e "${YELLOW}[2/4] Stopping old containers...${NC}"
docker-compose -f docker-compose.prod.yml down

echo -e "${YELLOW}[3/4] Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${YELLOW}[4/4] Waiting for services to start...${NC}"
sleep 10

# Check health
echo ""
echo "Checking service health..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "unhealthy\|restarting"; then
    echo -e "${RED}Some services failed to start. Checking logs...${NC}"
    docker-compose -f docker-compose.prod.yml logs --tail=50
    exit 1
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_VPS_IP")

echo ""
echo "=========================================="
echo -e "${GREEN}   Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Services:"
echo "  API:       http://${SERVER_IP}/api/"
echo "  WebSocket: ws://${SERVER_IP}/ws/"
echo "  Health:    http://${SERVER_IP}/health"
echo "  Docs:      http://${SERVER_IP}/api/docs"
echo ""
echo "Management:"
echo "  Logs:      docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart:   docker-compose -f docker-compose.prod.yml restart"
echo "  Stop:      docker-compose -f docker-compose.prod.yml down"
echo "  Status:    docker-compose -f docker-compose.prod.yml ps"
echo ""
