# Design Document - ML Anomaly Detection System

## Overview

Bu doküman, minibar yönetim sistemine entegre edilecek makine öğrenmesi tabanlı anomali tespit ve uyarı sisteminin teknik tasarımını detaylandırır. Sistem, mevcut Flask/PostgreSQL altyapısı üzerine inşa edilecek ve Python ML kütüphaneleri (scikit-learn, pandas) kullanacaktır.

### Temel Hedefler

1. **Gerçek Zamanlı İzleme**: Stok, tüketim ve dolum metriklerini sürekli izleme
2. **Proaktif Uyarılar**: Anormal durumları tespit edip admin'e bildirme
3. **Sürekli Öğrenme**: Zaman içinde model doğruluğunu artırma
4. **Minimal Performans Etkisi**: Mevcut sistemi yavaşlatmadan çalışma

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Data       │───▶│   ML Engine  │───▶│   Alert      │  │
│  │   Collector  │    │   (Anomaly   │    │   Manager    │  │
│  │              │    │   Detection) │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            PostgreSQL Database                        │  │
│  │  - ml_metrics                                         │  │
│  │  - ml_models                                          │  │
│  │  - ml_alerts                                          │  │
│  │  - ml_training_logs                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Background Scheduler (APScheduler)            │  │
│  │  - Veri toplama (15 dakika)                          │  │
│  │  - Model eğitimi (gece yarısı)                       │  │
│  │  - Anomali tespiti (5 dakika)                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     ML System Components                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  utils/ml/                                                    │
│  ├── data_collector.py      # Veri toplama servisi          │
│  ├── anomaly_detector.py    # ML anomali tespit motoru      │
│  ├── model_trainer.py       # Model eğitim servisi          │
│  ├── alert_manager.py       # Uyarı yönetimi                │
│  ├── metrics_calculator.py  # Metrik hesaplama              │
│  └── __init__.py                                             │
│                                                               │
│  routes/                                                      │
│  └── ml_routes.py            # ML dashboard ve API routes    │
│                                                               │
│  templates/admin/                                             │
│  └── ml_dashboard.html       # ML uyarı dashboard'u         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Database Models (models.py)

#### MLMetric Model
```python
class MLMetric(db.Model):
    """ML metrik kayıtları - zaman serisi verileri"""
    __tablename__ = 'ml_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.Enum('stok_seviye', 'tuketim_miktar', 
                                     'dolum_sure', 'stok_bitis_tahmini'))
    entity_type = db.Column(db.String(50))  # 'urun', 'oda', 'kat_sorumlusu'
    entity_id = db.Column(db.Integer)
    metric_value = db.Column(db.Float)
    timestamp = db.Column(db.DateTime(timezone=True))
    metadata = db.Column(JSONB)  # Ek bilgiler
```

#### MLModel Model
```python
class MLModel(db.Model):
    """Eğitilmiş ML modelleri"""
    __tablename__ = 'ml_models'
    
    id = db.Column(db.Integer, primary_key=True)
    model_type = db.Column(db.String(50))  # 'isolation_forest', 'z_score'
    metric_type = db.Column(db.String(50))
    model_data = db.Column(db.LargeBinary)  # Pickle serialized model
    parameters = db.Column(JSONB)
    training_date = db.Column(db.DateTime(timezone=True))
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
```

#### MLAlert Model
```python
class MLAlert(db.Model):
    """ML uyarıları"""
    __tablename__ = 'ml_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.Enum('stok_anomali', 'tuketim_anomali', 
                                    'dolum_gecikme', 'stok_bitis_uyari'))
    severity = db.Column(db.Enum('dusuk', 'orta', 'yuksek', 'kritik'))
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    metric_value = db.Column(db.Float)
    expected_value = db.Column(db.Float)
    deviation_percent = db.Column(db.Float)
    message = db.Column(db.Text)
    suggested_action = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True))
    is_read = db.Column(db.Boolean, default=False)
    is_false_positive = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime(timezone=True))
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
```

