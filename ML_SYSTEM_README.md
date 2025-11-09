# ML Anomali Tespit Sistemi - Kurulum ve Kullanım Kılavuzu

## 📋 Genel Bakış

Bu sistem, minibar yönetim uygulamasına entegre edilmiş makine öğrenmesi tabanlı bir anomali tespit ve uyarı sistemidir. Stok seviyeleri, tüketim miktarları ve dolum sürelerini sürekli izleyerek anormal durumları tespit eder ve proaktif uyarılar oluşturur.

## 🎯 Özellikler

- **Otomatik Veri Toplama**: Her 15 dakikada bir metrik toplama
- **Anomali Tespiti**: Z-Score ve Isolation Forest algoritmaları
- **Proaktif Uyarılar**: 4 seviyeli uyarı sistemi (düşük, orta, yüksek, kritik)
- **Stok Bitiş Tahmini**: Linear regression ile stok tükenme tahmini
- **Sürekli Öğrenme**: Günlük model eğitimi ve yanlış pozitif öğrenme
- **Admin Dashboard**: Gerçek zamanlı izleme ve yönetim

## 🚀 Kurulum

### 1. Dependencies Yükleme

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

`.env` dosyanıza aşağıdaki değişkenleri ekleyin:

```bash
# ML System Configuration
ML_ENABLED=true
ML_DATA_COLLECTION_INTERVAL=900  # 15 dakika
ML_ANOMALY_CHECK_INTERVAL=300  # 5 dakika
ML_TRAINING_SCHEDULE=0 0 * * *  # Her gece yarısı
ML_MIN_DATA_POINTS=100
ML_ACCURACY_THRESHOLD=0.85
```

### 3. Database Migration

```bash
python migrations/add_ml_tables.py
```

Bu komut şu tabloları oluşturur:
- `ml_metrics` - Metrik verileri
- `ml_models` - Eğitilmiş modeller
- `ml_alerts` - Uyarılar
- `ml_training_logs` - Eğitim logları

### 4. İlk Model Eğitimi (Opsiyonel)

Sistem otomatik olarak veri toplamaya başlar ve yeterli veri biriktiğinde modelleri eğitir. Manuel eğitim için:

```python
from utils.ml.model_trainer import ModelTrainer
from models import db

trainer = ModelTrainer(db)
trainer.train_all_models()
```

## 📊 Kullanım

### Admin Dashboard

ML Dashboard'a erişim:
```
http://your-domain/ml/dashboard
```

**Erişim**: Sadece `admin` ve `sistem_yoneticisi` rolleri

### Dashboard Özellikleri

1. **Özet Kartlar**
   - Aktif uyarı sayısı
   - Kritik stok ürün sayısı
   - Son 24 saat veri toplama
   - Aktif model sayısı

2. **Aktif Uyarılar**
   - Severity bazlı filtreleme
   - Okundu işaretleme
   - Yanlış pozitif işaretleme

3. **İstatistikler**
   - Son 30 gün alert istatistikleri
   - Yanlış pozitif oranı
   - Doğruluk oranı

4. **Model Performansı**
   - Accuracy, Precision, Recall metrikleri
   - Son eğitim bilgileri

## 🔧 API Endpoints

### Alertleri Getir
```
GET /ml/api/alerts?severity=kritik&limit=10
```

### Alert Okundu İşaretle
```
POST /ml/api/alerts/{alert_id}/read
```

### Yanlış Pozitif İşaretle
```
POST /ml/api/alerts/{alert_id}/false-positive
```

### Metrikleri Getir
```
GET /ml/api/metrics?days=7&type=stok_seviye
```

### Model Performansı
```
GET /ml/api/model-performance
```

### İstatistikler
```
GET /ml/api/statistics?days=30
```

## 🔄 Sistem Çalışma Akışı

### Adım 1: Veri Toplama (Her 15 Dakika)

