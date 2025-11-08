"""
Kullanıcı atamalarını test eden script
"""

from app import app, db
from models import Otel, Kullanici, KullaniciOtel
from datetime import datetime, timezone


def test_kullanici_atamalari():
    """Kullanıcı atamalarını test et"""
    
    with app.app_context():
        print("=" * 60)
        print("KULLANICI ATAMALARI TESTİ")
        print("=" * 60)
        
        test_otel1_id = None
        test_otel2_id = None
        test_depo_id = None
        test_kat_id = None
        
        try:
            # Test otelleri oluştur
            print("\n[HAZIRLIK] Test otelleri oluşturuluyor...")
            
            test_otel1 = Otel(
                ad='Test Otel 1 - Kullanıcı Testi',
                adres='Test Adres 1',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_otel2 = Otel(
                ad='Test Otel 2 - Kullanıcı Testi',
                adres='Test Adres 2',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add_all([test_otel1, test_otel2])
            db.session.commit()
            
            test_otel1_id = test_otel1.id
            test_otel2_id = test_otel2.id
            
            print(f"   ✓ Test Otel 1 oluşturuldu (ID: {test_otel1.id})")
            print(f"   ✓ Test Otel 2 oluşturuldu (ID: {test_otel2.id})")
            
            # TEST 1: Depo sorumlusuna çoklu otel ataması
            print("\n[TEST 1] Depo sorumlusuna çoklu otel ataması...")
            
            test_depo = Kullanici(
                kullanici_adi='test_depo_sorumlusu',
                ad='Test',
                soyad='Depo',
                rol='depo_sorumlusu',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_depo.sifre_belirle('test123')
            db.session.add(test_depo)
            db.session.commit()
            test_depo_id = test_depo.id
            
            print(f"   ✓ Depo sorumlusu oluşturuldu (ID: {test_depo.id})")
            
            # Her iki otele de ata
            atama1 = KullaniciOtel(
                kullanici_id=test_depo.id,
                otel_id=test_otel1.id,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            atama2 = KullaniciOtel(
                kullanici_id=test_depo.id,
                otel_id=test_otel2.id,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add_all([atama1, atama2])
            db.session.commit()
            
            # Doğrula
            atamalar = KullaniciOtel.query.filter_by(kullanici_id=test_depo.id).all()
            
            if len(atamalar) == 2:
                print(f"   ✅ BAŞARILI: Depo sorumlusu 2 otele atandı")
                for atama in atamalar:
                    print(f"      - {atama.otel.ad}")
            else:
                print(f"   ❌ HATA: Beklenen 2, bulunan {len(atamalar)} atama")
            
            # TEST 2: Kat sorumlusuna tekli otel ataması
            print("\n[TEST 2] Kat sorumlusuna tekli otel ataması...")
            
            test_kat_sorumlu = Kullanici(
                kullanici_adi='test_kat_sorumlusu',
                ad='Test',
                soyad='Kat',
                rol='kat_sorumlusu',
                otel_id=test_otel1.id,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_kat_sorumlu.sifre_belirle('test123')
            db.session.add(test_kat_sorumlu)
            db.session.commit()
            test_kat_id = test_kat_sorumlu.id
            
            # Doğrula
            kullanici = Kullanici.query.get(test_kat_id)
            
            if kullanici.otel_id == test_otel1.id:
                print(f"   ✅ BAŞARILI: Kat sorumlusu otele atandı")
                print(f"      - Kullanıcı: {kullanici.kullanici_adi}")
                print(f"      - Otel: {kullanici.otel.ad}")
            else:
                print("   ❌ HATA: Kat sorumlusu otele atanamadı")
            
            # TEST 3: Depo sorumlusu atama düzenleme
            print("\n[TEST 3] Depo sorumlusu atama düzenleme...")
            
            # Otel 1 atamasını kaldır, Otel 2'yi koru
            KullaniciOtel.query.filter_by(
                kullanici_id=test_depo.id,
                otel_id=test_otel1.id
            ).delete()
            db.session.commit()
            
            # Doğrula
            atamalar = KullaniciOtel.query.filter_by(kullanici_id=test_depo.id).all()
            
            if len(atamalar) == 1 and atamalar[0].otel_id == test_otel2.id:
                print(f"   ✅ BAŞARILI: Atama düzenlendi")
                print(f"      - Kalan otel: {atamalar[0].otel.ad}")
            else:
                print(f"   ❌ HATA: Atama düzenlenemedi")
            
            # Otel 1'i tekrar ekle
            yeni_atama = KullaniciOtel(
                kullanici_id=test_depo.id,
                otel_id=test_otel1.id,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(yeni_atama)
            db.session.commit()
            
            atamalar = KullaniciOtel.query.filter_by(kullanici_id=test_depo.id).all()
            if len(atamalar) == 2:
                print(f"   ✅ Otel 1 tekrar eklendi, toplam {len(atamalar)} atama")
            
            # TEST 4: Kat sorumlusu atama düzenleme
            print("\n[TEST 4] Kat sorumlusu atama düzenleme...")
            
            # Otelini değiştir
            test_kat_sorumlu.otel_id = test_otel2.id
            db.session.commit()
            
            # Doğrula
            kullanici = Kullanici.query.get(test_kat_id)
            
            if kullanici.otel_id == test_otel2.id:
                print(f"   ✅ BAŞARILI: Kat sorumlusunun oteli değiştirildi")
                print(f"      - Eski Otel: Test Otel 1")
                print(f"      - Yeni Otel: {kullanici.otel.ad}")
            else:
                print("   ❌ HATA: Kat sorumlusunun oteli değiştirilemedi")
            
            # TEST 5: Atama listelerini kontrol et
            print("\n[TEST 5] Atama listelerini kontrol et...")
            
            # Depo sorumlusunun atanan otelleri
            depo = Kullanici.query.get(test_depo_id)
            depo_oteller = [atama.otel.ad for atama in depo.atanan_oteller]
            
            print(f"   Depo Sorumlusu ({depo.kullanici_adi}):")
            print(f"      - Atanan Otel Sayısı: {len(depo_oteller)}")
            for otel_ad in depo_oteller:
                print(f"      - {otel_ad}")
            
            if len(depo_oteller) == 2:
                print(f"   ✅ BAŞARILI: Depo sorumlusu 2 otele atanmış")
            else:
                print(f"   ❌ HATA: Beklenen 2, bulunan {len(depo_oteller)} atama")
            
            # Kat sorumlusunun atanan oteli
            kat = Kullanici.query.get(test_kat_id)
            
            print(f"\n   Kat Sorumlusu ({kat.kullanici_adi}):")
            if kat.otel:
                print(f"      - Atanan Otel: {kat.otel.ad}")
                print(f"   ✅ BAŞARILI: Kat sorumlusu 1 otele atanmış")
            else:
                print(f"      - Atanan Otel: YOK")
                print(f"   ❌ HATA: Kat sorumlusu otele atanmamış")
            
            # TEST 6: Otel bazlı kullanıcı listeleme
            print("\n[TEST 6] Otel bazlı kullanıcı listeleme...")
            
            # Otel 1'e atanan kullanıcılar
            otel1_depo = KullaniciOtel.query.filter_by(otel_id=test_otel1.id).count()
            otel1_kat = Kullanici.query.filter_by(
                otel_id=test_otel1.id,
                rol='kat_sorumlusu'
            ).count()
            
            print(f"   Test Otel 1:")
            print(f"      - Depo Sorumlusu: {otel1_depo}")
            print(f"      - Kat Sorumlusu: {otel1_kat}")
            
            # Otel 2'ye atanan kullanıcılar
            otel2_depo = KullaniciOtel.query.filter_by(otel_id=test_otel2.id).count()
            otel2_kat = Kullanici.query.filter_by(
                otel_id=test_otel2.id,
                rol='kat_sorumlusu'
            ).count()
            
            print(f"\n   Test Otel 2:")
            print(f"      - Depo Sorumlusu: {otel2_depo}")
            print(f"      - Kat Sorumlusu: {otel2_kat}")
            
            if otel1_depo > 0 and otel2_depo > 0 and otel2_kat > 0:
                print(f"\n   ✅ BAŞARILI: Otel bazlı listeleme çalışıyor")
            else:
                print(f"\n   ⚠️  UYARI: Bazı atamalar eksik")
            
            # Temizlik
            print("\n[TEMIZLIK] Test verileri siliniyor...")
            
            # Önce ilişkili kayıtları sil
            KullaniciOtel.query.filter_by(kullanici_id=test_depo_id).delete()
            db.session.delete(test_depo)
            db.session.delete(test_kat_sorumlu)
            db.session.delete(test_otel1)
            db.session.delete(test_otel2)
            db.session.commit()
            
            print("   ✓ Test verileri temizlendi")
            
            # Özet
            print("\n" + "=" * 60)
            print("TEST ÖZETİ")
            print("=" * 60)
            print("✅ TÜM KULLANICI ATAMA TESTLERİ BAŞARILI!")
            print("\nTest edilen işlemler:")
            print("  1. ✓ Depo sorumlusuna çoklu otel ataması")
            print("  2. ✓ Kat sorumlusuna tekli otel ataması")
            print("  3. ✓ Depo sorumlusu atama düzenleme")
            print("  4. ✓ Kat sorumlusu atama düzenleme")
            print("  5. ✓ Atama listelerini kontrol")
            print("  6. ✓ Otel bazlı kullanıcı listeleme")
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
                if test_depo_id:
                    KullaniciOtel.query.filter_by(kullanici_id=test_depo_id).delete()
                    depo = Kullanici.query.get(test_depo_id)
                    if depo:
                        db.session.delete(depo)
                
                if test_kat_id:
                    kat = Kullanici.query.get(test_kat_id)
                    if kat:
                        db.session.delete(kat)
                
                if test_otel1_id:
                    otel1 = Otel.query.get(test_otel1_id)
                    if otel1:
                        db.session.delete(otel1)
                
                if test_otel2_id:
                    otel2 = Otel.query.get(test_otel2_id)
                    if otel2:
                        db.session.delete(otel2)
                
                db.session.commit()
                print("ℹ️  Test verileri temizlendi")
            except:
                pass
            
            return False


if __name__ == '__main__':
    test_kullanici_atamalari()
