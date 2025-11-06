# Implementation Plan

- [x] 1. Veritabanı değişikliklerini uygula


  - PersonelZimmetDetay tablosuna `kritik_stok_seviyesi` alanını ekle
  - Migration script'i oluştur ve çalıştır
  - _Requirements: 2.1, 2.2_




- [x] 2. Backend helper fonksiyonlarını implement et

- [x] 2.1 get_kat_sorumlusu_zimmet_stoklari() fonksiyonunu yaz

  - Aktif zimmetleri ve detaylarını getir
  - Kullanım yüzdesi hesapla


  - Stok durumu kategorileri belirle (kritik/dikkat/normal/stokout)
  - Badge class ve text bilgilerini ekle
  - _Requirements: 1.1, 1.2, 1.3, 1.5_



- [x] 2.2 get_kat_sorumlusu_kritik_stoklar() fonksiyonunu yaz

  - Kritik seviye karşılaştırması yap
  - Stokout, kritik, dikkat ve risk kategorilerine ayır
  - İstatistik bilgilerini hesapla


  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [x] 2.3 olustur_otomatik_siparis() fonksiyonunu yaz

  - Kritik seviyedeki ürünleri tespit et


  - Önerilen sipariş miktarını hesapla (kritik seviye - kalan + güvenlik marjı)
  - Aciliyet seviyelerini belirle (stokout = acil, diğerleri = normal)
  - _Requirements: 4.1, 4.2, 4.3_



- [x] 2.4 kaydet_siparis_talebi() fonksiyonunu yaz

  - Sipariş talebini veritabanına kaydet
  - Audit log kaydı oluştur
  - Sistem log kaydı oluştur

  - _Requirements: 4.4, 4.5_

- [x] 2.5 get_zimmet_urun_gecmisi() fonksiyonunu yaz

  - MinibarIslemDetay tablosundan ürün hareketlerini getir
  - Günlük tüketim istatistiklerini hesapla
  - Tarih filtreleme uygula
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2.6 guncelle_kritik_seviye() fonksiyonunu yaz

  - Input validasyonu yap (pozitif tam sayı)
  - PersonelZimmetDetay kaydını güncelle
  - Audit trail kaydı oluştur
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 2.7 export_zimmet_stok_excel() fonksiyonunu yaz



  - Zimmet stoklarını Excel formatında hazırla
  - Renk kodlaması uygula (kritik = kırmızı, dikkat = sarı)
  - Sütun genişliklerini ayarla
  - _Requirements: 6.5_

- [x] 2.8 Helper fonksiyonları için unit testler yaz







  - test_get_kat_sorumlusu_zimmet_stoklari()
  - test_get_kritik_stoklar()
  - test_olustur_otomatik_siparis()
  - test_guncelle_kritik_seviye()
  - _Requirements: Tüm requirements_

- [x] 3. Dashboard iyileştirmelerini yap


- [x] 3.1 Dashboard kartlarını güncelle


  - Toplam zimmet ürün sayısı kartı ekle
  - Kritik stok sayısı kartı ekle (kırmızı vurgu)
  - Stokout ürün sayısı kartı ekle (kırmızı vurgu)
  - Bugünkü kullanım kartı ekle
  - Kartlara tıklanabilirlik ekle (ilgili sayfaya yönlendirme)
  - _Requirements: 7.1, 7.3, 7.4_

- [x] 3.2 Dashboard grafiklerini ekle

  - En çok kullanılan 5 ürün bar chart'ı (Chart.js)
  - Zimmet kullanım durumu doughnut chart'ı
  - Günlük tüketim trendi line chart'ı (son 7 gün)
  - _Requirements: 7.2_

- [x] 3.3 Dashboard yenileme fonksiyonunu ekle


  - AJAX ile veri yenileme
  - Loading indicator göster
  - _Requirements: 7.5_

- [x] 4. Zimmet stoklarım sayfasını oluştur

- [x] 4.1 /kat-sorumlusu/zimmet-stoklarim route'unu yaz

  - get_kat_sorumlusu_zimmet_stoklari() fonksiyonunu çağır
  - Template'e veri gönder
  - Log kaydı oluştur
  - _Requirements: 1.1_

