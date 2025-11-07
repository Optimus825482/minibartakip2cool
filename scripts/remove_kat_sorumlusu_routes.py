"""
app.py'den kat sorumlusu route'larını kaldıran script
"""

# app.py'yi oku
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Kaldırılacak route'lar
routes_to_remove = [
    '/dolum-talepleri',
    '/minibar-kontrol',
    '/kat-odalari',
    '/minibar-urunler',
    '/toplu-oda-doldurma',
    '/kat-bazli-rapor',
    '/zimmetim',
    '/kat-raporlar',
]

# Yeni satırlar
new_lines = []
skip_until_next_route = False
removed_count = 0

i = 0
while i < len(lines):
    line = lines[i]
    
    # Route başlangıcını kontrol et
    if "@app.route(" in line:
        # Bu route kaldırılacak mı?
        should_remove = any(route in line for route in routes_to_remove)
        
        if should_remove:
            skip_until_next_route = True
            removed_count += 1
            i += 1
            continue
    
    # Yeni bir route veya önemli bölüm başladı mı?
    if skip_until_next_route and ("@app.route(" in line or "# ============" in line or "# Excel Export" in line or "if __name__" in line):
        skip_until_next_route = False
    
    # Satırı ekle veya atla
    if not skip_until_next_route:
        new_lines.append(line)
    
    i += 1

# Yeni içeriği yaz
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ {removed_count} adet kat sorumlusu route kaldırıldı")
print("✅ app.py temizlendi")
