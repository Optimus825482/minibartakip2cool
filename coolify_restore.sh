#!/bin/bash
# Coolify Restore Script'i
# Backup'tan database ve uploads'ı geri yükler

set -e

# Renkli output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "♻️  Minibar Restore Başlatılıyor..."
echo "=========================================="

# Backup dizini
BACKUP_DIR="/root/minibar_backups"

if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup dizini bulunamadı: $BACKUP_DIR${NC}"
    exit 1
fi

# Mevcut backupları listele
echo ""
echo "📋 Mevcut Backuplar:"
echo ""

BACKUPS=($(ls -1t "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo -e "${RED}❌ Hiç backup bulunamadı!${NC}"
    exit 1
fi

# Backupları numaralandır
for i in "${!BACKUPS[@]}"; do
    BACKUP_FILE="${BACKUPS[$i]}"
    BACKUP_NAME=$(basename "$BACKUP_FILE")
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    BACKUP_DATE=$(stat -c %y "$BACKUP_FILE" | cut -d' ' -f1,2 | cut -d'.' -f1)
    
    echo -e "${BLUE}[$((i+1))]${NC} $BACKUP_NAME"
    echo "    Boyut: $BACKUP_SIZE"
    echo "    Tarih: $BACKUP_DATE"
    echo ""
done

# Kullanıcıdan seçim al
echo -n "Hangi backup'ı restore etmek istiyorsunuz? (1-${#BACKUPS[@]}): "
read SELECTION

if ! [[ "$SELECTION" =~ ^[0-9]+$ ]] || [ "$SELECTION" -lt 1 ] || [ "$SELECTION" -gt ${#BACKUPS[@]} ]; then
    echo -e "${RED}❌ Geçersiz seçim!${NC}"
    exit 1
fi

SELECTED_BACKUP="${BACKUPS[$((SELECTION-1))]}"
echo ""
echo -e "${GREEN}✅ Seçilen backup: $(basename $SELECTED_BACKUP)${NC}"

# Onay al
echo ""
echo -e "${YELLOW}⚠️  UYARI: Bu işlem mevcut database'i silecek!${NC}"
echo -n "Devam etmek istediğinize emin misiniz? (yes/no): "
read CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}❌ İşlem iptal edildi${NC}"
    exit 0
fi

# PostgreSQL container'ı bul
POSTGRES_CONTAINER=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -n 1)

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo -e "${RED}❌ PostgreSQL container bulunamadı!${NC}"
    exit 1
fi

# Database bilgilerini al
DB_USER=$(docker exec $POSTGRES_CONTAINER printenv POSTGRES_USER)
DB_NAME=$(docker exec $POSTGRES_CONTAINER printenv POSTGRES_DB)

echo ""
echo "🗄️  Database restore ediliyor..."

# Backup'ı uncompress et
TEMP_SQL="/tmp/restore_$(date +%s).sql"
gunzip -c "$SELECTED_BACKUP" > "$TEMP_SQL"

# Database'i temizle ve restore et
docker exec -i $POSTGRES_CONTAINER psql -U $DB_USER -d postgres << EOF
-- Mevcut bağlantıları kes
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '$DB_NAME'
  AND pid <> pg_backend_pid();

-- Database'i drop ve yeniden oluştur
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF

# SQL dosyasını restore et
cat "$TEMP_SQL" | docker exec -i $POSTGRES_CONTAINER psql -U $DB_USER -d $DB_NAME

# Temp dosyayı sil
rm -f "$TEMP_SQL"

echo -e "${GREEN}✅ Database restore başarılı!${NC}"

# Uploads restore (varsa)
UPLOADS_BACKUP="${SELECTED_BACKUP/postgres_/uploads_}"
UPLOADS_BACKUP="${UPLOADS_BACKUP/.sql.gz/.tar.gz}"

if [ -f "$UPLOADS_BACKUP" ]; then
    echo ""
    echo "📁 Uploads restore ediliyor..."
    
    APP_CONTAINER=$(docker ps --filter "name=minibar-app" --format "{{.Names}}" | head -n 1)
    
    if [ -n "$APP_CONTAINER" ]; then
        # Mevcut uploads'ı yedekle
        docker exec $APP_CONTAINER mv /app/uploads /app/uploads.old 2>/dev/null || true
        
        # Yeni uploads'ı restore et
        cat "$UPLOADS_BACKUP" | docker exec -i $APP_CONTAINER tar -xzf - -C /
        
        # Eski uploads'ı sil
        docker exec $APP_CONTAINER rm -rf /app/uploads.old 2>/dev/null || true
        
        echo -e "${GREEN}✅ Uploads restore başarılı!${NC}"
    else
        echo -e "${YELLOW}⚠️  App container bulunamadı, uploads restore atlandı${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Uploads backup bulunamadı, atlandı${NC}"
fi

# Container'ları restart et
echo ""
echo "🔄 Container'lar yeniden başlatılıyor..."

if [ -n "$APP_CONTAINER" ]; then
    docker restart $APP_CONTAINER
    echo -e "${GREEN}✅ App container restart edildi${NC}"
fi

echo ""
echo "=========================================="
echo "✅ Restore Tamamlandı!"
echo "=========================================="
echo ""
echo "📊 Restore Özeti:"
echo "   - Database: $DB_NAME"
echo "   - Backup: $(basename $SELECTED_BACKUP)"
echo "   - Tarih: $(date)"
echo ""
echo "🔍 Kontrol için:"
echo "   docker logs -f $APP_CONTAINER"
echo ""
echo "=========================================="
