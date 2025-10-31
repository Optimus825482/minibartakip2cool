"""
Audit Trail Tablosunu Oluşturma Scripti
"""

from app import app, db
from models import AuditLog

def create_audit_table():
    """Audit log tablosunu oluştur"""
    with app.app_context():
        try:
            # Tabloyu oluştur
            db.create_all()
            print("✅ Audit log tablosu başarıyla oluşturuldu!")
            
            # Index'leri kontrol et
            inspector = db.inspect(db.engine)
            indexes = inspector.get_indexes('audit_logs')
            
            print(f"\n📊 Oluşturulan Index'ler ({len(indexes)} adet):")
            for idx in indexes:
                print(f"  - {idx['name']}: {idx['column_names']}")
            
            print("\n✨ Audit Trail sistemi hazır!")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            db.session.rollback()


if __name__ == '__main__':
    create_audit_table()
