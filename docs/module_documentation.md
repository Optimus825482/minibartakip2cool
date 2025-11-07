# Route Modülleri Dokümantasyonu

## Genel Bakış
Bu dokümantasyon, tüm route modüllerinin sorumluluklarını, endpoint'lerini ve rol gereksinimlerini açıklar.

---

## 1. routes/auth_routes.py

### Sorumluluk
Kullanıcı kimlik doğrulama ve oturum yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/` | GET | index | Ana sayfa yönlendirmesi |
| `/setup` | GET, POST | setup | İlk sistem kurulumu |
| `/login` | GET, POST | login | Kullanıcı girişi |
| `/logout` | GET | logout | Kullanıcı çıkışı |

### Roller
- Herkese açık (setup, login)
- Giriş yapmış kullanıcılar (logout)

### Bağımlılıklar
- forms.LoginForm, SetupForm
- models.Kullanici, Otel
- utils.decorators
- utils.audit

---

## 2. routes/dashboard_routes.py

### Sorumluluk
Rol bazlı dashboard yönlendirmeleri ve görüntüleme

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/dashboard` | GET | dashboard | Rol bazlı yönlendirme |
| `/sistem-yoneticisi` | GET | sistem_yoneticisi_dashboard | Sistem yöneticisi paneli |
| `/depo` | GET | depo_dashboard | Depo sorumlusu paneli |
| `/kat-sorumlusu` | GET | kat_sorumlusu_dashboard | Kat sorumlusu paneli |
| `/kat-sorumlusu/dashboard` | GET | kat_sorumlusu_dashboard | Alternatif route |

### Roller
- sistem_yoneticisi
- admin
- depo_sorumlusu
- kat_sorumlusu

### Bağımlılıklar
- models (tüm modeller)
- utils.helpers (stok, log fonksiyonları)

---

## 3. routes/sistem_yoneticisi_routes.py

### Sorumluluk
Otel, kat ve oda yönetimi işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/otel-tanimla` | GET, POST | otel_tanimla | Otel bilgilerini tanımla |
| `/kat-tanimla` | GET, POST | kat_tanimla | Yeni kat ekle |
| `/kat-duzenle/<int:kat_id>` | GET, POST | kat_duzenle | Kat bilgilerini düzenle |
| `/kat-sil/<int:kat_id>` | POST | kat_sil | Kat sil |
| `/oda-tanimla` | GET, POST | oda_tanimla | Yeni oda ekle |
| `/oda-duzenle/<int:oda_id>` | GET, POST | oda_duzenle | Oda bilgilerini düzenle |
| `/oda-sil/<int:oda_id>` | POST | oda_sil | Oda sil |
| `/sistem-loglari` | GET | sistem_loglari | Sistem loglarını görüntüle |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- forms (OtelForm, KatForm, OdaForm)
- models (Otel, Kat, Oda)
- utils.audit

---

## 4. routes/admin_routes.py

### Sorumluluk
Personel, ürün grubu ve ürün yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/personel-tanimla` | GET, POST | personel_tanimla | Yeni personel ekle |
| `/personel-duzenle/<int:personel_id>` | GET, POST | personel_duzenle | Personel düzenle |
| `/personel-pasif-yap/<int:personel_id>` | POST | personel_pasif_yap | Personel pasif yap |
| `/personel-aktif-yap/<int:personel_id>` | POST | personel_aktif_yap | Personel aktif yap |
| `/urun-gruplari` | GET, POST | urun_gruplari | Ürün grupları yönetimi |
| `/grup-duzenle/<int:grup_id>` | GET, POST | grup_duzenle | Grup düzenle |
| `/grup-sil/<int:grup_id>` | POST | grup_sil | Grup sil |
| `/grup-pasif-yap/<int:grup_id>` | POST | grup_pasif_yap | Grup pasif yap |
| `/grup-aktif-yap/<int:grup_id>` | POST | grup_aktif_yap | Grup aktif yap |
| `/urunler` | GET, POST | urunler | Ürün yönetimi |
| `/urun-duzenle/<int:urun_id>` | GET, POST | urun_duzenle | Ürün düzenle |
| `/urun-sil/<int:urun_id>` | POST | urun_sil | Ürün sil |
| `/urun-pasif-yap/<int:urun_id>` | POST | urun_pasif_yap | Ürün pasif yap |
| `/urun-aktif-yap/<int:urun_id>` | POST | urun_aktif_yap | Ürün aktif yap |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- forms (PersonelForm, UrunGrupForm, UrunForm)
- models (Kullanici, UrunGrup, Urun)
- utils.audit

