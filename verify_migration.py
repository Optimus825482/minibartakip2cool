"""
Migration sonrası veri bütünlüğü kontrolü
"""

from app import app, db
from models import Otel, Kat, Kullanici, KullaniciOtel
from sqlalchemy import func


def verify_migration():
    """Migration sonrası veri bütünlüğünü kontrol et"""
    
    with app.app_context():
        print("=" * 60)
        print("VERİ BÜTÜNLÜĞÜ KONTROLÜ")
        print("=" * 60)
        
        # 1. Otel kontrolü
        print("\n[1/5] Otel Kontrolü")
        print("-" * 60)
        oteller = Otel.query.all()
        print(f"Toplam Otel Sayısı: {len(oteller)}")
        for otel in oteller:
            print(f"  - {otel.ad} (ID: {otel.id}, Aktif: {otel.aktif})")
        
        # 2. Kat kontrolü
        print("\n[2/5] Kat Kontrolü")
        print("-" * 60)
        toplam_kat = Kat.query.count()
        otel_atanmis_kat = Kat.query.filter(Kat.otel_id.isnot(None)).count()
        otel_atanmamis_kat = Kat.query.filter(Kat.otel_id.is_(None)).count()
        
        print(f"Toplam Kat: {toplam_kat}")
        print(f"Otele Atanmış Kat: {otel_atanmis_kat}")
        print(f"Otele Atanmamış Kat: {otel_atanmamis_kat}")
        
        if otel_atanmamis_kat > 0:
            print("\n⚠️  UYARI: Otele atanmamış katlar var!")
            atanmamis_katlar = Kat.query.filter(Kat.otel_id.is_(None)).all()
            for kat in atanmamis_katlar:
                print(f"  - Kat ID: {kat.id}, Ad: {kat.ad}")
        
        # Otel bazında kat dağılımı
        print("\nOtel Bazında Kat Dağılımı:")
        kat_dagilim = db.session.query(
            Otel.ad,
            func.count(Kat.id).label('kat_sayisi')
        ).join(Kat, Kat.otel_id == Otel.id).group_by(Otel.ad).all()
        
        for otel_ad, kat_sayisi in kat_dagilim:
            print(f"  - {otel_ad}: {kat_sayisi} kat")
        
        # 3. Kat Sorumlusu kontrolü
        print("\n[3/5] Kat Sorumlusu Kontrolü")
        print("-" * 60)
        toplam_kat_sorumlu = Kullanici.query.filter_by(rol='kat_sorumlusu').count()
        otel_atanmis_kat_sorumlu = Kullanici.query.filter_by(
            rol='kat_sorumlusu'
        ).filter(Kullanici.otel_id.isnot(None)).count()
        otel_atanmamis_kat_sorumlu = Kullanici.query.filter_by(
            rol='kat_sorumlusu'
        ).filter(Kullanici.otel_id.is_(None)).count()
        
        print(f"Toplam Kat Sorumlusu: {toplam_kat_sorumlu}")
        print(f"Otele Atanmış: {otel_atanmis_kat_sorumlu}")
        print(f"Otele Atanmamış: {otel_atanmamis_kat_sorumlu}")
        
        if otel_atanmamis_kat_sorumlu > 0:
            print("\n⚠️  UYARI: Otele atanmamış kat sorumluları var!")
            atanmamis = Kullanici.query.filter_by(
                rol='kat_sorumlusu'
            ).filter(Kullanici.otel_id.is_(None)).all()
            for kullanici in atanmamis:
                print(f"  - {kullanici.kullanici_adi} (ID: {kullanici.id})")
        
        # Otel bazında kat sorumlusu dağılımı
        print("\nOtel Bazında Kat Sorumlusu Dağılımı:")
        kat_sorumlu_dagilim = db.session.query(
            Otel.ad,
            func.count(Kullanici.id).label('sorumlu_sayisi')
        ).join(
            Kullanici, Kullanici.otel_id == Otel.id
        ).filter(
            Kullanici.rol == 'kat_sorumlusu'
        ).group_by(Otel.ad).all()
        
        for otel_ad, sorumlu_sayisi in kat_sorumlu_dagilim:
            print(f"  - {otel_ad}: {sorumlu_sayisi} kat sorumlusu")
        
        # 4. Depo Sorumlusu kontrolü
        print("\n[4/5] Depo Sorumlusu Kontrolü")
        print("-" * 60)
        toplam_depo_sorumlu = Kullanici.query.filter_by(rol='depo_sorumlusu').count()
        print(f"Toplam Depo Sorumlusu: {toplam_depo_sorumlu}")
        
        # KullaniciOtel kayıtları
        toplam_atama = KullaniciOtel.query.count()
        print(f"Toplam Otel Ataması (KullaniciOtel): {toplam_atama}")
        
        # Depo sorumlusu bazında atamalar
        print("\nDepo Sorumlusu Bazında Otel Atamaları:")
        depo_sorumlular = Kullanici.query.filter_by(rol='depo_sorumlusu').all()
        for depo_sorumlu in depo_sorumlular:
            atamalar = KullaniciOtel.query.filter_by(
                kullanici_id=depo_sorumlu.id
            ).join(Otel).all()
            otel_adlari = [atama.otel.ad for atama in atamalar]
            print(f"  - {depo_sorumlu.kullanici_adi}: {len(otel_adlari)} otel")
            for otel_ad in otel_adlari:
                print(f"    • {otel_ad}")
        
        # 5. İlişki bütünlüğü kontrolü
        print("\n[5/5] İlişki Bütünlüğü Kontrolü")
        print("-" * 60)
        
        # Geçersiz otel_id'li katlar
        gecersiz_kat = db.session.query(Kat).filter(
            Kat.otel_id.isnot(None)
        ).filter(
            ~Kat.otel_id.in_(db.session.query(Otel.id))
        ).count()
        
        print(f"Geçersiz otel_id'li kat sayısı: {gecersiz_kat}")
        if gecersiz_kat > 0:
            print("❌ HATA: Bazı katlar var olmayan otellere atanmış!")
        else:
            print("✅ Tüm katlar geçerli otellere atanmış")
        
        # Geçersiz otel_id'li kat sorumluları
        gecersiz_kat_sorumlu = db.session.query(Kullanici).filter(
            Kullanici.rol == 'kat_sorumlusu',
            Kullanici.otel_id.isnot(None)
        ).filter(
            ~Kullanici.otel_id.in_(db.session.query(Otel.id))
        ).count()
        
        print(f"Geçersiz otel_id'li kat sorumlusu sayısı: {gecersiz_kat_sorumlu}")
        if gecersiz_kat_sorumlu > 0:
            print("❌ HATA: Bazı kat sorumluları var olmayan otellere atanmış!")
        else:
            print("✅ Tüm kat sorumluları geçerli otellere atanmış")
        
        # Geçersiz KullaniciOtel kayıtları
        gecersiz_kullanici_otel = db.session.query(KullaniciOtel).filter(
            ~KullaniciOtel.kullanici_id.in_(db.session.query(Kullanici.id)) |
            ~KullaniciOtel.otel_id.in_(db.session.query(Otel.id))
        ).count()
        
        print(f"Geçersiz KullaniciOtel kaydı sayısı: {gecersiz_kullanici_otel}")
        if gecersiz_kullanici_otel > 0:
            print("❌ HATA: Bazı KullaniciOtel kayıtları geçersiz!")
        else:
            print("✅ Tüm KullaniciOtel kayıtları geçerli")
        
        # Özet
        print("\n" + "=" * 60)
        print("ÖZET")
        print("=" * 60)
        
        hata_sayisi = 0
        if otel_atanmamis_kat > 0:
            hata_sayisi += 1
            print("❌ Otele atanmamış katlar var")
        
        if otel_atanmamis_kat_sorumlu > 0:
            hata_sayisi += 1
            print("❌ Otele atanmamış kat sorumluları var")
        
        if gecersiz_kat > 0:
            hata_sayisi += 1
            print("❌ Geçersiz otel_id'li katlar var")
        
        if gecersiz_kat_sorumlu > 0:
            hata_sayisi += 1
            print("❌ Geçersiz otel_id'li kat sorumluları var")
        
        if gecersiz_kullanici_otel > 0:
            hata_sayisi += 1
            print("❌ Geçersiz KullaniciOtel kayıtları var")
        
        if hata_sayisi == 0:
            print("✅ TÜM KONTROLLER BAŞARILI!")
            print("✅ Veri bütünlüğü sağlanmış")
        else:
            print(f"\n⚠️  {hata_sayisi} adet sorun tespit edildi!")
        
        print()


if __name__ == '__main__':
    verify_migration()
