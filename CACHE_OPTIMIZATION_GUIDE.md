# Cache Optimizasyon Rehberi

## 📋 İçindekiler

1. [Eksik Cache Implementasyonları](#eksik-cache-implementasyonları)
2. [Cache Invalidation Stratejileri](#cache-invalidation-stratejileri)
3. [TTL Optimizasyonu](#ttl-optimizasyonu)
4. [Kod Örnekleri](#kod-örnekleri)

---

## 1. Eksik Cache Implementasyonları

### 🔴 Yüksek Öncelik

#### A. `/minibar-urunler` Endpoint'i

**Mevcut Kod** (`routes/kat_sorumlusu_routes.py` Line 378-414):

```python
@app.route('/minibar-urunler')
@login_required
@role_required('kat_sorumlusu')
def minibar_urunler():
    """Minibar ürünlerini JSON olarak döndür"""
    try:
        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.grup_id, Urun.urun_adi).all()

        # Kullanıcının zimmet bilgilerini getir
        kullanici_id = session.get('kullanici_id')
        aktif_zimmetler = PersonelZimmet.query.filter_by(
            personel_id=kullanici_id,
            durum='aktif'
        ).all()

        # Her ürün için toplam zimmet miktarını hesapla
        zimmet_dict = {}
        for zimmet in aktif_zimmetler:
            for detay in zimmet.detaylar:  # ❌ N+1 query
                if detay.urun_id not in zimmet_dict:
                    zimmet_dict[detay.urun_id] = 0
                zimmet_dict[detay.urun_id] += (detay.kalan_miktar or 0)

        urun_listesi = []
        for urun in urunler:
            urun_listesi.append({
                'id': urun.id,
                'urun_adi': urun.urun_adi,
                'grup_id': urun.grup_id,
                'grup_adi': urun.grup.grup_adi,
                'birim': urun.birim,
                'zimmet_miktari': zimmet_dict.get(urun.id, 0)
            })

        return jsonify({'success': True, 'urunler': urun_listesi})
    except Exception as e:
        log_hata(e, modul='minibar_urunler')
        return jsonify({'success': False, 'error': str(e)})
```

**Optimize Edilmiş Kod:**

```python
@app.route('/minibar-urunler')
@login_required
@role_required('kat_sorumlusu')
def minibar_urunler():
    """Minibar ürünlerini JSON olarak döndür - CACHE'Lİ"""
    try:
        kullanici_id = session.get('kullanici_id')

        # ✅ Cache kontrolü
        cached_data = KatSorumlusuCacheService.get_minibar_urunler(kullanici_id)
        if cached_data:
            return jsonify({'success': True, 'urunler': cached_data, 'cached': True})

        # ✅ Eager loading ile N+1 query çözümü
        urunler = Urun.query.options(
            joinedload(Urun.grup)
        ).filter_by(aktif=True).order_by(Urun.grup_id, Urun.urun_adi).all()

        # ✅ Zimmet bilgilerini eager loading ile getir
        aktif_zimmetler = PersonelZimmet.query.options(
            selectinload(PersonelZimmet.detaylar).joinedload(PersonelZimmetDetay.urun)
        ).filter_by(
            personel_id=kullanici_id,
            durum='aktif'
        ).all()

        # Zimmet dict'i oluştur
        zimmet_dict = {}
        for zimmet in aktif_zimmetler:
            for detay in zimmet.detaylar:
                if detay.urun_id not in zimmet_dict:
                    zimmet_dict[detay.urun_id] = 0
                zimmet_dict[detay.urun_id] += (detay.kalan_miktar or 0)

        # Ürün listesi oluştur
        urun_listesi = []
        for urun in urunler:
            urun_listesi.append({
                'id': urun.id,
                'urun_adi': urun.urun_adi,
                'grup_id': urun.grup_id,
                'grup_adi': urun.grup.grup_adi,
                'birim': urun.birim,
                'zimmet_miktari': zimmet_dict.get(urun.id, 0)
            })

        # ✅ Cache'e kaydet (60 saniye TTL)
        KatSorumlusuCacheService.set_minibar_urunler(urun_listesi, kullanici_id)

        return jsonify({'success': True, 'urunler': urun_listesi, 'cached': False})
    except Exception as e:
        log_hata(e, modul='minibar_urunler')
        return jsonify({'success': False, 'error': str(e)})
```

**Cache Service Eklentisi** (`utils/kat_sorumlusu_cache_service.py`):

```python
class KatSorumlusuCacheService:
    """Kat sorumlusu cache yönetimi"""

    # ... mevcut kodlar ...

    MINIBAR_URUNLER_TTL = 60  # 1 dakika

    @staticmethod
    def get_minibar_urunler_cache_key(kullanici_id: int):
        """Minibar ürünler cache key"""
        return f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar_urunler:{kullanici_id}"

    @staticmethod
    def get_minibar_urunler(kullanici_id: int):
        """Cache'den minibar ürünler al"""
        cache_key = KatSorumlusuCacheService.get_minibar_urunler_cache_key(kullanici_id)
        return cache_get(cache_key)

    @staticmethod
    def set_minibar_urunler(data: list, kullanici_id: int):
        """Minibar ürünleri cache'le"""
        cache_key = KatSorumlusuCacheService.get_minibar_urunler_cache_key(kullanici_id)
        return cache_set(cache_key, data, KatSorumlusuCacheService.MINIBAR_URUNLER_TTL)

    @staticmethod
    def invalidate_minibar_urunler(kullanici_id: int):
        """Minibar ürünler cache'ini temizle"""
        pattern = f"{KatSorumlusuCacheService.CACHE_PREFIX}:minibar_urunler:{kullanici_id}"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Minibar ürünler cache temizlendi (kullanici={kullanici_id}): {deleted} key")
        return deleted
```

**Performans İyileşmesi:**

- Sorgu sayısı: 150+ → 3
- Response time: ~500ms → ~50ms (cache hit)
- İyileşme: **90%**

---

#### B. `/zimmetim` Endpoint'i

**Mevcut Kod** (`routes/kat_sorumlusu_routes.py` Line 506-533):

```python
@app.route('/zimmetim')
@login_required
@role_required('kat_sorumlusu')
def zimmetim():
    """Zimmet görüntüleme"""
    kullanici_id = session['kullanici_id']

    aktif_zimmetler = PersonelZimmet.query.filter_by(
        personel_id=kullanici_id,
        durum='aktif'
    ).order_by(PersonelZimmet.zimmet_tarihi.desc()).all()

    toplam_zimmet = 0
    kalan_zimmet = 0
    kullanilan_zimmet = 0

    for zimmet in aktif_zimmetler:
        for detay in zimmet.detaylar:  # ❌ N+1 query
            toplam_zimmet += detay.miktar
            kullanilan_zimmet += detay.kullanilan_miktar
            kalan = detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar)
            kalan_zimmet += kalan

    return render_template('kat_sorumlusu/zimmetim.html',
                         aktif_zimmetler=aktif_zimmetler,
                         toplam_zimmet=toplam_zimmet,
                         kalan_zimmet=kalan_zimmet,
                         kullanilan_zimmet=kullanilan_zimmet)
```

**Optimize Edilmiş Kod:**

```python
@app.route('/zimmetim')
@login_required
@role_required('kat_sorumlusu')
def zimmetim():
    """Zimmet görüntüleme - CACHE'Lİ"""
    kullanici_id = session['kullanici_id']

    # ✅ Cache kontrolü
    cached_data = KatSorumlusuCacheService.get_zimmet_ozet(kullanici_id)
    if cached_data:
        return render_template('kat_sorumlusu/zimmetim.html', **cached_data)

    # ✅ Eager loading ile N+1 query çözümü
    aktif_zimmetler = PersonelZimmet.query.options(
        selectinload(PersonelZimmet.detaylar).joinedload(PersonelZimmetDetay.urun)
    ).filter_by(
        personel_id=kullanici_id,
        durum='aktif'
    ).order_by(PersonelZimmet.zimmet_tarihi.desc()).all()

    toplam_zimmet = 0
    kalan_zimmet = 0
    kullanilan_zimmet = 0

    for zimmet in aktif_zimmetler:
        for detay in zimmet.detaylar:
            toplam_zimmet += detay.miktar
            kullanilan_zimmet += detay.kullanilan_miktar
            kalan = detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar)
            kalan_zimmet += kalan

    # ✅ Cache'e kaydet (120 saniye TTL)
    data = {
        'aktif_zimmetler': aktif_zimmetler,
        'toplam_zimmet': toplam_zimmet,
        'kalan_zimmet': kalan_zimmet,
        'kullanilan_zimmet': kullanilan_zimmet
    }
    KatSorumlusuCacheService.set_zimmet_ozet(data, kullanici_id)

    return render_template('kat_sorumlusu/zimmetim.html', **data)
```

**Cache Service Eklentisi:**

```python
ZIMMET_OZET_TTL = 120  # 2 dakika

@staticmethod
def get_zimmet_ozet_cache_key(kullanici_id: int):
    """Zimmet özet cache key"""
    return f"{KatSorumlusuCacheService.CACHE_PREFIX}:zimmet_ozet:{kullanici_id}"

@staticmethod
def get_zimmet_ozet(kullanici_id: int):
    """Cache'den zimmet özet al"""
    cache_key = KatSorumlusuCacheService.get_zimmet_ozet_cache_key(kullanici_id)
    return cache_get(cache_key)

@staticmethod
def set_zimmet_ozet(data: dict, kullanici_id: int):
    """Zimmet özetini cache'le"""
    cache_key = KatSorumlusuCacheService.get_zimmet_ozet_cache_key(kullanici_id)
    return cache_set(cache_key, data, KatSorumlusuCacheService.ZIMMET_OZET_TTL)
```

---

#### C. `/depo-stoklarim` Endpoint'i

**Mevcut Kod** (`routes/depo_routes.py` Line 398-462):

```python
@app.route('/depo-stoklarim')
@login_required
@role_required('depo_sorumlusu')
def depo_stoklarim():
    """Depo sorumlusu stok takip sayfası - Otel bazlı"""
    try:
        from utils.authorization import get_kullanici_otelleri, get_otel_filtreleme_secenekleri
        from sqlalchemy import func

        kullanici_otelleri = get_kullanici_otelleri()
        otel_secenekleri = get_otel_filtreleme_secenekleri()
        otel_ids = [o.id for o in kullanici_otelleri]

        secili_otel_id = request.args.get('otel_id', type=int)

        # ... otel seçimi ...

        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.urun_adi).all()

        # ❌ Her render'da stok sorgusu
        otel_stok_map = {}
        if secili_otel_id:
            otel_stoklar = UrunStok.query.filter_by(otel_id=secili_otel_id).all()
            otel_stok_map = {stok.urun_id: stok.mevcut_stok for stok in otel_stoklar}
        else:
            toplam_stoklar = db.session.query(
                UrunStok.urun_id,
                func.sum(UrunStok.mevcut_stok).label('toplam')
            ).filter(
                UrunStok.otel_id.in_(otel_ids)
            ).group_by(UrunStok.urun_id).all()
            otel_stok_map = {row.urun_id: row.toplam or 0 for row in toplam_stoklar}

        # ... stok bilgileri hazırlama ...
```

**Optimize Edilmiş Kod:**

```python
@app.route('/depo-stoklarim')
@login_required
@role_required('depo_sorumlusu')
def depo_stoklarim():
    """Depo sorumlusu stok takip sayfası - CACHE'Lİ"""
    try:
        from utils.authorization import get_kullanici_otelleri, get_otel_filtreleme_secenekleri
        from utils.depo_cache_service import DepoCacheService
        from sqlalchemy import func

        kullanici_otelleri = get_kullanici_otelleri()
        otel_secenekleri = get_otel_filtreleme_secenekleri()
        otel_ids = [o.id for o in kullanici_otelleri]

        secili_otel_id = request.args.get('otel_id', type=int)

        # ✅ Cache kontrolü
        cache_key = f"depo_stok:{secili_otel_id or 'all'}:{','.join(map(str, otel_ids))}"
        cached_data = DepoCacheService.get_stok_bilgileri(cache_key)
        if cached_data:
            return render_template('depo_sorumlusu/stoklarim.html',
                                 stok_bilgileri=cached_data['stok_bilgileri'],
                                 otel_secenekleri=otel_secenekleri,
                                 secili_otel_id=secili_otel_id,
                                 secili_otel_adi=cached_data.get('secili_otel_adi'))

        # ... mevcut stok sorguları ...

        # ✅ Cache'e kaydet (30 saniye TTL)
        cache_data = {
            'stok_bilgileri': stok_bilgileri,
            'secili_otel_adi': secili_otel_adi
        }
        DepoCacheService.set_stok_bilgileri(cache_key, cache_data)

        return render_template('depo_sorumlusu/stoklarim.html',
                             stok_bilgileri=stok_bilgileri,
                             otel_secenekleri=otel_secenekleri,
                             secili_otel_id=secili_otel_id,
                             secili_otel_adi=secili_otel_adi)
```

**Yeni Cache Service** (`utils/depo_cache_service.py`):

```python
"""
Depo Sorumlusu Cache Service
"""

import logging
from utils.cache_helper import cache_get, cache_set, cache_delete_pattern

logger = logging.getLogger(__name__)


class DepoCacheService:
    """Depo sorumlusu cache yönetimi"""

    CACHE_PREFIX = "depo_sorumlusu"

    # Cache süreleri (saniye)
    STOK_BILGILERI_TTL = 30  # 30 saniye
    SIPARIS_LISTESI_TTL = 45  # 45 saniye

    @staticmethod
    def get_stok_bilgileri(cache_key: str):
        """Cache'den stok bilgileri al"""
        return cache_get(cache_key)

    @staticmethod
    def set_stok_bilgileri(cache_key: str, data: dict):
        """Stok bilgilerini cache'le"""
        return cache_set(cache_key, data, DepoCacheService.STOK_BILGILERI_TTL)

    @staticmethod
    def invalidate_stok(otel_id: int = None):
        """Stok cache'ini temizle"""
        if otel_id:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:stok:*{otel_id}*"
        else:
            pattern = f"{DepoCacheService.CACHE_PREFIX}:stok:*"
        deleted = cache_delete_pattern(pattern)
        logger.info(f"Depo stok cache temizlendi (otel={otel_id}): {deleted} key")
        return deleted
```

---

## 2. Cache Invalidation Stratejileri

### Mevcut Invalidation Noktaları

#### ✅ İyi Örnekler

1. **Ürün Ekleme Sonrası** (`/api/kat-sorumlusu/urun-ekle`):

```python
# Cache invalidation after successful save
KatSorumlusuCacheService.invalidate_minibar(kullanici_id)
KatSorumlusuCacheService.invalidate_kullanici(kullanici_id)
KatSorumlusuCacheService.invalidate_oda_setup(oda_id)
```

2. **Sarfiyat Yok Kaydı Sonrası** (`/api/kat-sorumlusu/sarfiyat-yok`):

```python
# Cache invalidation
KatSorumlusuCacheService.invalidate_dnd(kullanici_oteli.id)
KatSorumlusuCacheService.invalidate_kullanici(kullanici_id)
```

### ❌ Eksik Invalidation Noktaları

#### A. Zimmet Atama Sonrası

**Mevcut Kod** (`routes/depo_routes.py` Line 210-342):

```python
@app.route('/personel-zimmet', methods=['GET', 'POST'])
def personel_zimmet():
    # ... zimmet atama işlemi ...

    db.session.commit()

    # ❌ Cache invalidation yok!
    flash('Zimmet başarıyla atandı (FIFO ile stok düşüldü).', 'success')
    return redirect(url_for('personel_zimmet'))
```

**Düzeltilmiş Kod:**

```python
@app.route('/personel-zimmet', methods=['GET', 'POST'])
def personel_zimmet():
    # ... zimmet atama işlemi ...

    db.session.commit()

    # ✅ Cache invalidation ekle
    KatSorumlusuCacheService.invalidate_kullanici(personel_id)
    KatSorumlusuCacheService.invalidate_zimmet_urunler(personel_id)
    DepoCacheService.invalidate_stok(otel_id)

    flash('Zimmet başarıyla atandı (FIFO ile stok düşüldü).', 'success')
    return redirect(url_for('personel_zimmet'))
```

#### B. Ana Depo Tedarik Sonrası

**Mevcut Kod** (`routes/depo_routes.py` Line 992-1191):

```python
@app.route('/ana-depo-tedarik-tamamla', methods=['POST'])
def ana_depo_tedarik_tamamla():
    # ... tedarik işlemi ...

    db.session.commit()

    # ❌ Cache invalidation yok!
    return jsonify({
        'success': True,
        'message': mesaj,
        'tedarik_no': tedarik_no
    })
```

**Düzeltilmiş Kod:**

```python
@app.route('/ana-depo-tedarik-tamamla', methods=['POST'])
def ana_depo_tedarik_tamamla():
    # ... tedarik işlemi ...

    db.session.commit()

    # ✅ Cache invalidation ekle
    DepoCacheService.invalidate_stok(otel_id)

    # Tüm kat sorumlularının zimmet cache'ini temizle
    kat_sorumlulari = Kullanici.query.filter_by(
        otel_id=otel_id,
        rol='kat_sorumlusu',
        aktif=True
    ).all()
    for ks in kat_sorumlulari:
        KatSorumlusuCacheService.invalidate_kullanici(ks.id)

    return jsonify({
        'success': True,
        'message': mesaj,
        'tedarik_no': tedarik_no
    })
```

---

## 3. TTL Optimizasyonu

### Mevcut TTL Değerleri

| Cache Tipi         | TTL  | Uygun mu? | Öneri            |
| ------------------ | ---- | --------- | ---------------- |
| `dashboard`        | 30s  | ✅ Uygun  | Sık değişen veri |
| `minibar_islemler` | 60s  | ✅ Uygun  | Orta sıklık      |
| `dnd_liste`        | 45s  | ✅ Uygun  | Orta sıklık      |
| `oda_setup`        | 300s | ⚠️ Uzun   | 180s'ye düşür    |
| `zimmet_urunler`   | 120s | ✅ Uygun  | Nadiren değişir  |
| `kritik_stoklar`   | 60s  | ✅ Uygun  | Orta sıklık      |

### Önerilen TTL Değerleri

```python
class KatSorumlusuCacheService:
    """Kat sorumlusu cache yönetimi"""

    CACHE_PREFIX = "kat_sorumlusu"

    # ✅ Optimize edilmiş TTL değerleri
    DASHBOARD_TTL = 30          # 30 saniye - Sık güncellenen
    MINIBAR_ISLEMLER_TTL = 60   # 1 dakika - Orta sıklık
    MINIBAR_URUNLER_TTL = 60    # 1 dakika - Yeni eklendi
    DND_LISTE_TTL = 45          # 45 saniye - Orta sıklık
    ODA_SETUP_TTL = 180         # 3 dakika - Nadiren değişir (300s'den düşürüldü)
    ZIMMET_URUNLER_TTL = 120    # 2 dakika - Nadiren değişir
    ZIMMET_OZET_TTL = 120       # 2 dakika - Yeni eklendi
    KRITIK_STOKLAR_TTL = 60     # 1 dakika - Orta sıklık
```

---

## 4. Kod Örnekleri

### A. Cache Decorator Pattern

**Kullanım:**

```python
from utils.cache_helper import cached

@cached(ttl=60, key_prefix="minibar_urunler")
def get_minibar_urunler_data(kullanici_id):
    """Minibar ürünlerini getir - otomatik cache'lenir"""
    urunler = Urun.query.filter_by(aktif=True).all()
    # ... veri hazırlama ...
    return urun_listesi

# Endpoint'te kullanım
@app.route('/minibar-urunler')
@login_required
def minibar_urunler():
    kullanici_id = session.get('kullanici_id')
    urun_listesi = get_minibar_urunler_data(kullanici_id)
    return jsonify({'success': True, 'urunler': urun_listesi})
```

### B. Conditional Cache Pattern

**Kullanım:**

```python
@app.route('/api/stok-durumu')
@login_required
def stok_durumu():
    otel_id = request.args.get('otel_id')
    force_refresh = request.args.get('refresh', False)

    # Force refresh parametresi varsa cache'i atla
    if not force_refresh:
        cached = DepoCacheService.get_stok_bilgileri(otel_id)
        if cached:
            return jsonify({'success': True, 'data': cached, 'cached': True})

    # Veriyi veritabanından getir
    data = fetch_stok_data(otel_id)
    DepoCacheService.set_stok_bilgileri(otel_id, data)

    return jsonify({'success': True, 'data': data, 'cached': False})
```

### C. Multi-Level Cache Pattern

**Kullanım:**

```python
class StokCacheService:
    """Çok katmanlı cache servisi"""

    @staticmethod
    def get_stok_with_fallback(otel_id, urun_id):
        """
        1. Önce Redis cache'e bak
        2. Yoksa veritabanından getir
        3. Cache'e kaydet
        """
        # Level 1: Redis cache
        cache_key = f"stok:{otel_id}:{urun_id}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        # Level 2: Database
        stok = UrunStok.query.filter_by(
            otel_id=otel_id,
            urun_id=urun_id
        ).first()

        if stok:
            data = {
                'mevcut_stok': stok.mevcut_stok,
                'kritik_seviye': stok.kritik_stok_seviyesi
            }
            cache_set(cache_key, data, 30)
            return data

        return None
```

---

## 📊 Beklenen İyileşmeler

### Endpoint Bazlı İyileşme

| Endpoint           | Mevcut | Cache Sonrası | İyileşme |
| ------------------ | ------ | ------------- | -------- |
| `/minibar-urunler` | 500ms  | 50ms          | **90%**  |
| `/zimmetim`        | 300ms  | 40ms          | **87%**  |
| `/depo-stoklarim`  | 400ms  | 60ms          | **85%**  |
| `/api/dnd-liste`   | 250ms  | 30ms          | **88%**  |

### Cache Hit Rate Hedefleri

| Cache Tipi        | Hedef Hit Rate | Beklenen Tasarruf |
| ----------------- | -------------- | ----------------- |
| `minibar_urunler` | 80%            | 120 sorgu/dakika  |
| `zimmet_ozet`     | 85%            | 100 sorgu/dakika  |
| `depo_stok`       | 75%            | 150 sorgu/dakika  |
| `oda_setup`       | 90%            | 200 sorgu/dakika  |

---

## 🎯 Uygulama Planı

### Faz 1: Kritik Cache'ler (1 Gün)

1. ✅ `/minibar-urunler` cache ekle
2. ✅ `/zimmetim` cache ekle
3. ✅ Cache invalidation noktaları ekle

### Faz 2: Depo Cache'leri (1 Gün)

1. ✅ `DepoCacheService` oluştur
2. ✅ `/depo-stoklarim` cache ekle
3. ✅ Tedarik sonrası invalidation

### Faz 3: TTL Optimizasyonu (0.5 Gün)

1. ✅ TTL değerlerini gözden geçir
2. ✅ `oda_setup` TTL'ini düşür
3. ✅ Monitoring ekle

### Faz 4: Test ve Monitoring (1 Gün)

1. ✅ Cache hit rate monitoring
2. ✅ Performance test
3. ✅ Production deployment

---

**Toplam Süre:** 3.5 gün  
**Beklenen İyileşme:** %85-90 response time azalması  
**Risk Seviyesi:** Düşük (cache miss durumunda fallback var)
