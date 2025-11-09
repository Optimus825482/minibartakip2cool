# Implementation Plan - ML Anomaly Detection System

- [x] 1. Database modelleri ve migration oluştur


  - MLMetric, MLModel, MLAlert, MLTrainingLog modellerini models.py'ye ekle
  - PostgreSQL JSONB ve LargeBinary field'ları kullan
  - Gerekli index'leri tanımla (metric_type, timestamp, severity, entity)
  - Migration script'i oluştur ve test et
  - _Requirements: 1.1, 1.2, 1.3, 5.1, 7.1, 7.2_

- [x] 2. Veri toplama servisi (Data Collector) implementasyonu


  - [x] 2.1 DataCollector sınıfını oluştur (utils/ml/data_collector.py)


    - collect_stok_metrics() fonksiyonu: Urun ve StokHareket tablolarından stok seviyelerini topla
    - collect_tuketim_metrics() fonksiyonu: MinibarIslem ve MinibarIslemDetay'dan tüketim verilerini topla
    - collect_dolum_metrics() fonksiyonu: MinibarIslem'den dolum sürelerini hesapla
    - collect_all_metrics() fonksiyonu: Tüm metrikleri topla ve MLMetric tablosuna kaydet
    - _Requirements: 1.1, 2.1, 3.1, 7.1, 7.2_

  - [x] 2.2 APScheduler entegrasyonu


    - Flask app'e APScheduler ekle
    - Her 15 dakikada collect_all_metrics() çalıştır
    - Hata yönetimi ve retry mekanizması ekle
    - _Requirements: 7.2, 8.2_

  - [ ]* 2.3 Data Collector unit testleri
    - Metrik toplama doğruluğu testleri
    - Edge case testleri (boş veri, null değerler)
    - _Requirements: 7.1, 7.2_

- [x] 3. Anomali tespit motoru (Anomaly Detector) implementasyonu


  - [x] 3.1 AnomalyDetector sınıfını oluştur (utils/ml/anomaly_detector.py)


    - Z-Score metodunu implement et (basit, hızlı tespit için)
    - Isolation Forest metodunu implement et (gelişmiş tespit için)
    - calculate_severity() fonksiyonu: Sapma yüzdesine göre önem seviyesi belirle
    - _Requirements: 1.2, 1.5, 2.2, 2.5, 3.2, 6.3_

  - [x] 3.2 Anomali tespit fonksiyonları

    - detect_stok_anomalies(): Stok seviyesi anomalilerini tespit et
    - detect_tuketim_anomalies(): Tüketim anomalilerini tespit et (oda bazlı)
    - detect_dolum_anomalies(): Dolum süresi anomalilerini tespit et
    - Her tespit için MLAlert kaydı oluştur
    - _Requirements: 1.2, 1.3, 2.2, 3.2_

  - [ ]* 3.3 Anomaly Detector unit testleri
    - Z-Score ve Isolation Forest doğruluk testleri
    - Severity hesaplama testleri
    - _Requirements: 1.2, 2.2, 3.2_

- [x] 4. Model eğitim servisi (Model Trainer) implementasyonu


  - [x] 4.1 ModelTrainer sınıfını oluştur (utils/ml/model_trainer.py)


    - train_isolation_forest(): Son 30 günlük veri ile model eğit
    - evaluate_model(): Model performansını değerlendir (accuracy, precision, recall)
    - optimize_thresholds(): Threshold değerlerini optimize et
    - save_model(): Modeli pickle ile serialize edip MLModel tablosuna kaydet
    - _Requirements: 6.1, 6.4, 6.5_

  - [x] 4.2 Günlük model eğitimi scheduler

    - Her gece yarısı train_all_models() çalıştır
    - MLTrainingLog'a eğitim kayıtlarını yaz
    - Başarısız eğitimlerde hata logla
    - _Requirements: 6.1, 6.5_

  - [ ]* 4.3 Model Trainer unit testleri
    - Model eğitim süreci testleri
    - Performans metrik hesaplama testleri
    - _Requirements: 6.1, 6.5_

