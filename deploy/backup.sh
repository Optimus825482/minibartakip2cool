#!/bin/bash
# ============================================
# Minibar Takip - Database Backup Script
# Crontab'a ekle: 0 3 * * * /opt/minibar/deploy/backup.sh
# ============================================
set -e

APP_DIR="/opt/minibar"
BACKUP_DIR="$APP_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

mkdir -p $BACKUP_DIR

echo "📦 Database backup alınıyor..."

# Docker container içinden pg_dump çalıştır
docker compose -f $APP_DIR/docker-compose.yml exec -T postgres \
    pg_dump -U minibar_user -d minibar_takip --format=custom \
    > "$BACKUP_DIR/minibar_${DATE}.dump"

# Boyut kontrol
SIZE=$(du -h "$BACKUP_DIR/minibar_${DATE}.dump" | cut -f1)
echo "✅ Backup alındı: minibar_${DATE}.dump ($SIZE)"

# Eski backup'ları temizle
find $BACKUP_DIR -name "minibar_*.dump" -mtime +$KEEP_DAYS -delete
echo "🗑️  $KEEP_DAYS günden eski backup'lar temizlendi"
