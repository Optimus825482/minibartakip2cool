"""
Hem Railway hem Docker'da migration ve düzeltmeleri çalıştır
"""

import os
import sys
import subprocess


def run_railway_migration():
    """Railway'de migration çalıştır"""
    print("=" * 70)
    print("RAILWAY MİGRASYON VE DÜZELTME")
    print("=" * 70)
    
    try:
        # Railway env'i yükle
        print("\n[1] Railway environment yükleniyor...")
        with open('.env.railway', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("   ✅ Railway environment yüklendi")
        
        # Migration script'ini çalıştır
        print("\n[2] Railway migration çalıştırılıyor...")
        result = subprocess.run(
            ['python', 'railway_fix_migration.py'],
            input='evet\n',
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        if result.returncode == 0:
            print("   ✅ Railway migration başarılı!")
            return True
        else:
            print(f"   ❌ Railway migration hatası: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_docker_migration():
    """Docker'da migration çalıştır"""
    print("\n" + "=" * 70)
    print("DOCKER MİGRASYON VE DÜZELTME")
    print("=" * 70)
    
    try:
        # Docker env'i yükle
        print("\n[1] Docker environment yükleniyor...")
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("   ✅ Docker environment yüklendi")
        
        # Migration script'ini çalıştır
        print("\n[2] Docker migration çalıştırılıyor...")
        
        # Önce migrate_to_multi_hotel.py'yi çalıştır
        print("\n   [2.1] migrate_to_multi_hotel.py çalıştırılıyor...")
        result1 = subprocess.run(
            ['python', 'migrate_to_multi_hotel.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result1.stdout)
        if result1.returncode != 0:
            print(f"   ⚠️  Uyarı: {result1.stderr}")
        
        # Sonra fix_hotel_assignments.py'yi çalıştır
        print("\n   [2.2] fix_hotel_assignments.py çalıştırılıyor...")
        result2 = subprocess.run(
            ['python', 'fix_hotel_assignments.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result2.stdout)
        if result2.returncode == 0:
            print("   ✅ Docker migration başarılı!")
            return True
        else:
            print(f"   ❌ Docker migration hatası: {result2.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_all():
    """Her iki ortamı da doğrula"""
    print("\n" + "=" * 70)
    print("DOĞRULAMA")
    print("=" * 70)
    
    # Railway doğrulama
    print("\n[RAILWAY DOĞRULAMA]")
    try:
        with open('.env.railway', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        
        result = subprocess.run(
            ['python', 'verify_migration_test.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ Railway doğrulama hatası: {str(e)}")
    
    # Docker doğrulama
    print("\n[DOCKER DOĞRULAMA]")
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        
        result = subprocess.run(
            ['python', 'verify_migration_test.py'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ Docker doğrulama hatası: {str(e)}")


def main():
    """Ana fonksiyon"""
    print("\n" + "=" * 70)
    print("ÇOKLU ORTAM MİGRASYON VE DÜZELTME")
    print("=" * 70)
    print("\nBu script hem Railway hem Docker ortamlarında migration çalıştıracak.")
    print()
    
    # Railway migration
    railway_success = run_railway_migration()
    
    # Docker migration
    docker_success = run_docker_migration()
    
    # Doğrulama
    verify_all()
    
    # Sonuç
    print("\n" + "=" * 70)
    print("GENEL SONUÇ")
    print("=" * 70)
    
    if railway_success:
        print("✅ Railway: BAŞARILI")
    else:
        print("❌ Railway: BAŞARISIZ")
    
    if docker_success:
        print("✅ Docker: BAŞARILI")
    else:
        print("❌ Docker: BAŞARISIZ")
    
    if railway_success and docker_success:
        print("\n🎉 TÜM ORTAMLARDA MİGRASYON BAŞARILI!")
    else:
        print("\n⚠️  Bazı ortamlarda sorun var, lütfen kontrol edin.")
    
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
