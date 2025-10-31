"""Tüm template dosyalarında overflow-x-auto'yu table-wrapper ile değiştir"""
import os
import re

def update_templates():
    templates_dir = 'templates'
    updated_files = []

    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # overflow-x-auto'yu table-wrapper ile değiştir
                    new_content = content.replace('class="overflow-x-auto"', 'class="table-wrapper"')

                    # Bazı durumlarda border ve rounded-lg de olabilir
                    new_content = new_content.replace('class="overflow-x-auto border', 'class="table-wrapper border')
                    new_content = new_content.replace('class="overflow-x-auto -mx-4', 'class="table-wrapper -mx-4')

                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        updated_files.append(filepath)
                        print(f'✓ Güncellendi: {filepath}')

                except Exception as e:
                    print(f'✗ Hata ({filepath}): {e}')

    print(f'\n✓ {len(updated_files)} dosya güncellendi!')
    return updated_files

if __name__ == '__main__':
    print('Template dosyaları güncelleniyor...\n')
    update_templates()
