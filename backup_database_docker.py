"""
Docker PostgreSQL Veritabanı Yedekleme Script'i
Docker container içinden yedek alır
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

def backup_database_docker():
    """Docker PostgreSQL container'ından yedek al"""
    
    # Veritabanı bilgileri
    db_name = os.getenv('DB_NAME', 'minibar_takip')
    db_user = os.getenv('DB_USER', 'postgres')
    
    # Docker container adı
    container_name = os.getenv('POSTGRES_CONTAINER', 'minibar_postgres')
    
    # Yedek klasörü
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Yedek dosya adı (tarih-saat ile)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'minibar_backup_{timestamp}.sql'
    backup_path = os.path.join(backup_dir, backup_file)
    
    print("=" * 60)
    print("DOCKER POSTGRESQL VERİTABANI YEDEKLEME")
    print("=" * 60)
    print(f"\nVeritabanı: {db_name}")
    print(f"Container: {container_name}")
    print(f"Yedek Dosyası: {backup_path}")
    print()
    
    try:
        # Önce container'ın çalıştığını kontrol et
        print("Docker container kontrol ediliyor...")
        check_cmd = ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}']
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        
        if container_name not in result.stdout:
            print()
            print("=" * 60)
            print("❌ HATA: PostgreSQL container çalışmıyor!")
            print("=" * 60)
            print(f"\nContainer adı: {container_name}")
            print("\nÇalışan container'ları görmek için:")
            print("  docker ps")
            print()
            return False
        
        print("✓ Container çalışıyor")
        print()
        print("Yedekleme başlıyor...")
        
        # Docker exec ile pg_dump çalıştır
        cmd = [
            'docker', 'exec', '-t', container_name,
            'pg_dump',
            '-U', db_user,
            '-d', db_name,
            '--no-owner',
            '--no-acl'
        ]
        
        # Komutu çalıştır ve çıktıyı dosyaya yaz
        with open(backup_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode == 0:
            # Dosya boyutunu al
            file_size = os.path.getsize(backup_path)
            file_size_mb = file_size / (1024 * 1024)
            
            print()
            print("=" * 60)
            print("✅ YEDEKLEME BAŞARILI!")
            print("=" * 60)
            print(f"\nYedek Dosyası: {backup_path}")
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
            
            # Hatalı dosyayı sil
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            return False
            
    except FileNotFoundError:
        print()
        print("=" * 60)
        print("❌ HATA: Docker bulunamadı!")
        print("=" * 60)
        print()
        print("Docker kurulu değil veya PATH'de değil.")
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
        
        # Hatalı dosyayı sil
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
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
    success = backup_database_docker()
    
    # Çıkış kodu
    exit(0 if success else 1)
