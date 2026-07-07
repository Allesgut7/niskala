#!/bin/bash
# Niskala - Restore Script
# Restore PostgreSQL and Redis from backup

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_DIR="/opt/niskala/backups"

echo "=========================================="
echo "   Niskala Restore"
echo "=========================================="

# List available backups
echo -e "${YELLOW}Available PostgreSQL backups:${NC}"
ls -1 "${BACKUP_DIR}"/postgres_*.sql.gz 2>/dev/null | head -10

echo ""
echo -e "${YELLOW}Available Redis backups:${NC}"
ls -1 "${BACKUP_DIR}"/redis_*.rdb 2>/dev/null | head -10

echo ""
read -p "Enter PostgreSQL backup filename (or 'latest'): " PG_BACKUP
read -p "Enter Redis backup filename (or 'latest' or 'skip'): " REDIS_BACKUP

# Handle 'latest'
if [ "$PG_BACKUP" = "latest" ]; then
    PG_BACKUP=$(ls -t "${BACKUP_DIR}"/postgres_*.sql.gz | head -1)
fi

if [ "$REDIS_BACKUP" = "latest" ]; then
    REDIS_BACKUP=$(ls -t "${BACKUP_DIR}"/redis_*.rdb | head -1)
fi

# Confirm
echo ""
echo -e "${RED}WARNING: This will overwrite current data!${NC}"
read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

# Restore PostgreSQL
if [ -n "$PG_BACKUP" ] && [ -f "$PG_BACKUP" ] && [ "$PG_BACKUP" != "skip" ]; then
    echo -e "${YELLOW}[1/2] Restoring PostgreSQL from ${PG_BACKUP}...${NC}"
    
    # Stop API temporarily
    docker-compose -f docker-compose.prod.yml stop api worker
    
    # Restore
    gunzip -c "$PG_BACKUP" | docker exec -i niskala-postgres psql -U niskala -d niskala
    
    # Restart API
    docker-compose -f docker-compose.prod.yml start api worker
    
    echo -e "${GREEN}PostgreSQL restore complete${NC}"
else
    echo -e "${YELLOW}Skipping PostgreSQL restore${NC}"
fi

# Restore Redis
if [ -n "$REDIS_BACKUP" ] && [ -f "$REDIS_BACKUP" ] && [ "$REDIS_BACKUP" != "skip" ]; then
    echo -e "${YELLOW}[2/2] Restoring Redis from ${REDIS_BACKUP}...${NC}"
    
    # Stop Redis
    docker-compose -f docker-compose.prod.yml stop redis
    
    # Restore
    docker cp "$REDIS_BACKUP" niskala-redis:/data/dump.rdb
    
    # Start Redis
    docker-compose -f docker-compose.prod.yml start redis
    
    echo -e "${GREEN}Redis restore complete${NC}"
else
    echo -e "${YELLOW}Skipping Redis restore${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}   Restore Complete!${NC}"
echo "=========================================="
echo ""
