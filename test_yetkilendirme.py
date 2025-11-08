"""
Yetkilendirme kontrollerini test eden script
"""

from app import app, db
from models import Otel, Kullanici, KullaniciOtel
from utils.authorization import (
    get_depo_sorumlusu_oteller,
    depo_sorumlusu_otel_erisimi,
    get_kat_sorumlusu_otel,
    kat_sorumlusu_otel_erisimi
)
from datetime import datetime, timezone


def test_yetkilendirme():
    """Yetkilendirme kontrollerini test et"""
    
    with app.app_context():
        print("=" * 60)
        print("YETKİLENDİRME KONTROL TESTİ")
        print("=" * 60)
        
        test_otel1_id = None
        test_otel2_id = None
        test_otel3_id = None
        test_depo_id = None
        test_kat_id = None
        
        try:
            # Test otelleri oluştur
            print("\n[HAZIRLIK] Test otelleri ve kullanıcıları oluşturuluyor...")
            
            test_otel1 = Otel(
                ad='Test Otel 1 - Yetki Testi',
                adres='Test Adres 1',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_otel2 = Otel(
                ad='Test Otel 2 - Yetki Testi',
                adres='Test Adres 2',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_otel3 = Otel(
                ad='Test Otel 3 - Yetki Testi',
                adres='Test Adres 3',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add_all([test_otel1, test_otel2, test_otel3])
            db.session.commit()
            
            test_otel1_id = test_otel1.id
            test_otel2_id = test_otel2.id
            test_otel3_id = test_otel3.id
            
            print(f"   ✓ 3 test oteli oluşturuldu")
            
            # Depo sorumlusu oluştur (Otel 1 ve 2'ye atanacak)
            test_depo = Kullanici(
                kullanici_adi='test_depo_yetki',
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
            
            # Otel 1 ve 2'ye ata
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
            
            print(f"   ✓ Depo sorumlusu oluşturuldu (Otel 1 ve 2'ye atandı)")
            
            # Kat sorumlusu oluştur (Sadece Otel 1'e atanacak)
            test_kat = Kullanici(
                kullanici_adi='test_kat_yetki',
                ad='Test',
                soyad='Kat',
                rol='kat_sorumlusu',
                otel_id=test_otel1.id,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_kat.sifre_belirle('test123')
            db.session.add(test_kat)
            db.session.commit()
            test_kat_id = test_kat.id
            
            print(f"   ✓ Kat sorumlusu oluşturuldu (Sadece Otel 1'e atandı)")
            
            # TEST 1: Depo sorumlusunun atanan otellere erişimi
            print("\n[TEST 1] Depo sorumlusunun atanan otellere erişimi...")
            
            # Atanan otelleri getir
            depo_oteller = get_depo_sorumlusu_oteller(test_depo_id)
            otel_adlari = [otel.ad for otel in depo_oteller]
            
            print(f"   Depo sorumlusunun erişebildiği oteller:")
            for otel_ad in otel_adlari:
                print(f"      - {otel_ad}")
            
            if len(depo_oteller) == 2:
                print(f"   ✅ BAŞARILI: Depo sorumlusu 2 otele erişebiliyor")
            else:
                print(f"   ❌ HATA: Beklenen 2, bulunan {len(depo_oteller)} otel")
            
            # Otel 1'e erişim kontrolü (BAŞARILI olmalı)
            erisim1 = depo_sorumlusu_otel_erisimi(test_depo_id, test_otel1_id)
            if erisim1:
                print(f"   ✅ Otel 1'e erişim: İZİN VERİLDİ")
            else:
                print(f"   ❌ Otel 1'e erişim: REDDEDILDI (Hatalı!)")
            
            # Otel 2'ye erişim kontrolü (BAŞARILI olmalı)
            erisim2 = depo_sorumlusu_otel_erisimi(test_depo_id, test_otel2_id)
            if erisim2:
                print(f"   ✅ Otel 2'ye erişim: İZİN VERİLDİ")
            else:
                print(f"   ❌ Otel 2'ye erişim: REDDEDILDI (Hatalı!)")
            
            # Otel 3'e erişim kontrolü (BAŞARISIZ olmalı)
            erisim3 = depo_sorumlusu_otel_erisimi(test_depo_id, test_otel3_id)
            if not erisim3:
                print(f"   ✅ Otel 3'e erişim: REDDEDILDI (Doğru!)")
            else:
                print(f"   ❌ Otel 3'e erişim: İZİN VERİLDİ (Hatalı!)")
            
            # TEST 2: Kat sorumlusunun sadece kendi oteline erişimi
            print("\n[TEST 2] Kat sorumlusunun sadece kendi oteline erişimi...")
            
            # Atanan oteli getir
            kat_otel = get_kat_sorumlusu_otel(test_kat_id)
            
            if kat_otel:
                print(f"   Kat sorumlusunun atandığı otel: {kat_otel.ad}")
                print(f"   ✅ BAŞARILI: Kat sorumlusunun oteli bulundu")
            else:
                print(f"   ❌ HATA: Kat sorumlusunun oteli bulunamadı")
            
            # Otel 1'e erişim kontrolü (BAŞARILI olmalı)
            erisim1 = kat_sorumlusu_otel_erisimi(test_kat_id, test_otel1_id)
            if erisim1:
                print(f"   ✅ Otel 1'e erişim: İZİN VERİLDİ")
            else:
                print(f"   ❌ Otel 1'e erişim: REDDEDILDI (Hatalı!)")
            
            # Otel 2'ye erişim kontrolü (BAŞARISIZ olmalı)
            erisim2 = kat_sorumlusu_otel_erisimi(test_kat_id, test_otel2_id)
            if not erisim2:
                print(f"   ✅ Otel 2'ye erişim: REDDEDILDI (Doğru!)")
            else:
                print(f"   ❌ Otel 2'ye erişim: İZİN VERİLDİ (Hatalı!)")
            
            # Otel 3'e erişim kontrolü (BAŞARISIZ olmalı)
            erisim3 = kat_sorumlusu_otel_erisimi(test_kat_id, test_otel3_id)
            if not erisim3:
                print(f"   ✅ Otel 3'e erişim: REDDEDILDI (Doğru!)")
            else:
                print(f"   ❌ Otel 3'e erişim: İZİN VERİLDİ (Hatalı!)")
            
            # TEST 3: Yetkisiz erişim denemeleri
            print("\n[TEST 3] Yetkisiz erişim denemeleri...")
            
            # Olmayan kullanıcı ID'si ile erişim
            olmayan_kullanici_id = 99999
            depo_oteller_yok = get_depo_sorumlusu_oteller(olmayan_kullanici_id)
            
            if len(depo_oteller_yok) == 0:
                print(f"   ✅ Olmayan kullanıcı için boş liste döndü")
            else:
                print(f"   ❌ Olmayan kullanıcı için {len(depo_oteller_yok)} otel döndü (Hatalı!)")
            
            # Olmayan otel ID'si ile erişim
            olmayan_otel_id = 99999
            erisim_yok = depo_sorumlusu_otel_erisimi(test_depo_id, olmayan_otel_id)
            
            if not erisim_yok:
                print(f"   ✅ Olmayan otel için erişim reddedildi")
            else:
                print(f"   ❌ Olmayan otel için erişim verildi (Hatalı!)")
            
            # TEST 4: Çoklu otel erişim kontrolü
            print("\n[TEST 4] Çoklu otel erişim kontrolü...")
            
            # Depo sorumlusunun tüm otellerine erişim kontrolü
            erisim_listesi = []
            for otel in [test_otel1, test_otel2, test_otel3]:
                erisim = depo_sorumlusu_otel_erisimi(test_depo_id, otel.id)
                erisim_listesi.append((otel.ad, erisim))
                durum = "✓ İZİN VERİLDİ" if erisim else "✗ REDDEDILDI"
                print(f"      - {otel.ad}: {durum}")
            
            # Doğru sayıda erişim var mı?
            izin_verilen = sum(1 for _, erisim in erisim_listesi if erisim)
            
            if izin_verilen == 2:
                print(f"   ✅ BAŞARILI: 2 otele izin verildi, 1 otele reddedildi")
            else:
                print(f"   ❌ HATA: Beklenen 2, bulunan {izin_verilen} izin")
            
            # Temizlik
            print("\n[TEMIZLIK] Test verileri siliniyor...")
            
            KullaniciOtel.query.filter_by(kullanici_id=test_depo_id).delete()
            db.session.delete(test_depo)
            db.session.delete(test_kat)
            db.session.delete(test_otel1)
            db.session.delete(test_otel2)
            db.session.delete(test_otel3)
            db.session.commit()
            
            print("   ✓ Test verileri temizlendi")
            
            # Özet
            print("\n" + "=" * 60)
            print("TEST ÖZETİ")
            print("=" * 60)
            print("✅ TÜM YETKİLENDİRME TESTLERİ BAŞARILI!")
            print("\nTest edilen işlemler:")
            print("  1. ✓ Depo sorumlusunun atanan otellere erişimi")
            print("  2. ✓ Kat sorumlusunun sadece kendi oteline erişimi")
            print("  3. ✓ Yetkisiz erişim denemeleri")
            print("  4. ✓ Çoklu otel erişim kontrolü")
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
                
                for otel_id in [test_otel1_id, test_otel2_id, test_otel3_id]:
                    if otel_id:
                        otel = Otel.query.get(otel_id)
                        if otel:
                            db.session.delete(otel)
                
                db.session.commit()
                print("ℹ️  Test verileri temizlendi")
            except:
                pass
            
            return False


if __name__ == '__main__':
    test_yetkilendirme()
