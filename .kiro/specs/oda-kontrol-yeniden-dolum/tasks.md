# Implementation Plan

- [x] 1. Backend API endpoint'lerini oluştur



  - Yeni route dosyası oluştur veya mevcut route dosyasına ekle
  - `/kat-sorumlusu/oda-kontrol` GET endpoint'i - Oda kontrol sayfasını render et, kat listesini gönder
  - `/api/kat-sorumlusu/minibar-urunler` POST endpoint'i - Seçilen odanın minibar ürünlerini getir
  - `/api/kat-sorumlusu/yeniden-dolum` POST endpoint'i - Yeniden dolum işlemini gerçekleştir
  - Tüm endpoint'lerde `@login_required` ve `@role_required('kat_sorumlusu')` decorator'larını kullan
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3_

- [x] 1.1 Minibar ürünleri API endpoint'ini implement et


  - POST request'ten `oda_id` parametresini al ve validate et
  - Odanın son minibar işlemini sorgula (en son islem_id)
  - İşlem detaylarından ürün listesini, mevcut miktarları ve zimmet_detay_id'leri getir
  - Ürün bilgilerini (ad, birim) join ile al
  - Boş minibar durumunu handle et
  - JSON response döndür (success, data, message)
  - Hata durumlarını handle et ve loglama yap
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 1.2 Yeniden dolum API endpoint'ini implement et

  - POST request'ten parametreleri al: `oda_id`, `urun_id`, `eklenecek_miktar`, `zimmet_detay_id`
  - Input validasyonu yap (miktar > 0, geçerli ID'ler)
  - Zimmet stoğunu kontrol et (yeterli miktar var mı)
  - Transaction başlat
  - PersonelZimmetDetay'ı güncelle (kalan_miktar düş, kullanilan_miktar artır)
  - MinibarIslem kaydı oluştur (islem_tipi='doldurma')
  - MinibarIslemDetay kaydı oluştur (baslangic_stok, bitis_stok, eklenen_miktar, zimmet_detay_id)
  - Transaction commit et
  - Başarı mesajı ve güncel bilgileri döndür
  - Hata durumunda rollback yap ve hata mesajı döndür
  - Tüm işlemleri logla
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 6.4_

- [x] 2. Oda kontrol template'ini oluştur


  - `templates/kat_sorumlusu/oda_kontrol.html` dosyasını oluştur
  - Base template'i extend et
  - Oda seçim bölümünü ekle (QR kod butonu, kat/oda dropdown'ları)
  - Ürün listesi tablosunu ekle (ürün adı, miktar, birim kolonları)
  - Tıklanabilir satır stilleri ekle
  - Boş durum mesajı bölümü ekle
  - Yeniden dolum modalını ekle (ürün bilgileri, miktar input, butonlar)
  - Onay modalını ekle (işlem özeti, bilgilendirme, butonlar)
  - Loading state'leri ekle
  - Mevcut tema stillerine uygun tasarım yap
  - _Requirements: 1.1, 1.4, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 4.3, 4.4, 4.5, 4.6_


- [x] 3. JavaScript modülünü implement et

  - `static/js/oda_kontrol.js` dosyasını oluştur
  - QR kod okutma fonksiyonunu implement et (mevcut QR sistemi ile entegre)
  - Kat seçildiğinde oda dropdown'unu doldur
  - Oda seçildiğinde API'den ürünleri getir ve listele
  - Ürün listesini render et (tablo satırları)
  - Boş durum mesajını göster (ürün yoksa)
  - Ürün satırına tıklama event handler'ı ekle
  - Yeniden dolum modalını aç/kapat fonksiyonları
  - Miktar input validasyonu (sayısal, pozitif)
  - Dolum yap butonuna tıklama handler'ı
  - Onay modalını aç/kapat fonksiyonları
  - İşlemi onayla fonksiyonu (API çağrısı)
  - Toast notification fonksiyonları (başarı, hata)
  - Loading state yönetimi
  - CSRF token'ı tüm POST request'lere ekle
  - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 5.6, 5.7_

- [x] 4. Menü yapısını güncelle


  - Dashboard template'inde menü bölümünü bul
  - "Minibar Kontrol" menü öğesini "İlk Dolum" olarak güncelle
  - "Oda Kontrol" yeni menü öğesini ekle
  - Her iki menü öğesine uygun icon'lar ekle
  - Link URL'lerini güncelle (`/kat-sorumlusu/ilk-dolum`, `/kat-sorumlusu/oda-kontrol`)
  - Menü sıralamasını düzenle (İlk Dolum, Oda Kontrol)
  - Aktif sayfa vurgulama stillerini kontrol et
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 5. Mevcut minibar_kontrol.html'i ilk_dolum.html olarak ayır


  - `templates/kat_sorumlusu/minibar_kontrol.html` dosyasını kopyala
  - Yeni dosyayı `ilk_dolum.html` olarak kaydet
  - İlk dolum dışındaki işlem tiplerini (kontrol, doldurma) kaldır
  - İşlem tipi dropdown'ını kaldır (sadece ilk dolum olacak)
  - Sayfa başlığını "İlk Dolum" olarak güncelle
  - İlgili JavaScript kodunu temizle
  - Route'u `/kat-sorumlusu/ilk-dolum` olarak güncelle
  - _Requirements: 1.1, 1.2_

- [x] 6. Route registration'ı güncelle


  - `app.py` veya ilgili route dosyasında yeni route'ları kaydet
  - İlk dolum route'unu güncelle (`/kat-sorumlusu/ilk-dolum`)
  - Oda kontrol route'larını ekle
  - Route'ların doğru sırada yüklendiğini kontrol et
  - Blueprint kullanımı varsa blueprint'e ekle
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 7. Unit testleri yaz


  - `tests/test_oda_kontrol.py` dosyasını oluştur
  - Minibar ürünleri API testi (başarılı durum)
  - Minibar ürünleri API testi (boş minibar)
  - Minibar ürünleri API testi (geçersiz oda_id)
  - Yeniden dolum API testi (başarılı durum)
  - Yeniden dolum API testi (yetersiz stok)
  - Yeniden dolum API testi (geçersiz miktar)
  - Yeniden dolum API testi (negatif miktar)
  - Zimmet düşüş hesaplama testi
  - Transaction rollback testi
  - _Requirements: 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3_

- [x] 8. Integration testleri yaz


  - End-to-end flow testi (oda seçimi → ürün listesi → dolum)
  - QR kod ile oda seçimi testi
  - Çoklu dolum işlemi testi
  - Stok tükenmesi senaryosu testi
  - _Requirements: 2.1, 2.2, 3.1, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [x] 9. Hata yönetimi ve loglama ekle

  - Backend'de tüm hata durumlarını handle et
  - Hata mesajlarını kullanıcı dostu yap
  - `log_hata()` fonksiyonunu tüm catch bloklarında kullan
  - `log_islem()` fonksiyonunu başarılı işlemlerde kullan
  - Frontend'de API hata yanıtlarını handle et
  - Toast notification ile kullanıcıya bildir
  - Console'a detaylı hata logları yaz (development)
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 10. UI/UX iyileştirmeleri ve responsive tasarım


  - Mobil cihazlarda tablo responsive yap
  - Modal'ların mobilde düzgün görünmesini sağla
  - Loading spinner'ları ekle (API çağrıları sırasında)
  - Buton disabled state'leri ekle (işlem sırasında)
  - Hover efektleri ekle (ürün satırları)
  - Focus state'leri ekle (accessibility)
  - Keyboard navigation desteği (modal'larda ESC tuşu)
  - Animasyonlar ekle (modal açılma/kapanma)
  - _Requirements: 1.4, 2.3, 2.4, 3.3, 3.4, 3.5, 4.3, 4.4, 4.5, 4.6_

- [x] 11. Manuel test ve doğrulama


  - Tüm fonksiyonel gereksinimleri test et
  - Farklı tarayıcılarda test et (Chrome, Firefox, Safari)
  - Farklı cihazlarda test et (mobil, tablet, desktop)
  - QR kod okutma işlemini test et
  - Manuel oda seçimi işlemini test et
  - Boş minibar durumunu test et
  - Yetersiz stok durumunu test et
  - Hata mesajlarını test et
  - Toast notification'ları test et
  - Performance test (ürün listesi yükleme hızı)
  - _Requirements: Tüm requirements_
