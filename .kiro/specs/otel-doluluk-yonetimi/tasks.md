# Otel Doluluk Yönetimi - Görev Listesi

## Genel Bakış
Bu görev listesi, otel doluluk yönetimi özelliğinin adım adım implementasyonunu içerir. Her görev, önceki görevlerin üzerine inşa edilir ve sonunda tam işlevsel bir sistem oluşturur.

## Görevler

- [x] 1. Veritabanı modellerini oluştur



  - MisafirKayit ve DosyaYukleme modellerini models.py'ye ekle
  - Gerekli enum tiplerini tanımla (misafir_kayit_tipi, dosya_tipi, yukleme_durum)
  - Veritabanı indekslerini ekle (performans için)
  - Migration dosyası oluştur ve uygula
  - _Gereksinimler: 1.1, 1.2, 1.3, 2.1, 2.2_



- [ ] 2. Excel işleme servisini oluştur
  - utils/excel_service.py dosyasını oluştur
  - ExcelProcessingService sınıfını implement et
  - detect_file_type() metodunu yaz (sütun başlıklarından otomatik algılama)
  - process_excel_file() metodunu yaz (Excel okuma ve veritabanına kaydetme)
  - validate_row() metodunu yaz (veri doğrulama)
  - parse_date() ve parse_time() metodlarını yaz
  - get_or_create_oda() metodunu yaz


  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 3. Dosya yönetim servisini oluştur
  - utils/file_management_service.py dosyasını oluştur
  - FileManagementService sınıfını implement et
  - save_uploaded_file() metodunu yaz (dosya kaydetme ve validasyon)
  - generate_islem_kodu() metodunu yaz (benzersiz kod oluşturma)
  - delete_upload_by_islem_kodu() metodunu yaz (toplu silme)
  - cleanup_old_files() metodunu yaz (4 günden eski dosyaları silme)


  - uploads/doluluk/ dizin yapısını oluştur
  - _Gereksinimler: 1.4, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 9.1_


- [ ] 4. Oda doluluk hesaplama servisini oluştur
  - utils/occupancy_service.py dosyasını oluştur
  - OccupancyService sınıfını implement et


  - get_oda_doluluk_durumu() metodunu yaz (belirli tarihteki oda durumu)
  - get_gunluk_doluluk_raporu() metodunu yaz (günlük özet rapor)
  - get_oda_detay_bilgileri() metodunu yaz (oda detay bilgileri)
  - Tarih hesaplama yardımcı fonksiyonlarını ekle
  - _Gereksinimler: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 5. Doluluk yönetimi route'larını oluştur
  - routes/doluluk_routes.py dosyasını oluştur
  - /doluluk-yonetimi endpoint'ini yaz (ana sayfa - GET)
  - /doluluk-yonetimi/yukle endpoint'ini yaz (dosya yükleme - POST)


  - /doluluk-yonetimi/sil/<islem_kodu> endpoint'ini yaz (silme - POST)
  - /doluluk-yonetimi/durum/<islem_kodu> endpoint'ini yaz (durum sorgulama - GET/AJAX)
  - Yetki kontrollerini ekle (@role_required decorator)
  - Hata yönetimini ekle (try-catch blokları)
  - Audit log kayıtlarını ekle
  - app.py'ye route'ları kaydet


  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 6. Oda doluluk route'larını oluştur
  - routes/doluluk_routes.py'ye devam et
  - /oda-doluluk/<int:oda_id> endpoint'ini yaz (oda detay - GET)
  - /gunluk-doluluk endpoint'ini yaz (günlük rapor - GET)
  - Otel bazlı filtreleme ekle
  - Yetki kontrollerini ekle (kat_sorumlusu, depo_sorumlusu, sistem_yoneticisi)
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 6.3, 6.4, 6.5_

- [x] 7. Doluluk yönetimi UI sayfasını oluştur


  - templates/depo_sorumlusu/doluluk_yonetimi.html oluştur
  - Tek dosya yükleme formu ekle (drag & drop desteği)
  - Yükleme geçmişi tablosu ekle
  - İşlem kodu ile silme butonu ekle
  - İlerleme göstergesi ekle (asenkron işleme için)
  - Hata detayları modal ekle
  - Dosya tipi badge'i ekle (IN HOUSE / ARRIVALS)
  - JavaScript kodlarını ekle (AJAX, ilerleme takibi)
  - Responsive tasarım uygula


  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 7.1, 7.2, 7.3, 9.6, 9.7_


- [ ] 8. Oda detay sayfasını oluştur
  - templates/kat_sorumlusu/oda_doluluk_detay.html oluştur
  - Oda bilgileri kartı ekle
  - Mevcut misafir bilgileri bölümü ekle (giriş/çıkış tarihi, kalan gün, misafir sayısı)
  - Gelecek rezervasyonlar listesi ekle (tarih, saat, misafir sayısı)
  - Geçmiş kayıtlar tablosu ekle


  - Tarih hesaplama JavaScript fonksiyonları ekle
  - Renk kodlaması ekle (bugün çıkış, yarın giriş vb.)
  - Responsive tasarım uygula
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4_


