"""
Kat Sorumlusu İlk Dolum ve Ek Dolum Route'ları
"""

from flask import jsonify, request, session
from models import db, Oda, Urun, MinibarIslem, MinibarIslemDetay, PersonelZimmet, PersonelZimmetDetay
from utils.helpers import log_islem, log_hata
from utils.decorators import login_required, role_required
from utils.audit import audit_create
from datetime import datetime


def register_kat_sorumlusu_ilk_dolum_routes(app):
    """Kat sorumlusu ilk dolum route'larını kaydet"""
    
    @app.route('/api/kat-sorumlusu/ilk-dolum-kontrol/<int:oda_id>/<int:urun_id>', methods=['GET'])
    @login_required
    @role_required('kat_sorumlusu')
    def api_ilk_dolum_kontrol(oda_id, urun_id):
        """Bir ürüne ilk dolum yapılmış mı kontrol et"""
        try:
            # Kat sorumlusunun otelini kontrol et
            from utils.authorization import get_kat_sorumlusu_otel
            kullanici_id = session['kullanici_id']
            kullanici_oteli = get_kat_sorumlusu_otel(kullanici_id)
            
            if not kullanici_oteli:
                return jsonify({
                    'success': False,
                    'message': 'Otel atamanız bulunamadı'
                }), 403
            
            # Odanın bu otele ait olduğunu kontrol et
            oda = db.session.get(Oda, oda_id)
            if not oda or oda.kat.otel_id != kullanici_oteli.id:
                return jsonify({
                    'success': False,
                    'message': 'Bu odaya erişim yetkiniz yok'
                }), 403
            
            # Bu oda için bu ürüne ilk dolum yapılmış mı?
            ilk_dolum = db.session.query(MinibarIslemDetay).join(
                MinibarIslem
            ).filter(
                MinibarIslem.oda_id == oda_id,
                MinibarIslem.islem_tipi == 'ilk_dolum',
                MinibarIslemDetay.urun_id == urun_id
            ).first()
            
            ilk_dolum_yapilmis = ilk_dolum is not None
            
            # Mevcut stok bilgisi
            mevcut_stok = 0
            if ilk_dolum_yapilmis:
                # Son işlemdeki stok miktarını bul
                son_islem = MinibarIslem.query.filter_by(
                    oda_id=oda_id
                ).order_by(MinibarIslem.id.desc()).first()
                
                if son_islem:
                    son_detay = next(
                        (d for d in son_islem.detaylar if d.urun_id == urun_id),
                        None
                    )
                    if son_detay:
                        mevcut_stok = son_detay.bitis_stok or 0
            
            return jsonify({
                'success': True,
                'ilk_dolum_yapilmis': ilk_dolum_yapilmis,
                'mevcut_stok': mevcut_stok
            })
            
        except Exception as e:
            log_hata(e, modul='api_ilk_dolum_kontrol')
            return jsonify({
                'success': False,
                'message': 'Kontrol sırasında bir hata oluştu'
            }), 500
    
    
    @app.route('/api/kat-sorumlusu/ek-dolum', methods=['POST'])
    @login_required
    @role_required('kat_sorumlusu')
    def api_ek_dolum():
        """Ek dolum işlemi - Tüketim kaydedilmeden stok artırma"""
        try:
            data = request.get_json() or {}
            oda_id = data.get('oda_id')
            urun_id = data.get('urun_id')
            ek_miktar = data.get('ek_miktar')
            
            # Validasyon
            if not all([oda_id, urun_id, ek_miktar]):
                return jsonify({
                    'success': False,
                    'message': 'Eksik parametre'
                }), 400
            
            # Miktar kontrolü
            try:
                ek_miktar = float(ek_miktar)
                if ek_miktar <= 0:
                    return jsonify({
                        'success': False,
                        'message': 'Lütfen geçerli bir miktar giriniz'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'Geçersiz miktar formatı'
                }), 400
            
            # Kat sorumlusunun otelini kontrol et
            from utils.authorization import get_kat_sorumlusu_otel
            kullanici_id = session['kullanici_id']
            kullanici_oteli = get_kat_sorumlusu_otel(kullanici_id)
            
            if not kullanici_oteli:
                return jsonify({
                    'success': False,
                    'message': 'Otel atamanız bulunamadı'
                }), 403
            
            # Oda ve ürün kontrolü
            oda = db.session.get(Oda, oda_id)
            urun = db.session.get(Urun, urun_id)
            
            if not oda:
                return jsonify({
                    'success': False,
                    'message': 'Oda bulunamadı'
                }), 404
            
            # Odanın bu otele ait olduğunu kontrol et
            if oda.kat.otel_id != kullanici_oteli.id:
                return jsonify({
                    'success': False,
                    'message': 'Bu odaya erişim yetkiniz yok'
                }), 403
            
            if not urun:
                return jsonify({
                    'success': False,
                    'message': 'Ürün bulunamadı'
                }), 404
            
            # İlk dolum kontrolü
            ilk_dolum = db.session.query(MinibarIslemDetay).join(
                MinibarIslem
            ).filter(
                MinibarIslem.oda_id == oda_id,
                MinibarIslem.islem_tipi == 'ilk_dolum',
                MinibarIslemDetay.urun_id == urun_id
            ).first()
            
            if not ilk_dolum:
                return jsonify({
                    'success': False,
                    'message': 'Bu ürüne henüz ilk dolum yapılmamış. Önce ilk dolum yapmalısınız.'
                }), 400
            
            # Kullanıcının zimmet stoğunu kontrol et
            kullanici_id = session['kullanici_id']
            
            # Aktif zimmetlerde bu ürünü ara
            zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
            ).filter(
                PersonelZimmet.personel_id == kullanici_id,
                PersonelZimmet.durum == 'aktif',
                PersonelZimmetDetay.urun_id == urun_id
            ).all()
            
            if not zimmet_detaylar:
                return jsonify({
                    'success': False,
                    'message': f'Zimmetinizde {urun.urun_adi} bulunmamaktadır'
                }), 422
            
            # Toplam kalan miktarı hesapla
            toplam_kalan = sum(detay.kalan_miktar or 0 for detay in zimmet_detaylar)
            
            if toplam_kalan < ek_miktar:
                return jsonify({
                    'success': False,
                    'message': f'Zimmetinizde yeterli {urun.urun_adi} bulunmamaktadır. Mevcut: {toplam_kalan}, İstenen: {ek_miktar}'
                }), 422
            
            # Odanın son minibar işlemini bul
            son_islem = MinibarIslem.query.filter_by(
                oda_id=oda_id
            ).order_by(MinibarIslem.id.desc()).first()
            
            if not son_islem:
                return jsonify({
                    'success': False,
                    'message': 'Minibar işlemi bulunamadı'
                }), 404
            
            # Son işlemdeki bu ürünün detayını bul
            son_detay = next(
                (d for d in son_islem.detaylar if d.urun_id == urun_id),
                None
            )
            
            if not son_detay:
                return jsonify({
                    'success': False,
                    'message': 'Ürün detayı bulunamadı'
                }), 404
            
            mevcut_stok = son_detay.bitis_stok or 0
            yeni_stok = mevcut_stok + ek_miktar
            
            # Yeni minibar işlemi oluştur (ek_dolum)
            minibar_islem = MinibarIslem(
                oda_id=oda_id,
                personel_id=kullanici_id,
                islem_tipi='ek_dolum',
                aciklama=f'Ek dolum - {urun.urun_adi}'
            )
            db.session.add(minibar_islem)
            db.session.flush()
            
            # İşlem detayı oluştur
            detay = MinibarIslemDetay(
                islem_id=minibar_islem.id,
                urun_id=urun_id,
                baslangic_stok=mevcut_stok,
                bitis_stok=yeni_stok,
                tuketim=0,  # Ek dolum tüketim değil!
                eklenen_miktar=ek_miktar
            )
            db.session.add(detay)
            
            # Zimmetlerden düş (FIFO mantığı ile)
            kalan_miktar = ek_miktar
            for zimmet_detay in sorted(zimmet_detaylar, key=lambda x: x.id):
                if kalan_miktar <= 0:
                    break
                
                zimmet_kalan = zimmet_detay.kalan_miktar or 0
                if zimmet_kalan > 0:
                    dusulecek = min(kalan_miktar, zimmet_kalan)
                    zimmet_detay.kalan_miktar = zimmet_kalan - dusulecek
                    kalan_miktar -= dusulecek
                    
                    # Detaya zimmet referansı ekle
                    if not detay.zimmet_detay_id:
                        detay.zimmet_detay_id = zimmet_detay.id
            
            db.session.commit()
            
            # Audit log
            audit_create(
                tablo_adi='minibar_islemleri',
                kayit_id=minibar_islem.id,
                yeni_deger={
                    'islem_tipi': 'ek_dolum',
                    'oda_id': oda_id,
                    'oda_no': oda.oda_no,
                    'urun_id': urun_id,
                    'urun_adi': urun.urun_adi,
                    'mevcut_stok': mevcut_stok,
                    'ek_miktar': ek_miktar,
                    'yeni_stok': yeni_stok,
                    'personel_id': kullanici_id
                },
                aciklama=f'Ek dolum işlemi - {oda.oda_no} - {urun.urun_adi}'
            )
            
            # Log kaydı
            log_islem('ekleme', 'ek_dolum', {
                'oda_id': oda_id,
                'oda_no': oda.oda_no,
                'urun_id': urun_id,
                'urun_adi': urun.urun_adi,
                'ek_miktar': ek_miktar,
                'yeni_stok': yeni_stok
            })
            
            return jsonify({
                'success': True,
                'message': f'{urun.urun_adi} için ek dolum başarıyla kaydedildi',
                'yeni_stok': yeni_stok
            })
            
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul='api_ek_dolum')
            return jsonify({
                'success': False,
                'message': 'Ek dolum işlemi sırasında bir hata oluştu'
            }), 500
    
    
    @app.route('/api/kat-sorumlusu/ilk-dolum', methods=['POST'])
    @login_required
    @role_required('kat_sorumlusu')
    def api_kat_sorumlusu_ilk_dolum():
        """Kat sorumlusu ilk dolum işlemi"""
        try:
            data = request.get_json() or {}
            oda_id = data.get('oda_id')
            urunler = data.get('urunler', [])
            aciklama = data.get('aciklama', 'İlk dolum')
            
            # Validasyon
            if not oda_id:
                return jsonify({
                    'success': False,
                    'message': 'Oda seçimi zorunludur'
                }), 400
            
            if not urunler:
                return jsonify({
                    'success': False,
                    'message': 'En az bir ürün seçmelisiniz'
                }), 400
            
            # Kat sorumlusunun otelini kontrol et
            from utils.authorization import get_kat_sorumlusu_otel
            kullanici_id = session['kullanici_id']
            kullanici_oteli = get_kat_sorumlusu_otel(kullanici_id)
            
            if not kullanici_oteli:
                return jsonify({
                    'success': False,
                    'message': 'Otel atamanız bulunamadı'
                }), 403
            
            # Oda kontrolü
            oda = db.session.get(Oda, oda_id)
            if not oda:
                return jsonify({
                    'success': False,
                    'message': 'Oda bulunamadı'
                }), 404
            
            # Odanın bu otele ait olduğunu kontrol et
            if oda.kat.otel_id != kullanici_oteli.id:
                return jsonify({
                    'success': False,
                    'message': 'Bu odaya erişim yetkiniz yok'
                }), 403
            
            # Bu oda için hangi ürünlere ilk dolum yapılmış kontrol et
            mevcut_ilk_dolumlar = db.session.query(MinibarIslemDetay.urun_id).join(
                MinibarIslem
            ).filter(
                MinibarIslem.oda_id == oda_id,
                MinibarIslem.islem_tipi == 'ilk_dolum'
            ).all()
            
            mevcut_urun_idler = {detay.urun_id for detay in mevcut_ilk_dolumlar}
            
            # Gelen ürünlerden hangilerine daha önce ilk dolum yapılmış kontrol et
            tekrar_urunler = []
            for urun_data in urunler:
                urun_id = urun_data.get('urun_id')
                if urun_id in mevcut_urun_idler:
                    urun = db.session.get(Urun, urun_id)
                    if urun:
                        tekrar_urunler.append(urun.urun_adi)
            
            if tekrar_urunler:
                return jsonify({
                    'success': False,
                    'message': f'Bu oda için şu ürünlere daha önce ilk dolum yapılmış: {", ".join(tekrar_urunler)}. Ek dolum yapmak için ürünü tekrar seçin ve ek dolum seçeneğini kullanın.'
                }), 400
            
            # Minibar işlemi oluştur
            minibar_islem = MinibarIslem(
                oda_id=oda_id,
                personel_id=kullanici_id,
                islem_tipi='ilk_dolum',
                aciklama=aciklama
            )
            db.session.add(minibar_islem)
            db.session.flush()
            
            # Her ürün için detay oluştur
            for urun_data in urunler:
                urun_id = urun_data.get('urun_id')
                miktar = urun_data.get('miktar', 0)
                
                if miktar <= 0:
                    continue
                
                # Ürün kontrolü
                urun = db.session.get(Urun, urun_id)
                if not urun:
                    continue
                
                # Zimmet kontrolü
                zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                    PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
                ).filter(
                    PersonelZimmet.personel_id == kullanici_id,
                    PersonelZimmet.durum == 'aktif',
                    PersonelZimmetDetay.urun_id == urun_id
                ).all()
                
                if not zimmet_detaylar:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'message': f'Zimmetinizde {urun.urun_adi} bulunmamaktadır'
                    }), 422
                
                toplam_kalan = sum(detay.kalan_miktar or 0 for detay in zimmet_detaylar)
                
                if toplam_kalan < miktar:
                    db.session.rollback()
                    return jsonify({
                        'success': False,
                        'message': f'Zimmetinizde yeterli {urun.urun_adi} bulunmamaktadır. Mevcut: {toplam_kalan}, İstenen: {miktar}'
                    }), 422
                
                # Minibar işlem detayı
                detay = MinibarIslemDetay(
                    islem_id=minibar_islem.id,
                    urun_id=urun_id,
                    baslangic_stok=0,
                    bitis_stok=miktar,
                    tuketim=0,  # İlk dolum tüketim değil!
                    eklenen_miktar=miktar
                )
                db.session.add(detay)
                db.session.flush()
                
                # Zimmetlerden düş (FIFO mantığı ile)
                kalan_miktar = miktar
                for zimmet_detay in sorted(zimmet_detaylar, key=lambda x: x.id):
                    if kalan_miktar <= 0:
                        break
                    
                    zimmet_kalan = zimmet_detay.kalan_miktar or 0
                    if zimmet_kalan > 0:
                        dusulecek = min(kalan_miktar, zimmet_kalan)
                        zimmet_detay.kalan_miktar = zimmet_kalan - dusulecek
                        kalan_miktar -= dusulecek
                        
                        # Detaya zimmet referansı ekle
                        if not detay.zimmet_detay_id:
                            detay.zimmet_detay_id = zimmet_detay.id
            
            db.session.commit()
            
            # Audit log
            audit_create(
                tablo_adi='minibar_islemleri',
                kayit_id=minibar_islem.id,
                yeni_deger={
                    'islem_tipi': 'ilk_dolum',
                    'oda_id': oda_id,
                    'oda_no': oda.oda_no,
                    'urun_sayisi': len(urunler),
                    'personel_id': kullanici_id
                },
                aciklama=f'İlk dolum işlemi - {oda.oda_no}'
            )
            
            # Log kaydı
            log_islem('ekleme', 'ilk_dolum', {
                'oda_id': oda_id,
                'oda_no': oda.oda_no,
                'urun_sayisi': len(urunler)
            })
            
            return jsonify({
                'success': True,
                'message': f'{oda.oda_no} numaralı oda için ilk dolum başarıyla tamamlandı',
                'islem_id': minibar_islem.id
            })
            
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul='api_kat_sorumlusu_ilk_dolum')
            return jsonify({
                'success': False,
                'message': 'İlk dolum işlemi sırasında bir hata oluştu'
            }), 500
