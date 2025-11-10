#!/bin/bash
# Coolify Backup Script'i
# Database ve uploads klasörünü yedekler

set -e

# Konfigürasyon
BACKUP_DIR="/root/minibar_backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Renkli output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "💾 Minibar Backup Başlatılıyor..."
echo "=========================================="

# Backup dizini oluştur
mkdir -p "$BACKUP_DIR"

# PostgreSQL container adını bul
POSTGRES_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -n 1)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo -e "${RED}❌ PostgreSQL container bulunamadı!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL container: $POSTGRES_CONTAINER${NC}"

# Database bilgilerini al
DB_USER=$(docker exec $POSTGRES_CONTAINER printenv POSTGRES_USER)
DB_NAME=$(docker exec $POSTGRES_CONTAINER printenv POSTGRES_DB)

echo ""
echo "📊 Backup Bilgileri:"
echo "   - Database: $DB_NAME"
echo "   - User: $DB_USER"
echo "   - Date: $DATE"

# 1. PostgreSQL Backup
echo ""
echo "🗄️  PostgreSQL backup alınıyor..."

BACKUP_FILE="$BACKUP_DIR/postgres_${DATE}.sql"

docker exec $POSTGRES_CONTAINER pg_dump -U $DB_USER $DB_NAME > "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ PostgreSQL backup başarılı: $BACKUP_SIZE${NC}"
    
    # Compress
    gzip "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backup sıkıştırıldı: ${BACKUP_FILE}.gz${NC}"
else
    echo -e "${RED}❌ PostgreSQL backup başarısız!${NC}"
    exit 1
fi

# 2. Uploads Backup
echo ""
echo "📁 Uploads klasörü yedekleniyor..."

APP_CONTAINER=$(docker ps --filter "name=minibar-app" --format "{{.Names}}" | head -n 1)

if [ -n "$APP_CONTAINER" ]; then
    UPLOADS_BACKUP="$BACKUP_DIR/uploads_${DATE}.tar.gz"
    
    docker exec $APP_CONTAINER tar -czf - /app/uploads > "$UPLOADS_BACKUP" 2>/dev/null || true
    
    if [ -f "$UPLOADS_BACKUP" ]; then
        UPLOADS_SIZE=$(du -h "$UPLOADS_BACKUP" | cut -f1)
        echo -e "${GREEN}✅ Uploads backup başarılı: $UPLOADS_SIZE${NC}"
    else
        echo -e "${YELLOW}⚠️  Uploads backup atlandı (klasör boş olabilir)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  App container bulunamadı, uploads backup atlandı${NC}"
fi

# 3. Eski backupları temizle
echo ""
echo "🧹 Eski backuplar temizleniyor (${RETENTION_DAYS} günden eski)..."

find "$BACKUP_DIR" -name "*.gz" -type f -mtime +$RETENTION_DAYS -delete

REMAINING_BACKUPS=$(ls -1 "$BACKUP_DIR"/*.gz 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Temizlik tamamlandı. Kalan backup sayısı: $REMAINING_BACKUPS${NC}"

# 4. Backup özeti
echo ""
echo "=========================================="
echo "✅ Backup Tamamlandı!"
echo "=========================================="
echo ""
echo "📊 Backup Özeti:"
ls -lh "$BACKUP_DIR" | tail -n +2 | awk '{print "   - " $9 " (" $5 ")"}'
echo ""
echo "📁 Backup Dizini: $BACKUP_DIR"
echo "🔄 Retention: $RETENTION_DAYS gün"
echo ""

# 5. Disk kullanımı uyarısı
DISK_USAGE=$(df -h "$BACKUP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${RED}⚠️  UYARI: Disk kullanımı %${DISK_USAGE}! Yer açmanız gerekebilir.${NC}"
elif [ "$DISK_USAGE" -gt 70 ]; then
    echo -e "${YELLOW}⚠️  Disk kullanımı %${DISK_USAGE}${NC}"
else
    echo -e "${GREEN}✅ Disk kullanımı: %${DISK_USAGE}${NC}"
fi

echo ""
echo "=========================================="