#### MLTrainingLog Model
```python
class MLTrainingLog(db.Model):
    """Model eğitim logları"""
    __tablename__ = 'ml_training_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'))
    training_start = db.Column(db.DateTime(timezone=True))
    training_end = db.Column(db.DateTime(timezone=True))
    data_points = db.Column(db.Integer)
    success = db.Column(db.Boolean)
    error_message = db.Column(db.Text)
    metrics = db.Column(JSONB)  # Performans metrikleri
```

### 2. Data Collector Service (utils/ml/data_collector.py)

**Sorumluluklar:**
- Her 15 dakikada bir metrik toplama
- Mevcut tablolardan veri çekme
- MLMetric tablosuna kaydetme

**Temel Fonksiyonlar:**

```python
class DataCollector:
    def collect_stok_metrics():
        """Tüm ürünler için stok seviyelerini topla"""
        
    def collect_tuketim_metrics():
        """Oda bazlı tüketim verilerini topla"""
        
    def collect_dolum_metrics():
        """Dolum süresi metriklerini topla"""
        
    def collect_all_metrics():
        """Tüm metrikleri topla ve kaydet"""
```

**Veri Kaynakları:**
- `Urun` + `StokHareket` → Stok seviyeleri
- `MinibarIslem` + `MinibarIslemDetay` → Tüketim miktarları
- `MinibarIslem` → Dolum süreleri (islem_tarihi farkları)

### 3. Anomaly Detector (utils/ml/anomaly_detector.py)

**Sorumluluklar:**
- Anomali tespit algoritmalarını çalıştırma
- Threshold kontrolü
- Alert oluşturma

**Algoritma Seçimi:**

1. **Z-Score Method** (Basit, hızlı)
   - Normal dağılım varsayımı
   - 3-sigma kuralı (99.7%)
   - Gerçek zamanlı tespit için ideal

2. **Isolation Forest** (Gelişmiş)
   - Outlier detection
   - Çok boyutlu anomali tespiti
   - Daha yüksek doğruluk

**Temel Fonksiyonlar:**

```python
class AnomalyDetector:
    def detect_stok_anomalies():
        """Stok seviyesi anomalilerini tespit et"""
        
    def detect_tuketim_anomalies():
        """Tüketim anomalilerini tespit et"""
        
    def detect_dolum_anomalies():
        """Dolum süresi anomalilerini tespit et"""
        
    def calculate_severity(deviation_percent):
        """Sapma yüzdesine göre önem seviyesi belirle"""
        # < 30%: dusuk
        # 30-50%: orta
        # 50-80%: yuksek
        # > 80%: kritik
```

### 4. Model Trainer (utils/ml/model_trainer.py)

**Sorumluluklar:**
- Günlük model eğitimi (gece yarısı)
- Model performans değerlendirmesi
- Threshold optimizasyonu

**Temel Fonksiyonlar:**

```python
class ModelTrainer:
    def train_isolation_forest(metric_type, data):
        """Isolation Forest modelini eğit"""
        
    def evaluate_model(model, test_data):
        """Model performansını değerlendir"""
        
    def optimize_thresholds(model, validation_data):
        """Threshold değerlerini optimize et"""
        
    def save_model(model, model_type, metric_type):
        """Modeli veritabanına kaydet"""
```

**Eğitim Stratejisi:**
- Son 30 günlük veri kullanımı
- 80/20 train/test split
- Cross-validation (5-fold)
- Yanlış pozitif geri bildirimi ile iyileştirme

### 5. Alert Manager (utils/ml/alert_manager.py)

**Sorumluluklar:**
- Alert oluşturma ve yönetme
- Bildirim gönderme
- Alert önceliklendirme

**Temel Fonksiyonlar:**

```python
class AlertManager:
    def create_alert(alert_data):
        """Yeni alert oluştur"""
        
    def get_active_alerts(severity=None):
        """Aktif alertleri getir"""
        
    def mark_as_read(alert_id, user_id):
        """Alert'i okundu olarak işaretle"""
        
    def mark_as_false_positive(alert_id, user_id):
        """Yanlış pozitif olarak işaretle"""
        
    def send_notification(alert):
        """Bildirim gönder (email, SMS, push)"""
```

### 6. Metrics Calculator (utils/ml/metrics_calculator.py)

