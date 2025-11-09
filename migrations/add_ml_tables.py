"""
ML Anomaly Detection System - Database Migration
Tarih: 2025-11-09
Açıklama: ML metrik, model, alert ve training log tablolarını ekler
"""

from flask import Flask
from models import db
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması oluştur
app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

def upgrade():
    """ML tablolarını oluştur"""
    with app.app_context():
        try:
            print("🚀 ML tabloları oluşturuluyor...")
            
            # Tüm tabloları oluştur (sadece yeni olanlar oluşturulur)
            db.create_all()
            
            print("✅ ML tabloları başarıyla oluşturuldu!")
            print("   - ml_metrics")
            print("   - ml_models")
            print("   - ml_alerts")
            print("   - ml_training_logs")
            print("   - Index'ler oluşturuldu")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            raise

def downgrade():
    """ML tablolarını sil (dikkatli kullan!)"""
    with app.app_context():
        try:
            print("⚠️  ML tabloları siliniyor...")
            
            # Tabloları sil
            db.session.execute(db.text('DROP TABLE IF EXISTS ml_training_logs CASCADE'))
            db.session.execute(db.text('DROP TABLE IF EXISTS ml_alerts CASCADE'))
            db.session.execute(db.text('DROP TABLE IF EXISTS ml_models CASCADE'))
            db.session.execute(db.text('DROP TABLE IF EXISTS ml_metrics CASCADE'))
            
            # Enum tiplerini sil
            db.session.execute(db.text('DROP TYPE IF EXISTS ml_metric_type CASCADE'))
            db.session.execute(db.text('DROP TYPE IF EXISTS ml_alert_type CASCADE'))
            db.session.execute(db.text('DROP TYPE IF EXISTS ml_alert_severity CASCADE'))
            
            db.session.commit()
            
            print("✅ ML tabloları başarıyla silindi!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Hata: {str(e)}")
            raise

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        confirm = input("⚠️  TÜM ML VERİLERİ SİLİNECEK! Emin misiniz? (yes/no): ")
        if confirm.lower() == 'yes':
            downgrade()
        else:
            print("❌ İşlem iptal edildi.")
    else:
        upgrade()
