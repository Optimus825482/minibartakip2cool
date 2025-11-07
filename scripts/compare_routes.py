"""
Yedek ve şimdiki app.py'deki route'ları karşılaştır
"""

# Yedek dosyadan route'ları çıkar
with open('app_backup_20251107_211724.py', 'r', encoding='utf-8') as f:
    backup_lines = f.readlines()

backup_routes = []
for i, line in enumerate(backup_lines):
    if '@app.route(' in line:
        # Route path'ini çıkar
        route_line = line.strip()
        # Bir sonraki satırlarda fonksiyon adını bul
        for j in range(i+1, min(i+10, len(backup_lines))):
            if 'def ' in backup_lines[j]:
                func_name = backup_lines[j].strip().split('def ')[1].split('(')[0]
                backup_routes.append((route_line, func_name))
                break

# Şimdiki dosyadan route'ları çıkar
with open('app.py', 'r', encoding='utf-8') as f:
    current_lines = f.readlines()

current_routes = []
for i, line in enumerate(current_lines):
    if '@app.route(' in line:
        route_line = line.strip()
        for j in range(i+1, min(i+10, len(current_lines))):
            if 'def ' in current_lines[j]:
                func_name = current_lines[j].strip().split('def ')[1].split('(')[0]
                current_routes.append((route_line, func_name))
                break

print("="*60)
print("YEDEK DOSYA ROUTE'LARI")
print("="*60)
print(f"Toplam: {len(backup_routes)}\n")

print("="*60)
print("ŞİMDİKİ APP.PY ROUTE'LARI")
print("="*60)
print(f"Toplam: {len(current_routes)}\n")

# Yedekte olup şimdi olmayan route'lar
backup_funcs = {func for _, func in backup_routes}
current_funcs = {func for _, func in current_routes}

missing_funcs = backup_funcs - current_funcs
print("="*60)
print("APP.PY'DEN KALDIRILAN ROUTE'LAR (Modüllere taşındı)")
print("="*60)
print(f"Toplam: {len(missing_funcs)}\n")
for func in sorted(missing_funcs)[:20]:  # İlk 20'yi göster
    print(f"  - {func}")

if len(missing_funcs) > 20:
    print(f"  ... ve {len(missing_funcs) - 20} tane daha")

print("\n" + "="*60)
print("ÖZET")
print("="*60)
print(f"Yedek: {len(backup_routes)} route")
print(f"Şimdi: {len(current_routes)} route")
print(f"Taşınan: {len(missing_funcs)} route")
print(f"Kalan: {len(current_funcs)} route")