---

## 5. routes/admin_minibar_routes.py

### Sorumluluk
Admin minibar işlemleri ve stok yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/admin/depo-stoklari` | GET | admin_depo_stoklari | Depo stok durumu |
| `/admin/oda-minibar-stoklari` | GET | admin_oda_minibar_stoklari | Oda minibar stokları |
| `/admin/oda-minibar-detay/<int:oda_id>` | GET | admin_oda_minibar_detay | Oda minibar detayı |
| `/admin/minibar-sifirla` | POST | admin_minibar_sifirla | Minibar sıfırlama |
| `/admin/minibar-islemleri` | GET | admin_minibar_islemleri | Minibar işlem listesi |
| `/admin/minibar-islem-sil/<int:islem_id>` | POST | admin_minibar_islem_sil | Minibar işlem sil |
| `/admin/minibar-durumlari` | GET | admin_minibar_durumlari | Minibar durumları |
| `/api/minibar-islem-detay/<int:islem_id>` | GET | api_minibar_islem_detay | İşlem detayı (JSON) |
| `/api/admin/verify-password` | POST | api_admin_verify_password | Şifre doğrulama (JSON) |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- models (MinibarIslem, MinibarIslemDetay, Oda, Urun)
- utils.helpers

---

## 6. routes/admin_stok_routes.py

### Sorumluluk
Admin stok girişi ve stok hareketleri yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/admin/stok-giris` | GET, POST | admin_stok_giris | Stok girişi |
| `/admin/stok-hareketleri` | GET | admin_stok_hareketleri | Stok hareketleri listesi |
| `/admin/stok-hareket-duzenle/<int:hareket_id>` | GET, POST | admin_stok_hareket_duzenle | Stok hareket düzenle |
| `/admin/stok-hareket-sil/<int:hareket_id>` | POST | admin_stok_hareket_sil | Stok hareket sil |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- forms.StokGirisForm
- models (StokHareket, Urun)
- utils.audit

---

## 7. routes/admin_zimmet_routes.py

### Sorumluluk
Personel zimmet yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/admin/personel-zimmetleri` | GET | admin_personel_zimmetleri | Zimmet listesi |
| `/admin/zimmet-detay/<int:zimmet_id>` | GET | admin_zimmet_detay | Zimmet detayı |
| `/admin/zimmet-iade/<int:zimmet_id>` | POST | admin_zimmet_iade | Zimmet iade |
| `/admin/zimmet-iptal/<int:zimmet_id>` | POST | admin_zimmet_iptal | Zimmet iptal |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- models (PersonelZimmet, PersonelZimmetDetay)
- utils.audit

---

## 8. routes/depo_routes.py

### Sorumluluk
Depo sorumlusu stok ve zimmet işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/stok-giris` | GET, POST | stok_giris | Depo stok girişi |
| `/stok-duzenle/<int:hareket_id>` | GET, POST | stok_duzenle | Stok hareket düzenle |
| `/stok-sil/<int:hareket_id>` | POST | stok_sil | Stok hareket sil |
| `/personel-zimmet` | GET, POST | personel_zimmet | Personel zimmet oluştur |

### Roller
- depo_sorumlusu

### Bağımlılıklar
- forms (StokGirisForm, PersonelZimmetForm)
- models (StokHareket, PersonelZimmet)
- utils.audit

---

## 9. routes/admin_qr_routes.py

### Sorumluluk
QR kod oluşturma ve yönetimi

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/admin/oda-qr-olustur/<int:oda_id>` | POST | admin_oda_qr_olustur | Oda için QR oluştur |
| `/admin/toplu-qr-olustur` | POST | admin_toplu_qr_olustur | Toplu QR oluştur |
| `/admin/oda-qr-goruntule/<int:oda_id>` | GET | admin_oda_qr_goruntule | QR görüntüle |
| `/admin/oda-qr-indir/<int:oda_id>` | GET | admin_oda_qr_indir | QR indir |
| `/admin/toplu-qr-indir` | GET | admin_toplu_qr_indir | Toplu QR indir |
| `/admin/oda-misafir-mesaji/<int:oda_id>` | GET, POST | admin_oda_misafir_mesaji | Misafir mesajı |
| `/qr/<token>` | GET | qr_redirect | QR yönlendirme |

### Roller
- sistem_yoneticisi
- admin

### Bağımlılıklar
- qrcode
- models (Oda, OdaQR)

---

## 10. routes/kat_sorumlusu_qr_routes.py

### Sorumluluk
Kat sorumlusu QR okutma işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/kat-sorumlusu/qr-okut` | GET, POST | kat_sorumlusu_qr_okut | QR okutma sayfası |
| `/api/kat-sorumlusu/qr-parse` | POST | api_kat_sorumlusu_qr_parse | QR parse (JSON) |

