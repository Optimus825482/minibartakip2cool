# Çoklu Otel Yönetim Sistemi - Görev Listesi

## Genel Bakış

Bu görev listesi, çoklu otel yönetim sisteminin adım adım implementasyonunu içerir. Her görev, bir önceki göreve bağımlıdır ve sistem kademeli olarak geliştirilecektir.

---

## Görevler

- [x] 1. Veritabanı Modeli Güncellemeleri


  - KullaniciOtel ara tablosu oluştur
  - Kullanici modeline otel_id alanı ekle
  - Otel modeline ilişkiler ve helper metodlar ekle
  - Database migration script'i hazırla
  - _Gereksinimler: 1.1, 5.2, 6.2_

- [x] 1.1 KullaniciOtel ara tablosu oluştur


  - models.py dosyasına KullaniciOtel sınıfını ekle
  - Many-to-many ilişki için gerekli alanları tanımla (kullanici_id, otel_id)
  - Unique constraint ekle (aynı kullanıcı aynı otele birden fazla kez atanamaz)
  - Index'leri tanımla (idx_kullanici_otel)
  - _Gereksinimler: 5.2, 7.1_

- [x] 1.2 Kullanici modeline otel_id alanı ekle


  - Kullanici sınıfına otel_id foreign key alanı ekle (nullable=True)
  - Otel ile relationship tanımla (kat sorumlusu için)
  - atanan_oteller relationship'i ekle (depo sorumlusu için)
  - _Gereksinimler: 6.2, 8.1_


- [x] 1.3 Otel modeline helper metodlar ekle

  - get_depo_sorumlu_sayisi() metodu yaz
  - get_kat_sorumlu_sayisi() metodu yaz
  - kullanici_atamalari relationship'i ekle
  - _Gereksinimler: 9.1, 9.2_


- [x] 1.4 Database migration script'i hazırla



  - Alembic migration dosyası oluştur
  - upgrade() fonksiyonunda yeni tabloları ve alanları ekle
  - downgrade() fonksiyonunda rollback mantığını yaz
  - _Gereksinimler: 4.1, 4.2_

- [x] 2. Veri Migrasyonu Script'i

  - Merit Royal Diamond oteli oluştur
  - Mevcut katları otele ata
  - Mevcut kullanıcıları otele ata
  - Migration script'ini test et
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2.1 Merit Royal Diamond oteli oluştur




  - migrate_to_multi_hotel.py dosyası oluştur
  - Otel kaydı oluşturma fonksiyonu yaz
  - Duplicate kontrolü ekle (zaten varsa atla)
  - _Gereksinimler: 4.1_


- [x] 2.2 Mevcut katları otele ata

  - otel_id NULL olan tüm katları bul
  - Merit Royal Diamond otel_id'sini ata
  - Başarı/hata loglaması ekle
  - _Gereksinimler: 4.2, 4.4_



- [x] 2.3 Mevcut kullanıcıları otele ata

  - Tüm kat sorumlularına otel_id ata
  - Tüm depo sorumlularına KullaniciOtel kaydı oluştur
  - Duplicate kontrolü ekle


  - _Gereksinimler: 5.5, 6.5, 4.3_



- [x] 2.4 Migration script'ini çalıştır ve test et




  - Script'i development ortamında çalıştır
  - Veri bütünlüğünü kontrol et
  - Log kayıtlarını incele
  - _Gereksinimler: 4.4, 4.5_


- [x] 3. Form Sınıfları Oluştur/Güncelle

  - OtelForm oluştur
  - KatForm'a otel_id ekle

  - OdaForm'a otel_id ekle
  - DepoSorumlusuForm'a otel_ids ekle
  - KatSorumlusuForm'a otel_id ekle
  - _Gereksinimler: 1.4, 2.1, 3.1, 5.1, 6.1_

