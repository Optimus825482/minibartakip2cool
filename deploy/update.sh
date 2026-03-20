#!/bin/bash
# ============================================
# Minibar Takip - Güncelleme Script
# Yeni kod deploy etmek için kullan
# ============================================
set -e

APP_DIR="/opt/minibar"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔄 Minibar güncelleniyor...${NC}"

cd $APP_DIR

# 1. Yeni dosyaları kopyala (git pull veya rsync)
if [ -d ".git" ]; then
    echo "Git pull yapılıyor..."
    git pull origin main
else
    echo -e "${YELLOW}Git repo değil. Dosyaları manuel kopyala veya git init yap.${NC}"
fi

# 2. Sadece web ve celery container'larını rebuild et (DB'ye dokunma)
echo "Container'lar rebuild ediliyor..."
docker compose build web celery-worker celery-beat

# 3. Zero-downtime restart
echo "Yeniden başlatılıyor..."
docker compose up -d --no-deps web celery-worker celery-beat

# 4. Sağlık kontrolü
echo "Sağlık kontrolü..."
sleep 10
if curl -sf http://localhost:5001/health > /dev/null; then
    echo -e "${GREEN}✅ Güncelleme başarılı! Uygulama çalışıyor.${NC}"
else
    echo -e "${YELLOW}⚠️  Health check başarısız. Logları kontrol et:${NC}"
    echo "  docker compose logs --tail=50 web"
fi

docker compose ps
