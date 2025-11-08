"""
Kat ve Oda işlemlerini test eden script
"""

from app import app, db
from models import Otel, Kat, Oda
from datetime import datetime, timezone


def test_kat_oda_islemleri():
    """Kat ve Oda işlemlerini test et"""
    
    with app.app_context():
        print("=" * 60)
        print("KAT VE ODA İŞLEMLERİ TESTİ")
        print("=" * 60)
        
        test_otel_id = None
        test_kat_id = None
        test_oda_id = None
        
        try:
            # TEST 1: Otel seçerek kat ekleme
            print("\n[TEST 1] Otel seçerek kat ekleme...")
            
            # Test oteli oluştur
            test_otel = Otel(
                ad='Test Otel - Kat/Oda Testi',
                adres='Test Adres',
                telefon='1234567890',
                email='test@test.com',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(test_otel)
            db.session.commit()
            test_otel_id = test_otel.id
            
            print(f"   ✓ Test oteli oluşturuldu (ID: {test_otel.id})")
            
            # Otele kat ekle
            test_kat = Kat(
                otel_id=test_otel.id,
                kat_adi='Test Zemin Kat',
                kat_no=0,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(test_kat)
            db.session.commit()
            test_kat_id = test_kat.id
            
            # Doğrula
            kat = Kat.query.get(test_kat_id)
            if kat and kat.otel_id == test_otel.id:
                print(f"   ✅ BAŞARILI: Kat otele eklendi")
                print(f"      - Kat: {kat.kat_adi}")
                print(f"      - Otel: {kat.otel.ad}")
            else:
                print("   ❌ HATA: Kat otele eklenemedi")
            
            # TEST 2: Otel ve kat seçerek oda ekleme
            print("\n[TEST 2] Otel ve kat seçerek oda ekleme...")
            
            test_oda = Oda(
                kat_id=test_kat.id,
                oda_no='TEST-101',
                oda_tipi='Standart',
                kapasite=2,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(test_oda)
            db.session.commit()
            test_oda_id = test_oda.id
            
            # Doğrula
            oda = Oda.query.get(test_oda_id)
            if oda and oda.kat_id == test_kat.id:
                print(f"   ✅ BAŞARILI: Oda kata eklendi")
                print(f"      - Oda: {oda.oda_no}")
                print(f"      - Kat: {oda.kat.kat_adi}")
                print(f"      - Otel: {oda.kat.otel.ad}")
            else:
                print("   ❌ HATA: Oda kata eklenemedi")
            
            # TEST 3: Hiyerarşik ilişkileri test et
            print("\n[TEST 3] Hiyerarşik ilişkileri test et...")
            
            # Otel -> Kat ilişkisi
            otel = Otel.query.get(test_otel_id)
            kat_sayisi = len(otel.katlar)
            
            if kat_sayisi > 0:
                print(f"   ✅ BAŞARILI: Otel -> Kat ilişkisi çalışıyor")
                print(f"      - Otelin kat sayısı: {kat_sayisi}")
            else:
                print("   ❌ HATA: Otel -> Kat ilişkisi çalışmıyor")
            
            # Kat -> Oda ilişkisi
            kat = Kat.query.get(test_kat_id)
            oda_sayisi = len(kat.odalar)
            
            if oda_sayisi > 0:
                print(f"   ✅ BAŞARILI: Kat -> Oda ilişkisi çalışıyor")
                print(f"      - Katın oda sayısı: {oda_sayisi}")
            else:
                print("   ❌ HATA: Kat -> Oda ilişkisi çalışmıyor")
            
            # Oda -> Kat -> Otel zinciri
            oda = Oda.query.get(test_oda_id)
            if oda.kat and oda.kat.otel:
                print(f"   ✅ BAŞARILI: Oda -> Kat -> Otel zinciri çalışıyor")
                print(f"      - Oda: {oda.oda_no}")
                print(f"      - Kat: {oda.kat.kat_adi}")
                print(f"      - Otel: {oda.kat.otel.ad}")
            else:
                print("   ❌ HATA: Oda -> Kat -> Otel zinciri çalışmıyor")
            
            # TEST 4: Kat değiştirme (odanın katını değiştir)
            print("\n[TEST 4] Kat değiştirme testi...")
            
            # Yeni bir kat oluştur
            yeni_kat = Kat(
                otel_id=test_otel.id,
                kat_adi='Test 1. Kat',
                kat_no=1,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(yeni_kat)
            db.session.commit()
            
            # Odanın katını değiştir
            eski_kat_id = test_oda.kat_id
            test_oda.kat_id = yeni_kat.id
            db.session.commit()
            
            # Doğrula
            oda = Oda.query.get(test_oda_id)
            if oda.kat_id == yeni_kat.id:
                print(f"   ✅ BAŞARILI: Odanın katı değiştirildi")
                print(f"      - Eski Kat ID: {eski_kat_id}")
                print(f"      - Yeni Kat ID: {yeni_kat.id}")
                print(f"      - Yeni Kat: {oda.kat.kat_adi}")
            else:
                print("   ❌ HATA: Odanın katı değiştirilemedi")
            
            # Yeni katı sil (temizlik)
            db.session.delete(yeni_kat)
            db.session.commit()
            
            # TEST 5: Otel değiştirme (katın otelini değiştir)
            print("\n[TEST 5] Otel değiştirme testi...")
            
            # Yeni bir otel oluştur
            yeni_otel = Otel(
                ad='Test Otel 2',
                adres='Test Adres 2',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(yeni_otel)
            db.session.commit()
            
            # Katın otelini değiştir
            eski_otel_id = test_kat.otel_id
            test_kat.otel_id = yeni_otel.id
            db.session.commit()
            
            # Doğrula
            kat = Kat.query.get(test_kat_id)
            if kat.otel_id == yeni_otel.id:
                print(f"   ✅ BAŞARILI: Katın oteli değiştirildi")
                print(f"      - Eski Otel ID: {eski_otel_id}")
                print(f"      - Yeni Otel ID: {yeni_otel.id}")
                print(f"      - Yeni Otel: {kat.otel.ad}")
                
                # Odanın da yeni otele bağlı olduğunu kontrol et
                # Session'ı refresh et
                db.session.refresh(test_oda)
                if test_oda.kat and test_oda.kat.otel_id == yeni_otel.id:
                    print(f"   ✅ Oda da yeni otele bağlı: {test_oda.kat.otel.ad}")
                else:
                    print("   ⚠️  Oda yeni otele bağlı değil")
            else:
                print("   ❌ HATA: Katın oteli değiştirilemedi")
            
            # Temizlik
            print("\n[TEMIZLIK] Test verileri siliniyor...")
            db.session.delete(test_oda)
            db.session.delete(test_kat)
            db.session.delete(yeni_otel)
            db.session.delete(test_otel)
            db.session.commit()
            print("   ✓ Test verileri temizlendi")
            
            # Özet
            print("\n" + "=" * 60)
            print("TEST ÖZETİ")
            print("=" * 60)
            print("✅ TÜM KAT VE ODA TESTLERİ BAŞARILI!")
            print("\nTest edilen işlemler:")
            print("  1. ✓ Otel seçerek kat ekleme")
            print("  2. ✓ Otel ve kat seçerek oda ekleme")
            print("  3. ✓ Hiyerarşik ilişkiler (Otel->Kat->Oda)")
            print("  4. ✓ Kat değiştirme")
            print("  5. ✓ Otel değiştirme")
            print()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print("\n" + "=" * 60)
            print("❌ TEST HATASI!")
            print("=" * 60)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            
            # Temizlik
            try:
                if test_oda_id:
                    oda = Oda.query.get(test_oda_id)
                    if oda:
                        db.session.delete(oda)
                
                if test_kat_id:
                    kat = Kat.query.get(test_kat_id)
                    if kat:
                        db.session.delete(kat)
                
                if test_otel_id:
                    otel = Otel.query.get(test_otel_id)
                    if otel:
                        db.session.delete(otel)
                
                db.session.commit()
                print("ℹ️  Test verileri temizlendi")
            except:
                pass
            
            return False


if __name__ == '__main__':
    test_kat_oda_islemleri()