### Roller
- kat_sorumlusu

### Bağımlılıklar
- models (Oda, OdaQR)

---

## 11. routes/kat_sorumlusu_ilk_dolum_routes.py

### Sorumluluk
Kat sorumlusu ilk dolum işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/api/kat-sorumlusu/ilk-dolum-kontrol/<int:oda_id>/<int:urun_id>` | GET | api_ilk_dolum_kontrol | İlk dolum kontrolü |
| `/api/kat-sorumlusu/ek-dolum` | POST | api_ek_dolum | Ek dolum |
| `/api/kat-sorumlusu/ilk-dolum` | POST | api_ilk_dolum | İlk dolum |

### Roller
- kat_sorumlusu

### Bağımlılıklar
- models (MinibarIslem, MinibarIslemDetay)
- utils.helpers

---

## 12. routes/kat_sorumlusu_routes.py ✨ YENİ

### Sorumluluk
Kat sorumlusu genel işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/dolum-talepleri` | GET | dolum_talepleri | Dolum talepleri sayfası |
| `/minibar-kontrol` | GET, POST | minibar_kontrol | Minibar kontrol işlemleri |
| `/kat-odalari` | GET | kat_odalari | Kata göre oda listesi (JSON) |
| `/minibar-urunler` | GET | minibar_urunler | Minibar ürünleri (JSON) |
| `/toplu-oda-doldurma` | GET | toplu_oda_doldurma | Toplu oda doldurma sayfası |
| `/kat-bazli-rapor` | GET | kat_bazli_rapor | Kat bazlı rapor |
| `/zimmetim` | GET | zimmetim | Zimmet görüntüleme |
| `/kat-raporlar` | GET | kat_raporlar | Kat sorumlusu raporları |

### Roller
- kat_sorumlusu
- admin (bazı raporlar için)
- depo_sorumlusu (bazı raporlar için)

### Bağımlılıklar
- models (Kat, Oda, Urun, PersonelZimmet, MinibarIslem)
- utils.helpers
- utils.audit

---

## 13. routes/misafir_qr_routes.py

### Sorumluluk
Misafir dolum talebi işlemleri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/misafir/dolum-talebi/<token>` | GET, POST | misafir_dolum_talebi | Misafir dolum talebi |

### Roller
- Herkese açık (token ile)

### Bağımlılıklar
- models (DolumTalebi, Oda)

---

## 14. routes/dolum_talebi_routes.py

### Sorumluluk
Dolum talebi yönetimi ve API

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/api/dolum-talepleri` | GET | api_dolum_talepleri | Dolum talepleri listesi |
| `/api/dolum-talebi-tamamla/<int:talep_id>` | POST | api_dolum_talebi_tamamla | Talep tamamla |
| `/api/dolum-talebi-iptal/<int:talep_id>` | POST | api_dolum_talebi_iptal | Talep iptal |
| `/api/dolum-talepleri-admin` | GET | api_dolum_talepleri_admin | Admin dolum talepleri |
| `/api/dolum-talepleri-istatistik` | GET | api_dolum_talepleri_istatistik | İstatistikler |

### Roller
- kat_sorumlusu
- admin
- sistem_yoneticisi

### Bağımlılıklar
- models (DolumTalebi)

---

## 15. routes/api_routes.py

### Sorumluluk
Genel API endpoint'leri

