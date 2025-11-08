"""
Migration sonuçlarını detaylı kontrol eden test script'i
"""

from app import app, db
from models import Otel, Kat, Kullanici, KullaniciOtel


def test_migration_detailed():
    """Migration sonuçlarını detaylı kontrol et"""
    
    with app.app_context():
        print("=" * 70)
        print("DETAYLI MİGRASYON DOĞRULAMA TESTİ")
        print("=" * 70)
        
        # 1. Otel Detayları
        print("\n[1] OTEL DETAYLARI")
        print("-" * 70)
        oteller = Otel.query.all()
        print(f"Toplam Otel Sayısı: {len(oteller)}")
        
        for otel in oteller:
            print(f"\n  📍 {otel.ad} (ID: {otel.id})")
            print(f"     - Adres: {otel.adres or 'Belirtilmemiş'}")
            print(f"     - Telefon: {otel.telefon or 'Belirtilmemiş'}")
            print(f"     - Email: {otel.email or 'Belirtilmemiş'}")
            print(f"     - Aktif: {'✓' if otel.aktif else '✗'}")
            print(f"     - Kat Sayısı: {len(otel.katlar)}")
            print(f"     - Depo Sorumlusu: {otel.get_depo_sorumlu_sayisi()}")
            print(f"     - Kat Sorumlusu: {otel.get_kat_sorumlu_sayisi()}")
        
        # 2. Kat Detayları
        print("\n[2] KAT DETAYLARI")
        print("-" * 70)
        katlar = Kat.query.all()
        print(f"Toplam Kat Sayısı: {len(katlar)}")
        
        for kat in katlar:
            otel_adi = kat.otel.ad if kat.otel else "Atanmamış"
            print(f"  🏢 {kat.kat_adi} (ID: {kat.id}) → {otel_adi}")
            print(f"     - Kat No: {kat.kat_no}")
            print(f"     - Oda Sayısı: {len(kat.odalar)}")
            print(f"     - Aktif: {'✓' if kat.aktif else '✗'}")
        
        # 3. Kat Sorumlusu Detayları
        print("\n[3] KAT SORUMLUSU DETAYLARI")
        print("-" * 70)
        kat_sorumlu_list = Kullanici.query.filter_by(rol='kat_sorumlusu').all()
        print(f"Toplam Kat Sorumlusu: {len(kat_sorumlu_list)}")
        
        for kullanici in kat_sorumlu_list:
            otel_adi = kullanici.otel.ad if kullanici.otel else "Atanmamış"
            print(f"  👤 {kullanici.ad} {kullanici.soyad} ({kullanici.kullanici_adi})")
            print(f"     - Otel: {otel_adi}")
            print(f"     - Email: {kullanici.email or 'Belirtilmemiş'}")
            print(f"     - Telefon: {kullanici.telefon or 'Belirtilmemiş'}")
            print(f"     - Aktif: {'✓' if kullanici.aktif else '✗'}")
        
        # 4. Depo Sorumlusu Detayları
        print("\n[4] DEPO SORUMLUSU DETAYLARI")
        print("-" * 70)
        depo_sorumlu_list = Kullanici.query.filter_by(rol='depo_sorumlusu').all()
        print(f"Toplam Depo Sorumlusu: {len(depo_sorumlu_list)}")
        
        for kullanici in depo_sorumlu_list:
            atamalar = KullaniciOtel.query.filter_by(kullanici_id=kullanici.id).all()
            print(f"  👤 {kullanici.ad} {kullanici.soyad} ({kullanici.kullanici_adi})")
            print(f"     - Atanan Otel Sayısı: {len(atamalar)}")
            
            for atama in atamalar:
                otel = Otel.query.get(atama.otel_id)
                print(f"       • {otel.ad} (ID: {otel.id})")
            
            print(f"     - Email: {kullanici.email or 'Belirtilmemiş'}")
            print(f"     - Telefon: {kullanici.telefon or 'Belirtilmemiş'}")
            print(f"     - Aktif: {'✓' if kullanici.aktif else '✗'}")
        
        # 5. KullaniciOtel İlişkileri
        print("\n[5] KULLANICI-OTEL İLİŞKİLERİ")
        print("-" * 70)
        iliskiler = KullaniciOtel.query.all()
        print(f"Toplam İlişki Sayısı: {len(iliskiler)}")
        
        for iliski in iliskiler:
            kullanici = Kullanici.query.get(iliski.kullanici_id)
            otel = Otel.query.get(iliski.otel_id)
            print(f"  🔗 {kullanici.kullanici_adi} → {otel.ad}")
            print(f"     - Oluşturma Tarihi: {iliski.olusturma_tarihi}")
        
        # 6. Veri Bütünlüğü Kontrolleri
        print("\n[6] VERİ BÜTÜNLÜĞÜ KONTROLLERİ")
        print("-" * 70)
        
        # Atanmamış katlar
        atanmamis_katlar = Kat.query.filter(
            (Kat.otel_id.is_(None)) | (Kat.otel_id == 0)
        ).count()
        print(f"  ✓ Atanmamış Kat: {atanmamis_katlar}")
        
        # Atanmamış kat sorumluları
        atanmamis_kat_sorumlu = Kullanici.query.filter_by(
            rol='kat_sorumlusu'
        ).filter(
            (Kullanici.otel_id.is_(None)) | (Kullanici.otel_id == 0)
        ).count()
        print(f"  ✓ Atanmamış Kat Sorumlusu: {atanmamis_kat_sorumlu}")
        
        # Hiç otele atanmamış depo sorumluları
        depo_sorumlu_ids = [d.id for d in depo_sorumlu_list]
        atanmamis_depo = []
        for ds_id in depo_sorumlu_ids:
            atama_sayisi = KullaniciOtel.query.filter_by(kullanici_id=ds_id).count()
            if atama_sayisi == 0:
                atanmamis_depo.append(ds_id)
        
        print(f"  ✓ Hiç Otele Atanmamış Depo Sorumlusu: {len(atanmamis_depo)}")
        
        # Duplicate kontrol
        duplicates = db.session.query(
            KullaniciOtel.kullanici_id,
            KullaniciOtel.otel_id,
            db.func.count(KullaniciOtel.id)
        ).group_by(
            KullaniciOtel.kullanici_id,
            KullaniciOtel.otel_id
        ).having(
            db.func.count(KullaniciOtel.id) > 1
        ).all()
        
        print(f"  ✓ Duplicate İlişki: {len(duplicates)}")
        
        # 7. Sonuç
        print("\n" + "=" * 70)
        print("TEST SONUCU")
        print("=" * 70)
        
        basarili = (
            len(oteller) > 0 and
            atanmamis_katlar == 0 and
            atanmamis_kat_sorumlu == 0 and
            len(atanmamis_depo) == 0 and
            len(duplicates) == 0
        )
        
        if basarili:
            print("✅ TÜM KONTROLLER BAŞARILI!")
            print("\nMigration tamamen başarılı ve veri bütünlüğü sağlanmış.")
        else:
            print("⚠️  BAZI KONTROLLER UYARI VERDİ")
            print("\nLütfen yukarıdaki detayları inceleyin.")
        
        print()
        return basarili


if __name__ == '__main__':
    test_migration_detailed()