```
┌─────────────────────────────────────────────────────────────┐
│  1. STOK VERİLERİ                                           │
│     - Tüm ürünlerin mevcut stok seviyeleri                  │
│     - Kritik stok seviyesi ile karşılaştırma                │
│     - Extra data: ürün adı, grup, kritik seviye             │
│                                                              │
│  2. TÜKETİM VERİLERİ                                        │
│     - Son 24 saat minibar tüketim kayıtları                 │
│     - Oda bazlı tüketim miktarları                          │
│     - Extra data: oda no, oda tipi, kat                     │
│                                                              │
│  3. DOLUM SÜRESİ VERİLERİ                                   │
│     - Kat sorumlusu bazlı ortalama dolum süreleri           │
│     - Son 7 gün işlem sayısı                                │
│     - Extra data: personel adı, işlem sayısı, otel          │
│                                                              │
│  4. ZİMMET VERİLERİ                                         │
│     - Zimmet kullanım oranları                              │
│     - Fire/kayıp oranları                                   │
│     - Extra data: toplam zimmet, kullanım, fire             │
│                                                              │
│  5. DOLULUK VERİLERİ                                        │
│     - Otel doluluk oranları                                 │
│     - Boş oda tüketim kontrolleri                           │
│                                                              │
│  6. QR VERİLERİ                                             │
│     - QR okutma sıklıkları                                  │
│     - Personel performans metrikleri                        │
│                                                              │
│  ➜ Toplanan veriler ml_metrics tablosuna kaydedilir        │
└─────────────────────────────────────────────────────────────┘
```

### Adım 2: Sapma Analizi (Her 5 Dakika)

```
┌─────────────────────────────────────────────────────────────┐
│  1. VERİ HAZIRLIĞI                                          │
│     - Son 30 gün stok verileri çekilir                      │
│     - Son 7 gün tüketim verileri çekilir                    │
│     - Son 7 gün dolum verileri çekilir                      │
│                                                              │
│  2. İSTATİSTİKSEL ANALİZ                                    │
│     ┌─────────────────────────────────────┐                │
│     │  Z-Score Metodu                     │                │
│     │  - Ortalama (μ) hesapla             │                │
│     │  - Standart sapma (σ) hesapla       │                │
│     │  - Z = (X - μ) / σ                  │                │
│     │  - |Z| > 3 ise anomali              │                │
│     └─────────────────────────────────────┘                │
│                                                              │
│  3. MAKİNE ÖĞRENMESİ ANALİZİ                                │
│     ┌─────────────────────────────────────┐                │
│     │  Isolation Forest                   │                │
│     │  - Eğitilmiş model yükle            │                │
│     │  - Yeni veri predict et             │                │
│     │  - Anomaly score hesapla            │                │
│     │  - Score < threshold ise anomali    │                │
│     └─────────────────────────────────────┘                │
│                                                              │
│  4. SAPMA TESPİTİ                                           │
│     - Stok Sapması: %30+ sapma → Alert                     │
│     - Tüketim Sapması: %40+ sapma → Alert                  │
│     - Dolum Gecikmesi: %50+ uzun → Alert                   │
│     - Zimmet Fire: %20+ fire → Alert                       │
│     - Boş Oda Tüketim: Tüketim var → Alert                 │
│                                                              │
│  5. UYARI OLUŞTURMA                                         │
│     - Severity belirleme (düşük/orta/yüksek/kritik)         │
│     - Mesaj ve önerilen aksiyon oluşturma                   │
│     - Duplicate kontrol (son 1-24 saat)                     │
│     - ml_alerts tablosuna kaydetme                          │
│                                                              │
│  ➜ Tespit edilen sapmalar alert olarak kaydedilir          │
└─────────────────────────────────────────────────────────────┘
```

### Adım 3: Model Eğitimi (Her Gece 00:00)