- [ ] 9. Günlük doluluk raporu sayfasını oluştur
  - templates/kat_sorumlusu/gunluk_doluluk.html oluştur
  - Tarih seçici (datepicker) ekle
  - Özet istatistikler kartları ekle (toplam oda, dolu oda, giriş/çıkış sayıları)
  - Kat bazlı dolu oda listesi ekle
  - Detaylı oda tablosu ekle
  - Filtreleme özellikleri ekle (kat, doluluk durumu)
  - Yazdırma özelliği ekle


  - Responsive tasarım uygula
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 10. Sidebar menüsüne "Doluluk Yönetimi" ekle
  - templates/depo_sorumlusu/dashboard.html veya base template'i güncelle
  - Sidebar menüsüne "Doluluk Yönetimi" menü öğesi ekle

  - İkon ekle (takvim veya doluluk ikonu)
  - Aktif sayfa vurgulama ekle
  - _Gereksinimler: 1.1_

- [ ] 11. Asenkron dosya işleme mekanizmasını ekle
  - Flask-Executor veya threading kullanarak asenkron işleme ekle
  - process_excel_file() metodunu arka planda çalıştır
  - İlerleme durumu takibi ekle (veritabanı veya cache)
  - Durum sorgulama endpoint'ini tamamla
  - Hata durumunda bildirim mekanizması ekle
  - _Gereksinimler: 10.1, 10.2, 10.3, 10.4, 10.5_


- [ ] 12. Otomatik dosya temizleme scheduler'ı ekle
  - APScheduler veya cron job ile zamanlanmış görev oluştur
  - cleanup_old_files() metodunu günlük çalıştır (saat 02:00)
  - 4 günden eski dosyaları sil
  - Silme işlemlerini logla
  - app.py'de scheduler'ı başlat
  - _Gereksinimler: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 13. Hata yönetimi ve validasyon ekle
  - Dosya formatı validasyonu ekle (.xlsx, .xls)
  - Dosya boyutu kontrolü ekle (10 MB limit)
  - Sütun başlıkları kontrolü ekle
  - Oda numarası validasyonu ekle
  - Tarih formatı validasyonu ekle
  - Misafir sayısı validasyonu ekle
  - Detaylı hata mesajları ekle
  - Hata raporlama mekanizması ekle
  - _Gereksinimler: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 14. Güvenlik önlemlerini ekle

  - Dosya uzantısı kontrolü ekle
  - Güvenli dosya adı oluşturma ekle (UUID)
  - CSRF token kontrolü ekle
  - SQL injection koruması kontrol et (ORM kullanımı)
  - XSS koruması kontrol et (template escaping)
  - Yetkilendirme kontrollerini test et
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 15. Performans optimizasyonlarını uygula

  - Veritabanı indekslerini kontrol et
  - Batch insert kullan (toplu ekleme)
  - Query optimizasyonu yap
  - Chunk-based Excel okuma ekle (büyük dosyalar için)
  - Connection pooling kontrol et
  - _Gereksinimler: 10.1, 10.2, 10.5_

- [x] 16. Test senaryolarını yaz ve çalıştır


  - Excel işleme servis testleri yaz
  - Dosya yönetim servis testleri yaz
  - Doluluk hesaplama servis testleri yaz
  - Route testleri yaz (endpoint testleri)
  - Entegrasyon testleri yaz (end-to-end)
  - Edge case testlerini yaz
  - Performans testlerini yaz (500 satır/30 saniye)
  - _Gereksinimler: Tüm gereksinimler_


- [x] 17. Dokümantasyon ve son kontroller



  - README dosyasına özellik açıklaması ekle
  - Kullanım kılavuzu oluştur
  - API dokümantasyonu ekle (endpoint'ler)
  - Veritabanı şeması dokümantasyonu ekle
  - Deployment notları ekle
  - Gerekli paketleri requirements.txt'ye ekle (openpyxl, APScheduler)
  - Ortam değişkenlerini .env.example'a ekle
  - Son testleri çalıştır
  - _Gereksinimler: Tüm gereksinimler_

## Notlar

### Önemli Hatırlatmalar
- Her görev tamamlandığında test edilmeli
- Hata yönetimi her aşamada eklenmelidir
- Audit log kayıtları unutulmamalı
- Responsive tasarım tüm sayfalarda uygulanmalı
- Türkçe karakter desteği kontrol edilmeli

### Bağımlılıklar
- Görev 2, 3, 4 birbirinden bağımsız (paralel yapılabilir)
- Görev 5, 6 → Görev 2, 3, 4'e bağımlı
- Görev 7, 8, 9 → Görev 5, 6'ya bağımlı
- Görev 11 → Görev 2, 5'e bağımlı
- Görev 12 → Görev 3'e bağımlı
- Görev 16 → Tüm görevlere bağımlı

### Teknik Detaylar
- Excel kütüphanesi: openpyxl (pandas opsiyonel)
- Asenkron işleme: Flask-Executor veya threading
- Scheduler: APScheduler
- Dosya depolama: uploads/doluluk/
- Dosya saklama süresi: 4 gün
- Maksimum dosya boyutu: 10 MB
- Performans hedefi: 500 satır/30 saniye
