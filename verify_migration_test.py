"""
Migration sonuçlarını doğrulama script'i
"""

from app import app, db
from models import Otel, Kat, Kullanici, KullaniciOtel


def verify_migration():
    """Migration sonuçlarını doğrula"""
    
    with app.app_context():
        print("=" * 60)
        print("MİGRASYON DOĞRULAMA TESTİ")
        print("=" * 60)
        
        # 1. Merit Royal Diamond otelinin varlığını kontrol et
        print("\n[TEST 1] Merit Royal Diamond oteli kontrolü...")
        merit_otel = Otel.query.filter(
            Otel.ad.like('%Merit Royal Diamond%')
        ).first()
        
        if merit_otel:
            print(f"   ✅ BAŞARILI: Merit Royal Diamond oteli mevcut (ID: {merit_otel.id})")
            print(f"      - Adres: {merit_otel.adres or 'Belirtilmemiş'}")
            print(f"      - Telefon: {merit_otel.telefon or 'Belirtilmemiş'}")
            print(f"      - Aktif: {'Evet' if merit_otel.aktif else 'Hayır'}")
        else:
            print("   ❌ HATA: Merit Royal Diamond oteli bulunamadı!")
            return False
        
        # 2. Tüm katların otele atandığını kontrol et
        print("\n[TEST 2] Kat atamaları kontrolü...")
        tum_katlar = Kat.query.all()
        atanmamis_katlar = Kat.query.filter(
            (Kat.otel_id.is_(None)) | (Kat.otel_id == 0)
        ).all()
        
        print(f"   Toplam Kat Sayısı: {len(tum_katlar)}")
        print(f"   Merit Royal Diamond'a Atanan: {len([k for k in tum_katlar if k.otel_id == merit_otel.id])}")
        print(f"   Atanmamış Kat: {len(atanmamis_katlar)}")
        
        if len(atanmamis_katlar) == 0:
            print("   ✅ BAŞARILI: Tüm katlar bir otele atanmış")
        else:
            print(f"   ⚠️  UYARI: {len(atanmamis_katlar)} kat henüz otele atanmamış")
            for kat in atanmamis_katlar:
                print(f"      - Kat: {kat.kat_adi} (ID: {kat.id})")
        
        # 3. Kat sorumlularının otele atandığını kontrol et
        print("\n[TEST 3] Kat sorumlusu atamaları kontrolü...")
        kat_sorumlu_list = Kullanici.query.filter_by(rol='kat_sorumlusu').all()
        atanmamis_kat_sorumlu = [k for k in kat_sorumlu_list if not k.otel_id or k.otel_id == 0]
        
        print(f"   Toplam Kat Sorumlusu: {len(kat_sorumlu_list)}")
        print(f"   Merit Royal Diamond'a Atanan: {len([k for k in kat_sorumlu_list if k.otel_id == merit_otel.id])}")
        print(f"   Atanmamış: {len(atanmamis_kat_sorumlu)}")
        
        if len(atanmamis_kat_sorumlu) == 0:
            print("   ✅ BAŞARILI: Tüm kat sorumluları bir otele atanmış")
        else:
            print(f"   ⚠️  UYARI: {len(atanmamis_kat_sorumlu)} kat sorumlusu henüz otele atanmamış")
            for kullanici in atanmamis_kat_sorumlu:
                print(f"      - Kullanıcı: {kullanici.kullanici_adi} (ID: {kullanici.id})")
        
        # 4. Depo sorumlularının otele atandığını kontrol et
        print("\n[TEST 4] Depo sorumlusu atamaları kontrolü...")
        depo_sorumlu_list = Kullanici.query.filter_by(rol='depo_sorumlusu').all()
        
        print(f"   Toplam Depo Sorumlusu: {len(depo_sorumlu_list)}")
        
        for depo_sorumlu in depo_sorumlu_list:
            atamalar = KullaniciOtel.query.filter_by(kullanici_id=depo_sorumlu.id).all()
            merit_atama = KullaniciOtel.query.filter_by(
                kullanici_id=depo_sorumlu.id,
                otel_id=merit_otel.id
            ).first()
            
            print(f"   - {depo_sorumlu.kullanici_adi}: {len(atamalar)} otel ataması", end="")
            if merit_atama:
                print(" (Merit Royal Diamond ✓)")
            else:
                print(" (Merit Royal Diamond ✗)")
        
        atanmamis_depo = [d for d in depo_sorumlu_list 
                          if not KullaniciOtel.query.filter_by(kullanici_id=d.id).first()]
        
        if len(atanmamis_depo) == 0:
            print("   ✅ BAŞARILI: Tüm depo sorumluları en az bir otele atanmış")
        else:
            print(f"   ⚠️  UYARI: {len(atanmamis_depo)} depo sorumlusu hiçbir otele atanmamış")
        
        # 5. Genel özet
        print("\n" + "=" * 60)
        print("DOĞRULAMA ÖZETİ")
        print("=" * 60)
        
        basarili = (
            merit_otel is not None and
            len(atanmamis_katlar) == 0 and
            len(atanmamis_kat_sorumlu) == 0 and
            len(atanmamis_depo) == 0
        )
        
        if basarili:
            print("✅ TÜM TESTLER BAŞARILI!")
            print("\nMigration tamamen başarılı. Sistem çoklu otel desteğine hazır.")
        else:
            print("⚠️  BAZI TESTLER UYARI VERDİ")
            print("\nMigration kısmen tamamlanmış. Bazı veriler henüz atanmamış olabilir.")
        
        print()
        return basarili


if __name__ == '__main__':
    verify_migration()