- [x] 4.2 zimmet_stoklarim.html template'ini oluştur


  - Zimmet listesi tablosu
  - Her zimmet için accordion/collapse detay
  - Ürün detayları tablosu (progress bar ile)
  - Kritik seviye belirleme butonu
  - Renk kodlaması (kritik = kırmızı, dikkat = sarı)
  - _Requirements: 1.2, 1.3, 1.4, 1.5_

- [x] 4.3 Kritik seviye belirleme modal'ını ekle

  - Modal HTML yapısı
  - Form validasyonu (min=1, required)
  - AJAX submit fonksiyonu
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 4.4 /api/kat-sorumlusu/kritik-seviye-guncelle API endpoint'ini yaz

  - POST request handler
  - Input validasyonu
  - guncelle_kritik_seviye() fonksiyonunu çağır
  - JSON response döndür
  - _Requirements: 2.2, 2.4, 2.5_

- [x] 5. Kritik stoklar sayfasını oluştur

- [x] 5.1 /kat-sorumlusu/kritik-stoklar route'unu yaz

  - get_kat_sorumlusu_kritik_stoklar() fonksiyonunu çağır
  - Template'e veri gönder
  - Log kaydı oluştur
  - _Requirements: 3.1_

- [x] 5.2 kritik_stoklar.html template'ini oluştur


  - Stokout ürünler bölümü (en üstte, kırmızı)
  - Kritik ürünler bölümü (kırmızı)
  - Dikkat ürünler bölümü (sarı)
  - Her ürün için: kalan miktar, kritik seviye, eksik miktar
  - Sipariş hazırla butonu
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [x] 6. Sipariş hazırlama sayfasını oluştur

- [x] 6.1 /kat-sorumlusu/siparis-hazirla route'unu yaz

  - olustur_otomatik_siparis() fonksiyonunu çağır
  - Template'e sipariş listesi gönder
  - Log kaydı oluştur
  - _Requirements: 4.1_

- [x] 6.2 siparis_hazirla.html template'ini oluştur

  - Sipariş listesi tablosu
  - Her ürün için: mevcut stok, kritik seviye, önerilen miktar
  - Manuel düzenleme input'ları
  - Aciliyet badge'leri (acil = kırmızı, normal = mavi)
  - Sipariş onaylama butonu
  - _Requirements: 4.2, 4.3, 4.4_

- [x] 6.3 Sipariş onaylama modal'ını ekle

  - Confirmation modal
  - Ek açıklama textarea
  - AJAX submit fonksiyonu
  - _Requirements: 4.5_

- [x] 6.4 /api/kat-sorumlusu/siparis-kaydet API endpoint'ini yaz

  - POST request handler
  - kaydet_siparis_talebi() fonksiyonunu çağır
  - JSON response döndür
  - _Requirements: 4.5_

- [x] 7. Ürün geçmişi sayfasını oluştur

- [x] 7.1 /kat-sorumlusu/urun-gecmisi/<urun_id> route'unu yaz

  - get_zimmet_urun_gecmisi() fonksiyonunu çağır
  - Tarih filtresi parametrelerini al
  - Template'e veri gönder
  - _Requirements: 6.1, 6.2_

- [x] 7.2 urun_gecmisi.html template'ini oluştur

  - Ürün bilgileri kartı
  - Hareketler tablosu (tarih, işlem tipi, oda, miktar)
  - Tarih filtresi form'u
  - İstatistik kartları (toplam kullanım, günlük ortalama)
  - _Requirements: 6.2, 6.3_

- [x] 7.3 Grafik görünümü ekle


  - Günlük tüketim line chart'ı (Chart.js)
  - Grafik/Tablo görünüm toggle butonu
  - _Requirements: 6.4_

- [x] 7.4 Excel export fonksiyonunu ekle


  - /kat-sorumlusu/zimmet-export route'u
  - export_zimmet_stok_excel() fonksiyonunu çağır
  - Excel dosyasını indir
  - _Requirements: 6.5_

