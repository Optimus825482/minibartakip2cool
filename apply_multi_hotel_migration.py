"""
Çoklu otel desteği için database migration'ı uygula
"""

from app import app, db
from sqlalchemy import text


def apply_migration():
    """Migration'ı uygula"""
    
    with app.app_context():
        try:
            print("=" * 60)
            print("DATABASE MIGRATION BAŞLIYOR")
            print("=" * 60)
            
            # 1. KullaniciOtel tablosunu oluştur
            print("\n[1/2] kullanici_otel tablosu oluşturuluyor...")
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS kullanici_otel (
                id SERIAL PRIMARY KEY,
                kullanici_id INTEGER NOT NULL,
                otel_id INTEGER NOT NULL,
                olusturma_tarihi TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_kullanici_otel_kullanici 
                    FOREIGN KEY (kullanici_id) 
                    REFERENCES kullanicilar(id) 
                    ON DELETE CASCADE,
                CONSTRAINT fk_kullanici_otel_otel 
                    FOREIGN KEY (otel_id) 
                    REFERENCES oteller(id) 
                    ON DELETE CASCADE,
                CONSTRAINT uq_kullanici_otel 
                    UNIQUE (kullanici_id, otel_id)
            );
            """
            
            db.session.execute(text(create_table_sql))
            print("   ✅ kullanici_otel tablosu oluşturuldu")
            
            # Index oluştur
            index_sql = """
            CREATE INDEX IF NOT EXISTS idx_kullanici_otel 
            ON kullanici_otel (kullanici_id, otel_id);
            """
            db.session.execute(text(index_sql))
            print("   ✅ Index oluşturuldu")
            
            # 2. Kullanicilar tablosuna otel_id alanı ekle
            print("\n[2/2] kullanicilar tablosuna otel_id alanı ekleniyor...")
            
            # Önce kolon var mı kontrol et
            check_column_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='kullanicilar' AND column_name='otel_id';
            """
            result = db.session.execute(text(check_column_sql))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                add_column_sql = """
                ALTER TABLE kullanicilar 
                ADD COLUMN otel_id INTEGER;
                """
                db.session.execute(text(add_column_sql))
                print("   ✅ otel_id alanı eklendi")
                
                # Foreign key constraint ekle
                fk_sql = """
                ALTER TABLE kullanicilar 
                ADD CONSTRAINT fk_kullanici_otel 
                FOREIGN KEY (otel_id) 
                REFERENCES oteller(id) 
                ON DELETE SET NULL;
                """
                db.session.execute(text(fk_sql))
                print("   ✅ Foreign key constraint eklendi")
            else:
                print("   ℹ️  otel_id alanı zaten mevcut")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ MIGRATION BAŞARIYLA TAMAMLANDI!")
            print("=" * 60)
            print()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print("\n" + "=" * 60)
            print("❌ MIGRATION HATASI!")
            print("=" * 60)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    apply_migration()
