# Implementation Plan

## Genel Bakış

Bu implementation plan, app.py dosyasının modüler yapıya dönüştürülmesi için gereken tüm adımları içerir. Her task, önceki task'lerin başarıyla tamamlanmasına bağlıdır.

---

## Aşama 1: Hazırlık ve Analiz

- [x] 1. Analiz araçlarını oluştur


  - Python script'i ile app.py'deki tüm @app.route dekoratörlerini tespit et
  - Template dosyalarındaki tüm url_for çağrılarını tespit et
  - Static JS dosyalarındaki API çağrılarını tespit et
  - Kullanılmayan endpoint'leri belirle
  - Analiz raporunu `docs/refactoring_analysis.md` dosyasına kaydet
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Yedekleme sistemi oluştur



  - `scripts/backup_app.py` script'ini oluştur
  - app.py'nin tarih-saat damgalı yedeğini al
  - Yedekleme başarısını doğrula
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Test ortamını hazırla




  - Flask uygulamasının çalıştığını doğrula
  - Tüm import'ların çalıştığını kontrol et
  - Temel endpoint'lerin erişilebilir olduğunu test et
  - _Requirements: 6.1, 6.2, 6.3_

---

## Aşama 2: Error Handlers Modülü



- [x] 4. Error handlers modülünü oluştur


  - `routes/error_handlers.py` dosyasını oluştur
  - `register_error_handlers(app)` fonksiyonunu implement et
  - Rate limit error handler'ı taşı (429)
  - CSRF error handler'ı taşı
  - app.py'de error handler'ları register et
  - Flask uygulamasını başlat ve test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3_

---

## Aşama 3: Auth Routes Modülü





- [x] 5. Auth routes modülünü oluştur

  - `routes/auth_routes.py` dosyasını oluştur
  - `register_auth_routes(app)` fonksiyonunu implement et
  - `/` (index) endpoint'ini taşı
  - `/setup` endpoint'ini taşı
  - `/login` endpoint'ini taşı
  - `/logout` endpoint'ini taşı
  - Gerekli import'ları ekle (forms, models, utils)
  - app.py'de auth routes'u register et
  - Login/logout işlemlerini test et
  - Setup sayfasını test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_


---


## Aşama 4: Dashboard Routes Modülü

- [x] 6. Dashboard routes modülünü oluştur



  - `routes/dashboard_routes.py` dosyasını oluştur
  - `register_dashboard_routes(app)` fonksiyonunu implement et
  - `/dashboard` endpoint'ini taşı (rol bazlı yönlendirme)
  - `/sistem-yoneticisi` endpoint'ini taşı
  - `/depo` endpoint'ini taşı
  - `/kat-sorumlusu` ve `/kat-sorumlusu/dashboard` endpoint'lerini taşı
  - Gerekli import'ları ekle
  - app.py'de dashboard routes'u register et
  - Her rol için dashboard'u test et
  - Grafik verilerinin doğru yüklendiğini kontrol et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 5: Sistem Yöneticisi Routes Modülü



- [x] 7. Sistem yöneticisi routes modülünü oluştur


  - `routes/sistem_yoneticisi_routes.py` dosyasını oluştur
  - `register_sistem_yoneticisi_routes(app)` fonksiyonunu implement et
  - `/otel-tanimla` endpoint'ini taşı
  - `/kat-tanimla` endpoint'ini taşı
  - `/kat-duzenle/<int:kat_id>` endpoint'ini taşı
  - `/kat-sil/<int:kat_id>` endpoint'ini taşı
  - `/oda-tanimla` endpoint'ini taşı
  - `/oda-duzenle/<int:oda_id>` endpoint'ini taşı
  - `/oda-sil/<int:oda_id>` endpoint'ini taşı
  - `/sistem-loglari` endpoint'ini taşı
  - Gerekli import'ları ekle (forms, models, utils)
  - app.py'de sistem yöneticisi routes'u register et
  - Otel tanımlama işlemini test et
  - Kat ekleme/düzenleme/silme işlemlerini test et
  - Oda ekleme/düzenleme/silme işlemlerini test et
  - Sistem loglarını test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 6: Admin Routes Modülü (Temel)

