# Nginx Access Log Analizi

## Genel Bilgiler

- **Tarih**: 19 Mart 2026
- **Zaman Aralığı**: 15:32 - 15:57 (25 dakika)
- **Domain**: minibartakip.com

## Trafik İstatistikleri

### En Çok Erişilen Endpoint'ler

1. `/api/dolum-talepleri` - Dolum talepleri API
2. `/api/bekleyen-dolum-sayisi` - Bekleyen dolum sayısı
3. `/api/son-aktiviteler?limit=10` - Son aktiviteler
4. `/api/system-monitor/*` - Sistem monitoring endpoint'leri
5. `/api/bildirimler/poll` - Bildirim polling (long-polling)
6. `/api/depo/bekleyen-siparisler` - Depo siparişleri
7. `/gorevler/api/bekleyen` - Bekleyen görevler

### Kullanıcı Rolleri

- **Sistem Yöneticisi**: `/sistem-yoneticisi`
- **Kat Sorumlusu**: `/kat-sorumlusu/dashboard`
- **Depo**: `/depo`
- **System Monitor**: `/system-monitor`

## Performans Metrikleri

### Response Time Analizi (mikrosaniye)

- **Hızlı (<1ms)**: Çoğu API endpoint
- **Orta (1-10ms)**: Dashboard ve rapor sayfaları
- **Yavaş (>100ms)**:
  - `/raporlar/kat-sorumlusu/gun-sonu-raporum-olustur`: 1.6s - 4.9s
  - `/oteller`: 1.8s (büyük veri)
  - `/kat-sorumlusu/dashboard`: 3.2s - 3.9s

### En Yavaş Endpoint'ler

```
POST /raporlar/kat-sorumlusu/gun-sonu-raporum-olustur
- 15:50:41 → 1606ms
- 15:51:15 → 4898ms
- 15:51:31 → 4128ms
- 15:51:53 → 5743ms
- 15:52:02 → 2383ms
```

## Sistem Monitoring Aktivitesi

System Monitor sayfası çok aktif polling yapıyor:

- `/api/system-monitor/endpoints?sort=avg_time` - Her 10-15 saniyede
- `/api/system-monitor/error-log?limit=50` - Her 10-15 saniyede
- `/api/system-monitor/db-stats` - Her 10-15 saniyede
- `/api/system-monitor/overview` - Her 10-15 saniyede

## Polling Pattern'leri

### Bildirim Polling

- `/api/bildirimler/poll?son_kontrol=...` - Her 60 saniyede
- Long-polling pattern kullanılıyor

### Dashboard Polling

- Dolum talepleri: ~15 saniye
- Bekleyen dolum sayısı: ~15 saniye
- Son aktiviteler: ~15 saniye
- Görev listesi: ~30 saniye

## IP Adresleri

### Ana Kullanıcılar

- `88.231.129.62` - En aktif kullanıcı (sistem yöneticisi)
- `94.78.89.124` - Kat sorumlusu
- `88.255.145.211` - Kat sorumlusu (rapor oluşturuyor)
- `94.79.101.193` - Mobil kullanıcı (iPhone)
- `127.0.0.1` - Health check (local)

### Bot/Crawler

- `54.174.110.188` - Bingbot
- `52.202.237.12` - HeadlessChrome (monitoring?)

## Hata ve Uyarılar

### 404 Hatalar

```
/apple-touch-icon-precomposed.png - 404
/favicon.ico - 404
/apple-touch-icon.png - 404
/.env - 404 (güvenlik taraması)
```

### Error Log İçeriği

- Bazı endpoint'lerde 211 byte error log
- Bazı endpoint'lerde 378 byte error log
- Bazı endpoint'lerde 1836 byte error log

## Öneriler

### 1. Performans İyileştirmeleri

- **Rapor Oluşturma**: `gun-sonu-raporum-olustur` endpoint'i 1.6-4.9s arası sürdüğü için:
  - Background job'a taşınmalı
  - Redis cache kullanılmalı
  - Pagination eklenmeli

### 2. Polling Optimizasyonu

- System Monitor polling'i çok sık (10-15 saniye)
- WebSocket veya Server-Sent Events kullanılabilir
- Polling interval'i 30-60 saniyeye çıkarılabilir

### 3. Caching Stratejisi

- Static asset'ler için 304 Not Modified doğru çalışıyor
- API endpoint'leri için Redis cache eklenebilir:
  - `/api/dolum-talepleri` - 30 saniye TTL
  - `/api/bekleyen-dolum-sayisi` - 30 saniye TTL
  - `/api/son-aktiviteler` - 15 saniye TTL

### 4. Database Optimizasyonu

- `/api/system-monitor/db-stats` sık çağrılıyor
- Connection pooling kontrol edilmeli
- Slow query log'ları incelenmeli

### 5. Güvenlik

- `.env` dosyası için 404 dönüyor (iyi)
- Rate limiting eklenebilir (özellikle polling endpoint'leri için)
- IP bazlı throttling düşünülebilir

### 6. Monitoring

- Response time threshold'ları belirlenebilir
- Alerting sistemi kurulabilir (>2s için)
- Error rate tracking eklenebilir

## Kullanıcı Davranışları

### Aktif Saatler

15:32 - 15:57 arası yoğun aktivite:

- Sistem yöneticisi sürekli monitoring yapıyor
- Kat sorumluları rapor oluşturuyor
- Depo personeli sipariş takibi yapıyor

### Mobil Kullanım

- iPhone Safari kullanıcıları var
- PWA install script'leri yükleniyor
- Responsive tasarım aktif

## Sonuç

Sistem genel olarak stabil çalışıyor ancak:

1. Rapor oluşturma endpoint'i optimize edilmeli
2. Polling frequency azaltılmalı
3. Caching stratejisi güçlendirilmeli
4. Real-time özellikler için WebSocket düşünülmeli
