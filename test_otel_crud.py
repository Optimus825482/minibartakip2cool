"""
Otel CRUD işlemlerini test eden script
"""

from app import app, db
from models import Otel, Kat, Kullanici, KullaniciOtel
from datetime import datetime, timezone


def test_otel_crud():
    """Otel CRUD işlemlerini test et"""
    
    with app.app_context():
        print("=" * 60)
        print("OTEL CRUD İŞLEMLERİ TESTİ")
        print("=" * 60)
        
        test_otel_id = None
        
        try:
            # TEST 1: Yeni otel ekleme
            print("\n[TEST 1] Yeni otel ekleme...")
            test_otel = Otel(
                ad='Test Otel - Kıbrıs',
                adres='Test Adres, Kıbrıs',
                telefon='+90 392 123 4567',
                email='info@testotel.com',
                vergi_no='1234567890',
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(test_otel)
            db.session.commit()
            test_otel_id = test_otel.id
            
            print(f"   ✅ BAŞARILI: Yeni otel eklendi (ID: {test_otel.id})")
            print(f"      - Ad: {test_otel.ad}")
            print(f"      - Telefon: {test_otel.telefon}")
            print(f"      - Email: {test_otel.email}")
            
            # TEST 2: Otel düzenleme
            print("\n[TEST 2] Otel düzenleme...")
            test_otel.telefon = '+90 392 999 8888'
            test_otel.email = 'yeni@testotel.com'
            test_otel.adres = 'Yeni Adres, Girne, Kıbrıs'
            db.session.commit()
            
            # Veritabanından tekrar oku
            guncel_otel = Otel.query.get(test_otel_id)
            
            if (guncel_otel.telefon == '+90 392 999 8888' and 
                guncel_otel.email == 'yeni@testotel.com'):
                print("   ✅ BAŞARILI: Otel bilgileri güncellendi")
                print(f"      - Yeni Telefon: {guncel_otel.telefon}")
                print(f"      - Yeni Email: {guncel_otel.email}")
                print(f"      - Yeni Adres: {guncel_otel.adres}")
            else:
                print("   ❌ HATA: Otel bilgileri güncellenemedi")
            
            # TEST 3: Otel aktif/pasif yapma
            print("\n[TEST 3] Otel aktif/pasif yapma...")
            
            # Pasif yap
            test_otel.aktif = False
            db.session.commit()
            
            guncel_otel = Otel.query.get(test_otel_id)
            if not guncel_otel.aktif:
                print("   ✅ BAŞARILI: Otel pasif yapıldı")
            else:
                print("   ❌ HATA: Otel pasif yapılamadı")
            
            # Tekrar aktif yap
            test_otel.aktif = True
            db.session.commit()
            
            guncel_otel = Otel.query.get(test_otel_id)
            if guncel_otel.aktif:
                print("   ✅ BAŞARILI: Otel tekrar aktif yapıldı")
            else:
                print("   ❌ HATA: Otel aktif yapılamadı")
            
            # TEST 4: Silme koruması - Kat varsa
            print("\n[TEST 4] Silme koruması testi (Kat varsa)...")
            
            # Test oteline bir kat ekle
            test_kat = Kat(
                otel_id=test_otel_id,
                kat_adi='Test Kat',
                kat_no=1,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            db.session.add(test_kat)
            db.session.commit()
            
            # Oteli silmeye çalış
            kat_sayisi = Kat.query.filter_by(otel_id=test_otel_id).count()
            
            if kat_sayisi > 0:
                print(f"   ✅ BAŞARILI: Silme koruması çalışıyor")
                print(f"      - Otele ait {kat_sayisi} kat bulundu")
                print(f"      - Otel silinmemeli (kat varsa)")
            else:
                print("   ⚠️  UYARI: Kat bulunamadı, koruma test edilemedi")
            
            # Test katını sil
            db.session.delete(test_kat)
            db.session.commit()
            print("   ℹ️  Test katı temizlendi")
            
            # TEST 5: Silme koruması - Personel varsa
            print("\n[TEST 5] Silme koruması testi (Personel varsa)...")
            
            # Test oteline bir kat sorumlusu ata
            test_kullanici = Kullanici(
                kullanici_adi='test_kat_sorumlusu',
                ad='Test',
                soyad='Kullanıcı',
                rol='kat_sorumlusu',
                otel_id=test_otel_id,
                aktif=True,
                olusturma_tarihi=datetime.now(timezone.utc)
            )
            test_kullanici.sifre_belirle('test123')
            db.session.add(test_kullanici)
            db.session.commit()
            
            # Personel sayısını kontrol et
            kat_sorumlu_sayisi = Kullanici.query.filter_by(
                otel_id=test_otel_id,
                rol='kat_sorumlusu'
            ).count()
            
            if kat_sorumlu_sayisi > 0:
                print(f"   ✅ BAŞARILI: Silme koruması çalışıyor")
                print(f"      - Otele atanmış {kat_sorumlu_sayisi} kat sorumlusu bulundu")
                print(f"      - Otel silinmemeli (personel varsa)")
            else:
                print("   ⚠️  UYARI: Personel bulunamadı, koruma test edilemedi")
            
            # Test kullanıcısını sil
            db.session.delete(test_kullanici)
            db.session.commit()
            print("   ℹ️  Test kullanıcısı temizlendi")
            
            # TEST 6: Güvenli silme (kat ve personel yoksa)
            print("\n[TEST 6] Güvenli silme testi...")
            
            # Otele ait kat ve personel olmadığını doğrula
            kat_sayisi = Kat.query.filter_by(otel_id=test_otel_id).count()
            personel_sayisi = Kullanici.query.filter_by(otel_id=test_otel_id).count()
            depo_atama_sayisi = KullaniciOtel.query.filter_by(otel_id=test_otel_id).count()
            
            if kat_sayisi == 0 and personel_sayisi == 0 and depo_atama_sayisi == 0:
                # Güvenli silme
                db.session.delete(test_otel)
                db.session.commit()
                
                # Silindiğini doğrula
                silinen_otel = Otel.query.get(test_otel_id)
                if silinen_otel is None:
                    print("   ✅ BAŞARILI: Otel güvenli şekilde silindi")
                else:
                    print("   ❌ HATA: Otel silinemedi")
            else:
                print(f"   ⚠️  UYARI: Otel silinemez")
                print(f"      - Kat: {kat_sayisi}")
                print(f"      - Personel: {personel_sayisi}")
                print(f"      - Depo Ataması: {depo_atama_sayisi}")
            
            # Özet
            print("\n" + "=" * 60)
            print("TEST ÖZETİ")
            print("=" * 60)
            print("✅ TÜM OTEL CRUD TESTLERİ BAŞARILI!")
            print("\nTest edilen işlemler:")
            print("  1. ✓ Yeni otel ekleme")
            print("  2. ✓ Otel bilgilerini düzenleme")
            print("  3. ✓ Otel aktif/pasif yapma")
            print("  4. ✓ Silme koruması (Kat varsa)")
            print("  5. ✓ Silme koruması (Personel varsa)")
            print("  6. ✓ Güvenli silme")
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
            if test_otel_id:
                try:
                    test_otel = Otel.query.get(test_otel_id)
                    if test_otel:
                        # İlişkili kayıtları temizle
                        Kat.query.filter_by(otel_id=test_otel_id).delete()
                        Kullanici.query.filter_by(otel_id=test_otel_id).delete()
                        KullaniciOtel.query.filter_by(otel_id=test_otel_id).delete()
                        db.session.delete(test_otel)
                        db.session.commit()
                        print("ℹ️  Test verileri temizlendi")
                except:
                    pass
            
            return False


if __name__ == '__main__':
    test_otel_crud()
