"""SQLAlchemy 2.0 uyumluluğu için query.get() metodlarını güncelle"""
import re

def update_query_get():
    filepath = 'app.py'

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Orijinal içeriği sakla
    original_content = content

    # Pattern: Model.query.get(id_variable)
    # Replace: db.session.get(Model, id_variable)

    patterns = [
        # Model.query.get(variable)
        (r'(\w+)\.query\.get\(([^)]+)\)', r'db.session.get(\1, \2)'),
    ]

    replacements = 0
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        replacements += len(re.findall(pattern, content))
        content = new_content

    if content != original_content:
        # Backup oluştur
        with open('app.py.backup', 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Yeni içeriği yaz
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'✓ {replacements} adet query.get() kullanımı güncellendi!')
        print(f'✓ Backup: app.py.backup')

        # Güncellenenleri göster
        print('\nGüncellenen satırlar:')
        for line_num, line in enumerate(content.split('\n'), 1):
            if 'db.session.get(' in line and line_num in [167, 994, 1370, 1562, 1806, 1814, 1998, 2051, 2205, 2267, 2298, 2420, 2710, 2978]:
                print(f'  {line_num}: {line.strip()}')
    else:
        print('Güncellenecek bir şey bulunamadı.')

if __name__ == '__main__':
    print('SQLAlchemy 2.0 uyumluluk güncellemesi başlatılıyor...\n')
    update_query_get()
