"""
Veritabanı İşlem Verilerini Temizleme Scripti

Bu script şunları SİLER:
- Tüm stok hareketleri (giriş/çıkış kayıtları)
- Tüm zimmet kayıtları (zimmet_detay dahil)
- Tüm minibar işlemleri (minibar_islem_detay dahil)
- Tüm ürünler
- Tüm ürün grupları

Bu script şunları KORUR:
- Kullanıcılar (sistem yöneticisi, admin, depo sorumlusu, kat sorumlusu)
- Oteller
- Katlar
- Odalar
- Personel tanımları

UYARI: Bu işlem geri alınamaz!
"""

from app import app, db
from models import (
    StokHareket, 
    PersonelZimmet, 
    PersonelZimmetDetay,
    MinibarIslem,
    MinibarIslemDetay,
    Urun,
    UrunGrup
)

def temizle_islem_verileri():
    """İşlem verilerini temizle, tanımları koru"""
    
    with app.app_context():
        try:
            print("🔄 Veritabanı temizliği başlıyor...")
            print("=" * 60)
            
            # 1. Minibar İşlem Detaylarını Sil
            minibar_detay_count = MinibarIslemDetay.query.delete()
            print(f"✅ {minibar_detay_count} adet minibar işlem detayı silindi")
            
            # 2. Minibar İşlemlerini Sil
            minibar_islem_count = MinibarIslem.query.delete()
            print(f"✅ {minibar_islem_count} adet minibar işlemi silindi")
            
            # 3. Personel Zimmet Detaylarını Sil
            zimmet_detay_count = PersonelZimmetDetay.query.delete()
            print(f"✅ {zimmet_detay_count} adet zimmet detayı silindi")
            
            # 4. Personel Zimmetlerini Sil
            zimmet_count = PersonelZimmet.query.delete()
            print(f"✅ {zimmet_count} adet zimmet kaydı silindi")
            
            # 5. Stok Hareketlerini Sil
            stok_hareket_count = StokHareket.query.delete()
            print(f"✅ {stok_hareket_count} adet stok hareketi silindi")
            
            # 6. Ürünleri Sil
            urun_count = Urun.query.delete()
            print(f"✅ {urun_count} adet ürün silindi")
            
            # 7. Ürün Gruplarını Sil
            grup_count = UrunGrup.query.delete()
            print(f"✅ {grup_count} adet ürün grubu silindi")
            
            # Değişiklikleri kaydet
            db.session.commit()
            
            print("=" * 60)
            print("✅ Veritabanı temizliği başarıyla tamamlandı!")
            print()
            print("📋 Korunan Veriler:")
            print("   - Kullanıcı hesapları")
            print("   - Otel tanımları")
            print("   - Kat tanımları")
            print("   - Oda tanımları")
            print("   - Personel tanımları")
            print()
            print("🎯 Şimdi yapabilirsiniz:")
            print("   1. Ürün grupları tanımlayabilirsiniz")
            print("   2. Ürünler tanımlayabilirsiniz")
            print("   3. Stok girişi yapabilirsiniz")
            print("   4. Personele zimmet atayabilirsiniz")
            print("   5. Minibar işlemlerini başlatabilirsiniz")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ HATA: {str(e)}")
            print("⚠️ Veritabanı değişiklikleri geri alındı.")
            raise

if __name__ == '__main__':
    print("⚠️  UYARI: Bu işlem şunları silecek:")
    print("   - Tüm işlem kayıtları (stok, zimmet, minibar)")
    print("   - Tüm ürünler")
    print("   - Tüm ürün grupları")
    print()
    print("✅ Korunacaklar:")
    print("   - Kullanıcılar, Oteller, Katlar, Odalar, Personel")
    print()
    onay = input("Devam etmek istiyor musunuz? (EVET yazın): ")
    
    if onay.strip().upper() == "EVET":
        temizle_islem_verileri()
    else:
        print("❌ İşlem iptal edildi.")
