#!/usr/bin/env python3
"""
MySQL to PostgreSQL Migration Script
Docker ortamında MySQL'den PostgreSQL'e veri aktarımı yapar
"""

import os
import sys
from datetime import datetime, timezone
from utils.migration_manager import MigrationManager
from utils.data_validator import DataValidator


def main():
    """Ana migration fonksiyonu"""
    
    print("\n" + "="*70)
    print("🚀 MySQL to PostgreSQL Migration Tool")
    print("="*70)
    
    # Connection strings
    mysql_url = "mysql+pymysql://minibar:518518Erkan@localhost:3306/minibar_takip"
    postgres_url = "postgresql://minibar_user:minibar123@localhost:5433/minibar_takip"
    
    print(f"\n📍 Source (MySQL):      {mysql_url.split('@')[1]}")
    print(f"📍 Target (PostgreSQL): {postgres_url.split('@')[1]}")
    
    # Onay al
    print("\n⚠️  WARNING: Bu işlem PostgreSQL veritabanındaki mevcut verileri etkileyebilir!")
    response = input("\nDevam etmek istiyor musunuz? (yes/no): ")
    
    if response.lower() not in ['yes', 'y', 'evet', 'e']:
        print("\n❌ Migration iptal edildi.")
        return
    
    # Migration başlat
    print("\n" + "="*70)
    print("📦 Migration başlatılıyor...")
    print("="*70)
    
    manager = None
    try:
        # Migration Manager oluştur
        manager = MigrationManager(mysql_url, postgres_url)
        
        # Tüm tabloları migrate et
        result = manager.migrate_all()
        
        if result['success']:
            print("\n" + "="*70)
            print("✅ Migration başarıyla tamamlandı!")
            print("="*70)
            
            # Validation yap
            print("\n🔍 Veri doğrulama başlatılıyor...")
            validator = DataValidator(mysql_url, postgres_url)
            validation_result = validator.validate_all()
            
            if validation_result['success']:
                print("\n✅ Tüm validasyon kontrolleri başarılı!")
            else:
                print("\n⚠️  Bazı validasyon kontrolleri başarısız!")
                print(f"Başarısız kontroller: {len(validation_result['failed_checks'])}")
                
                for check in validation_result['failed_checks'][:5]:
                    print(f"   - {check}")
        else:
            print("\n❌ Migration hatalarla tamamlandı!")
            print(f"Toplam hata sayısı: {len(result['stats']['errors'])}")
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        if manager:
            manager.close()
            print("\n🔌 Bağlantılar kapatıldı.")
    
    print("\n" + "="*70)
    print("🏁 Migration işlemi tamamlandı")
    print("="*70)


if __name__ == "__main__":
    main()
