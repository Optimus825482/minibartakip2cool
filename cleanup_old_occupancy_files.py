"""
Eski doluluk dosyalarını temizleme script'i
4 günden eski Excel dosyalarını otomatik siler

Kullanım:
    python cleanup_old_occupancy_files.py

Cron Job (Her gün saat 02:00):
    0 2 * * * cd /path/to/app && python cleanup_old_occupancy_files.py >> logs/cleanup.log 2>&1
"""

from app import app
from utils.file_management_service import FileManagementService
from datetime import datetime


def main():
    """Ana temizleme fonksiyonu"""
    with app.app_context():
        print("=" * 60)
        print(f"DOSYA TEMİZLEME BAŞLADI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Eski dosyaları temizle
            result = FileManagementService.cleanup_old_files()
            
            if result['success']:
                print(f"\n✅ Başarılı: {result['message']}")
                print(f"   Silinen dosya sayısı: {result['deleted_count']}")
            else:
                print(f"\n❌ Hata: {result['message']}")
            
            print("\n" + "=" * 60)
            print("DOSYA TEMİZLEME TAMAMLANDI")
            print("=" * 60)
            
            return result['success']
            
        except Exception as e:
            print(f"\n❌ Kritik Hata: {str(e)}")
            print("\n" + "=" * 60)
            print("DOSYA TEMİZLEME BAŞARISIZ")
            print("=" * 60)
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
