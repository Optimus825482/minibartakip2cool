"""
Mevcut Odalar İçin QR Kod Oluşturma Scripti
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Oda
from utils.qr_service import QRKodService


def generate_qr_for_all_odalar(dry_run=False):
    """Tüm aktif odalar için QR kod oluştur"""
    
    with app.app_context():
        print("=" * 60)
        print("MEVCUT ODALAR İÇİN QR KOD OLUŞTURMA")
        print("=" * 60)
        print()
        
        if dry_run:
            print("⚠️  DRY RUN MODU - Değişiklikler kaydedilmeyecek")
            print()
        
        # Aktif odaları getir
        odalar = Oda.query.filter_by(aktif=True).all()
        
        if not odalar:
            print("❌ Aktif oda bulunamadı")
            return
        
        print(f"📊 Toplam {len(odalar)} aktif oda bulundu")
        print()
        
        # QR'sız odaları say
        qrsiz_odalar = [oda for oda in odalar if not oda.qr_kod_token]
        print(f"🔍 QR kodu olmayan oda sayısı: {len(qrsiz_odalar)}")
        print()
        
        if not qrsiz_odalar:
            print("✅ Tüm odalarda QR kod mevcut!")
            return
        
        # Onay al
        if not dry_run:
            cevap = input(f"❓ {len(qrsiz_odalar)} oda için QR kod oluşturulsun mu? (E/H): ")
            if cevap.upper() != 'E':
                print("❌ İşlem iptal edildi")
                return
            print()
        
        # QR kodları oluştur
        basarili = 0
        basarisiz = 0
        
        for i, oda in enumerate(qrsiz_odalar, 1):
            try:
                print(f"[{i}/{len(qrsiz_odalar)}] Oda {oda.oda_no}...", end=" ")
                
                result = QRKodService.create_qr_for_oda(oda)
                
                if result['success']:
                    basarili += 1
                    print("✅")
                else:
                    basarisiz += 1
                    print(f"❌ {result.get('error', 'Bilinmeyen hata')}")
                
                # Her 50 odada bir commit (dry run değilse)
                if not dry_run and (i % 50 == 0):
                    db.session.commit()
                    print(f"   💾 {i} oda kaydedildi")
                    
            except Exception as e:
                basarisiz += 1
                print(f"❌ Hata: {str(e)}")
        
        # Final commit
        if not dry_run:
            db.session.commit()
        
        print()
        print("=" * 60)
        print("ÖZET")
        print("=" * 60)
        print(f"✅ Başarılı: {basarili}")
        print(f"❌ Başarısız: {basarisiz}")
        print(f"📊 Toplam: {len(qrsiz_odalar)}")
        
        if dry_run:
            print()
            print("⚠️  DRY RUN - Değişiklikler kaydedilmedi")
        else:
            print()
            print("✅ İşlem tamamlandı!")


if __name__ == '__main__':
    # Komut satırı argümanları
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    generate_qr_for_all_odalar(dry_run=dry_run)
