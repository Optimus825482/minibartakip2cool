#!/bin/bash
# ============================================
# Minibar Takip Sistemi - VPS Deploy Script
# Tek komutla sunucuya kur
# ============================================
set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MINIBAR TAKİP - VPS DEPLOY SCRIPT${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================
# 1. PARAMETRELER
# ============================================
DOMAIN=${1:-""}
EMAIL=${2:-""}
APP_DIR="/opt/minibar"

if [ -z "$DOMAIN" ]; then
    echo -e "${YELLOW}Kullanım: ./deploy.sh <domain> <email>${NC}"
    echo -e "${YELLOW}Örnek:    ./deploy.sh minibar.example.com admin@example.com${NC}"
    echo ""
    echo -e "Domain olmadan localhost kurulumu yapılacak (SSL yok)."
    echo -n "Devam etmek istiyor musun? (e/h): "
    read -r CONFIRM
    if [ "$CONFIRM" != "e" ]; then
        echo "İptal edildi."
        exit 0
    fi
fi

# ============================================
# 2. SİSTEM GÜNCELLEMESİ + BAĞIMLILIKLAR
# ============================================
echo -e "\n${GREEN}[1/7] Sistem güncelleniyor...${NC}"
apt-get update -qq
apt-get install -y -qq docker.io docker-compose-plugin curl git ufw > /dev/null 2>&1

# Docker servisini başlat
systemctl enable docker
systemctl start docker

echo -e "${GREEN}✅ Docker ve bağımlılıklar kuruldu${NC}"

# ============================================
# 3. FIREWALL AYARLARI
# ============================================
echo -e "\n${GREEN}[2/7] Firewall ayarlanıyor...${NC}"
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable
echo -e "${GREEN}✅ Firewall aktif (22, 80, 443 açık)${NC}"

# ============================================
# 4. UYGULAMA DİZİNİ
# ============================================
echo -e "\n${GREEN}[3/7] Uygulama dizini hazırlanıyor...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/backups
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/xls
mkdir -p $APP_DIR/static
mkdir -p $APP_DIR/ml_models

# Eğer bu script repo içinden çalışıyorsa, dosyaları kopyala
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$REPO_DIR/app.py" ]; then
    echo "Repo dosyaları kopyalanıyor..."
    rsync -a --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
          --exclude='.env' --exclude='*.pyc' --exclude='venv' \
          "$REPO_DIR/" "$APP_DIR/"
    echo -e "${GREEN}✅ Dosyalar kopyalandı${NC}"
else
    echo -e "${YELLOW}⚠️  Repo bulunamadı. Dosyaları manuel olarak $APP_DIR dizinine kopyala.${NC}"
fi

# ============================================
# 5. ENV DOSYASI OLUŞTUR
# ============================================
echo -e "\n${GREEN}[4/7] Environment dosyası oluşturuluyor...${NC}"

if [ ! -f "$APP_DIR/.env" ]; then
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))" 2>/dev/null || openssl rand -base64 48)
    DB_PASS=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))" 2>/dev/null || openssl rand -base64 24)

    cat > "$APP_DIR/.env" << EOF
# ============================================
# Minibar Takip - Production Environment
# Oluşturulma: $(date +%Y-%m-%d)
# ============================================

# Database
DB_USER=minibar_user
DB_PASSWORD=${DB_PASS}
DB_NAME=minibar_takip
DATABASE_URL=postgresql://minibar_user:${DB_PASS}@postgres:5432/minibar_takip

# Flask
FLASK_ENV=production
SECRET_KEY=${SECRET}

# Redis (Celery broker)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Gunicorn
GUNICORN_WORKERS=3
GUNICORN_THREADS=6
GUNICORN_TIMEOUT=300

# ML
ML_ENABLED=true
ML_MIN_DATA_POINTS=30

# Timezone
TZ=Europe/Nicosia
PYTHONUNBUFFERED=1
EOF

    echo -e "${GREEN}✅ .env dosyası oluşturuldu (güçlü şifreler üretildi)${NC}"
    echo -e "${YELLOW}   DB Password: ${DB_PASS}${NC}"
    echo -e "${YELLOW}   Bu şifreyi güvenli bir yere kaydet!${NC}"
else
    echo -e "${YELLOW}⚠️  .env zaten mevcut, dokunulmadı${NC}"
fi

# ============================================
# 6. NGINX + SSL KURULUMU
# ============================================
echo -e "\n${GREEN}[5/7] Nginx kurulumu...${NC}"

if [ -n "$DOMAIN" ]; then
    # Nginx kur
    apt-get install -y -qq nginx certbot python3-certbot-nginx > /dev/null 2>&1

    # Nginx config'i kopyala ve domain'i yerleştir
    cp "$APP_DIR/deploy/nginx/minibar.conf" /etc/nginx/sites-available/minibar
    sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/minibar

    # Aktifleştir
    ln -sf /etc/nginx/sites-available/minibar /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default

    # Static dosyalar için symlink
    ln -sf $APP_DIR/static /opt/minibar/static
    ln -sf $APP_DIR/uploads /opt/minibar/uploads

    # Nginx'i test et ve başlat
    nginx -t
    systemctl restart nginx

    echo -e "${GREEN}✅ Nginx kuruldu${NC}"

    # SSL sertifikası al
    if [ -n "$EMAIL" ]; then
        echo -e "\n${GREEN}[6/7] SSL sertifikası alınıyor...${NC}"
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect
        echo -e "${GREEN}✅ SSL sertifikası alındı (otomatik yenileme aktif)${NC}"
    else
        echo -e "${YELLOW}⚠️  Email verilmedi, SSL atlanıyor. Manuel kur:${NC}"
        echo -e "${YELLOW}   certbot --nginx -d $DOMAIN${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Domain verilmedi, Nginx atlanıyor (localhost:5001 üzerinden erişim)${NC}"
fi

# ============================================
# 7. DOCKER COMPOSE BAŞLAT
# ============================================
echo -e "\n${GREEN}[7/7] Docker Compose başlatılıyor...${NC}"

cd $APP_DIR

# Eski container'ları durdur
docker compose down 2>/dev/null || true

# Build ve başlat
docker compose up -d --build

# Durumu kontrol et
echo ""
echo -e "${GREEN}Container durumları:${NC}"
docker compose ps

# ============================================
# SONUÇ
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ DEPLOY TAMAMLANDI!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ -n "$DOMAIN" ]; then
    echo -e "🌐 Uygulama: https://$DOMAIN"
else
    echo -e "🌐 Uygulama: http://SUNUCU_IP:5001"
fi

echo -e "📊 pgAdmin:   http://SUNUCU_IP:8080 (docker compose --profile tools up -d)"
echo ""
echo -e "${YELLOW}Faydalı komutlar:${NC}"
echo -e "  cd $APP_DIR"
echo -e "  docker compose logs -f web          # Uygulama logları"
echo -e "  docker compose logs -f celery-worker # Celery logları"
echo -e "  docker compose restart web           # Uygulamayı yeniden başlat"
echo -e "  docker compose down && docker compose up -d --build  # Tam rebuild"
echo ""
