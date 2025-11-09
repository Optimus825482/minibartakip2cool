# Implementation Plan

- [x] 1. Base template header yapısını güncelle


  - base.html dosyasındaki header section'ını yeniden tasarla (satır ~1110-1190)
  - Logo boyutunu 32px'den 40-48px'e çıkar
  - Yeni page_description block'unu ekle
  - Header padding'i optimize et (py-3'ten py-2.5'e)
  - Otel logosu ve başlık için yeni flex layout uygula
  - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 5.1, 5.2_

- [x] 2. CSS optimizasyonlarını uygula


  - Header min-height değerlerini ekle (56px mobile, 64px desktop)
  - Logo max-height değerlerini tanımla (40px mobile, 48px desktop)
  - Page description için responsive visibility kuralları ekle
  - Dark mode uyumluluğunu kontrol et
  - _Requirements: 2.2, 3.3, 5.1, 5.2, 5.3_

- [ ] 3. Dashboard sayfalarını güncelle
- [-] 3.1 Sistem yöneticisi dashboard'unu güncelle

  - templates/sistem_yoneticisi/dashboard.html dosyasını aç
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır (varsa)
  - İşlem butonlarını content başına taşı (varsa)
  - _Requirements: 1.1, 1.3, 3.1, 4.1_

- [ ] 3.2 Kat sorumlusu dashboard'unu güncelle
  - templates/kat_sorumlusu/dashboard.html dosyasını aç
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır (varsa)
  - İşlem butonlarını content başına taşı (varsa)
  - _Requirements: 1.1, 1.3, 3.1, 4.1_

- [ ] 4. Sistem yönetimi sayfalarını güncelle
- [ ] 4.1 Otel listesi sayfasını güncelle
  - templates/sistem_yoneticisi/otel_listesi.html dosyasını güncelle
  - page_description block'u ekle: "Sistemdeki tüm otelleri görüntüleyin ve yönetin"
  - Sayfa içindeki h2 başlığını ve açıklama paragrafını kaldır
  - "Yeni Otel Ekle" butonunu content başına taşı
  - _Requirements: 1.1, 1.3, 3.1, 3.2, 4.1, 4.2_

- [ ] 4.2 Otel tanımlama sayfasını güncelle
  - templates/sistem_yoneticisi/otel_tanimla.html dosyasını güncelle
  - page_description block'u ekle (varsa)
  - Sayfa içindeki gereksiz başlıkları temizle
  - _Requirements: 1.1, 1.3, 3.1_

- [ ] 4.3 Kat yönetimi sayfasını güncelle
  - templates/sistem_yoneticisi/kat_tanimla.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - "Yeni Kat Ekle" butonunu content başına taşı
  - _Requirements: 1.1, 1.4, 3.1, 4.1_

- [ ] 4.4 Oda yönetimi sayfasını güncelle
  - templates/sistem_yoneticisi/oda_tanimla.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - "Yeni Oda Ekle" butonunu content başına taşı
  - _Requirements: 1.1, 3.1, 4.1_

- [ ] 5. Ürün yönetimi sayfalarını güncelle
- [ ] 5.1 Ürün grupları sayfasını güncelle
  - templates/sistem_yoneticisi/urun_gruplari.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 4.1_

- [ ] 5.2 Ürünler sayfasını güncelle
  - templates/sistem_yoneticisi/urunler.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 4.1_

