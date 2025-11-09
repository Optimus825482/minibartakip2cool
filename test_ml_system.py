"""
ML Sistemi Test Scripti
Veri toplama, anomali tespiti ve model eğitimini test eder
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🧪 ML SİSTEMİ TEST")
print("=" * 60)
print()

from app import app, db

with app.app_context():
    print("1️⃣ Veri Toplama Testi...")
    try:
        from utils.ml.data_collector import DataCollector
        collector = DataCollector(db)
        
        stok_count = collector.collect_stok_metrics()
        tuketim_count = collector.collect_tuketim_metrics()
        dolum_count = collector.collect_dolum_metrics()
        
        print(f"   ✅ Stok metrikleri: {stok_count} kayıt")
        print(f"   ✅ Tüketim metrikleri: {tuketim_count} kayıt")
        print(f"   ✅ Dolum metrikleri: {dolum_count} kayıt")
        print()
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        print()
    
    print("2️⃣ Anomali Tespiti Testi...")
    try:
        from utils.ml.anomaly_detector import AnomalyDetector
        detector = AnomalyDetector(db)
        
        alert_count = detector.detect_all_anomalies()
        print(f"   ✅ {alert_count} anomali tespit edildi")
        print()
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        print()
    
    print("3️⃣ Stok Bitiş Tahmini Testi...")
    try:
        from utils.ml.metrics_calculator import MetricsCalculator
        calculator = MetricsCalculator(db)
        
        alert_count = calculator.check_stock_depletion_alerts()
        print(f"   ✅ {alert_count} stok bitiş uyarısı oluşturuldu")
        print()
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        print()
    
    print("4️⃣ Dashboard Metrikleri Testi...")
    try:
        from utils.ml.metrics_calculator import MetricsCalculator
        calculator = MetricsCalculator(db)
        
        metrics = calculator.get_dashboard_metrics()
        print(f"   ✅ Aktif alertler: {metrics.get('aktif_alert_count', 0)}")
        print(f"   ✅ Kritik ürünler: {metrics.get('kritik_urun_count', 0)}")
        print(f"   ✅ Stok metrikleri (24h): {metrics.get('stok_metrik_count_24h', 0)}")
        print()
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        print()
    
    print("5️⃣ Tablo İstatistikleri...")
    try:
        from models import MLMetric, MLModel, MLAlert, MLTrainingLog
        
        print(f"   📊 ml_metrics: {db.session.query(MLMetric).count()} kayıt")
        print(f"   📊 ml_models: {db.session.query(MLModel).count()} kayıt")
        print(f"   📊 ml_alerts: {db.session.query(MLAlert).count()} kayıt")
        print(f"   📊 ml_training_logs: {db.session.query(MLTrainingLog).count()} kayıt")
        print()
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        print()

print("=" * 60)
print("✅ TEST TAMAMLANDI!")
print("=" * 60)
