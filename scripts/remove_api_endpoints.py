"""
app.py'den API endpoint'lerini kaldıran script
"""

import re

# app.py'yi oku
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# API endpoint'lerini bul ve kaldır
# Pattern: @app.route('/api/...) ile başlayan ve sonraki endpoint'e kadar olan kısım
api_patterns = [
    r"# AJAX endpoint.*?\n@app\.route\('/api/odalar'\).*?(?=\n@app\.route|# AJAX endpoint|@app\.route\('/minibar-durumlari'\))",
    r"# AJAX endpoint.*?\n@app\.route\('/api/odalar-by-kat.*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/urun-gruplari'\).*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/urunler'\).*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/urunler-by-grup.*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/stok-giris'.*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/minibar-islem-kaydet'.*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/minibar-ilk-dolum'.*?(?=\n@app\.route|# AJAX endpoint)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/minibar-ilk-dolum-kontrol.*?(?=\n@app\.route|# AJAX endpoint|@app\.route\('/api/urun-stok)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/urun-stok.*?(?=\n@app\.route|# AJAX endpoint|@app\.route\('/api/zimmetim)",
    r"# AJAX endpoint.*?\n@app\.route\('/api/zimmetim'\).*?(?=\n@app\.route\('/zimmet-detay)",
    r"@app\.route\('/api/minibar-icerigi.*?(?=\n@app\.route\('/api/minibar-doldur)",
    r"@app\.route\('/api/minibar-doldur'.*?(?=\n@app\.route\('/toplu-oda-doldurma)",
    r"@app\.route\('/api/toplu-oda-mevcut-durum'.*?(?=\n@app\.route\('/api/toplu-oda-doldur)",
    r"@app\.route\('/api/toplu-oda-doldur'.*?(?=\n@app\.route\('/kat-bazli-rapor)",
    r"@app\.route\('/api/kat-rapor-veri'.*?(?=\n@app\.route\('/zimmetim'\)|# ============================================================================)",
]

# Her pattern'i kaldır
for pattern in api_patterns:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Yedek al
with open('app_backup_before_api_removal.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ API endpoint'leri kaldırıldı")
print("✅ Yedek: app_backup_before_api_removal.py")
print("\nLütfen app_backup_before_api_removal.py dosyasını app.py olarak kaydedin")
