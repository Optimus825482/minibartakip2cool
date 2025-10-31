# PWA İkonları

Bu klasöre PWA ikonlarını ekleyin. Aşağıdaki boyutlarda PNG ikonlar gereklidir:

## Gerekli İkon Boyutları

- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-192x192.png
- icon-384x384.png
- icon-512x512.png

## Hızlı Çözüm



ŞİMDİ UI/UX İYİLEŞTİRMELERİ YAPALIM **Tema Seçeneği**  DARK MODE LIGHT MODE ZATEN VAR Renk şemaları EKLEYELIM **Loading Göstergeleri**  **Toast
  Bildirimleri**

### Yöntem 1: Online Araç Kullan
1. https://www.pwabuilder.com/imageGenerator adresine gidin
2. Bir logo/görsel yükleyin
3. Tüm boyutları otomatik oluşturun
4. İndirip bu klasöre kopyalayın

### Yöntem 2: Placeholder İkon (Geçici)
Geliştirme aşamasında placeholder olarak aşağıdaki komutu kullanabilirsiniz:

**Windows (PowerShell):**
```powershell
$sizes = @(72, 96, 128, 144, 152, 192, 384, 512)
foreach ($size in $sizes) {
    $null | Out-File -FilePath "icon-$size`x$size.png" -Encoding ascii
}
```

**Linux/Mac:**
```bash
for size in 72 96 128 144 152 192 384 512; do
    touch icon-${size}x${size}.png
done
```

### Yöntem 3: Pillow ile Python Script
```python
from PIL import Image, ImageDraw

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    img = Image.new('RGB', (size, size), color='#475569')
    draw = ImageDraw.Draw(img)
    draw.rectangle([5, 5, size-5, size-5], outline='white', width=3)
    img.save(f'icon-{size}x{size}.png')
```

## Önemli Notlar

- İkonlar PNG formatında olmalıdır
- Şeffaf arka plan (alpha channel) kullanılabilir
- Maskable icon'lar için güvenli alan (safe zone) bırakın
- Minimum 512x512 boyutunda bir master ikon hazırlayın

## Tasarım İpuçları

- Basit ve net tasarım kullanın
- Küçük boyutlarda da okunabilir olmasına dikkat edin
- Marka renklerinizi kullanın
- Çok fazla detay eklemeyin (küçük ekranlarda kaybolur)
