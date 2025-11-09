@echo off
echo ========================================
echo Docker'dan Railway'e Direkt Transfer
echo ========================================
echo.

echo [1/3] Schema dump aliniyor...
docker exec minibar_postgres pg_dump -U minibar_user -d minibar_takip --schema-only --no-owner --no-acl > railway_schema_clean.sql
if %errorlevel% neq 0 (
    echo HATA: Schema dump alinamadi!
    pause
    exit /b 1
)
echo OK - Schema dump alindi

echo.
echo [2/3] Data dump aliniyor...
docker exec minibar_postgres pg_dump -U minibar_user -d minibar_takip --data-only --no-owner --no-acl --column-inserts > railway_data_clean.sql
if %errorlevel% neq 0 (
    echo HATA: Data dump alinamadi!
    pause
    exit /b 1
)
echo OK - Data dump alindi

echo.
echo [3/3] Railway'e yukleme icin hazir!
echo.
echo SIMDI RAILWAY TERMINALINDE SU KOMUTLARI CALISTIR:
echo.
echo \i D:/Claude/prof/railway_schema_clean.sql
echo \i D:/Claude/prof/railway_data_clean.sql
echo.
echo Ya da bu komutu calistir:
echo railway run psql $DATABASE_PUBLIC_URL -f railway_schema_clean.sql
echo railway run psql $DATABASE_PUBLIC_URL -f railway_data_clean.sql
echo.
pause