- [x] 8. Stokout uyarı sistemini implement et

- [x] 8.1 Stokout kontrolü fonksiyonunu yaz

  - Dashboard yüklenirken stokout ürünleri kontrol et
  - Stokout sayısını hesapla
  - _Requirements: 5.1, 5.2_

- [x] 8.2 Stokout uyarı badge'ini dashboard'a ekle

  - Kırmızı vurgulu alert badge
  - Stokout ürün sayısını göster
  - Kritik stoklar sayfasına link
  - _Requirements: 5.2_

- [x] 8.3 Stokout riski hesaplama ekle

  - Kritik seviyenin %50'sinin altındaki ürünleri tespit et
  - "Stokout Riski" badge'i ekle
  - _Requirements: 5.4_

- [x] 8.4 Acil sipariş işaretleme ekle

  - Stokout ürünler için sipariş "Acil" olarak işaretle
  - Acil siparişleri öncelikli göster
  - _Requirements: 5.5_

- [x] 9. UI/UX iyileştirmeleri ve responsive tasarım

- [x] 9.1 Renk kodlaması ve badge sistemini uygula

  - Stok durumu badge'leri (kritik/dikkat/normal)
  - Aciliyet badge'leri (acil/normal)
  - Progress bar renkleri
  - _Requirements: Tüm requirements_

- [x] 9.2 Responsive grid layout'ları ekle

  - Mobile: tek sütun
  - Tablet: 2 sütun
  - Desktop: 3-4 sütun
  - _Requirements: Tüm requirements_

- [x] 9.3 Loading indicator'ları ekle

  - AJAX işlemleri için spinner
  - Sayfa yüklenirken skeleton loader
  - _Requirements: Tüm requirements_

- [x] 9.4 Toast notification sistemi ekle

  - Başarılı işlemler için yeşil toast
  - Hata mesajları için kırmızı toast
  - Uyarılar için sarı toast
  - _Requirements: Tüm requirements_

- [x] 10. Güvenlik ve validasyon kontrollerini ekle

- [x] 10.1 Route yetkilendirme kontrollerini ekle

  - @role_required('kat_sorumlusu') decorator'ları
  - Veri izolasyonu (sadece kendi zimmetleri)
  - _Requirements: Tüm requirements_

- [x] 10.2 Input validasyon kontrollerini ekle

  - Backend validasyon (pozitif tam sayı, required)
  - Frontend validasyon (HTML5 attributes)
  - _Requirements: 2.2, 2.5, 4.4_

- [x] 10.3 CSRF protection kontrollerini ekle

  - Form token'ları
  - AJAX request header'ları
  - _Requirements: Tüm requirements_

- [x] 10.4 SQL injection prevention kontrollerini ekle



  - ORM kullanımı doğrula
  - Raw SQL kullanımı varsa parametrize et
  - _Requirements: Tüm requirements_

- [x] 11. Loglama ve audit trail sistemini entegre et


- [x] 11.1 Sistem log kayıtlarını ekle

  - Tüm route'lara log_islem() çağrıları
  - Başarılı işlemler için log
  - _Requirements: Tüm requirements_

- [x] 11.2 Hata log kayıtlarını ekle

  - Try-catch blokları
  - log_hata() çağrıları
  - Extra info parametreleri
  - _Requirements: Tüm requirements_

- [x] 11.3 Audit trail kayıtlarını ekle

  - Kritik seviye güncellemeleri için audit_update()
  - Sipariş kayıtları için audit_create()
  - _Requirements: 2.2, 4.5_

- [x] 12. Integration testler yaz







  - Zimmet stok görüntüleme flow testi
  - Kritik seviye belirleme flow testi
  - Sipariş hazırlama flow testi
  - _Requirements: Tüm requirements_

- [ ]* 13. Dokümantasyon ve kullanım kılavuzu oluştur
  - Kullanıcı kılavuzu (Türkçe)
  - API dokümantasyonu
  - Deployment notları
  - _Requirements: Tüm requirements_
