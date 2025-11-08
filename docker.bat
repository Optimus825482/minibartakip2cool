@echo off
REM Minibar Takip Sistemi - Docker Yönetim Script (Windows)

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
if "%1"=="build" goto build
if "%1"=="init-db" goto init-db
if "%1"=="backup" goto backup
if "%1"=="health" goto health
if "%1"=="status" goto status
if "%1"=="shell" goto shell
if "%1"=="phpmyadmin" goto phpmyadmin
goto help

:help
echo.
echo Minibar Takip Sistemi - Docker Komutlari
echo.
echo Kullanim: docker.bat [komut]
echo.
echo Komutlar:
echo   setup        - Ilk kurulum (env + build + start + init-db)
echo   start        - Container'lari baslat
echo   stop         - Container'lari durdur
echo   restart      - Container'lari yeniden baslat
echo   logs         - Loglari goster
echo   clean        - Container'lari ve volume'lari sil (DIKKAT!)
echo   build        - Image'lari yeniden build et
echo   init-db      - Database'i baslat
echo   backup       - Database backup al
echo   health       - Health check yap
echo   status       - Container durumlarini goster
echo   shell        - Web container'a baglan
echo   phpmyadmin   - phpMyAdmin'i baslat
echo.
goto end

:setup
echo.
echo [92m🚀 Ilk kurulum basliyor...[0m
if not exist .env (
    copy .env.docker .env
    echo [92m✅ .env dosyasi olusturuldu[0m
    echo [93m⚠️  .env dosyasini duzenlemeyi unutma! (SECRET_KEY ve DB_PASSWORD)[0m
)
docker-compose build
docker-compose up -d
echo [93m⏳ MySQL'in hazir olmasi bekleniyor (30 saniye)...[0m
timeout /t 30 /nobreak >nul
docker-compose exec web python init_db.py
docker-compose exec web python add_local_superadmin.py
echo [92m✅ Kurulum tamamlandi![0m
echo [96m🌐 Uygulama: http://localhost:5000[0m
echo [96m🔧 phpMyAdmin: http://localhost:8080[0m
goto end

:start
echo [92m🚀 Container'lar baslatiliyor...[0m
docker-compose up -d
echo [92m✅ Container'lar baslatildi[0m
goto end

:stop
echo [93m⏸️  Container'lar durduruluyor...[0m
docker-compose stop
echo [92m✅ Container'lar durduruldu[0m
goto end

:restart
echo [93m🔄 Container'lar yeniden baslatiliyor...[0m
docker-compose restart
echo [92m✅ Container'lar yeniden baslatildi[0m
goto end

:logs
echo [96mLoglari gosteriliyor (Ctrl+C ile cik)...[0m
docker-compose logs -f
goto end

:clean
echo [91m⚠️  DIKKAT: Tum container'lar ve data silinecek![0m
set /p confirm="Devam etmek istiyor musun? (y/N): "
if /i not "%confirm%"=="y" goto end
docker-compose down -v
echo [92m✅ Temizlik tamamlandi[0m
goto end

:build
echo [93m🔨 Image'lar build ediliyor...[0m
docker-compose build
echo [92m✅ Build tamamlandi[0m
goto end

:init-db
echo [93m🗄️  Database baslatiliyor...[0m
docker-compose exec web python init_db.py
docker-compose exec web python add_local_superadmin.py
echo [92m✅ Database hazir[0m
goto end

:backup
echo [93m💾 Backup aliniyor...[0m
if not exist backups mkdir backups
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
docker-compose exec -T db mysqldump -u root -p%DB_PASSWORD% minibar_takip > backups\backup_%mydate%_%mytime%.sql
echo [92m✅ Backup alindi: backups\[0m
goto end

:health
echo [93m🏥 Health check yapiliyor...[0m
curl -s http://localhost:5000/health
goto end

:status
docker-compose ps
goto end

:shell
docker-compose exec web bash
goto end

:phpmyadmin
docker-compose --profile tools up -d phpmyadmin
echo [92m✅ phpMyAdmin baslatildi: http://localhost:8080[0m
goto end

:end
