# Implementation Plan - Minibar QR Kod Sistemi

- [x] 1. Database schema güncellemeleri ve migration


  - Oda modeline qr_kod_token, qr_kod_gorsel, qr_kod_olusturma_tarihi, misafir_mesaji alanlarını ekle
  - MinibarDolumTalebi modelini oluştur (id, oda_id, talep_tarihi, durum, tamamlanma_tarihi, notlar)
  - QRKodOkutmaLog modelini oluştur (id, oda_id, kullanici_id, okutma_tarihi, okutma_tipi, ip_adresi, user_agent, basarili, hata_mesaji)
  - Index'leri ekle (qr_kod_token unique, oda_tarih, kullanici_tarih)
  - Migration scriptini oluştur ve test et
  - _Requirements: 1.1, 1.3, 5.5, 6.4, 8.5_

- [x] 2. QR Kod Service implementasyonu


  - utils/qr_service.py dosyasını oluştur
  - QRKodService sınıfını implement et (generate_token, generate_qr_url, generate_qr_image, create_qr_for_oda, validate_token, log_qr_scan)
  - qrcode ve Pillow kütüphanelerini kullanarak QR görsel oluşturma
  - Base64 encoding implementasyonu
  - Token güvenlik kontrollerini ekle
  - _Requirements: 1.1, 1.2, 1.3, 8.1, 8.2_

- [x] 3. Rate Limiting servisi


  - utils/rate_limiter.py dosyasını oluştur
  - RateLimiter sınıfını implement et (check_rate_limit metodu)
  - IP bazlı rate limiting (dakikada max 10 deneme)
  - Cache mekanizması (production'da Redis önerilir)
  - _Requirements: 8.6_

- [x] 4. Admin panel - QR kod oluşturma route'ları


  - /admin/oda-qr-olustur/<oda_id> POST endpoint'i (tek oda için QR oluştur)
  - /admin/toplu-qr-olustur POST endpoint'i (tüm odalar veya QR'sız odalar için)
  - /admin/oda-qr-goruntule/<oda_id> GET endpoint'i (QR modal göster)
  - /admin/oda-qr-indir/<oda_id> GET endpoint'i (PNG download)
  - /admin/toplu-qr-indir GET endpoint'i (ZIP download)
  - /admin/oda-misafir-mesaji/<oda_id> GET/POST endpoint'i (mesaj düzenleme)
  - Audit log entegrasyonu
  - Hata yönetimi ve validation
  - _Requirements: 1.1, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 5. Admin panel - Frontend güncellemeleri



  - templates/sistem_yoneticisi/odalar.html'e QR butonları ekle
  - QR görüntüleme modal'ı oluştur
  - Misafir mesajı düzenleme modal'ı oluştur
  - Toplu işlem butonları ekle
  - static/js/admin_qr.js dosyasını oluştur (AJAX işlemleri)
  - Toastr bildirimleri ekle
  - _Requirements: 2.5, 3.4, 7.1, 7.2, 7.3_

- [x] 6. Kat sorumlusu panel - QR okuyucu route'ları


  - /kat-sorumlusu/qr-okut GET endpoint'i (QR okuyucu sayfası)
  - /api/kat-sorumlusu/qr-parse POST endpoint'i (QR parse ve validate)
  - Token doğrulama ve oda bilgisi döndürme
  - QR okutma log kaydı
  - Hata yönetimi (geçersiz token, rate limit)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2_

- [x] 7. Kat sorumlusu panel - QR okuyucu frontend


  - templates/kat_sorumlusu/minibar_islemleri.html'e "QR Kod ile Başla" butonu ekle
  - QR scanner modal'ı oluştur
  - static/js/qr_scanner.js dosyasını oluştur
  - html5-qrcode kütüphanesini entegre et
  - Kamera erişimi ve QR okuma implementasyonu
  - Parse edilen bilgilerle form otomatik doldurma
  - Hata mesajları ve fallback (manuel seçim)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.7_

- [x] 8. Misafir arayüzü - QR yönlendirme ve dolum talebi


  - /qr/<token> GET endpoint'i (akıllı yönlendirme)
  - Kat sorumlusu panelinden mi yoksa dış kaynaktan mı kontrolü
  - /misafir/dolum-talebi/<token> GET/POST endpoint'i
  - templates/misafir_dolum_talebi.html oluştur (responsive, standalone)
  - Dolum talebi form işleme
  - MinibarDolumTalebi kaydı oluşturma
  - Başarı mesajı gösterme
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.7_

- [x] 9. Dolum talebi bildirim sistemi


  - /api/dolum-talepleri GET endpoint'i (kat sorumlusu için bekleyen talepler)
  - /api/dolum-talebi-tamamla/<talep_id> POST endpoint'i
  - Kat sorumlusu dashboard'a bildirim badge'i ekle
  - Real-time bildirim (opsiyonel - polling veya WebSocket)
  - Talep tamamlama işlemi
  - _Requirements: 6.5, 6.6_

- [x] 10. Güvenlik ve validation implementasyonu

  - Input sanitization (misafir mesajı için bleach)
  - CSRF token kontrolü tüm POST endpoint'lerinde
  - Rate limiting middleware ekle
  - Token validation güvenlik kontrolleri
  - Audit trail tüm QR işlemleri için
  - Güvenlik log kayıtları
  - _Requirements: 3.5, 8.1, 8.2, 8.3, 8.4, 8.6_

- [x] 11. Raporlama ve analitik

  - /admin/qr-okutma-raporlari GET endpoint'i
  - QR okutma geçmişi listesi (filtreleme: oda, tarih, tip)
  - En çok okutulan odalar raporu
  - Kat sorumlusu bazında QR kullanım istatistikleri
  - Misafir dolum talepleri raporu
  - Excel export özelliği
  - _Requirements: 5.3, 5.4_

- [x] 12. Mevcut odalar için QR oluşturma scripti


  - scripts/generate_qr_for_existing_odalar.py oluştur
  - Tüm aktif odalar için QR kod oluştur
  - Progress bar göster
  - Hata yönetimi ve log
  - Dry-run modu ekle
  - _Requirements: 2.1, 2.2_

- [x] 13. Test implementasyonu

- [x] 13.1 Unit testler

  - QRKodService testleri (token generation, QR image, validation)
  - RateLimiter testleri
  - Input sanitization testleri
  - _Requirements: Tüm requirements_

- [x] 13.2 Integration testler

  - Admin QR oluşturma akışı testi
  - Kat sorumlusu QR okutma akışı testi
  - Misafir dolum talebi akışı testi
  - Rate limiting testi
  - _Requirements: Tüm requirements_

- [x] 14. Deployment hazırlıkları


  - requirements.txt güncelle (qrcode, Pillow, bleach)
  - .env.example'a QR ayarları ekle
  - Migration scriptini production'a hazırla
  - Dokümantasyon güncelle (README, kullanım kılavuzu)
  - Rollback planı hazırla
  - _Requirements: Tüm requirements_