### Endpoint'ler
| Route | Method | Fonksiyon | Açıklama |
|-------|--------|-----------|----------|
| `/api/odalar` | GET | api_odalar | Tüm odalar |
| `/api/odalar-by-kat/<int:kat_id>` | GET | odalar_by_kat | Kata göre odalar |
| `/api/urun-gruplari` | GET | api_urun_gruplari | Ürün grupları |
| `/api/urunler` | GET | api_urunler | Tüm ürünler |
| `/api/urunler-by-grup/<int:grup_id>` | GET | urunler_by_grup | Gruba göre ürünler |
| `/api/stok-giris` | POST | api_stok_giris | Stok girişi |
| `/api/minibar-islem-kaydet` | POST | api_minibar_islem_kaydet | Minibar işlem kaydet |
| `/api/minibar-ilk-dolum` | POST | api_minibar_ilk_dolum | İlk dolum |
| `/api/minibar-ilk-dolum-kontrol/<int:oda_id>` | GET | api_minibar_ilk_dolum_kontrol | İlk dolum kontrol |
| `/api/urun-stok/<int:urun_id>` | GET | urun_stok | Ürün stok bilgisi |
| `/api/zimmetim` | GET | api_zimmetim | Zimmet bilgileri |
| `/api/minibar-icerigi/<int:oda_id>` | GET | api_minibar_icerigi | Minibar içeriği |
| `/api/minibar-doldur` | POST | api_minibar_doldur | Minibar doldur |
| `/api/toplu-oda-mevcut-durum` | POST | api_toplu_oda_mevcut_durum | Toplu oda durum |
| `/api/toplu-oda-doldur` | POST | api_toplu_oda_doldur | Toplu oda doldur |
| `/api/kat-rapor-veri` | GET | api_kat_rapor_veri | Kat rapor verisi |

### Roller
- sistem_yoneticisi
- admin
- depo_sorumlusu
- kat_sorumlusu

### Bağımlılıklar
- models (tüm modeller)
- utils.helpers
- utils.audit

---

## 16. routes/error_handlers.py

### Sorumluluk
Hata yönetimi ve error handler'lar

### Error Handler'lar
- 429 - Rate limit hatası
- CSRFError - CSRF doğrulama hatası

### Roller
- Tüm kullanıcılar

---

## 17. routes/__init__.py

### Sorumluluk
Merkezi route registration

### Fonksiyon
```python
register_all_routes(app)
```

Tüm route modüllerini sırayla register eder:
1. error_handlers
2. auth_routes
3. dashboard_routes
4. sistem_yoneticisi_routes
5. admin_routes
6. admin_minibar_routes
7. admin_stok_routes
8. admin_zimmet_routes
9. depo_routes
10. admin_qr_routes
11. kat_sorumlusu_qr_routes
12. kat_sorumlusu_ilk_dolum_routes
13. kat_sorumlusu_routes
14. misafir_qr_routes
15. dolum_talebi_routes
16. api_routes

---

## 📊 İstatistikler

### Modül Başına Route Sayısı
```
auth_routes.py: 4
dashboard_routes.py: 5
sistem_yoneticisi_routes.py: 8
admin_routes.py: 15
admin_minibar_routes.py: 10
admin_stok_routes.py: 4
admin_zimmet_routes.py: 4
depo_routes.py: 4
admin_qr_routes.py: 7
kat_sorumlusu_qr_routes.py: 2
kat_sorumlusu_ilk_dolum_routes.py: 3
kat_sorumlusu_routes.py: 10
misafir_qr_routes.py: 1
dolum_talebi_routes.py: 5
api_routes.py: 14
error_handlers.py: 2
---
Toplam: 94 route (modüllerde)
app.py: 30 route (kalan)
---
GENEL TOPLAM: 124 route
```

### Rol Bazlı Dağılım
- **sistem_yoneticisi**: 35+ route
- **admin**: 50+ route
- **depo_sorumlusu**: 20+ route
- **kat_sorumlusu**: 30+ route
- **Herkese açık**: 5 route

---

## 🎯 Yeni Endpoint Ekleme Prosedürü

### 1. Uygun Modülü Seç
Route'un sorumluluğuna göre ilgili modülü seç:
- Auth işlemleri → `auth_routes.py`
- Admin işlemleri → `admin_routes.py`
- API endpoint'leri → `api_routes.py`
- vb.

### 2. Route Ekle
```python
@app.route('/yeni-endpoint')
@login_required
@role_required('rol_adi')
def yeni_endpoint():
    """Endpoint açıklaması"""
    try:
        # İşlem mantığı
        pass
    except Exception as e:
        log_hata(e, modul='modul_adi')
        flash('Hata mesajı', 'danger')
        return redirect(url_for('fallback'))
```

### 3. Test Et
```bash
python -c "from app import app; print('✅ Flask çalışıyor')"
```

### 4. Dokümante Et
Bu dosyayı güncelle ve endpoint'i ekle.

---

**Dokümantasyon Tarihi**: 2024-11-08  
**Toplam Modül**: 17  
**Toplam Route**: 124  
**Durum**: ✅ GÜNCEL