- [x] 3.1 OtelForm oluştur


  - forms.py dosyasına OtelForm sınıfı ekle
  - Gerekli alanları tanımla (ad, adres, telefon, email, vergi_no, aktif)
  - Validatorları ekle (DataRequired, Length, Email)
  - _Gereksinimler: 1.4_







- [x] 3.2 KatForm'a otel_id ekle

  - otel_id SelectField ekle
  - DataRequired validator ekle
  - Choices dinamik yükleme için boş bırak
  - _Gereksinimler: 2.1, 2.2_


- [x] 3.3 OdaForm'a otel_id ve dinamik kat_id ekle

  - otel_id SelectField ekle
  - kat_id SelectField'i güncelle (dinamik yükleme için)
  - Validatorları ekle
  - _Gereksinimler: 3.1, 3.2, 3.3_


- [x] 3.4 DepoSorumlusuForm'a çoklu otel seçimi ekle

  - otel_ids SelectMultipleField ekle
  - DataRequired validator ekle
  - Choices dinamik yükleme için boş bırak
  - _Gereksinimler: 5.1, 5.2_


- [x] 3.5 KatSorumlusuForm'a tekli otel seçimi ekle

  - otel_id SelectField ekle
  - DataRequired validator ekle
  - Choices dinamik yükleme için boş bırak
  - _Gereksinimler: 6.1, 6.2_


- [x] 4. Otel Yönetimi Route'ları ve Template'leri


  - Otel listesi route ve template
  - Otel ekleme route ve template
  - Otel düzenleme route ve template
  - Otel aktif/pasif yapma route
  - Sidebar'a menü ekle
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 4.1 Otel listesi route ve template oluştur



  - admin_routes.py'ye /admin/oteller endpoint'i ekle
  - Pagination ekle
  - templates/admin/otel_listesi.html oluştur
  - Tablo görünümü (ID, Ad, Telefon, Kat Sayısı, Oda Sayısı, Personel, Durum)
  - _Gereksinimler: 1.2_

- [x] 4.2 Otel ekleme route ve template oluştur


  - /admin/oteller/ekle GET endpoint'i ekle
  - /admin/oteller/ekle POST endpoint'i ekle
  - templates/admin/otel_ekle.html oluştur
  - Form validasyonu ve hata mesajları ekle
  - _Gereksinimler: 1.3, 1.4_

- [x] 4.3 Otel düzenleme route ve template oluştur


  - /admin/oteller/<id>/duzenle GET endpoint'i ekle
  - /admin/oteller/<id>/duzenle POST endpoint'i ekle
  - templates/admin/otel_duzenle.html oluştur
  - Mevcut değerleri form'a yükle
  - _Gereksinimler: 1.3, 1.4_

- [x] 4.4 Otel aktif/pasif yapma route'u ekle

  - /admin/oteller/<id>/aktif-pasif POST endpoint'i ekle
  - Silme koruması ekle (kat/personel varsa uyarı)
  - Flash mesajları ekle
  - _Gereksinimler: 1.5, 9.1, 9.2_

- [x] 4.5 Sidebar'a Otel Yönetimi menüsü ekle


  - templates/base.html veya sidebar template'ini güncelle
  - "Sistem Yönetimi" altına "Otel Yönetimi" ekle
  - Icon ekle (🏨)
  - Yetki kontrolü ekle (sadece admin ve sistem yöneticisi görsün)
  - _Gereksinimler: 1.1, 10.5_

- [x] 5. Kat Yönetimi Güncellemeleri

  - Kat listesi template'ine otel kolonu ekle
  - Kat ekleme formuna otel seçimi ekle
  - Kat düzenleme formuna otel seçimi ekle
  - Kat listesi route'unda otel bilgisi göster
  - _Gereksinimler: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 5.1 Kat listesi template'ine otel kolonu ekle

  - templates/admin/kat_listesi.html'i güncelle
  - Otel adı kolonunu ekle
  - Otel filtreleme dropdown'u ekle (opsiyonel)
  - _Gereksinimler: 2.4_

