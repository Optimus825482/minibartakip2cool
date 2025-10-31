"""
Audit Logs kullanici_id kolonunu nullable yap
"""

from app import app, db

def update_audit_log_schema():
    """kullanici_id kolonunu nullable yap"""
    with app.app_context():
        try:
            print("🔧 Audit logs tablosu güncelleniyor...")
            
            # MySQL için ALTER TABLE komutu
            db.session.execute(db.text("""
                ALTER TABLE audit_logs 
                MODIFY COLUMN kullanici_id INT NULL
            """))
            
            db.session.commit()
            print("✅ kullanici_id kolonu başarıyla nullable yapıldı!")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    update_audit_log_schema()
