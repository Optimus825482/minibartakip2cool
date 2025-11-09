"""
Test kullanıcısı oluştur
"""
import psycopg2
from werkzeug.security import generate_password_hash

LOCAL = "postgresql://minibar_user:minibar123@localhost:5433/minibar_takip"

def main():
    conn = psycopg2.connect(LOCAL)
    cur = conn.cursor()
    
    # Test kullanıcısı bilgileri
    username = "testadmin"
    password = "test123"
    password_hash = generate_password_hash(password)
    
    # Kullanıcı var mı kontrol et
    cur.execute("SELECT id FROM kullanicilar WHERE kullanici_adi = %s", (username,))
    existing = cur.fetchone()
    
    if existing:
        # Şifreyi güncelle
        cur.execute("""
            UPDATE kullanicilar 
            SET sifre_hash = %s
            WHERE kullanici_adi = %s
        """, (password_hash, username))
        print(f"✅ Kullanıcı güncellendi: {username}")
    else:
        # Yeni kullanıcı oluştur
        cur.execute("""
            INSERT INTO kullanicilar 
            (kullanici_adi, sifre_hash, ad_soyad, rol, aktif, otel_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, password_hash, "Test Admin", "sistem_yoneticisi", True, 1))
        print(f"✅ Yeni kullanıcı oluşturuldu: {usernam