- [x] 8. Admin routes modülünü oluştur






  - `routes/admin_routes.py` dosyasını oluştur
  - `register_admin_routes(app)` fonksiyonunu implement et
  - `/personel-tanimla` endpoint'ini taşı
  - `/personel-duzenle/<int:personel_id>` endpoint'ini taşı
  - `/personel-pasif-yap/<int:personel_id>` endpoint'ini taşı
  - `/personel-aktif-yap/<int:personel_id>` endpoint'ini taşı
  - `/urun-gruplari` endpoint'ini taşı
  - `/grup-duzenle/<int:grup_id>` endpoint'ini taşı
  - `/grup-sil/<int:grup_id>` endpoint'ini taşı
  - `/grup-pasif-yap/<int:grup_id>` endpoint'ini taşı
  - `/grup-aktif-yap/<int:grup_id>` endpoint'ini taşı
  - `/urunler` endpoint'ini taşı
  - `/urun-duzenle/<int:urun_id>` endpoint'ini taşı
  - `/urun-sil/<int:urun_id>` endpoint'ini taşı
  - `/urun-pasif-yap/<int:urun_id>` endpoint'ini taşı
  - `/urun-aktif-yap/<int:urun_id>` endpoint'ini taşı
  - Gerekli import'ları ekle
  - app.py'de admin routes'u register et
  - Personel ekleme/düzenleme işlemlerini test et
  - Ürün grubu ekleme/düzenleme işlemlerini test et
  - Ürün ekleme/düzenleme işlemlerini test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 7: Admin Minibar Routes Modülü


- [x] 9. Admin minibar routes modülünü oluştur



  - `routes/admin_minibar_routes.py` dosyasını oluştur
  - `register_admin_minibar_routes(app)` fonksiyonunu implement et
  - `/admin/depo-stoklari` endpoint'ini taşı
  - `/admin/oda-minibar-stoklari` endpoint'ini taşı
  - `/admin/oda-minibar-detay/<int:oda_id>` endpoint'ini taşı
  - `/admin/minibar-sifirla` endpoint'ini taşı
  - `/admin/minibar-islemleri` endpoint'ini taşı
  - `/admin/minibar-islem-sil/<int:islem_id>` endpoint'ini taşı
  - `/admin/minibar-durumlari` endpoint'ini taşı
  - `/api/minibar-islem-detay/<int:islem_id>` endpoint'ini taşı
  - `/api/admin/verify-password` endpoint'ini taşı
  - Gerekli import'ları ekle
  - app.py'de admin minibar routes'u register et
  - Depo stokları sayfasını test et
  - Oda minibar stokları sayfasını test et
  - Minibar sıfırlama işlemini test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 8: Admin Stok Routes Modülü


- [x] 10. Admin stok routes modülünü oluştur

  - `routes/admin_stok_routes.py` dosyasını oluştur
  - `register_admin_stok_routes(app)` fonksiyonunu implement et
  - `/admin/stok-giris` endpoint'ini taşı
  - `/admin/stok-hareketleri` endpoint'ini taşı
  - `/admin/stok-hareket-duzenle/<int:hareket_id>` endpoint'ini taşı
  - `/admin/stok-hareket-sil/<int:hareket_id>` endpoint'ini taşı
  - Gerekli import'ları ekle
  - app.py'de admin stok routes'u register et
  - Stok girişi işlemini test et
  - Stok hareketleri listesini test et
  - Stok hareket düzenleme işlemini test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 9: Admin Zimmet Routes Modülü

- [x] 11. Admin zimmet routes modülünü oluştur

  - `routes/admin_zimmet_routes.py` dosyasını oluştur
  - `register_admin_zimmet_routes(app)` fonksiyonunu implement et
  - `/admin/personel-zimmetleri` endpoint'ini taşı
  - `/admin/zimmet-detay/<int:zimmet_id>` endpoint'ini taşı
  - `/admin/zimmet-iade/<int:zimmet_id>` endpoint'ini taşı
  - `/admin/zimmet-iptal/<int:zimmet_id>` endpoint'ini taşı
  - Gerekli import'ları ekle
  - app.py'de admin zimmet routes'u register et
  - Personel zimmetleri listesini test et
  - Zimmet detay sayfasını test et
  - Zimmet iade işlemini test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---




## Aşama 10: Depo Routes Modülü

- [x] 12. Depo routes modülünü oluştur
  - `routes/depo_routes.py` dosyasını oluştur
  - `register_depo_routes(app)` fonksiyonunu implement et
  - `/stok-giris` endpoint'ini taşı
  - `/stok-duzenle/<int:hareket_id>` endpoint'ini taşı
  - app.py'de kalan depo sorumlusu endpoint'lerini tespit et
  - Tespit edilen endpoint'leri taşı
  - Gerekli import'ları ekle
  - app.py'de depo routes'u register et
  - Depo sorumlusu stok girişi işlemini test et
  - Depo sorumlusu dashboard'unu test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 11: Kat Sorumlusu Routes Modülü