- [x] 5. Alert yönetim servisi (Alert Manager) implementasyonu


  - [x] 5.1 AlertManager sınıfını oluştur (utils/ml/alert_manager.py)



    - create_alert(): Yeni alert oluştur (severity, message, suggested_action)
    - get_active_alerts(): Aktif alertleri getir (severity filtreleme ile)
    - mark_as_read(): Alert'i okundu olarak işaretle
    - mark_as_false_positive(): Yanlış pozitif olarak işaretle
    - _Requirements: 1.3, 5.1, 5.2, 5.3, 6.3_

  - [x] 5.2 Bildirim sistemi (opsiyonel)

    - send_notification(): Email/SMS/Push notification gönder
    - Kullanıcı bildirim tercihlerini kontrol et
    - _Requirements: 5.5_

  - [ ]* 5.3 Alert Manager unit testleri
    - Alert CRUD işlem testleri
    - Yanlış pozitif işaretleme testleri
    - _Requirements: 5.1, 5.3, 6.3_

- [x] 6. Metrik hesaplama servisi (Metrics Calculator) implementasyonu


  - [x] 6.1 MetricsCalculator sınıfını oluştur (utils/ml/metrics_calculator.py)


    - predict_stock_depletion(): Linear regression ile stok bitiş tahmini
    - calculate_consumption_trend(): 7 günlük tüketim trendi hesapla
    - calculate_average_dolum_time(): Kat sorumlusu bazlı ortalama dolum süresi
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 6.2 Stok bitiş uyarı sistemi

    - Her gün stok bitiş tahminlerini hesapla
    - 7 gün veya daha az kalan ürünler için alert oluştur
    - _Requirements: 4.3_

  - [ ]* 6.3 Metrics Calculator unit testleri
    - Tahmin doğruluğu testleri
    - Trend hesaplama testleri
    - _Requirements: 4.1, 4.4, 4.5_


- [x] 7. ML Dashboard ve API routes implementasyonu

  - [x] 7.1 ML routes oluştur (routes/ml_routes.py)


    - /ml-dashboard: Ana ML dashboard sayfası
    - /api/ml/alerts: Aktif alertleri getir (JSON)
    - /api/ml/alerts/<id>/read: Alert'i okundu işaretle
    - /api/ml/alerts/<id>/false-positive: Yanlış pozitif işaretle
    - /api/ml/metrics: Son 24 saat/7 gün/30 gün metrikleri
    - /api/ml/model-performance: Model performans metrikleri
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.4_

  - [x] 7.2 Admin dashboard template (templates/admin/ml_dashboard.html)



    - Aktif alertleri severity'ye göre sıralı göster
    - Alert detay modal'ı (zaman, metrik, sapma, önerilen aksiyon)
    - Son 24 saat/7 gün/30 gün özet istatistikler
    - Model performans grafikleri (Chart.js)
    - Alert filtreleme (severity, tarih, tip)
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 7.3 Dashboard'a erişim kontrolü

    - @role_required('admin') decorator ekle
    - Sadece admin ve sistem_yoneticisi erişebilsin
    - _Requirements: 9.1_

- [x] 8. Güvenlik ve yetkilendirme implementasyonu


  - [x] 8.1 Input validation

    - Metrik verilerini doğrula (validate_metric_data)
    - SQL injection koruması (SQLAlchemy ORM kullanımı)
    - XSS koruması (template escaping)
    - _Requirements: 9.5_

  - [x] 8.2 Audit logging

    - Tüm ML işlemlerini audit_log'a kaydet
    - Alert görüntüleme, yanlış pozitif işaretleme logla
    - Model eğitimi ve yapılandırma değişikliklerini logla
    - _Requirements: 9.4_

  - [x] 8.3 Veri şifreleme

    - Model parametrelerini şifreli kaydet (Fernet encryption)
    - Hassas threshold değerlerini şifrele
    - _Requirements: 9.3_