```
┌─────────────────────────────────────────────────────────────┐
│  1. VERİ TOPLAMA VE HAZIRLIK                                │
│     - Son 90 gün metrik verileri çekilir                    │
│     - Minimum 100 veri noktası kontrolü                     │
│     - Eksik değerler temizlenir                             │
│     - Outlier'lar işaretlenir                               │
│                                                              │
│  2. ÖZELLİK MÜHENDİSLİĞİ                                    │
│     - Zaman bazlı özellikler (saat, gün, hafta)            │
│     - İstatistiksel özellikler (ortalama, std, min, max)   │
│     - Trend özellikleri (artış/azalış oranı)               │
│     - Mevsimsellik özellikleri                              │
│                                                              │
│  3. MODEL EĞİTİMİ                                           │
│     ┌─────────────────────────────────────┐                │
│     │  Isolation Forest Eğitimi           │                │
│     │  1. Veri setini train/test böl      │                │
│     │  2. Hyperparameter tuning           │                │
│     │     - n_estimators: 100             │                │
│     │     - contamination: 0.1            │                │
│     │     - max_samples: auto             │                │
│     │  3. Model eğit                      │                │
│     │  4. Cross-validation (5-fold)       │                │
│     └─────────────────────────────────────┘                │
│                                                              │
│  4. MODEL DEĞERLENDİRME                                     │
│     - Accuracy hesaplama                                    │
│     - Precision hesaplama                                   │
│     - Recall hesaplama                                      │
│     - F1-Score hesaplama                                    │
│     - Confusion Matrix analizi                              │
│     - ROC-AUC score                                         │
│                                                              │
│  5. YANLIŞPOZITIF ÖĞRENME                                   │
│     - Yanlış pozitif işaretli alertler çekilir             │
│     - Bu veriler "normal" olarak etiketlenir                │
│     - Model bu örneklerden öğrenir                          │
│     - Threshold değerleri optimize edilir                   │
│                                                              │
│  6. MODEL KAYDETME                                          │
│     - Model pickle formatında serialize edilir              │
│     - ml_models tablosuna kaydedilir                        │
│     - Eski model is_active=false yapılır                    │
│     - Yeni model is_active=true yapılır                     │
│     - Eğitim logları ml_training_logs'a yazılır             │
│                                                              │
│  7. PERFORMANS RAPORLAMA                                    │
│     - Eğitim süresi                                         │
│     - Veri noktası sayısı                                   │
│     - Model metrikleri                                      │
│     - Önceki modelle karşılaştırma                          │
│                                                              │
│  ➜ Eğitilmiş model sonraki sapma analizlerinde kullanılır  │
└─────────────────────────────────────────────────────────────┘
```

### Adım 4: Tahmin ve Öneriler (Sürekli)

```
┌─────────────────────────────────────────────────────────────┐
│  1. STOK BİTİŞ TAHMİNİ                                      │
│     - Son 30 gün stok tüketim hızı hesaplanır               │
│     - Linear regression ile trend belirlenir                │
│     - Mevcut stok / günlük tüketim = kalan gün              │
│     - 7 günden az ise uyarı oluşturulur                     │
│                                                              │
│  2. TÜKETİM TREND ANALİZİ                                   │
│     - Haftalık tüketim ortalaması                           │
│     - Aylık tüketim ortalaması                              │
│     - Artış/azalış yüzdeleri                                │
│     - Mevsimsel paternler                                   │
│                                                              │
│  3. PERFORMANS ÖLÇÜMLERİ                                    │
│     - Kat sorumlusu dolum hızı                              │
│     - Zimmet kullanım verimliliği                           │
│     - QR okutma sıklığı                                     │
│     - Talep yanıt süreleri                                  │
│                                                              │
│  4. ÖNERİLER OLUŞTURMA                                      │
│     - Kritik stok için sipariş önerisi                      │
│     - Yavaş personel için uyarı                             │
│     - Yüksek fire için inceleme önerisi                     │
│     - Boş oda tüketim için kontrol önerisi                  │
│                                                              │
│  ➜ Öneriler dashboard'da ve alert'lerde gösterilir         │
└─────────────────────────────────────────────────────────────┘
```

### Adım 5: Sürekli İyileştirme (Döngüsel)

```
┌─────────────────────────────────────────────────────────────┐
│  1. GERİ BİLDİRİM TOPLAMA                                   │
│     - Admin alert'leri okundu işaretler                     │
│     - Admin yanlış pozitif işaretler                        │
│     - Sistem gerçek durumları kaydeder                      │
│                                                              │
│  2. ÖĞRENME                                                 │
│     - Yanlış pozitifler analiz edilir                       │
│     - Threshold değerleri ayarlanır                         │
│     - Model yeniden eğitilir                                │
│     - Doğruluk oranı artar                                  │
│                                                              │
│  3. OPTİMİZASYON                                            │
│     - Yavaş sorgular optimize edilir                        │
│     - Gereksiz metrikler kaldırılır                         │
│     - Alert kuralları iyileştirilir                         │
│     - Performans artırılır                                  │
│                                                              │
│  ➜ Sistem zamanla daha akıllı ve doğru hale gelir          │
└─────────────────────────────────────────────────────────────┘
```

## 🤖 Sistem Bileşenleri

### 1. Data Collector
- **Dosya**: `utils/ml/data_collector.py`
- **Görev**: Metrik toplama
- **Çalışma**: Her 15 dakika (varsayılan)
- **Çıktı**: ml_metrics tablosuna veri kaydı

### 2. Anomaly Detector
- **Dosya**: `utils/ml/anomaly_detector.py`
- **Görev**: Sapma analizi
- **Çalışma**: Her 5 dakika (varsayılan)
- **Algoritmalar**: Z-Score, Isolation Forest
- **Çıktı**: ml_alerts tablosuna uyarı kaydı