- [x] 13. Kat sorumlusu routes modülünü oluştur



  - `routes/kat_sorumlusu_routes.py` dosyasını oluştur
  - `register_kat_sorumlusu_routes(app)` fonksiyonunu implement et
  - app.py'de kalan kat sorumlusu endpoint'lerini tespit et (ilk dolum hariç)
  - Tespit edilen endpoint'leri taşı
  - Gerekli import'ları ekle
  - app.py'de kat sorumlusu routes'u register et
  - Kat sorumlusu dashboard'unu test et
  - Kat sorumlusu işlemlerini test et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 12: API Routes Modülü

- [x] 14. API routes modülünü oluştur


  - `routes/api_routes.py` dosyasını oluştur
  - `register_api_routes(app)` fonksiyonunu implement et
  - app.py'de kalan tüm `/api/` endpoint'lerini tespit et
  - Tespit edilen API endpoint'lerini taşı
  - Gerekli import'ları ekle
  - app.py'de api routes'u register et
  - API endpoint'lerini test et
  - JSON response'ların doğru döndüğünü kontrol et
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 13: Merkezi Register ve app.py Temizliği

- [x] 15. Merkezi register modülünü oluştur






  - `routes/__init__.py` dosyasını oluştur
  - `register_all_routes(app)` fonksiyonunu implement et
  - Tüm route modüllerini import et
  - Her modülün register fonksiyonunu çağır
  - app.py'yi temizle ve sadece bootstrap kodunu bırak
  - Flask uygulamasını başlat ve test et
  - Tüm endpoint'lerin erişilebilir olduğunu doğrula
  - Import hatalarını kontrol et
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 6.1, 6.2, 6.3, 6.4_

- [x] 16. app.py'yi optimize et





  - Gereksiz import'ları temizle
  - Context processor'ları kontrol et
  - Kod formatını düzenle
  - Satır sayısının 300'ün altında olduğunu doğrula
  - _Requirements: 4.1, 4.2, 4.3, 6.1, 6.2, 6.3_

---

## Aşama 14: Kullanılmayan Kod Temizliği

- [x] 17. Kullanılmayan endpoint'leri temizle


  - Aşama 1'de oluşturulan analiz raporunu incele
  - Kullanılmayan endpoint'leri belirle
  - Her endpoint için son 90 günlük log kayıtlarını kontrol et
  - Kullanılmadığı kesin olan endpoint'leri sil
  - Silinen endpoint'lerin listesini `docs/removed_endpoints.md` dosyasına kaydet
  - Flask uygulamasını başlat ve test et
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 18. Kullanılmayan import'ları temizle



  - Her route modülündeki import'ları kontrol et
  - Kullanılmayan import'ları sil
  - app.py'deki import'ları kontrol et
  - Flask uygulamasını başlat ve import hatalarını kontrol et
  - _Requirements: 5.3, 6.1, 6.2, 6.3_

---

## Aşama 15: Dokümantasyon ve Finalizasyon

- [x] 19. Modül dokümantasyonunu oluştur (İptal edildi - Gerek yok)


  - Her route modülüne docstring ekle
  - Her modülün sorumluluklarını dokümante et
  - Endpoint listesini dokümante et
  - Rol gereksinimlerini dokümante et
  - _Requirements: 7.1, 7.2, 7.5_

- [x] 20. Refactoring raporunu oluştur



  - `docs/refactoring_report.md` dosyasını oluştur
  - Taşınan endpoint'lerin listesini ekle
  - Silinen endpoint'lerin listesini ekle
  - Yeni dizin yapısını dokümante et
  - Satır sayısı karşılaştırması yap (önce/sonra)
  - _Requirements: 7.2, 7.3, 7.4, 7.5_

- [x] 21. README'yi güncelle



  - Yeni proje yapısını README'ye ekle
  - Route modüllerini açıkla
  - Yeni endpoint ekleme prosedürünü dokümante et
  - Geliştirici kılavuzunu güncelle
  - _Requirements: 7.4, 7.5_

- [x] 22. Final test ve doğrulama


  - Tüm endpoint'leri manuel test et
  - Her rol için login yapıp işlemleri test et
  - Performans testleri yap
  - Memory leak kontrolü yap
  - Log sisteminin çalıştığını doğrula
  - Audit trail sisteminin çalıştığını doğrula
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_





- [ ] 23. Git commit ve cleanup


  - Tüm değişiklikleri commit et
  - Yedek dosyalarını temizle (veya .gitignore'a ekle)
  - Tag oluştur (v2.0-refactored)
  - Branch'i merge et
  - _Requirements: 8.4_

---

## Notlar

- Her task tamamlandığında, Flask uygulamasını başlatıp test edin
- Sorun çıkarsa, en son yedekten geri dönün
- Her aşamada git commit yapın
- Test sırasında tüm rolleri (sistem_yoneticisi, admin, depo_sorumlusu, kat_sorumlusu) kontrol edin
- API endpoint'lerini Postman veya curl ile test edin
