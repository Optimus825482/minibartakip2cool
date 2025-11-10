#!/bin/bash
# Coolify Hızlı Kurulum Script'i
# Sunucuda çalıştırılacak

set -e

echo "=========================================="
echo "🚀 Coolify Kurulum Başlatılıyor..."
echo "=========================================="

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Bu script root olarak çalıştırılmalı!"
    echo "Kullanım: sudo bash coolify_setup.sh"
    exit 1
fi

# Sistem güncellemesi
echo ""
echo "📦 Sistem güncelleniyor..."
apt-get update -qq
apt-get upgrade -y -qq

# Gerekli paketler
echo ""
echo "📦 Gerekli paketler kuruluyor..."
apt-get install -y -qq curl wget git ufw

# Firewall ayarları
echo ""
echo "🔒 Firewall ayarlanıyor..."
ufw --force enable
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # Coolify Dashboard
ufw reload

echo "✅ Firewall ayarlandı"

# Coolify kurulumu
echo ""
echo "🚀 Coolify kuruluyor..."
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Kurulum kontrolü
echo ""
echo "🔍 Kurulum kontrol ediliyor..."
sleep 5

if docker ps | grep -q coolify; then
    echo "✅ Coolify başarıyla kuruldu!"
else
    echo "❌ Coolify kurulumu başarısız!"
    exit 1
fi

# IP adresini al
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "=========================================="
echo "✅ Kurulum Tamamlandı!"
echo "=========================================="
echo ""
echo "📊 Bilgiler:"
echo "   - Coolify Dashboard: http://$SERVER_IP:8000"
echo "   - SSH Port: 22"
echo "   - HTTP Port: 80"
echo "   - HTTPS Port: 443"
echo ""
echo "🔐 Güvenlik Önerileri:"
echo "   1. Coolify dashboard'a giriş yap ve güçlü şifre belirle"
echo "   2. 2FA aktif et"
echo "   3. SSH key-based auth kullan"
echo "   4. Root login'i kapat"
echo ""
echo "📝 Sonraki Adımlar:"
echo "   1. http://$SERVER_IP:8000 adresine git"
echo "   2. İlk kullanıcıyı oluştur"
echo "   3. PostgreSQL database ekle"
echo "   4. Git repository'yi bağla"
echo "   5. Environment variables'ı ayarla"
echo "   6. Deploy et!"
echo ""
echo "=========================================="
