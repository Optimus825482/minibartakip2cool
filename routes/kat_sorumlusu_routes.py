"""
Kat Sorumlusu Routes Modülü

Bu modül kat sorumlusu ile ilgili endpoint'leri içerir.

Endpoint'ler:
- /dolum-talepleri - Dolum talepleri sayfası
- /minibar-kontrol - Minibar kontrol işlemleri
- /kat-odalari - Kata göre oda listesi (JSON)
- /minibar-urunler - Minibar ürünleri (JSON)
- /toplu-oda-doldurma - Toplu oda doldurma sayfası
- /kat-bazli-rapor - Kat bazlı rapor
- /zimmetim - Zimmet görüntüleme
- /kat-raporlar - Kat sorumlusu raporları
- /kat-sorumlusu/zimmet-stoklarim - Zimmet stokları
- /kat-sorumlusu/kritik-stoklar - Kritik stoklar
- /kat-sorumlusu/siparis-hazirla - Sipariş hazırlama
- /kat-sorumlusu/urun-gecmisi/<int:urun_id> - Ürün geçmişi
- /kat-sorumlusu/zimmet-export - Zimmet export
- /kat-sorumlusu/ilk-dolum - İlk dolum sayfası
- /kat-sorumlusu/oda-kontrol - Oda kontrol sayfası

Roller:
- kat_sorumlusu
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify, make_response
from datetime import datetime, timedelta, timezone
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

from models import (
    db, Kat, Oda, UrunGrup, Urun, PersonelZimmet, PersonelZimmetDetay,
    MinibarIslem, MinibarIslemDetay, Kullanici
)
from utils.decorators import login_required, role_required
from utils.helpers import log_islem, log_hata
from utils.audit import audit_create

def register_kat_sorumlusu_routes(app):
    """Kat sorumlusu route'larını kaydet"""
    
    @app.route('/dolum-talepleri')
    @login_required
    @role_required('kat_sorumlusu')
    def dolum_talepleri():
        """Kat Sorumlusu - Dolum talepleri sayfası"""
        return render_template('kat_sorumlusu/dolum_talepleri.html')
    
    @app.route('/minibar-kontrol', methods=['GET', 'POST'])
    @login_required
    @role_required('kat_sorumlusu')
    def minibar_kontrol():
        """Minibar kontrol işlemleri"""
        if request.method == 'POST':
            try:
                oda_id = int(request.form['oda_id'])
                islem_tipi = request.form['islem_tipi']
                aciklama = request.form.get('aciklama', '')
                kullanici_id = session['kullanici_id']
                
                # KONTROL İŞLEMİNDE KAYIT OLUŞTURMA - Sadece Görüntüleme
                if islem_tipi == 'kontrol':
                    flash('Kontrol işlemi tamamlandı. (Sadece görüntüleme - kayıt oluşturulmadı)', 'info')
                    log_islem(
                        kullanici_id=kullanici_id,
                        modul='minibar',
                        islem_tipi='kontrol',
                        aciklama=f'Oda {oda_id} minibar kontrolü yapıldı (görüntüleme)'
                    )
                    return redirect(url_for('minibar_kontrol'))
                
                # İlk dolum ve doldurma işlemleri için minibar kaydı oluştur
                islem = MinibarIslem(
                    oda_id=oda_id,
                    personel_id=kullanici_id,
                    islem_tipi=islem_tipi,
                    aciklama=aciklama
                )
                db.session.add(islem)
                db.session.flush()
                
                # Ürün detaylarını işle
                for key, value in request.form.items():
                    if key.startswith('miktar_') and value and int(value) > 0:
                        urun_id = int(key.split('_')[1])
                        miktar = int(value)
                        
                        if islem_tipi in ['ilk_dolum', 'doldurma']:
                            zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
                            ).filter(
                                PersonelZimmet.personel_id == kullanici_id,
                                PersonelZimmet.durum == 'aktif',
                                PersonelZimmetDetay.urun_id == urun_id
                            ).all()
                            
                            if not zimmet_detaylar:
                                urun = db.session.get(Urun, urun_id)
                                urun_adi = urun.urun_adi if urun else 'Bilinmeyen ürün'
                                raise Exception(f'Zimmetinizde bu ürün bulunmuyor: {urun_adi}')
                            
                            toplam_kalan = sum(detay.miktar - detay.kullanilan_miktar for detay in zimmet_detaylar)
                            
                            if toplam_kalan < miktar:
                                urun = db.session.get(Urun, urun_id)
                                urun_adi = urun.urun_adi if urun else 'Bilinmeyen ürün'
                                raise Exception(f'Zimmetinizde yeterli ürün yok: {urun_adi}. Kalan: {toplam_kalan}')
                            
                            # Zimmetlerden sırayla düş (FIFO)
                            kalan_miktar = miktar
                            for zimmet_detay in zimmet_detaylar:
                                if kalan_miktar <= 0:
                                    break
                                detay_kalan = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                                if detay_kalan > 0:
                                    kullanilacak = min(detay_kalan, kalan_miktar)
                                    zimmet_detay.kullanilan_miktar += kullanilacak
                                    zimmet_detay.kalan_miktar = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                                    kalan_miktar -= kullanilacak
                        
                        detay = MinibarIslemDetay(
                            islem_id=islem.id,
                            urun_id=urun_id,
                            baslangic_stok=0,
                            eklenen_miktar=miktar,
                            bitis_stok=miktar,
                            tuketim=0
                        )
                        db.session.add(detay)
                            
                    elif key.startswith('baslangic_') and value:
                        urun_id = int(key.split('_')[1])
                        baslangic = int(value)
                        bitis = int(request.form.get(f'bitis_{urun_id}', 0))
                        tuketim = max(0, baslangic - bitis)
                        
                        detay = MinibarIslemDetay(
                            islem_id=islem.id,
                            urun_id=urun_id,
                            baslangic_stok=baslangic,
                            bitis_stok=bitis,
                            tuketim=tuketim
                        )
                        db.session.add(detay)
                        
                        if islem_tipi == 'doldurma' and tuketim > 0:
                            zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
                            ).filter(
                                PersonelZimmet.personel_id == kullanici_id,
                                PersonelZimmet.durum == 'aktif',
                                PersonelZimmetDetay.urun_id == urun_id
                            ).all()
                            
                            if zimmet_detaylar:
                                toplam_kalan = sum(d.miktar - d.kullanilan_miktar for d in zimmet_detaylar)
                                if toplam_kalan >= tuketim:
                                    kalan_tuketim = tuketim
                                    for zimmet_detay in zimmet_detaylar:
                                        if kalan_tuketim <= 0:
                                            break
                                        detay_kalan = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                                        if detay_kalan > 0:
                                            kullanilacak = min(detay_kalan, kalan_tuketim)
                                            zimmet_detay.kullanilan_miktar += kullanilacak
                                            zimmet_detay.kalan_miktar = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                                            kalan_tuketim -= kullanilacak
                
                db.session.commit()
                audit_create('minibar_islem', islem.id, islem)
                flash('Minibar işlemi başarıyla kaydedildi. Zimmetinizden düşürülen ürünler güncellendi.', 'success')
                log_islem(
                    kullanici_id=kullanici_id,
                    modul='minibar',
                    islem_tipi=islem_tipi,
                    aciklama=f'Oda {oda_id} - {islem_tipi} işlemi'
                )
                return redirect(url_for('minibar_kontrol'))
                
            except Exception as e:
                db.session.rollback()
                log_hata(
                    exception=e,
                    modul='minibar',
                    extra_info={
                        'oda_id': request.form.get('oda_id'),
                        'islem_tipi': request.form.get('islem_tipi'),
                        'kullanici_id': session.get('kullanici_id')
                    }
                )
                flash(f'Hata oluştu: {str(e)}', 'danger')
        
        katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
        urun_gruplari = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
        return render_template('kat_sorumlusu/minibar_kontrol.html', 
                             katlar=katlar,
                             urun_gruplari=urun_gruplari)
    
    @app.route('/kat-odalari')
    @login_required
    @role_required('kat_sorumlusu')
    def kat_odalari():
        """Seçilen kata ait odaları JSON olarak döndür"""
        try:
            kat_id = request.args.get('kat_id', type=int)
            if not kat_id:
                return jsonify({'success': False, 'error': 'Kat ID gerekli'})
            
            odalar = Oda.query.filter_by(kat_id=kat_id, aktif=True).order_by(Oda.oda_no).all()
            
            oda_listesi = []
            for oda in odalar:
                oda_listesi.append({
                    'id': oda.id,
                    'oda_no': oda.oda_no
                })
            
            return jsonify({'success': True, 'odalar': oda_listesi})
        except Exception as e:
            log_hata(e, modul='kat_odalari')
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/minibar-urunler')
    @login_required
    @role_required('kat_sorumlusu')
    def minibar_urunler():
        """Minibar ürünlerini JSON olarak döndür"""
        try:
            urunler = Urun.query.filter_by(aktif=True).order_by(Urun.grup_id, Urun.urun_adi).all()
            
            # Kullanıcının zimmet bilgilerini getir
            kullanici_id = session.get('kullanici_id')
            aktif_zimmetler = PersonelZimmet.query.filter_by(
                personel_id=kullanici_id,
                durum='aktif'
            ).all()
            
            # Her ürün için toplam zimmet miktarını hesapla
            zimmet_dict = {}
            for zimmet in aktif_zimmetler:
                for detay in zimmet.detaylar:
                    if detay.urun_id not in zimmet_dict:
                        zimmet_dict[detay.urun_id] = 0
                    zimmet_dict[detay.urun_id] += (detay.kalan_miktar or 0)
            
            urun_listesi = []
            for urun in urunler:
                urun_listesi.append({
                    'id': urun.id,
                    'urun_adi': urun.urun_adi,
                    'grup_id': urun.grup_id,
                    'grup_adi': urun.grup.grup_adi,
                    'birim': urun.birim,
                    'zimmet_miktari': zimmet_dict.get(urun.id, 0)
                })
            
            return jsonify({'success': True, 'urunler': urun_listesi})
        except Exception as e:
            log_hata(e, modul='minibar_urunler')
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/toplu-oda-doldurma', methods=['GET'])
    @login_required
    @role_required('kat_sorumlusu')
    def toplu_oda_doldurma():
        """Toplu oda doldurma sayfası"""
        katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
        urun_gruplari = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
        return render_template('kat_sorumlusu/toplu_oda_doldurma.html',
                             katlar=katlar,
                             urun_gruplari=urun_gruplari)

    
    @app.route('/kat-bazli-rapor', methods=['GET'])
    @login_required
    @role_required('kat_sorumlusu', 'admin', 'depo_sorumlusu')
    def kat_bazli_rapor():
        """Kat bazlı tüketim raporu sayfası"""
        katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
        return render_template('raporlar/kat_bazli_rapor.html', katlar=katlar)
    
    @app.route('/zimmetim')
    @login_required
    @role_required('kat_sorumlusu')
    def zimmetim():
        """Zimmet görüntüleme"""
        kullanici_id = session['kullanici_id']
        
        aktif_zimmetler = PersonelZimmet.query.filter_by(
            personel_id=kullanici_id, 
            durum='aktif'
        ).order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
        
        toplam_zimmet = 0
        kalan_zimmet = 0
        kullanilan_zimmet = 0
        
        for zimmet in aktif_zimmetler:
            for detay in zimmet.detaylar:
                toplam_zimmet += detay.miktar
                kullanilan_zimmet += detay.kullanilan_miktar
                kalan = detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar)
                kalan_zimmet += kalan
        
        return render_template('kat_sorumlusu/zimmetim.html',
                             aktif_zimmetler=aktif_zimmetler,
                             toplam_zimmet=toplam_zimmet,
                             kalan_zimmet=kalan_zimmet,
                             kullanilan_zimmet=kullanilan_zimmet)
    
    @app.route('/kat-raporlar')
    @login_required
    @role_required('kat_sorumlusu')
    def kat_raporlar():
        """Kat sorumlusu raporları"""
        rapor_tipi = request.args.get('rapor_tipi', 'minibar_islem')
        baslangic_tarihi = request.args.get('baslangic_tarihi')
        bitis_tarihi = request.args.get('bitis_tarihi')
        
        rapor_verisi = []
        rapor_baslik = ""
        kullanici_id = session['kullanici_id']
        
        if rapor_tipi == 'minibar_islem':
            rapor_baslik = "Minibar İşlem Raporu"
            query = MinibarIslem.query.filter_by(personel_id=kullanici_id)
            
            if baslangic_tarihi:
                query = query.filter(MinibarIslem.islem_tarihi >= datetime.strptime(baslangic_tarihi, '%Y-%m-%d'))
            if bitis_tarihi:
                query = query.filter(MinibarIslem.islem_tarihi <= datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1))
            
            rapor_verisi = query.order_by(MinibarIslem.islem_tarihi.desc()).all()
        
        return render_template('kat_sorumlusu/raporlar.html', 
                             rapor_verisi=rapor_verisi, 
                             rapor_baslik=rapor_baslik,
                             rapor_tipi=rapor_tipi)