- [x] 9. Performans optimizasyonu

  - [x] 9.1 Caching implementasyonu

    - Redis cache ekle (flask-caching)
    - get_active_alerts() için 5 dakika cache
    - Dashboard verilerini cache'le
    - _Requirements: 8.1, 8.4_

  - [x] 9.2 Database indexing

    - ml_metrics için composite index (metric_type, timestamp)
    - ml_alerts için composite index (severity, is_read)
    - Query performansını test et
    - _Requirements: 8.4_

  - [x] 9.3 Async processing (opsiyonel)

    - Celery entegrasyonu
    - Model eğitimini arka planda çalıştır
    - Bildirim gönderimini async yap
    - _Requirements: 8.2, 8.3_



- [ ] 10. Raporlama ve analitik
  - [ ] 10.1 Rapor oluşturma fonksiyonları
    - generate_weekly_report(): Haftalık anomali raporu
    - generate_monthly_report(): Aylık anomali raporu
    - export_to_pdf(): PDF export
    - export_to_excel(): Excel export
    - _Requirements: 10.1, 10.2_


  - [ ] 10.2 Grafik ve trend analizleri
    - Anomali trend grafikleri (Chart.js)
    - En sık tespit edilen anomali tipleri
    - Etkilenen ürünler ve odalar
    - Model performans grafikleri
    - _Requirements: 10.3, 10.4_

  - [x] 10.3 Otomatik rapor gönderimi

    - Aylık raporu otomatik oluştur
    - Admin kullanıcılara email ile gönder
    - _Requirements: 10.5_

- [ ] 11. Integration ve end-to-end testler
  - [ ]* 11.1 End-to-end flow testleri
    - Veri toplama → Anomali tespiti → Alert oluşturma flow'u test et
    - Model eğitimi → Model kullanımı flow'u test et
    - Alert oluşturma → Bildirim gönderme flow'u test et
    - _Requirements: Tüm requirements_

  - [ ]* 11.2 Performance testleri
    - 1000+ oda verisi ile anomali tespiti
    - Dashboard yükleme süresi (< 2 saniye)
    - CPU kullanımı (< %30)
    - _Requirements: 8.1, 8.3, 8.5_

  - [ ]* 11.3 Load testing
    - Concurrent veri toplama testleri
    - Çoklu kullanıcı dashboard erişimi
    - _Requirements: 8.3_

- [x] 12. Deployment ve konfigürasyon




  - [x] 12.1 Environment variables

    - ML_ENABLED, ML_DATA_COLLECTION_INTERVAL, ML_TRAINING_SCHEDULE ekle
    - .env.example'a ekle
    - Railway environment variables'a ekle
    - _Requirements: Tüm requirements_

  - [x] 12.2 Dependencies


    - requirements.txt'e ML kütüphanelerini ekle (scikit-learn, pandas, APScheduler)
    - Redis dependency ekle (caching için)
    - _Requirements: Tüm requirements_

  - [x] 12.3 Migration ve deployment

    - Migration script'i çalıştır
    - İlk model eğitimini manuel başlat
    - Scheduler'ları aktif et
    - _Requirements: Tüm requirements_

- [ ] 13. Dokümantasyon ve kullanıcı eğitimi
  - [ ]* 13.1 Teknik dokümantasyon
    - API endpoint dokümantasyonu
    - ML algoritma açıklamaları
    - Troubleshooting guide
    - _Requirements: Tüm requirements_

  - [ ]* 13.2 Kullanıcı kılavuzu
    - ML Dashboard kullanım kılavuzu
    - Alert yönetimi kılavuzu
    - Yanlış pozitif işaretleme rehberi
    - _Requirements: 5.1, 5.3, 6.3_
