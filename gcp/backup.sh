#!/bin/bash
# Niskala - Backup Script
# Backup PostgreSQL and Redis data

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_DIR="/opt/niskala/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

echo "=========================================="
echo "   Niskala Backup - ${TIMESTAMP}"
echo "=========================================="

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup PostgreSQL
echo -e "${YELLOW}[1/2] Backing up PostgreSQL...${NC}"
docker exec niskala-postgres pg_dump -U niskala niskala | gzip > "${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"
echo -e "${GREEN}PostgreSQL backup complete${NC}"

# Backup Redis
echo -e "${YELLOW}[2/2] Backing up Redis...${NC}"
docker exec niskala-redis redis-cli BGSAVE
sleep 2
docker cp niskala-redis:/data/dump.rdb "${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"
echo -e "${GREEN}Redis backup complete${NC}"

# Cleanup old backups
echo -e "${YELLOW}Cleaning up backups older than ${KEEP_DAYS} days...${NC}"
find "${BACKUP_DIR}" -name "postgres_*.sql.gz" -mtime +${KEEP_DAYS} -delete
find "${BACKUP_DIR}" -name "redis_*.rdb" -mtime +${KEEP_DAYS} -delete

echo ""
echo "=========================================="
echo -e "${GREEN}   Backup Complete!${NC}"
echo "=========================================="
echo ""
echo "Backup location: ${BACKUP_DIR}"
echo "Files:"
ls -lh "${BACKUP_DIR}"/*_${TIMESTAMP}* 2>/dev/null
echo ""
