"""
app.py'den çakışan API endpoint'lerini kaldıran script
"""

# app.py'yi oku
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Çakışan endpoint'leri bul ve kaldır
endpoints_to_remove = [
    '/api/odalar',
    '/api/odalar-by-kat',
    '/api/urun-gruplari',
    '/api/urunler',
    '/api/urunler-by-grup',
    '/api/stok-giris',
    '/api/minibar-islem-kaydet',
    '/api/minibar-ilk-dolum',
    '/api/minibar-ilk-dolum-kontrol',
    '/api/urun-stok',
    '/api/zimmetim',
    '/api/minibar-icerigi',
    '/api/minibar-doldur',
    '/api/toplu-oda-mevcut-durum',
    '/api/toplu-oda-doldur',
    '/api/kat-rapor-veri',
]

# Yeni satırlar
new_lines = []
skip_until_next_route = False
skip_count = 0

i = 0
while i < len(lines):
    line = lines[i]
    
    # API endpoint başlangıcını kontrol et
    if "@app.route('/api/" in line:
        # Bu endpoint kaldırılacak mı?
        should_remove = any(endpoint in line for endpoint in endpoints_to_remove)
        
        if should_remove:
            # Bu endpoint'i ve sonraki satırları atla
            skip_until_next_route = True
            skip_count += 1
            i += 1
            continue
    
    # Yeni bir route başladı mı?
    if skip_until_next_route and ("@app.route(" in line or "# ============" in line or "if __name__" in line):
        skip_until_next_route = False
    
    # Satırı ekle veya atla
    if not skip_until_next_route:
        new_lines.append(line)
    
    i += 1

# Yeni içeriği yaz
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ {skip_count} adet çakışan API endpoint kaldırıldı")
print("✅ app.py temizlendi")
