# Yapılacaklar Listesi

## Kritik

- [x] `zimmet_iptal` ve `zimmet_iade` akışlarında eksik `current_user` kullanımını gider (Flask-Login entegre et veya `get_current_user` ile kullanıcıyı al, None kontrolleri ekle)
- [x] WTForms doğrulayıcılarının çalışmasını sağlayacak validatör fonksiyonları uygula (lambda yerine fonksiyon/`ValidationError` raise) ve kullanıcı adı/e-posta/şifre kontrollerini gözden geçir
- [x] `SECRET_KEY` yapılandırmasını düzelt (development/test fallback mantığını netleştir; production’da güvenli anahtar, development’ta otomatik değer ve hata fırlatma senaryosu)

## Önemli

- [x] Stok hesaplamalarını optimize et (`get_toplam_stok`, `get_stok_durumu`, dashboard/rapor sorgularını aggregate + `GROUP BY` ile tek sorguya indir)
- [x] Zimmet atama işlemlerinde depo stok kontrolü ekle; yetersiz stok için uygun uyarı/engelleme senaryosu uygula
- [x] Session güvenliğini güçlendir (`session.clear()` sonrası login, production’da `SESSION_COOKIE_SECURE=True` için yönerge)

## İyileştirme Önerileri

- [ ] Uygulamayı blueprint’lere bölerek modüler hale getir
- [ ] Ortak validator helper fonksiyonları oluştur ve formlarda kullan
- [ ] Ağır raporlama operasyonlarını background job yapısına taşı (örn. Celery/RQ)
- [ ] Kritik akışlar için Flask testleri yaz (login, zimmet iptal/iade, form validasyonları)
- [ ] Production konfigürasyonu otomatikleştir (SECRET_KEY, HTTPS, cookie ayarları için CI/CD adımları)
