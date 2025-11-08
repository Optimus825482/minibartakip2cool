"""
Kullanicilar tablosuna depo_sorumlusu_id kolonu ekle
"""

from app import app, db
from sqlalchemy import text


def add_depo_sorumlusu_column():
    """depo_sorumlusu_id kolonunu ekle"""
    
    with app.app_context():
        try:
            print("=" * 60)
            print("DEPO SORUMLUSU İLİŞKİSİ EKLEME")
            print("=" * 60)
            
            # Kolon var mı kontrol et
            check_column_sql = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='kullanicilar' AND column_name='depo_sorumlusu_id';
            """
            result = db.session.execute(text(check_column_sql))
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("\n[1/2] depo_sorumlusu_id kolonu ekleniyor...")
                add_column_sql = """
                ALTER TABLE kullanicilar 
                ADD COLUMN depo_sorumlusu_id INTEGER;
                """
                db.session.execute(text(add_column_sql))
                print("   ✅ depo_sorumlusu_id kolonu eklendi")
                
                # Foreign key constraint ekle
                print("\n[2/2] Foreign key constraint ekleniyor...")
                fk_sql = """
                ALTER TABLE kullanicilar 
                ADD CONSTRAINT fk_kullanici_depo_sorumlusu 
                FOREIGN KEY (depo_sorumlusu_id) 
                REFERENCES kullanicilar(id) 
                ON DELETE SET NULL;
                """
                db.session.execute(text(fk_sql))
                print("   ✅ Foreign key constraint eklendi")
            else:
                print("   ℹ️  depo_sorumlusu_id kolonu zaten mevcut")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ İŞLEM BAŞARIYLA TAMAMLANDI!")
            print("=" * 60)
            print()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print("\n" + "=" * 60)
            print("❌ HATA!")
            print("=" * 60)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    add_depo_sorumlusu_column()
