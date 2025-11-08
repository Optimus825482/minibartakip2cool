"""
Railway veritabanında migration ve kayıt düzeltme işlemleri
"""

import os
import sys

# Railway environment variables'ı yükle
def load_railway_env():
    """Railway .env dosyasını yükle"""
    try:
        with open('.env.railway', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Railway environment variables yüklendi")
        return True
    except FileNotFoundError:
        print("❌ .env.railway dosyası bulunamadı!")
        return False
    except Exception as e:
        print(f"❌ Environment variables yüklenirken hata: {str(e)}")
        return False

# Railway env'i yükle
if not load_railway_env():
    print("\n⚠️  .env.railway dosyası bulunamadı veya yüklenemedi!")
    print("Railway veritabanına bağlanmak için .env.railway dosyası gerekli.")
    sys.exit(1)

from app import app, db
from models import Otel, Kat, Oda, Kullanici, KullaniciOtel
from datetime import datetime, timezone


def railway_fix_migration():
    """Railway'de migration ve kayıt düzeltme"""
    
    with app.app_context():
        print("=" * 70)
        print("RAILWAY VERİTABANI - MİGRASYON VE DÜZELTME")
        print("=" * 70)
        
        try:
            # Veritabanı bağlantısını test et
            print("\n[1] Veritabanı bağlantısı test ediliyor...")
            db.session.execute(db.text('SELECT 1'))
            print("   ✅ Railway veritabanına bağlantı başarılı!")
            
            # Mevcut durumu kontrol et
            print("\n[2] Mevcut durum kontrol ediliyor...")
            oteller = Otel.query.all()
            katlar = Kat.query.all()
            odalar = Oda.query.all()
            kullanicilar = Kullanici.query.all()
            
            print(f"   - Otel Sayısı: {len(oteller)}")
            print(f"   - Kat Sayısı: {len(katlar)}")
            print(f"   - Oda Sayısı: {len(odalar)}")
            print(f"   - Kullanıcı Sayısı: {len(kullanicilar)}")
            
            # Otelleri listele
            print("\n[3] Mevcut oteller:")
            for otel in oteller:
                kat_sayisi = Kat.query.filter_by(otel_id=otel.id).count()
                print(f"   - ID: {otel.id}, Ad: {otel.ad}, Kat: {kat_sayisi}")
            
            # Merit Royal Diamond otellerini bul
            merit_oteller = Otel.query.filter(
                Otel.ad.like('%Merit Royal Diamond%')
            ).all()
            
            print(f"\n[4] Merit Royal Diamond otelleri: {len(merit_oteller)}")
            
            if len(merit_oteller) == 0:
                # Merit Royal Diamond oteli yok, oluştur
                print("\n   ⚠️  Merit Royal Diamond oteli bulunamadı, oluşturuluyor...")
                
                merit_otel = Otel(
                    ad='Merit Royal Diamond Hotel',
                    adres='Alsancak 99350 Kyrenia',
                    telefon='05338266625',
                    email='',
                    vergi_no='',
                    aktif=True,
                    olusturma_tarihi=datetime.now(timezone.utc)
                )
                db.session.add(merit_otel)
                db.session.flush()
                print(f"   ✅ Merit Royal Diamond oteli oluşturuldu (ID: {merit_otel.id})")
                
            elif len(merit_oteller) > 1:
                # Birden fazla Merit Royal Diamond var, birleştir
                print("\n   ⚠️  Birden fazla Merit Royal Diamond oteli var, birleştiriliyor...")
                
                for otel in merit_oteller:
                    kat_sayisi = Kat.query.filter_by(otel_id=otel.id).count()
                    kat_sorumlu = Kullanici.query.filter_by(otel_id=otel.id, rol='kat_sorumlusu').count()
                    depo_sorumlu = KullaniciOtel.query.filter_by(otel_id=otel.id).count()
                    print(f"      - ID: {otel.id}, Ad: {otel.ad}")
                    print(f"        Kat: {kat_sayisi}, Kat Sorumlusu: {kat_sorumlu}, Depo Sorumlusu: {depo_sorumlu}")
                
                # En çok kata sahip olanı seç
                dogru_otel = max(merit_oteller, key=lambda o: Kat.query.filter_by(otel_id=o.id).count())
                print(f"\n   ✓ Ana otel seçildi: ID {dogru_otel.id} ({dogru_otel.ad})")
                
                # Diğer otelleri birleştir
                for otel in merit_oteller:
                    if otel.id != dogru_otel.id:
                        print(f"\n   Otel ID {otel.id} birleştiriliyor...")
                        
                        # Katları taşı
                        katlar_tasindi = Kat.query.filter_by(otel_id=otel.id).update({'otel_id': dogru_otel.id})
                        if katlar_tasindi > 0:
                            print(f"      - {katlar_tasindi} kat taşındı")
                        
                        # Kat sorumlularını taşı
                        kat_sorumlu_tasindi = Kullanici.query.filter_by(
                            otel_id=otel.id, 
                            rol='kat_sorumlusu'
                        ).update({'otel_id': dogru_otel.id})
                        if kat_sorumlu_tasindi > 0:
                            print(f"      - {kat_sorumlu_tasindi} kat sorumlusu taşındı")
                        
                        # Depo sorumlusu atamalarını taşı
                        depo_atamalari = KullaniciOtel.query.filter_by(otel_id=otel.id).all()
                        tasindi = 0
                        silindi = 0
                        for atama in depo_atamalari:
                            mevcut = KullaniciOtel.query.filter_by(
                                kullanici_id=atama.kullanici_id,
                                otel_id=dogru_otel.id
                            ).first()
                            
                            if not mevcut:
                                atama.otel_id = dogru_otel.id
                                tasindi += 1
                            else:
                                db.session.delete(atama)
                                silindi += 1
                        
                        if tasindi > 0:
                            print(f"      - {tasindi} depo sorumlusu ataması taşındı")
                        if silindi > 0:
                            print(f"      - {silindi} duplicate atama silindi")
                        
                        # Boş oteli sil
                        db.session.delete(otel)
                        print(f"      - Otel ID {otel.id} silindi")
                
                merit_otel = dogru_otel
                
            else:
                merit_otel = merit_oteller[0]
                print(f"   ✅ Merit Royal Diamond oteli mevcut (ID: {merit_otel.id})")
            
            # Atanmamış katları Merit Royal Diamond'a ata
            print("\n[5] Kat atamaları kontrol ediliyor...")
            atanmamis_katlar = Kat.query.filter(
                (Kat.otel_id.is_(None)) | (Kat.otel_id == 0)
            ).all()
            
            if len(atanmamis_katlar) > 0:
                print(f"   ⚠️  {len(atanmamis_katlar)} atanmamış kat bulundu, atanıyor...")
                for kat in atanmamis_katlar:
                    kat.otel_id = merit_otel.id
                    print(f"      - {kat.kat_adi} -> Merit Royal Diamond")
                print(f"   ✅ {len(atanmamis_katlar)} kat atandı")
            else:
                print("   ✅ Tüm katlar zaten bir otele atanmış")
            
            # Atanmamış kat sorumlularını Merit Royal Diamond'a ata
            print("\n[6] Kat sorumlusu atamaları kontrol ediliyor...")
            atanmamis_kat_sorumlu = Kullanici.query.filter_by(
                rol='kat_sorumlusu'
            ).filter(
                (Kullanici.otel_id.is_(None)) | (Kullanici.otel_id == 0)
            ).all()
            
            if len(atanmamis_kat_sorumlu) > 0:
                print(f"   ⚠️  {len(atanmamis_kat_sorumlu)} atanmamış kat sorumlusu bulundu, atanıyor...")
                for kullanici in atanmamis_kat_sorumlu:
                    kullanici.otel_id = merit_otel.id
                    print(f"      - {kullanici.kullanici_adi} -> Merit Royal Diamond")
                print(f"   ✅ {len(atanmamis_kat_sorumlu)} kat sorumlusu atandı")
            else:
                print("   ✅ Tüm kat sorumluları zaten bir otele atanmış")
            
            # Atanmamış depo sorumlularını Merit Royal Diamond'a ata
            print("\n[7] Depo sorumlusu atamaları kontrol ediliyor...")
            depo_sorumlu_list = Kullanici.query.filter_by(rol='depo_sorumlusu').all()
            
            atandi = 0
            for depo_sorumlu in depo_sorumlu_list:
                mevcut = KullaniciOtel.query.filter_by(
                    kullanici_id=depo_sorumlu.id,
                    otel_id=merit_otel.id
                ).first()
                
                if not mevcut:
                    atama = KullaniciOtel(
                        kullanici_id=depo_sorumlu.id,
                        otel_id=merit_otel.id,
                        olusturma_tarihi=datetime.now(timezone.utc)
                    )
                    db.session.add(atama)
                    atandi += 1
                    print(f"      - {depo_sorumlu.kullanici_adi} -> Merit Royal Diamond")
            
            if atandi > 0:
                print(f"   ✅ {atandi} depo sorumlusu atandı")
            else:
                print("   ✅ Tüm depo sorumluları zaten bir otele atanmış")
            
            # Değişiklikleri kaydet
            print("\n[8] Değişiklikler kaydediliyor...")
            db.session.commit()
            print("   ✅ Tüm değişiklikler kaydedildi!")
            
            # Final kontrol
            print("\n" + "=" * 70)
            print("FİNAL DURUM")
            print("=" * 70)
            
            kat_sayisi = Kat.query.filter_by(otel_id=merit_otel.id).count()
            kat_sorumlu_sayisi = Kullanici.query.filter_by(
                otel_id=merit_otel.id, 
                rol='kat_sorumlusu'
            ).count()
            depo_sorumlu_sayisi = KullaniciOtel.query.filter_by(
                otel_id=merit_otel.id
            ).count()
            
            # Odaları say
            oda_sayisi = 0
            for oda in Oda.query.all():
                if oda.kat_id and oda.kat and oda.kat.otel_id == merit_otel.id:
                    oda_sayisi += 1
            
            print(f"\nMerit Royal Diamond Hotel (ID: {merit_otel.id}):")
            print(f"  ✓ Kat Sayısı: {kat_sayisi}")
            print(f"  ✓ Oda Sayısı: {oda_sayisi}")
            print(f"  ✓ Kat Sorumlusu: {kat_sorumlu_sayisi}")
            print(f"  ✓ Depo Sorumlusu: {depo_sorumlu_sayisi}")
            
            # Atanmamış kayıt kontrolü
            atanmamis_kat = Kat.query.filter(
                (Kat.otel_id.is_(None)) | (Kat.otel_id == 0)
            ).count()
            atanmamis_ks = Kullanici.query.filter_by(rol='kat_sorumlusu').filter(
                (Kullanici.otel_id.is_(None)) | (Kullanici.otel_id == 0)
            ).count()
            
            print(f"\nAtanmamış Kayıtlar:")
            print(f"  - Kat: {atanmamis_kat}")
            print(f"  - Kat Sorumlusu: {atanmamis_ks}")
            
            if atanmamis_kat == 0 and atanmamis_ks == 0:
                print("\n" + "=" * 70)
                print("✅ RAILWAY MİGRASYON VE DÜZELTME BAŞARILI!")
                print("=" * 70)
                print("\nTüm kayıtlar Merit Royal Diamond Hotel'e atandı.")
                print("Sistem çoklu otel desteğine hazır.")
            else:
                print("\n" + "=" * 70)
                print("⚠️  BAZI KAYITLAR HALA ATANMAMIŞ!")
                print("=" * 70)
            
            print()
            return True
            
        except Exception as e:
            db.session.rollback()
            print("\n" + "=" * 70)
            print("❌ HATA!")
            print("=" * 70)
            print(f"Hata: {str(e)}")
            print()
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("\n⚠️  DİKKAT: Bu script Railway PRODUCTION veritabanında çalışacak!")
    print("Devam etmek istediğinize emin misiniz? (evet/hayir): ", end='')
    
    onay = input().strip().lower()
    
    if onay in ['evet', 'e', 'yes', 'y']:
        print("\n✓ İşlem başlatılıyor...\n")
        railway_fix_migration()
    else:
        print("\n✗ İşlem iptal edildi.")