- [x] 5.2 Kat ekleme formuna otel seçimi ekle

  - templates/admin/kat_ekle.html'i güncelle
  - Otel dropdown'u ekle (Select2 ile)
  - JavaScript validasyonu ekle


  - _Gereksinimler: 2.1, 2.2, 10.1, 10.2_


- [x] 5.3 Kat ekleme route'unu güncelle



  - admin_routes.py'deki kat_ekle fonksiyonunu güncelle
  - Form'dan otel_id al ve kaydet
  - Validasyon ekle (otel_id zorunlu)
  - _Gereksinimler: 2.3, 10.3_

- [x] 5.4 Kat düzenleme formuna otel seçimi ekle

  - templates/admin/kat_duzenle.html'i güncelle
  - Mevcut otel seçimini göster
  - Otel değiştirme imkanı sun
  - _Gereksinimler: 2.5_

- [x] 5.5 Kat düzenleme route'unu güncelle

  - admin_routes.py'deki kat_duzenle fonksiyonunu güncelle
  - Otel değişikliğini kaydet
  - Oda ilişkilerini kontrol et
  - _Gereksinimler: 2.5, 9.3_


- [ ] 6. Oda Yönetimi Güncellemeleri
  - Oda listesi template'ine otel kolonu ekle
  - Oda ekleme formuna hiyerarşik seçim ekle
  - Oda düzenleme formuna hiyerarşik seçim ekle
  - JavaScript dinamik kat yükleme ekle
  - _Gereksinimler: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6.1 Oda listesi template'ine otel kolonu ekle

  - templates/admin/oda_listesi.html'i güncelle
  - Otel ve Kat kolonlarını ekle
  - Otel filtreleme dropdown'u ekle
  - _Gereksinimler: 3.4_

- [x] 6.2 Oda ekleme formuna hiyerarşik seçim ekle

  - templates/admin/oda_ekle.html'i güncelle


  - Otel dropdown'u ekle (birinci seviye)
  - Kat dropdown'u ekle (ikinci seviye, başlangıçta disabled)
  - _Gereksinimler: 3.1, 3.2, 10.1_

- [x] 6.3 JavaScript dinamik kat yükleme ekle

  - static/js/oda_form.js oluştur
  - Otel seçildiğinde AJAX ile katları yükle
  - Kat dropdown'unu aktif et ve doldur

  - Loading spinner ekle
  - _Gereksinimler: 3.2, 10.2_


- [x] 6.4 Oda ekleme route'unu güncelle




  - admin_routes.py'deki oda_ekle fonksiyonunu güncelle
  - Form'dan otel_id ve kat_id al
  - Validasyon ekle (her iki alan zorunlu)
  - Kat'ın seçilen otele ait olduğunu kontrol et
  - _Gereksinimler: 3.3, 10.3_


- [x] 6.5 Oda düzenleme formunu güncelle





  - templates/admin/oda_duzenle.html'i güncelle
  - Mevcut otel ve kat seçimlerini göster
  - Değiştirme imkanı sun
  - _Gereksinimler: 3.5_

- [x] 6.6 Oda düzenleme route'unu güncelle



  - admin_routes.py'deki oda_duzenle fonksiyonunu güncelle
  - Otel ve kat değişikliklerini kaydet
  - İlişki kontrolü yap
  - _Gereksinimler: 3.5, 9.3_

- [x] 7. API Endpoint'leri


  - Otele ait katları getir endpoint'i
  - Otele ait odaları getir endpoint'i
  - Kata ait odaları getir endpoint'i
  - _Gereksinimler: 3.2, 6.3_


- [x] 7.1 Otele ait katları getir endpoint'i

  - api_routes.py'ye /api/oteller/<id>/katlar ekle
  - JSON formatında kat listesi döndür
  - Sadece aktif katları döndür
  - Yetki kontrolü ekle
  - _Gereksinimler: 3.2_