### 3. Model Trainer
- **Dosya**: `utils/ml/model_trainer.py`
- **Görev**: Model eğitimi
- **Çalışma**: Her gece yarısı (varsayılan)
- **Çıktı**: ml_models tablosuna model kaydı

### 4. Alert Manager
- **Dosya**: `utils/ml/alert_manager.py`
- **Görev**: Uyarı yönetimi
- **Özellikler**: Okundu işaretleme, yanlış pozitif, temizleme

### 5. Metrics Calculator
- **Dosya**: `utils/ml/metrics_calculator.py`
- **Görev**: Stok bitiş tahmini, trend analizi
- **Özellikler**: Linear regression, istatistiksel analiz

## 📈 Metrik Tipleri

### 1. Stok Seviyesi (`stok_seviye`)
- **Entity**: `urun`
- **Toplama**: Her 15 dakika
- **Anomali Tespiti**: %30+ sapma

### 2. Tüketim Miktarı (`tuketim_miktar`)
- **Entity**: `oda`
- **Toplama**: Son 24 saat
- **Anomali Tespiti**: %40+ sapma

### 3. Dolum Süresi (`dolum_sure`)
- **Entity**: `kat_sorumlusu`
- **Toplama**: Son 7 gün ortalama
- **Anomali Tespiti**: %50+ uzun süre

## ⚠️ Alert Seviyeleri

| Severity | Sapma | Renk | Aksiyon |
|----------|-------|------|---------|
| **Düşük** | < %30 | Mavi | Bilgilendirme |
| **Orta** | %30-50 | Sarı | İzleme |
| **Yüksek** | %50-80 | Turuncu | Müdahale |
| **Kritik** | > %80 | Kırmızı | Acil Aksiyon |

## 🔄 Sürekli Öğrenme

Sistem, yanlış pozitif geri bildirimleri ile kendini geliştirir:

1. Admin bir alert'i "Yanlış Pozitif" olarak işaretler
2. Bu bilgi `ml_alerts` tablosunda kaydedilir
3. Günlük model eğitiminde bu veriler kullanılır
4. Threshold değerleri optimize edilir
5. Doğruluk oranı artar

## 🛠️ Bakım ve İzleme

### Log Kontrolü

```bash
# ML sistem logları
tail -f logs/ml_system.log
```

### Veri Temizleme

Eski veriler otomatik temizlenir:
- **Metrikler**: 90 gün
- **Alertler**: 90 gün (okunmuş)

Manuel temizleme:
```python
from utils.ml.data_collector import DataCollector
from utils.ml.alert_manager import AlertManager

collector = DataCollector(db)
collector.cleanup_old_metrics(days=90)

alert_manager = AlertManager(db)
alert_manager.cleanup_old_alerts(days=90)
```

### Model Performans İzleme

Dashboard'dan model performansını kontrol edin:
- **Accuracy**: > %85 hedef
- **False Positive Rate**: < %15 hedef

## 🐛 Troubleshooting

### Sistem Çalışmıyor

1. Environment variables kontrol edin
2. `ML_ENABLED=true` olduğundan emin olun
3. Scheduler loglarını kontrol edin

### Yetersiz Veri Hatası

Model eğitimi için minimum 100 veri noktası gerekir. Sistem otomatik olarak veri toplar, bekleyin.

### Yanlış Pozitif Oranı Yüksek

1. Yanlış pozitif alertleri işaretleyin
2. Sistem bir sonraki eğitimde öğrenecektir
3. Threshold değerleri otomatik optimize edilir

## 📝 Notlar

- İlk kurulumda veri birikmesi için 1-2 gün bekleyin
- Model eğitimi için yeterli veri gereklidir
- Yanlış pozitif işaretleme sistemi geliştirir
- Dashboard sadece admin kullanıcılar için erişilebilir

## 🎓 Teknik Detaylar

### Algoritmalar

**Z-Score Method**
- Basit ve hızlı
- Normal dağılım varsayımı
- 3-sigma kuralı (%99.7)

**Isolation Forest**
- Gelişmiş outlier detection
- Çok boyutlu anomali tespiti
- %10 contamination

### Performans

- Dashboard yükleme: < 2 saniye
- Anomali tespiti: < 5 saniye
- Model eğitimi: 1-5 dakika
- CPU kullanımı: < %30

## 📞 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Environment variables'ı doğrulayın
3. Database migration'ı kontrol edin

---

**Versiyon**: 1.0.0  
**Son Güncelleme**: 2025-11-09