- [ ] 6. Kat sorumlusu sayfalarını güncelle
- [ ] 6.1 Kritik stoklar sayfasını güncelle
  - templates/kat_sorumlusu/kritik_stoklar.html dosyasını güncelle
  - page_description block'u ekle: "Azalan ve stokout ürünleri takip edin"
  - Sayfa içindeki h2 başlığını ve açıklama paragrafını kaldır
  - İşlem butonlarını (Sipariş Hazırla, Dashboard'a Dön) content başına taşı
  - _Requirements: 1.1, 3.1, 3.2, 4.1, 4.2_

- [ ] 6.2 Zimmet stoklarım sayfasını güncelle
  - templates/kat_sorumlusu/zimmet_stoklarim.html dosyasını güncelle
  - page_description block'u ekle: "Aktif zimmetlerinizi ve stok durumlarını görüntüleyin"
  - Sayfa içindeki h2 başlığını ve açıklama paragrafını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 3.2, 4.1_

- [ ] 6.3 Sipariş hazırla sayfasını güncelle
  - templates/kat_sorumlusu/siparis_hazirla.html dosyasını güncelle
  - page_description block'u ekle: "Kritik seviyedeki ürünler için sipariş listesi"
  - Sayfa içindeki h2 başlığını ve açıklama paragrafını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 3.2, 4.1_

- [ ] 6.4 Minibar kontrol sayfasını güncelle
  - templates/kat_sorumlusu/minibar_kontrol.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 4.1_

- [ ] 7. Depo ve stok sayfalarını güncelle
- [ ] 7.1 Depo stokları sayfasını güncelle
  - templates/sistem_yoneticisi/depo_stoklari.html dosyasını güncelle
  - page_description block'u ekle: "Tüm ürünlerin depo stok durumlarını görüntüleyin"
  - Sayfa içindeki h2 başlığını ve açıklama paragrafını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 3.2, 4.1_

- [ ] 7.2 Oda minibar stokları sayfasını güncelle
  - templates/sistem_yoneticisi/admin_oda_minibar_stoklari.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - İşlem butonlarını content başına taşı
  - _Requirements: 1.1, 3.1, 4.1_

- [ ] 8. Rapor sayfalarını güncelle
- [ ] 8.1 Stok raporları sayfasını güncelle
  - templates/raporlar/stok_raporlari.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 8.2 Zimmet raporları sayfasını güncelle
  - templates/raporlar/zimmet_raporlari.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 8.3 Minibar raporları sayfasını güncelle
  - templates/raporlar/minibar_raporlari.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 9. Form sayfalarını güncelle
- [ ] 9.1 Personel tanımlama sayfasını güncelle
  - templates/sistem_yoneticisi/personel_tanimla.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 9.2 Kat düzenleme sayfasını güncelle
  - templates/sistem_yoneticisi/kat_duzenle.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 9.3 Oda düzenleme sayfasını güncelle
  - templates/sistem_yoneticisi/oda_duzenle.html dosyasını güncelle
  - page_description block'u ekle
  - Sayfa içindeki h2 başlığını kaldır
  - _Requirements: 1.1, 3.1_

- [ ] 10. Test ve doğrulama
- [ ] 10.1 Responsive test yap
  - Mobile (< 640px): Logo 40px, açıklama gizli, header 56px
  - Tablet (640-1024px): Logo 48px, açıklama görünür, header 64px
  - Desktop (> 1024px): Logo 48px, açıklama görünür, header 64px
  - _Requirements: 2.2, 3.3, 5.1, 5.2_

- [ ] 10.2 Dark mode uyumluluğunu test et
  - Tüm sayfalarda dark mode'da görünümü kontrol et
  - Text renkleri doğru mu kontrol et
  - Logo dark mode'da görünür mü kontrol et
  - _Requirements: 1.1, 2.1, 3.1_

- [ ] 10.3 Edge case senaryolarını test et
  - Logo olmayan otel senaryosu
  - Çok uzun sayfa başlığı (truncate çalışıyor mu?)
  - Çok uzun açıklama metni (truncate çalışıyor mu?)
  - Sidebar açık/kapalı durumlarında header görünümü
  - _Requirements: 1.1, 2.5, 3.4, 5.5_

- [ ] 10.4 Tüm sayfa tiplerinde manuel test
  - Dashboard sayfaları
  - Liste sayfaları
  - Form sayfaları
  - Rapor sayfaları
  - Detay sayfaları
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