- [x] 7.2 Otele ait odaları getir endpoint'i

  - api_routes.py'ye /api/oteller/<id>/odalar ekle
  - JSON formatında oda listesi döndür
  - Kat bilgilerini de dahil et
  - _Gereksinimler: 6.3_

- [x] 7.3 Kata ait odaları getir endpoint'i

  - api_routes.py'ye /api/katlar/<id>/odalar ekle
  - JSON formatında oda listesi döndür
  - Sadece aktif odaları döndür
  - _Gereksinimler: 6.3_



- [ ] 8. Depo Sorumlusu Atama Güncellemeleri
  - Depo sorumlusu ekleme formuna çoklu otel seçimi ekle
  - Depo sorumlusu düzenleme formunu güncelle
  - Depo sorumlusu listesinde otel bilgilerini göster
  - KullaniciOtel kayıtlarını yönet
  - _Gereksinimler: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8.1 Depo sorumlusu ekleme formuna çoklu otel seçimi ekle

  - templates/admin/depo_sorumlusu_ekle.html'i güncelle
  - Multi-select dropdown ekle (Select2 ile)
  - En az bir otel seçimi zorunlu yap
  - _Gereksinimler: 5.1, 5.2, 10.1_



- [x] 8.2 Depo sorumlusu ekleme route'unu güncelle


  - admin_user_routes.py'deki depo_sorumlusu_ekle fonksiyonunu güncelle
  - Kullanıcı kaydını oluştur
  - Seçilen her otel için KullaniciOtel kaydı oluştur
  - Transaction kullan (hata durumunda rollback)
  - _Gereksinimler: 5.2, 5.5_

- [x] 8.3 Depo sorumlusu düzenleme formunu güncelle



  - templates/admin/depo_sorumlusu_duzenle.html'i güncelle
  - Mevcut otel atamalarını göster (pre-selected)
  - Otel ekleme/çıkarma imkanı sun
  - _Gereksinimler: 5.3_

- [x] 8.4 Depo sorumlusu düzenleme route'unu güncelle

  - admin_user_routes.py'deki depo_sorumlusu_duzenle fonksiyonunu güncelle
  - Mevcut KullaniciOtel kayıtlarını sil
  - Yeni seçimlere göre KullaniciOtel kayıtları oluştur
  - _Gereksinimler: 5.3_


- [x] 8.5 Depo sorumlusu listesinde otel bilgilerini göster



  - templates/admin/kullanici_listesi.html'i güncelle
  - Depo sorumluları için atanan otelleri göster
  - Çoklu otel varsa virgülle ayır veya badge kullan
  - _Gereksinimler: 5.4_

- [x] 9. Kat Sorumlusu Atama Güncellemeleri

  - Kat sorumlusu ekleme formuna tekli otel seçimi ekle
  - Kat sorumlusu düzenleme formunu güncelle
  - Kat sorumlusu listesinde otel bilgisini göster
  - _Gereksinimler: 6.1, 6.2, 6.3, 6.4, 6.5_


- [x] 9.1 Kat sorumlusu ekleme formuna tekli otel seçimi ekle


  - templates/admin/kat_sorumlusu_ekle.html'i güncelle
  - Dropdown ekle (Select2 ile)
  - Otel seçimi zorunlu yap
  - _Gereksinimler: 6.1, 6.2, 10.1_


- [x] 9.2 Kat sorumlusu ekleme route'unu güncelle

  - admin_user_routes.py'deki kat_sorumlusu_ekle fonksiyonunu güncelle
  - Kullanıcı kaydını oluştur
  - otel_id alanını kaydet
  - _Gereksinimler: 6.2, 6.5_


