"""
Depo Sorumlusu Route'ları

Bu modül depo sorumlusu ile ilgili endpoint'leri içerir.

Endpoint'ler:
- /stok-giris - Stok giriş işlemi
- /stok-duzenle/<int:hareket_id> - Stok hareket düzenleme
- /stok-sil/<int:hareket_id> - Stok hareket silme
- /personel-zimmet - Personel zimmet atama

Roller:
- depo_sorumlusu
"""

from flask import render_template, request, redirect, url_for, flash, session
from models import db, StokHareket, Urun, UrunGrup, Kullanici, PersonelZimmet, PersonelZimmetDetay
from utils.decorators import login_required, role_required
from utils.helpers import log_islem, log_hata, get_stok_toplamlari
from utils.audit import audit_create, audit_update, audit_delete, serialize_model


def register_depo_routes(app):
    """Depo sorumlusu route'larını kaydet"""
    
    @app.route('/stok-giris', methods=['GET', 'POST'])
    @login_required
    @role_required('depo_sorumlusu')
    def stok_giris():
        """Depo sorumlusu stok giriş sayfası"""
        from utils.authorization import get_kullanici_otelleri, get_otel_filtreleme_secenekleri
        
        # Kullanıcının erişebileceği oteller
        kullanici_otelleri = get_kullanici_otelleri()
        otel_secenekleri = get_otel_filtreleme_secenekleri()
        
        # Seçili otel (query string'den veya ilk otel)
        secili_otel_id = request.args.get('otel_id', type=int)
        if not secili_otel_id and kullanici_otelleri:
            secili_otel_id = kullanici_otelleri[0].id
        
        if request.method == 'POST':
            try:
                urun_id = int(request.form['urun_id'])
                miktar = int(request.form['miktar'])
                hareket_tipi = request.form['hareket_tipi']
                aciklama = request.form.get('aciklama', '')
                
                urun = db.session.get(Urun, urun_id)
                stok_hareket = StokHareket(
                    urun_id=urun_id,
                    hareket_tipi=hareket_tipi,
                    miktar=miktar,
                    aciklama=aciklama,
                    islem_yapan_id=session['kullanici_id']
                )
                db.session.add(stok_hareket)
                db.session.commit()
                
                # Audit Trail
                audit_create('stok_hareket', stok_hareket.id, stok_hareket)
                
                # Log kaydı
                log_islem('ekleme', 'stok', {
                    'urun_id': urun_id,
                    'urun_adi': urun.urun_adi if urun else 'Bilinmeyen',
                    'hareket_tipi': hareket_tipi,
                    'miktar': miktar,
                    'aciklama': aciklama
                })
                
                flash('Stok girişi başarıyla yapıldı.', 'success')
                return redirect(url_for('stok_giris'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Hata oluştu: {str(e)}', 'danger')
        
        # Aktif ürün gruplarını getir
        gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
        
        # Aktif ürünleri grup ile birlikte getir
        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.urun_adi).all()
        
        # Son stok hareketlerini getir (otel filtrelemesi olmadan - tüm stok hareketleri)
        stok_hareketleri = StokHareket.query.order_by(StokHareket.islem_tarihi.desc()).limit(50).all()
        
        return render_template('depo_sorumlusu/stok_giris.html', 
                             gruplar=gruplar,
                             urunler=urunler, 
                             stok_hareketleri=stok_hareketleri,
                             otel_secenekleri=otel_secenekleri,
                             secili_otel_id=secili_otel_id)

    @app.route('/stok-duzenle/<int:hareket_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('depo_sorumlusu')
    def stok_duzenle(hareket_id):
        """Stok hareket düzenleme"""
        hareket = StokHareket.query.get_or_404(hareket_id)
        
        if request.method == 'POST':
            try:
                # Eski değerleri kaydet
                eski_deger = serialize_model(hareket)
                
                hareket.miktar = int(request.form['miktar'])
                hareket.hareket_tipi = request.form['hareket_tipi']
                hareket.aciklama = request.form.get('aciklama', '')
                
                db.session.commit()
                
                # Audit Trail
                audit_update('stok_hareket', hareket.id, eski_deger, hareket)
                
                # Log kaydı
                log_islem('guncelleme', 'stok', {
                    'hareket_id': hareket.id,
                    'urun_id': hareket.urun_id,
                    'urun_adi': hareket.urun.urun_adi,
                    'hareket_tipi': hareket.hareket_tipi,
                    'miktar': hareket.miktar
                })
                
                flash('Stok hareketi başarıyla güncellendi.', 'success')
                return redirect(url_for('stok_giris'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Hata oluştu: {str(e)}', 'danger')
        
        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.urun_adi).all()
        return render_template('depo_sorumlusu/stok_duzenle.html', hareket=hareket, urunler=urunler)

    @app.route('/stok-sil/<int:hareket_id>', methods=['POST'])
    @login_required
    @role_required('depo_sorumlusu')
    def stok_sil(hareket_id):
        """Stok hareket silme"""
        try:
            hareket = StokHareket.query.get_or_404(hareket_id)
            
            # Log kaydı için bilgileri sakla
            urun_adi = hareket.urun.urun_adi if hareket.urun else 'Bilinmeyen'
            hareket_tipi = hareket.hareket_tipi
            miktar = hareket.miktar
            
            # Eski değeri kaydet
            eski_deger = serialize_model(hareket)
            
            # Hareketi sil
            db.session.delete(hareket)
            db.session.commit()
            
            # Audit Trail
            audit_delete('stok_hareket', hareket_id, eski_deger)
            
            # Log kaydı
            log_islem('silme', 'stok', {
                'hareket_id': hareket_id,
                'urun_adi': urun_adi,
                'hareket_tipi': hareket_tipi,
                'miktar': miktar
            })
            
            flash('Stok hareketi başarıyla silindi.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
        
        return redirect(url_for('stok_giris'))

    @app.route('/personel-zimmet', methods=['GET', 'POST'])
    @login_required
    @role_required('depo_sorumlusu')
    def personel_zimmet():
        """Personel zimmet atama"""
        from utils.authorization import get_kullanici_otelleri, get_otel_filtreleme_secenekleri
        
        # Kullanıcının erişebileceği oteller
        kullanici_otelleri = get_kullanici_otelleri()
        otel_secenekleri = get_otel_filtreleme_secenekleri()
        
        # Seçili otel
        secili_otel_id = request.args.get('otel_id', type=int)
        if not secili_otel_id and kullanici_otelleri:
            secili_otel_id = kullanici_otelleri[0].id
        
        if request.method == 'POST':
            try:
                personel_id = int(request.form['personel_id'])
                aciklama = request.form.get('aciklama', '')
                urun_ids = request.form.getlist('urun_ids')

                if not urun_ids:
                    flash('En az bir ürün seçmelisiniz.', 'warning')
                    return redirect(url_for('personel_zimmet'))

                # İstenen ürün miktarlarını topla
                urun_miktarlari = {}
                for urun_id in urun_ids:
                    try:
                        miktar = int(request.form.get(f'miktar_{urun_id}', 0))
                    except (TypeError, ValueError):
                        miktar = 0

                    if miktar > 0:
                        uid = int(urun_id)
                        urun_miktarlari[uid] = urun_miktarlari.get(uid, 0) + miktar

                if not urun_miktarlari:
                    flash('Seçilen ürünler için geçerli bir miktar giriniz.', 'warning')
                    return redirect(url_for('personel_zimmet'))

                # Stok uygunluğunu kontrol et
                stok_map = get_stok_toplamlari(list(urun_miktarlari.keys()))
                urun_kayitlari = {
                    urun.id: urun for urun in Urun.query.filter(Urun.id.in_(urun_miktarlari.keys())).all()
                }

                yetersiz_stok = []
                for uid, talep_miktari in urun_miktarlari.items():
                    mevcut = stok_map.get(uid, 0)
                    if talep_miktari > mevcut:
                        urun = urun_kayitlari.get(uid)
                        urun_adi = f"{urun.urun_adi} ({urun.birim})" if urun else f'ID {uid}'
                        yetersiz_stok.append((urun_adi, talep_miktari, mevcut))

                if yetersiz_stok:
                    detay_mesaji = '; '.join(
                        f"{urun_adi}: istenen {talep}, mevcut {mevcut}" for urun_adi, talep, mevcut in yetersiz_stok
                    )
                    flash(f'Stok yetersiz: {detay_mesaji}', 'danger')
                    return redirect(url_for('personel_zimmet'))

                # Zimmet başlık oluştur
                zimmet = PersonelZimmet(
                    personel_id=personel_id,
                    teslim_eden_id=session['kullanici_id'],
                    aciklama=aciklama
                )
                db.session.add(zimmet)
                db.session.flush()  # ID'yi almak için

                # Zimmet detayları oluştur
                for uid, miktar in urun_miktarlari.items():
                    detay = PersonelZimmetDetay(
                        zimmet_id=zimmet.id,
                        urun_id=uid,
                        miktar=miktar,
                        kalan_miktar=miktar
                    )
                    db.session.add(detay)

                    # Stok çıkışı kaydet
                    stok_hareket = StokHareket(
                        urun_id=uid,
                        hareket_tipi='cikis',
                        miktar=miktar,
                        aciklama=f'Zimmet atama - {aciklama}',
                        islem_yapan_id=session['kullanici_id']
                    )
                    db.session.add(stok_hareket)
                
                db.session.commit()
                
                # Audit Trail
                audit_create('personel_zimmet', zimmet.id, zimmet)
                
                flash('Zimmet başarıyla atandı.', 'success')
                return redirect(url_for('personel_zimmet'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Hata oluştu: {str(e)}', 'danger')
        
        # Kat sorumlularını otel bazlı filtrele
        if secili_otel_id:
            kat_sorumlulari = Kullanici.query.filter_by(rol='kat_sorumlusu', aktif=True, otel_id=secili_otel_id).all()
        else:
            kat_sorumlulari = Kullanici.query.filter_by(rol='kat_sorumlusu', aktif=True).all()
        
        urun_gruplari = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
        aktif_zimmetler = PersonelZimmet.query.filter_by(durum='aktif').order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
        
        return render_template('depo_sorumlusu/personel_zimmet.html', 
                             kat_sorumlulari=kat_sorumlulari, 
                             urun_gruplari=urun_gruplari, 
                             aktif_zimmetler=aktif_zimmetler,
                             otel_secenekleri=otel_secenekleri,
                             secili_otel_id=secili_otel_id)
