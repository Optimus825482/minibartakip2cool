"""
PostgreSQL Veritabanı Yedekleme Script'i
Tüm tabloları ve verileri yedekler
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def backup_database():
    """PostgreSQL veritabanını yedekle"""
    
    # Veritabanı bilgileri
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'minibar_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    # Yedek klasörü
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Yedek dosya adı (tarih-saat ile)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'minibar_backup_{timestamp}.sql')
    
    print("=" * 60)
    print("POSTGRESQL VERİTABANI YEDEKLEME")
    print("=" * 60)
    print(f"\nVeritabanı: {db_name}")
    print(f"Host: {db_host}:{db_port}")
    print(f"Yedek Dosyası: {backup_file}")
    print()
    
    try:
        # Windows için PGPASSWORD ortam değişkeni
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password
        
        # pg_dump komutu
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-d', db_name,
            '-F', 'p',  # Plain text format
            '-f', backup_file,
            '--no-owner',
            '--no-acl',
            '--verbose'
        ]
        
        print("Yedekleme başlıyor...")
        print()
        
        # Komutu çalıştır
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Dosya boyutunu al
            file_size = os.path.getsize(backup_file)
            file_size_mb = file_size / (1024 * 1024)
            
            print()
            print("=" * 60)
            print("✅ YEDEKLEME BAŞARILI!")
            print("=" * 60)
            print(f"\nYedek Dosyası: {backup_file}")
            print(f"Dosya Boyutu: {file_size_mb:.2f} MB")
            print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            print()
            print("Yedek dosyasını güvenli bir yere kopyalayın!")
            print("=" * 60)
            return True
        else:
            print()
            print("=" * 60)
            print("❌ YEDEKLEME BAŞARISIZ!")
            print("=" * 60)
            print(f"\nHata: {result.stderr}")
            print()
            return False
            
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("❌ HATA: pg_dump bulunamadı!")
        print("=" * 60)
        print()
        print("PostgreSQL client tools kurulu değil.")
        print("Kurulum için:")
        print("  1. PostgreSQL'i indirin: https://www.postgresql.org/download/")
        print("  2. Sadece 'Command Line Tools' seçeneğini kurun")
        print("  3. PATH'e ekleyin")
        print()
        return False
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ BEKLENMEYEN HATA!")
        print("=" * 60)
        print(f"\nHata: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False


def list_backups():
    """Mevcut yedekleri listele"""
    backup_dir = 'backups'
    
    if not os.path.exists(backup_dir):
        print("Henüz yedek bulunamadı.")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
    
    if not backups:
        print("Henüz yedek bulunamadı.")
        return
    
    print()
    print("=" * 60)
    print("MEVCUT YEDEKLER")
    print("=" * 60)
    print()
    
    backups.sort(reverse=True)
    
    for backup in backups:
        file_path = os.path.join(backup_dir, backup)
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        print(f"📁 {backup}")
        print(f"   Boyut: {file_size_mb:.2f} MB")
        print(f"   Tarih: {file_time.strftime('%d.%m.%Y %H:%M:%S')}")
        print()


if __name__ == '__main__':
    # Önce mevcut yedekleri göster
    list_backups()
    
    # Yedekleme yap
    success = backup_database()
    
    # Çıkış kodu
    exit(0 if success else 1)