- [x] 9.3 Kat sorumlusu düzenleme formunu güncelle

  - templates/admin/kat_sorumlusu_duzenle.html'i güncelle
  - Mevcut otel seçimini göster
  - Otel değiştirme imkanı sun
  - _Gereksinimler: 6.3_


- [x] 9.4 Kat sorumlusu düzenleme route'unu güncelle


  - admin_user_routes.py'deki kat_sorumlusu_duzenle fonksiyonunu güncelle
  - otel_id güncellemesini kaydet
  - _Gereksinimler: 6.3_


- [x] 9.5 Kat sorumlusu listesinde otel bilgisini göster



  - templates/admin/kullanici_listesi.html'i güncelle
  - Kat sorumluları için atanan oteli göster
  - _Gereksinimler: 6.4_

- [x] 10. Yetkilendirme ve Filtreleme


  - Yetkilendirme helper fonksiyonları oluştur
  - Decorator'lar oluştur
  - Depo sorumlusu sayfalarına filtreleme ekle
  - Kat sorumlusu sayfalarına filtreleme ekle
  - _Gereksinimler: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_




- [x] 10.1 Yetkilendirme helper fonksiyonları oluştur


  - utils/authorization.py dosyası oluştur
  - get_depo_sorumlusu_oteller() fonksiyonu yaz
  - depo_sorumlusu_otel_erisimi() fonksiyonu yaz
  - get_kat_sorumlusu_otel() fonksiyonu yaz

  - kat_sorumlusu_otel_erisimi() fonksiyonu yaz
  - _Gereksinimler: 7.1, 7.2, 8.1, 8.2_


- [x] 10.2 Otel erişim decorator'u oluştur




  - utils/decorators.py dosyasına otel_erisim_gerekli decorator'u ekle
  - Rol bazlı erişim kontrolü yap
  - 403 hatası döndür (yetkisiz erişim)
  - _Gereksinimler: 7.3, 7.4, 7.5, 8.3, 8.4, 8.5_

- [x] 10.3 Depo sorumlusu route'larına filtreleme ekle


  - depo_routes.py'deki tüm route'ları güncelle
  - Sadece atanan otellerin verilerini göster
  - Otel filtreleme dropdown'u ekle
  - Query'lere otel_id filtresi ekle
  - _Gereksinimler: 7.2, 7.3, 7.4_


- [x] 10.4 Kat sorumlusu route'larına filtreleme ekle

  - kat_sorumlusu_routes.py'deki tüm route'ları güncelle
  - Sadece atanan otelin verilerini göster
  - Query'lere otel_id filtresi ekle
  - _Gereksinimler: 8.2, 8.3, 8.4_

- [x] 10.5 Stok ve zimmet işlemlerine otel bilgisi ekle

  - StokHareket kayıtlarına otel_id ekle (opsiyonel)
  - PersonelZimmet kayıtlarına otel_id ekle (opsiyonel)
  - Raporlarda otel bazlı gruplama ekle
  - _Gereksinimler: 7.5, 9.4, 9.5_

- [x] 11. Hata Yönetimi ve Validasyonlar

  - Form validasyonları ekle
  - Silme korumaları ekle
  - Hata mesajları ekle
  - Try-catch blokları ekle
  - _Gereksinimler: 9.1, 9.2, 9.3, 10.3, 10.4_

- [x] 11.1 Form validasyonları ekle


  - Tüm formlarda otel seçimi zorunluluğunu kontrol et
  - Kat-Otel ilişkisi kontrolü ekle
  - Oda-Kat-Otel ilişkisi kontrolü ekle
  - Flash mesajları ile kullanıcıyı bilgilendir
  - _Gereksinimler: 10.3, 10.4_

- [x] 11.2 Otel silme korumaları ekle


  - Otele ait kat varsa silmeyi engelle
  - Otele atanmış personel varsa silmeyi engelle
  - Uyarı mesajları göster
  - Aktif/pasif yapma öner
  - _Gereksinimler: 9.1, 9.2_