**Sorumluluklar:**
- Stok bitiş tahmini
- Trend analizi
- İstatistiksel hesaplamalar

**Temel Fonksiyonlar:**

```python
class MetricsCalculator:
    def predict_stock_depletion(urun_id):
        """Stok bitiş tarihini tahmin et"""
        # Linear regression kullanarak
        
    def calculate_consumption_trend(oda_id, days=7):
        """Tüketim trendini hesapla"""
        
    def calculate_average_dolum_time(kat_sorumlusu_id):
        """Ortalama dolum süresini hesapla"""
```

## Data Models

### Metric Data Structure

```json
{
  "metric_type": "stok_seviye",
  "entity_type": "urun",
  "entity_id": 123,
  "metric_value": 45.0,
  "timestamp": "2025-11-09T10:30:00Z",
  "metadata": {
    "urun_adi": "Coca Cola",
    "kritik_seviye": 10,
    "grup": "İçecekler"
  }
}
```

### Alert Data Structure

```json
{
  "alert_type": "stok_anomali",
  "severity": "yuksek",
  "entity_type": "urun",
  "entity_id": 123,
  "metric_value": 5.0,
  "expected_value": 45.0,
  "deviation_percent": 88.9,
  "message": "Coca Cola stok seviyesi normalden %88.9 düşük",
  "suggested_action": "Acil sipariş verin. Tahmini 2 gün içinde tükenecek.",
  "created_at": "2025-11-09T10:35:00Z"
}
```

## Error Handling

### Error Categories

1. **Data Collection Errors**
   - Database connection timeout
   - Missing data
   - Invalid data format

2. **Model Training Errors**
   - Insufficient data
   - Training timeout
   - Model convergence failure

3. **Anomaly Detection Errors**
   - Model not found
   - Prediction failure
   - Threshold calculation error

### Error Handling Strategy

```python
try:
    # ML operation
except InsufficientDataError:
    logger.warning("Yetersiz veri, varsayılan threshold kullanılıyor")
    use_default_threshold()
except ModelNotFoundError:
    logger.error("Model bulunamadı, Z-score yöntemine geçiliyor")
    fallback_to_zscore()
except Exception as e:
    logger.error(f"Beklenmeyen hata: {str(e)}")
    log_hata('ml_system', str(e))
    # Sistem çalışmaya devam etsin
```

## Testing Strategy

### Unit Tests

1. **Data Collector Tests**
   - Metrik toplama doğruluğu
   - Veri formatı kontrolü
   - Edge case'ler (boş veri, null değerler)

2. **Anomaly Detector Tests**
   - Anomali tespit doğruluğu
   - Threshold hesaplama
   - Severity belirleme

3. **Model Trainer Tests**
   - Model eğitim süreci
   - Performans metrik hesaplama
   - Model kaydetme/yükleme

### Integration Tests

1. **End-to-End Flow**
   - Veri toplama → Anomali tespiti → Alert oluşturma
   - Model eğitimi → Model kullanımı
   - Alert oluşturma → Bildirim gönderme

2. **Database Integration**
   - Model kaydetme/yükleme
   - Metrik kaydetme
   - Alert CRUD işlemleri

### Performance Tests

1. **Load Testing**
   - 1000+ oda verisi ile anomali tespiti
   - Concurrent veri toplama
   - Dashboard yükleme süresi

2. **Memory Testing**
   - Model memory footprint
   - Veri toplama memory kullanımı
   - Cache performansı

## Performance Optimization

### Caching Strategy

```python
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
})

@cache.memoize(timeout=300)  # 5 dakika cache
def get_active_alerts():
    return MLAlert.query.filter_by(is_read=False).all()
```

### Database Indexing

```sql
-- Metrik sorguları için
CREATE INDEX idx_ml_metrics_type_time ON ml_metrics(metric_type, timestamp DESC);
CREATE INDEX idx_ml_metrics_entity ON ml_metrics(entity_type, entity_id);

-- Alert sorguları için
CREATE INDEX idx_ml_alerts_severity_read ON ml_alerts(severity, is_read);
CREATE INDEX idx_ml_alerts_created ON ml_alerts(created_at DESC);
```

