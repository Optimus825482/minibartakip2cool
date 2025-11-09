# Minibar Takip Sistemi - Docker Makefile
# Windows için: make yerine "make.bat" kullanabilirsiniz

.PHONY: help setup start stop restart logs clean build init-db backup restore health

# Varsayılan hedef
.DEFAULT_GOAL := help

help: ## Bu yardım mesajını göster
	@echo "Minibar Takip Sistemi - Docker Komutları"
	@echo ""
	@echo "Kullanım: make [hedef]"
	@echo ""
	@echo "Hedefler:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup: ## İlk kurulum (env + build + start + init-db)
	@echo "🚀 İlk kurulum başlıyor..."
	@if [ ! -f .env ]; then cp .env.docker .env; echo "✅ .env dosyası oluşturuldu"; fi
	@echo "⚠️  .env dosyasını düzenlemeyi unutma! (SECRET_KEY ve DB_PASSWORD)"
	@docker-compose build
	@docker-compose up -d
	@echo "⏳ MySQL'in hazır olması bekleniyor (30 saniye)..."
	@sleep 30
	@docker-compose exec web python init_db.py
	@docker-compose exec web python add_local_superadmin.py
	@echo "✅ Kurulum tamamlandı!"
	@echo "🌐 Uygulama: http://localhost:5000"
	@echo "🔧 phpMyAdmin: http://localhost:8080"

start: ## Container'ları başlat
	@echo "🚀 Container'lar başlatılıyor..."
	@docker-compose up -d
	@echo "✅ Container'lar başlatıldı"

stop: ## Container'ları durdur
	@echo "⏸️  Container'lar durduruluyor..."
	@docker-compose stop
	@echo "✅ Container'lar durduruldu"

restart: ## Container'ları yeniden başlat
	@echo "🔄 Container'lar yeniden başlatılıyor..."
	@docker-compose restart
	@echo "✅ Container'lar yeniden başlatıldı"

logs: ## Logları göster (Ctrl+C ile çık)
	@docker-compose logs -f

logs-web: ## Web loglarını göster
	@docker-compose logs -f web

logs-db: ## Database loglarını göster
	@docker-compose logs -f db

clean: ## Container'ları ve volume'ları sil (DİKKAT: Tüm data silinir!)
	@echo "⚠️  DİKKAT: Tüm container'lar ve data silinecek!"
	@read -p "Devam etmek istiyor musun? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker-compose down -v
	@echo "✅ Temizlik tamamlandı"

build: ## Image'ları yeniden build et
	@echo "🔨 Image'lar build ediliyor..."
	@docker-compose build
	@echo "✅ Build tamamlandı"

rebuild: ## Cache kullanmadan yeniden build et
	@echo "🔨 Temiz build yapılıyor..."
	@docker-compose build --no-cache
	@echo "✅ Build tamamlandı"

init-db: ## Database'i başlat (tablolar + superadmin)
	@echo "🗄️  Database başlatılıyor..."
	@docker-compose exec web python init_db.py
	@docker-compose exec web python add_local_superadmin.py
	@echo "✅ Database hazır"

backup: ## Database backup al
	@echo "💾 Backup alınıyor..."
	@mkdir -p backups
	@docker-compose exec -T db mysqldump -u root -p$${DB_PASSWORD} minibar_takip > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup alındı: backups/"

restore: ## Database restore et (backup.sql dosyasından)
	@echo "⚠️  DİKKAT: Mevcut database silinecek!"
	@read -p "Devam etmek istiyor musun? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@if [ ! -f backup.sql ]; then echo "❌ backup.sql dosyası bulunamadı!"; exit 1; fi
	@docker-compose exec -T db mysql -u root -p$${DB_PASSWORD} minibar_takip < backup.sql
	@echo "✅ Restore tamamlandı"

health: ## Health check yap
	@echo "🏥 Health check yapılıyor..."
	@curl -s http://localhost:5000/health | python -m json.tool || echo "❌ Uygulama çalışmıyor!"

status: ## Container durumlarını göster
	@docker-compose ps

shell: ## Web container'a bash ile bağlan
	@docker-compose exec web bash

db-shell: ## MySQL shell'e bağlan
	@docker-compose exec db mysql -u root -p

phpmyadmin: ## phpMyAdmin'i başlat
	@docker-compose --profile tools up -d phpmyadmin
	@echo "✅ phpMyAdmin başlatıldı: http://localhost:8080"

pgadmin: ## pgAdmin'i başlat (PostgreSQL yönetimi)
	@docker-compose --profile tools up -d pgadmin
	@echo "✅ pgAdmin başlatıldı: http://localhost:8080"
	@echo "📧 Email: admin@minibar.com"
	@echo "🔑 Şifre: admin123"
	@echo ""
	@echo "PostgreSQL Bağlantı Bilgileri (pgAdmin içinde ekle):"
	@echo "  Host: postgres"
	@echo "  Port: 5432"
	@echo "  Database: minibar_takip"
	@echo "  Username: minibar_user"
	@echo "  Password: minibar123"

pgadmin-stop: ## pgAdmin'i durdur
	@docker-compose stop pgadmin
	@echo "✅ pgAdmin durduruldu"

update: ## Kodu güncelle ve yeniden başlat
	@echo "🔄 Güncelleme yapılıyor..."
	@git pull
	@docker-compose build web
	@docker-compose up -d web
	@echo "✅ Güncelleme tamamlandı"

stats: ## Container kaynak kullanımını göster
	@docker stats

prune: ## Kullanılmayan Docker kaynaklarını temizle
	@echo "🧹 Temizlik yapılıyor..."
	@docker system prune -f
	@echo "✅ Temizlik tamamlandı"