- [x] 11.3 Kat silme korumaları güncelle

  - Kata ait oda varsa silmeyi engelle
  - Uyarı mesajı göster
  - _Gereksinimler: 9.3_

- [x] 11.4 Try-catch blokları ekle


  - Tüm database işlemlerine try-catch ekle
  - Hata durumunda rollback yap
  - Log kayıtları oluştur
  - Kullanıcıya anlamlı hata mesajı göster
  - _Gereksinimler: 10.3, 10.4_

- [x] 12. UI/UX İyileştirmeleri


  - Select2 kütüphanesini entegre et
  - Loading spinner'ları ekle
  - Responsive tasarım kontrolleri
  - Türkçe mesajlar ve placeholder'lar
  - _Gereksinimler: 10.1, 10.2, 10.5_

- [x] 12.1 Select2 kütüphanesini entegre et


  - static/js/select2.min.js ve CSS dosyalarını ekle
  - base.html'e script ve style linklerini ekle
  - Tüm otel dropdown'larına Select2 uygula
  - Arama özelliğini aktif et
  - _Gereksinimler: 10.1_


- [x] 12.2 Loading spinner'ları ekle

  - AJAX istekleri sırasında loading göster
  - Form submit sırasında buton'u disable et
  - "Yükleniyor..." mesajı göster
  - _Gereksinimler: 10.2_

- [x] 12.3 Türkçe mesajlar ve placeholder'lar ekle


  - Tüm dropdown'lara "Otel Seçin..." placeholder'ı ekle
  - Hata mesajlarını Türkçeleştir
  - Başarı mesajlarını Türkçeleştir
  - _Gereksinimler: 10.4, 10.5_

- [x] 13. Test ve Doğrulama



  - Migration script'ini test et
  - Tüm formları test et
  - Yetkilendirme kontrollerini test et
  - Edge case'leri test et
  - _Gereksinimler: Tüm gereksinimler_









- [x] 13.1 Migration script'ini test et



  - Development ortamında migration'ı çalıştır
  - Merit Royal Diamond otelinin oluştuğunu doğrula
  - Tüm katların otele atandığını doğrula
  - Tüm kullanıcıların otele atandığını doğrula
  - _Gereksinimler: 4.1, 4.2, 4.3, 4.4, 4.5_


- [x] 13.2 Otel CRUD işlemlerini test et

  - Yeni otel eklemeyi test et
  - Otel düzenlemeyi test et
  - Otel aktif/pasif yapmayı test et
  - Silme korumasını test et
  - _Gereksinimler: 1.1, 1.2, 1.3, 1.4, 1.5_


- [x] 13.3 Kat ve Oda işlemlerini test et

  - Otel seçerek kat eklemeyi test et
  - Otel ve kat seçerek oda eklemeyi test et
  - Dinamik kat yüklemeyi test et
  - Hiyerarşik ilişkileri test et
  - _Gereksinimler: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_


- [x] 13.4 Kullanıcı atamalarını test et

  - Depo sorumlusuna çoklu otel atamasını test et
  - Kat sorumlusuna tekli otel atamasını test et
  - Atama düzenlemeyi test et
  - _Gereksinimler: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3_


- [x] 13.5 Yetkilendirme kontrollerini test et

  - Depo sorumlusunun sadece atanan otellere erişebildiğini test et
  - Kat sorumlusunun sadece kendi oteline erişebildiğini test et
  - Yetkisiz erişim denemelerini test et (403 hatası)
  - _Gereksinimler: 7.1, 7.2, 7.3, 7.4, 7.5, 8.1, 8.2, 8.3, 8.4, 8.5_

---

## Notlar

- Her görev tamamlandıkında checkbox işaretlenecek
- Görevler sırayla yapılmalı (bağımlılıklar var)
- Test görevleri opsiyonel değil, mutlaka yapılmalı
- Hata durumunda önceki görevlere dönülebilir