### Async Processing

```python
from celery import Celery

celery = Celery('ml_tasks', broker=os.getenv('REDIS_URL'))

@celery.task
def train_model_async(metric_type):
    """Model eğitimini arka planda çalıştır"""
    trainer = ModelTrainer()
    trainer.train_isolation_forest(metric_type)
```

## Security Considerations

### Data Privacy

- Hassas veriler şifrelenmeli (model parametreleri)
- Audit log tüm ML işlemlerini kaydetmeli
- Admin yetkisi olmayan kullanıcılar ML dashboard'a erişememeli

### Input Validation

```python
def validate_metric_data(data):
    """Metrik verilerini doğrula"""
    if not isinstance(data.get('metric_value'), (int, float)):
        raise ValueError("metric_value sayısal olmalı")
    if data.get('metric_value') < 0:
        raise ValueError("metric_value negatif olamaz")
```

### SQL Injection Prevention

- SQLAlchemy ORM kullanımı (parametreli sorgular)
- Raw SQL kullanımında parametre binding
- Input sanitization

## Deployment Considerations

### Environment Variables

```bash
# ML System Configuration
ML_ENABLED=true
ML_DATA_COLLECTION_INTERVAL=900  # 15 dakika (saniye)
ML_TRAINING_SCHEDULE="0 0 * * *"  # Her gece yarısı
ML_ANOMALY_CHECK_INTERVAL=300  # 5 dakika
ML_MIN_DATA_POINTS=100  # Minimum veri noktası
ML_ACCURACY_THRESHOLD=0.85  # %85 doğruluk hedefi
```

### Dependencies

```txt
# requirements.txt'e eklenecek
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
APScheduler==3.10.4
joblib==1.3.2  # Model serialization
redis==5.0.1  # Caching
celery==5.3.4  # Async tasks (opsiyonel)
```

### Migration Script

```python
# migrations/add_ml_tables.py
def upgrade():
    # MLMetric tablosu
    op.create_table('ml_metrics', ...)
    
    # MLModel tablosu
    op.create_table('ml_models', ...)
    
    # MLAlert tablosu
    op.create_table('ml_alerts', ...)
    
    # MLTrainingLog tablosu
    op.create_table('ml_training_logs', ...)
    
    # Index'ler
    op.create_index('idx_ml_metrics_type_time', ...)
```

## Monitoring and Logging

### Logging Strategy

```python
import logging

ml_logger = logging.getLogger('ml_system')
ml_logger.setLevel(logging.INFO)

# Her ML işlemi loglanmalı
ml_logger.info(f"Veri toplama başladı: {metric_type}")
ml_logger.warning(f"Yetersiz veri: {data_points} < {min_required}")
ml_logger.error(f"Model eğitimi başarısız: {error}")
```

### Metrics to Monitor

1. **System Health**
   - Veri toplama başarı oranı
   - Model eğitim süresi
   - Anomali tespit süresi

2. **Model Performance**
   - Doğruluk (accuracy)
   - Hassasiyet (precision)
   - Geri çağırma (recall)
   - Yanlış pozitif oranı

3. **Alert Statistics**
   - Günlük alert sayısı
   - Severity dağılımı
   - Çözülme süresi

## Future Enhancements

### Phase 2 Features

1. **Advanced ML Models**
   - LSTM for time series prediction
   - Prophet for seasonality detection
   - AutoML for model selection

2. **Real-time Streaming**
   - Apache Kafka integration
   - Real-time anomaly detection
   - Live dashboard updates

3. **Multi-Hotel Support**
   - Hotel-specific models
   - Cross-hotel comparison
   - Centralized monitoring

4. **Mobile Notifications**
   - Push notifications
   - SMS alerts
   - WhatsApp integration

### Scalability Roadmap

1. **Horizontal Scaling**
   - Microservices architecture
   - Separate ML service
   - Load balancing

2. **Data Pipeline**
   - Apache Airflow for orchestration
   - Data warehouse integration
   - ETL optimization

3. **Advanced Analytics**
   - Predictive maintenance
   - Demand forecasting
   - Revenue optimization
