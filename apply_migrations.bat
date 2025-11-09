@echo off
chcp 65001 >nul
echo.
echo ========================================
echo Railway Migration Uygulayıcı
echo ========================================
echo.
echo Bu script şunları ekleyecek:
echo   1. Oteller tablosuna 'logo' kolonu
echo   2. ML tabloları (ml_metrics, ml_models, ml_alerts, ml_training_logs)
echo.

python apply_migrations_railway.py

echo.
pause
