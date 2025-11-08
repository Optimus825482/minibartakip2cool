"""
Sistem Yöneticisi Route'ları

Bu modül sistem yöneticisi ve admin rolüne ait endpoint'leri içerir.

Endpoint'ler:
- /sistem-loglari - Sistem logları
- /otel-tanimla - Otel bilgileri
- /kat-tanimla - Kat tanımlama
- /kat-duzenle/<int:kat_id> - Kat düzenleme
- /kat-sil/<int:kat_id> - Kat silme
- /oda-tanimla - Oda tanımlama
- /oda-duzenle/<int:oda_id> - Oda düzenleme
- /oda-sil/<int:oda_id> - Oda silme

Roller:
- sistem_yoneticisi
- admin
"""

from flask import render_template, request, redirect, url_for, flash
from models import db, Otel, Kat, Oda, Kullanici, SistemLog
from utils.decorators import login_required, role_required
from utils.helpers import log_islem, log_hata
from utils.audit import audit_create, audit_update, audit_delete, serialize_model


def register_sistem_yoneticisi_routes(app):
    """Sistem yöneticisi route'larını kaydet"""
    
    @app.route('/sistem-loglari')
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def sistem_loglari():
        """Sistem logları listesi"""
        # Sayfa parametreleri
        sayfa = request.args.get('sayfa', 1, type=int)
        limit = 50
        
        # Filtreler
        islem_tipi = request.args.get('islem_tipi', '')
        modul = request.args.get('modul', '')
        kullanici_id = request.args.get('kullanici_id', type=int)
        
        # Sorgu oluştur
        query = SistemLog.query
        
        if islem_tipi:
            query = query.filter(SistemLog.islem_tipi == islem_tipi)
        if modul:
            query = query.filter(SistemLog.modul == modul)
        if kullanici_id:
            query = query.filter(SistemLog.kullanici_id == kullanici_id)
        
        # Sayfalama
        loglar = query.order_by(SistemLog.islem_tarihi.desc()).paginate(
            page=sayfa, per_page=limit, error_out=False
        )
        
        # Filtre seçenekleri
        kullanicilar = Kullanici.query.filter(Kullanici.aktif.is_(True)).order_by(Kullanici.ad, Kullanici.soyad).all()
        
        return render_template('sistem_yoneticisi/sistem_loglari.html',
                             loglar=loglar,
                             kullanicilar=kullanicilar,
                             islem_tipi=islem_tipi,
                             modul=modul,
                             kullanici_id=kullanici_id)
    
    
    @app.route('/otel-tanimla', methods=['GET', 'POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def otel_tanimla():
        """Otel bilgileri tanımlama/düzenleme"""
        from forms import OtelForm
        
        otel = Otel.query.first()
        form = OtelForm(obj=otel)
        
        if form.validate_on_submit():
            try:
                if otel:
                    # Eski değeri sakla
                    eski_deger = serialize_model(otel)
                    
                    # Güncelle
                    otel.ad = form.ad.data
                    otel.adres = form.adres.data
                    otel.telefon = form.telefon.data
                    otel.email = form.email.data
                    otel.vergi_no = form.vergi_no.data or ''
                    
                    # Audit log
                    audit_update(
                        tablo_adi='oteller',
                        kayit_id=otel.id,
                        eski_deger=eski_deger,
                        yeni_deger=serialize_model(otel),
                        aciklama='Otel bilgileri güncellendi'
                    )
                else:
                    # Yeni oluştur
                    otel = Otel(
                        ad=form.ad.data,
                        adres=form.adres.data,
                        telefon=form.telefon.data,
                        email=form.email.data,
                        vergi_no=form.vergi_no.data or ''
                    )
                    db.session.add(otel)
                    db.session.flush()
                    
                    # Audit log
                    audit_create(
                        tablo_adi='oteller',
                        kayit_id=otel.id,
                        yeni_deger=serialize_model(otel),
                        aciklama='Otel bilgileri oluşturuldu'
                    )
                
                db.session.commit()
                
                # Log kaydı
                log_islem('guncelleme' if otel else 'ekleme', 'otel', {
                    'otel_id': otel.id,
                    'otel_adi': otel.ad
                })
                
                flash('Otel bilgileri başarıyla kaydedildi.', 'success')
                return redirect(url_for('otel_tanimla'))
            except Exception as e:
                db.session.rollback()
                log_hata(e, modul='otel_tanimla')
                flash('Otel bilgileri kaydedilirken hata oluştu.', 'danger')
        
        return render_template('sistem_yoneticisi/otel_tanimla.html', otel=otel, form=form)
    
    
    @app.route('/kat-tanimla', methods=['GET', 'POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def kat_tanimla():
        """Kat tanımlama"""
        from forms import KatForm
        from models import Otel
        
        form = KatForm()
        
        # Otel listesini form'a yükle
        form.otel_id.choices = [(0, 'Otel Seçin...')] + [(o.id, o.ad) for o in Otel.query.filter_by(aktif=True).order_by(Otel.ad).all()]
        
        if form.validate_on_submit():
            try:
                # Otel seçimi kontrolü
                if not form.otel_id.data or form.otel_id.data == 0:
                    flash('Lütfen bir otel seçin!', 'danger')
                    return render_template('sistem_yoneticisi/kat_tanimla.html', katlar=[], form=form)
                
                kat = Kat(
                    otel_id=form.otel_id.data,
                    kat_adi=form.kat_adi.data,
                    kat_no=form.kat_no.data,
                    aciklama=form.aciklama.data,
                    aktif=form.aktif.data
                )
                db.session.add(kat)
                db.session.flush()
                
                # Audit log
                audit_create(
                    tablo_adi='katlar',
                    kayit_id=kat.id,
                    yeni_deger=serialize_model(kat),
                    aciklama=f'Kat oluşturuldu - {kat.kat_adi}'
                )
                
                db.session.commit()
                
                # Log kaydı
                log_islem('ekleme', 'kat', {
                    'kat_id': kat.id,
                    'otel_id': kat.otel_id,
                    'kat_adi': kat.kat_adi,
                    'kat_no': kat.kat_no
                })
                
                flash(f'{kat.kat_adi} başarıyla eklendi.', 'success')
                return redirect(url_for('kat_tanimla'))
            except Exception as e:
                db.session.rollback()
                log_hata(e, modul='kat_tanimla')
                flash('Kat eklenirken hata oluştu.', 'danger')
        
        # Mevcut katları listele (otel bilgisi ile)
        katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
        
        return render_template('sistem_yoneticisi/kat_tanimla.html', katlar=katlar, form=form)
    
    
    @app.route('/kat-duzenle/<int:kat_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def kat_duzenle(kat_id):
        """Kat düzenleme"""
        from forms import KatForm
        from models import Otel
        
        kat = db.session.get(Kat, kat_id)
        if not kat:
            flash('Kat bulunamadı.', 'danger')
            return redirect(url_for('kat_tanimla'))
        
        # Eski değeri sakla
        eski_deger = serialize_model(kat)
        
        form = KatForm(obj=kat)
        
        # Otel listesini form'a yükle
        form.otel_id.choices = [(o.id, o.ad) for o in Otel.query.filter_by(aktif=True).order_by(Otel.ad).all()]
        
        if form.validate_on_submit():
            try:
                kat.otel_id = form.otel_id.data
                kat.kat_adi = form.kat_adi.data
                kat.kat_no = form.kat_no.data
                kat.aciklama = form.aciklama.data
                kat.aktif = form.aktif.data
                
                db.session.commit()
                
                # Audit log
                audit_update(
                    tablo_adi='katlar',
                    kayit_id=kat.id,
                    eski_deger=eski_deger,
                    yeni_deger=serialize_model(kat),
                    aciklama=f'Kat güncellendi - {kat.kat_adi}'
                )
                
                # Log kaydı
                log_islem('guncelleme', 'kat', {
                    'kat_id': kat.id,
                    'kat_adi': kat.kat_adi
                })
                
                flash(f'{kat.kat_adi} başarıyla güncellendi.', 'success')
                return redirect(url_for('kat_tanimla'))
            except Exception as e:
                db.session.rollback()
                log_hata(e, modul='kat_duzenle')
                flash('Kat güncellenirken hata oluştu.', 'danger')
        
        return render_template('sistem_yoneticisi/kat_duzenle.html', kat=kat, form=form)
    
    
    @app.route('/kat-sil/<int:kat_id>', methods=['POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def kat_sil(kat_id):
        """Kat silme (pasif yapma)"""
        try:
            kat = db.session.get(Kat, kat_id)
            if not kat:
                flash('Kat bulunamadı.', 'danger')
                return redirect(url_for('kat_tanimla'))
            
            # Eski değeri sakla
            eski_deger = serialize_model(kat)
            
            # Pasif yap
            kat.aktif = False
            db.session.commit()
            
            # Audit log
            audit_delete(
                tablo_adi='katlar',
                kayit_id=kat.id,
                eski_deger=eski_deger,
                aciklama=f'Kat pasif yapıldı - {kat.kat_adi}'
            )
            
            # Log kaydı
            log_islem('silme', 'kat', {
                'kat_id': kat.id,
                'kat_adi': kat.kat_adi
            })
            
            flash(f'{kat.kat_adi} başarıyla silindi.', 'success')
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul='kat_sil')
            flash('Kat silinirken hata oluştu.', 'danger')
        
        return redirect(url_for('kat_tanimla'))
    
    
    @app.route('/oda-tanimla', methods=['GET', 'POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def oda_tanimla():
        """Oda tanımlama"""
        from forms import OdaForm
        from models import Otel
        
        form = OdaForm()
        
        # Otel listesini form'a yükle
        oteller = Otel.query.filter_by(aktif=True).order_by(Otel.ad).all()
        form.otel_id.choices = [(0, 'Otel Seçin...')] + [(o.id, o.ad) for o in oteller]
        form.kat_id.choices = [(0, 'Önce otel seçin...')]
        
        if form.validate_on_submit():
            try:
                # Otel ve kat seçimi kontrolü
                if not form.otel_id.data or form.otel_id.data == 0:
                    flash('Lütfen bir otel seçin!', 'danger')
                    return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=[], odalar=[], form=form)
                
                if not form.kat_id.data or form.kat_id.data == 0:
                    flash('Lütfen bir kat seçin!', 'danger')
                    return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=[], odalar=[], form=form)
                
                # Kat'ın seçilen otele ait olduğunu kontrol et
                kat = Kat.query.get(form.kat_id.data)
                if not kat or kat.otel_id != form.otel_id.data:
                    flash('Seçilen kat, seçilen otele ait değil!', 'danger')
                    return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=[], odalar=[], form=form)
                
                oda = Oda(
                    oda_no=form.oda_no.data,
                    kat_id=form.kat_id.data,
                    oda_tipi=form.oda_tipi.data,
                    kapasite=form.kapasite.data,
                    aktif=form.aktif.data
                )
                db.session.add(oda)
                db.session.flush()
                
                # Audit log
                audit_create(
                    tablo_adi='odalar',
                    kayit_id=oda.id,
                    yeni_deger=serialize_model(oda),
                    aciklama=f'Oda oluşturuldu - {oda.oda_no}'
                )
                
                db.session.commit()
                
                # Log kaydı
                log_islem('ekleme', 'oda', {
                    'oda_id': oda.id,
                    'oda_no': oda.oda_no,
                    'kat_id': oda.kat_id
                })
                
                flash(f'Oda {oda.oda_no} başarıyla eklendi.', 'success')
                return redirect(url_for('oda_tanimla'))
            except Exception as e:
                db.session.rollback()
                log_hata(e, modul='oda_tanimla')
                flash('Oda eklenirken hata oluştu.', 'danger')
        
        # Katlar ve odalar
        katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
        odalar = Oda.query.filter_by(aktif=True).order_by(Oda.oda_no).all()
        
        return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=katlar, odalar=odalar, form=form, oteller=oteller)
    
    
    @app.route('/oda-duzenle/<int:oda_id>', methods=['GET', 'POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def oda_duzenle(oda_id):
        """Oda düzenleme"""
        from forms import OdaForm
        from models import Otel
        
        oda = db.session.get(Oda, oda_id)
        if not oda:
            flash('Oda bulunamadı.', 'danger')
            return redirect(url_for('oda_tanimla'))
        
        # Eski değeri sakla
        eski_deger = serialize_model(oda)
        
        form = OdaForm(obj=oda)
        
        # Otel listesini yükle
        oteller = Otel.query.filter_by(aktif=True).order_by(Otel.ad).all()
        form.otel_id.choices = [(o.id, o.ad) for o in oteller]
        
        # Mevcut otel seçimini ayarla
        if oda.kat and oda.kat.otel_id:
            form.otel_id.data = oda.kat.otel_id
        
        # Kat listesini yükle (mevcut otel için)
        if oda.kat:
            katlar = Kat.query.filter_by(otel_id=oda.kat.otel_id, aktif=True).order_by(Kat.kat_no).all()
            form.kat_id.choices = [(k.id, k.kat_adi) for k in katlar]
        
        if form.validate_on_submit():
            try:
                # Kat'ın seçilen otele ait olduğunu kontrol et
                kat = Kat.query.get(form.kat_id.data)
                if not kat or kat.otel_id != form.otel_id.data:
                    flash('Seçilen kat, seçilen otele ait değil!', 'danger')
                    return render_template('sistem_yoneticisi/oda_duzenle.html', oda=oda, form=form, oteller=oteller)
                
                oda.oda_no = form.oda_no.data
                oda.kat_id = form.kat_id.data
                oda.oda_tipi = form.oda_tipi.data
                oda.kapasite = form.kapasite.data
                oda.aktif = form.aktif.data
                
                db.session.commit()
                
                # Audit log
                audit_update(
                    tablo_adi='odalar',
                    kayit_id=oda.id,
                    eski_deger=eski_deger,
                    yeni_deger=serialize_model(oda),
                    aciklama=f'Oda güncellendi - {oda.oda_no}'
                )
                
                # Log kaydı
                log_islem('guncelleme', 'oda', {
                    'oda_id': oda.id,
                    'oda_no': oda.oda_no
                })
                
                flash(f'Oda {oda.oda_no} başarıyla güncellendi.', 'success')
                return redirect(url_for('oda_tanimla'))
            except Exception as e:
                db.session.rollback()
                log_hata(e, modul='oda_duzenle')
                flash('Oda güncellenirken hata oluştu.', 'danger')
        
        return render_template('sistem_yoneticisi/oda_duzenle.html', oda=oda, form=form, oteller=oteller)
    
    
    @app.route('/oda-sil/<int:oda_id>', methods=['POST'])
    @login_required
    @role_required('sistem_yoneticisi', 'admin')
    def oda_sil(oda_id):
        """Oda silme (pasif yapma)"""
        try:
            oda = db.session.get(Oda, oda_id)
            if not oda:
                flash('Oda bulunamadı.', 'danger')
                return redirect(url_for('oda_tanimla'))
            
            # Eski değeri sakla
            eski_deger = serialize_model(oda)
            
            # Pasif yap
            oda.aktif = False
            db.session.commit()
            
            # Audit log
            audit_delete(
                tablo_adi='odalar',
                kayit_id=oda.id,
                eski_deger=eski_deger,
                aciklama=f'Oda pasif yapıldı - {oda.oda_no}'
            )
            
            # Log kaydı
            log_islem('silme', 'oda', {
                'oda_id': oda.id,
                'oda_no': oda.oda_no
            })
            
            flash(f'Oda {oda.oda_no} başarıyla silindi.', 'success')
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul='oda_sil')
            flash('Oda silinirken hata oluştu.', 'danger')
        
        return redirect(url_for('oda_tanimla'))
