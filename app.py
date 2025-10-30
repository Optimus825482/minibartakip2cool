from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify
from datetime import datetime, timedelta
import os
import io
import openpyxl
from openpyxl.styles import Font, PatternFill
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması oluştur
app = Flask(__name__)

# Konfigürasyonu yükle
app.config.from_object('config.Config')

# Veritabanı başlat
from models import db
db.init_app(app)

# Yardımcı modülleri import et
from utils.decorators import login_required, role_required, setup_required, setup_not_completed
from utils.helpers import get_current_user, get_toplam_stok, get_kritik_stok_urunler, log_islem, get_son_loglar, get_kullanici_loglari, get_modul_loglari

# Modelleri import et
from models import (
    Otel, Kullanici, Kat, Oda, UrunGrup, Urun, StokHareket, 
    PersonelZimmet, PersonelZimmetDetay, MinibarIslem, MinibarIslemDetay, SistemAyar, SistemLog
)

# Context processor - tüm template'lere kullanıcı bilgisini gönder
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# Ana sayfa yönlendirmesi
@app.route('/')
def index():
    # Setup kontrolü
    setup_tamamlandi = SistemAyar.query.filter_by(anahtar='setup_tamamlandi').first()
    
    if not setup_tamamlandi or setup_tamamlandi.deger != '1':
        return redirect(url_for('setup'))
    
    # Giriş yapmış kullanıcı varsa dashboard'a yönlendir
    if 'kullanici_id' in session:
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))

# Setup sayfası
@app.route('/setup', methods=['GET', 'POST'])
@setup_not_completed
def setup():
    if request.method == 'POST':
        try:
            # Otel bilgileri
            otel = Otel(
                ad=request.form['otel_adi'],
                adres=request.form['adres'],
                telefon=request.form['telefon'],
                email=request.form['email'],
                vergi_no=request.form.get('vergi_no', '')
            )
            db.session.add(otel)
            db.session.flush()  # ID'yi almak için
            
            # Sistem yöneticisi oluştur
            sistem_yoneticisi = Kullanici(
                kullanici_adi=request.form['kullanici_adi'],
                ad=request.form['ad'],
                soyad=request.form['soyad'],
                email=request.form['admin_email'],
                telefon=request.form.get('admin_telefon', ''),
                rol='sistem_yoneticisi'
            )
            sistem_yoneticisi.sifre_belirle(request.form['sifre'])
            db.session.add(sistem_yoneticisi)
            
            # Setup tamamlandı işaretle
            setup_ayar = SistemAyar(
                anahtar='setup_tamamlandi',
                deger='1',
                aciklama='İlk kurulum tamamlandı'
            )
            db.session.add(setup_ayar)
            
            db.session.commit()
            
            flash('İlk kurulum başarıyla tamamlandı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Kurulum sırasında hata oluştu: {str(e)}', 'danger')
    
    return render_template('setup.html')

# Login sayfası
@app.route('/login', methods=['GET', 'POST'])
@setup_required
def login():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        remember_me = 'remember_me' in request.form
        
        kullanici = Kullanici.query.filter_by(
            kullanici_adi=kullanici_adi, 
            aktif=True
        ).first()
        
        if kullanici and kullanici.sifre_kontrol(sifre):
            session['kullanici_id'] = kullanici.id
            session['kullanici_adi'] = kullanici.kullanici_adi
            session['ad'] = kullanici.ad
            session['soyad'] = kullanici.soyad
            session['rol'] = kullanici.rol
            
            # Remember me
            if remember_me:
                session.permanent = True
            
            # Son giriş tarihini güncelle
            kullanici.son_giris = datetime.utcnow()
            db.session.commit()
            
            # Log kaydı
            log_islem('giris', 'sistem', {
                'kullanici_adi': kullanici.kullanici_adi,
                'ad_soyad': f'{kullanici.ad} {kullanici.soyad}',
                'rol': kullanici.rol
            })
            
            flash(f'Hoş geldiniz, {kullanici.ad} {kullanici.soyad}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'danger')
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    # Log kaydı (session temizlenmeden önce)
    kullanici_id = session.get('kullanici_id')
    if kullanici_id:
        kullanici = Kullanici.query.get(kullanici_id)
        if kullanici:
            log_islem('cikis', 'sistem', {
                'kullanici_adi': kullanici.kullanici_adi,
                'ad_soyad': f'{kullanici.ad} {kullanici.soyad}',
                'rol': kullanici.rol
            })
    
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

# Dashboard - rol bazlı yönlendirme
@app.route('/dashboard')
@login_required
def dashboard():
    rol = session.get('rol')
    
    if rol == 'sistem_yoneticisi':
        return redirect(url_for('sistem_yoneticisi_dashboard'))
    elif rol == 'admin':
        return redirect(url_for('sistem_yoneticisi_dashboard'))  # Admin de sistem yöneticisi dashboard'ını kullanır
    elif rol == 'depo_sorumlusu':
        return redirect(url_for('depo_dashboard'))
    elif rol == 'kat_sorumlusu':
        return redirect(url_for('kat_sorumlusu_dashboard'))
    else:
        flash('Geçersiz kullanıcı rolü!', 'danger')
        return redirect(url_for('logout'))

# Sistem Yöneticisi Dashboard
@app.route('/sistem-yoneticisi')
@login_required
@role_required('sistem_yoneticisi', 'admin')
def sistem_yoneticisi_dashboard():
    # İstatistikler
    toplam_kat = Kat.query.count()
    toplam_oda = Oda.query.count()
    toplam_kullanici = Kullanici.query.filter(
        Kullanici.rol.in_(['admin', 'depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).count()
    toplam_personel = Kullanici.query.filter(
        Kullanici.rol.in_(['depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).count()
    
    # Son eklenen katlar
    son_katlar = Kat.query.order_by(Kat.olusturma_tarihi.desc()).limit(5).all()
    
    # Son eklenen odalar
    son_odalar = Oda.query.order_by(Oda.olusturma_tarihi.desc()).limit(5).all()
    
    # Grafik verileri
    # Kullanıcı rol dağılımı
    admin_count = Kullanici.query.filter_by(rol='admin', aktif=True).count()
    depo_count = Kullanici.query.filter_by(rol='depo_sorumlusu', aktif=True).count()
    kat_count = Kullanici.query.filter_by(rol='kat_sorumlusu', aktif=True).count()
    
    # Kat bazlı oda sayıları
    katlar = Kat.query.filter_by(aktif=True).all()
    kat_labels = [kat.kat_adi for kat in katlar]
    kat_oda_sayilari = [len(kat.odalar) for kat in katlar]
    
    # Ürün grup sayıları (admin için)
    toplam_urun_grup = UrunGrup.query.filter_by(aktif=True).count()
    toplam_urun = Urun.query.filter_by(aktif=True).count()
    kritik_urunler = get_kritik_stok_urunler()
    
    # Son eklenen personeller (admin için)
    son_personeller = Kullanici.query.filter(
        Kullanici.rol.in_(['depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).order_by(Kullanici.olusturma_tarihi.desc()).limit(5).all()
    
    # Son eklenen ürünler (admin için)
    son_urunler = Urun.query.filter_by(aktif=True).order_by(Urun.olusturma_tarihi.desc()).limit(5).all()
    
    return render_template('sistem_yoneticisi/dashboard.html',
                         toplam_kat=toplam_kat,
                         toplam_oda=toplam_oda,
                         toplam_kullanici=toplam_kullanici,
                         toplam_personel=toplam_personel,
                         son_katlar=son_katlar,
                         son_odalar=son_odalar,
                         admin_count=admin_count,
                         depo_count=depo_count,
                         kat_count=kat_count,
                         kat_labels=kat_labels,
                         kat_oda_sayilari=kat_oda_sayilari,
                         toplam_urun_grup=toplam_urun_grup,
                         toplam_urun=toplam_urun,
                         kritik_urunler=kritik_urunler,
                         son_personeller=son_personeller,
                         son_urunler=son_urunler)

# Sistem Logları
@app.route('/sistem-loglari')
@login_required
@role_required('sistem_yoneticisi', 'admin')
def sistem_loglari():
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

# Admin dashboard kaldırıldı - Sistem Yöneticisi dashboard'ı kullanılıyor

# Depo Sorumlusu Dashboard
@app.route('/depo')
@login_required
@role_required('depo_sorumlusu')
def depo_dashboard():
    # İstatistikler
    toplam_urun = Urun.query.filter_by(aktif=True).count()
    kritik_urunler = get_kritik_stok_urunler()
    aktif_zimmetler = PersonelZimmet.query.filter_by(durum='aktif').count()
    
    # Zimmet iade istatistikleri
    toplam_iade_edilen = db.session.query(db.func.sum(PersonelZimmetDetay.iade_edilen_miktar)).filter(
        PersonelZimmetDetay.iade_edilen_miktar > 0
    ).scalar() or 0
    
    # Bu ay yapılan iade işlemleri
    from datetime import datetime, timedelta
    ay_basi = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    bu_ay_iadeler = StokHareket.query.filter(
        StokHareket.hareket_tipi == 'giris',
        StokHareket.aciklama.like('%Zimmet iadesi%'),
        StokHareket.islem_tarihi >= ay_basi
    ).count()
    
    # İptal edilen zimmetler
    iptal_zimmetler = PersonelZimmet.query.filter_by(durum='iptal').count()
    
    # Son stok hareketleri
    son_hareketler = StokHareket.query.order_by(StokHareket.islem_tarihi.desc()).limit(10).all()
    
    # Grafik verileri
    # Ürün grup bazlı stok durumu
    gruplar = UrunGrup.query.filter_by(aktif=True).all()
    grup_labels = []
    grup_stok_miktarlari = []
    
    for grup in gruplar:
        urunler = Urun.query.filter_by(grup_id=grup.id, aktif=True).all()
        toplam_stok = 0
        for urun in urunler:
            # Mevcut stok hesapla
            giris = db.session.query(db.func.sum(StokHareket.miktar)).filter(
                StokHareket.urun_id == urun.id,
                StokHareket.hareket_tipi == 'giris'
            ).scalar() or 0
            cikis = db.session.query(db.func.sum(StokHareket.miktar)).filter(
                StokHareket.urun_id == urun.id,
                StokHareket.hareket_tipi == 'cikis'
            ).scalar() or 0
            toplam_stok += (giris - cikis)
        
        if toplam_stok > 0:  # Sadece stoku olan grupları göster
            grup_labels.append(grup.grup_adi)
            grup_stok_miktarlari.append(toplam_stok)
    
    # Son 7 günün stok hareket istatistikleri
    from datetime import datetime, timedelta
    bugun = datetime.now().date()
    gun_labels = []
    giris_verileri = []
    cikis_verileri = []
    
    for i in range(6, -1, -1):  # Son 7 gün
        tarih = bugun - timedelta(days=i)
        gun_labels.append(tarih.strftime('%d.%m'))
        
        # Giriş
        giris = db.session.query(db.func.sum(StokHareket.miktar)).filter(
            db.func.date(StokHareket.islem_tarihi) == tarih,
            StokHareket.hareket_tipi == 'giris'
        ).scalar() or 0
        giris_verileri.append(float(giris))
        
        # Çıkış
        cikis = db.session.query(db.func.sum(StokHareket.miktar)).filter(
            db.func.date(StokHareket.islem_tarihi) == tarih,
            StokHareket.hareket_tipi == 'cikis'
        ).scalar() or 0
        cikis_verileri.append(float(cikis))
    
    return render_template('depo_sorumlusu/dashboard.html',
                         toplam_urun=toplam_urun,
                         kritik_urunler=kritik_urunler,
                         aktif_zimmetler=aktif_zimmetler,
                         toplam_iade_edilen=toplam_iade_edilen,
                         bu_ay_iadeler=bu_ay_iadeler,
                         iptal_zimmetler=iptal_zimmetler,
                         son_hareketler=son_hareketler,
                         grup_labels=grup_labels,
                         grup_stok_miktarlari=grup_stok_miktarlari,
                         gun_labels=gun_labels,
                         giris_verileri=giris_verileri,
                         cikis_verileri=cikis_verileri)

# Kat Sorumlusu Dashboard
@app.route('/kat-sorumlusu')
@login_required
@role_required('kat_sorumlusu')
def kat_sorumlusu_dashboard():
    kullanici_id = session['kullanici_id']
    
    # İstatistikler
    aktif_zimmetler = PersonelZimmet.query.filter_by(
        personel_id=kullanici_id, 
        durum='aktif'
    ).count()
    
    # Zimmetindeki toplam ürün miktarı
    zimmet_detaylari = db.session.query(
        db.func.sum(PersonelZimmetDetay.kalan_miktar)
    ).join(PersonelZimmet).filter(
        PersonelZimmet.personel_id == kullanici_id,
        PersonelZimmet.durum == 'aktif'
    ).scalar() or 0
    
    # Son minibar işlemleri
    son_islemler = MinibarIslem.query.filter_by(
        personel_id=kullanici_id
    ).order_by(MinibarIslem.islem_tarihi.desc()).limit(10).all()
    
    # Grafik verileri
    # Zimmet kullanım durumu (ürün bazlı)
    zimmet_urunler = db.session.query(
        Urun.urun_adi,
        db.func.sum(PersonelZimmetDetay.miktar).label('teslim_edilen'),
        db.func.sum(PersonelZimmetDetay.kullanilan_miktar).label('kullanilan'),
        db.func.sum(PersonelZimmetDetay.kalan_miktar).label('kalan')
    ).join(Urun, PersonelZimmetDetay.urun_id == Urun.id).join(
        PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
    ).filter(
        PersonelZimmet.personel_id == kullanici_id,
        PersonelZimmet.durum == 'aktif'
    ).group_by(Urun.id, Urun.urun_adi).all()
    
    zimmet_urun_labels = [u[0] for u in zimmet_urunler]
    zimmet_kullanilan = [float(u[2] or 0) for u in zimmet_urunler]
    zimmet_kalan = [float(u[3] or 0) for u in zimmet_urunler]
    
    # Minibar işlem tipi dağılımı
    islem_ilk_dolum = MinibarIslem.query.filter_by(
        personel_id=kullanici_id,
        islem_tipi='ilk_dolum'
    ).count()
    islem_kontrol = MinibarIslem.query.filter_by(
        personel_id=kullanici_id,
        islem_tipi='kontrol'
    ).count()
    islem_doldurma = MinibarIslem.query.filter_by(
        personel_id=kullanici_id,
        islem_tipi='doldurma'
    ).count()
    
    return render_template('kat_sorumlusu/dashboard.html',
                         aktif_zimmetler=aktif_zimmetler,
                         zimmet_toplam=zimmet_detaylari,
                         son_islemler=son_islemler,
                         zimmet_urun_labels=zimmet_urun_labels,
                         zimmet_kullanilan=zimmet_kullanilan,
                         zimmet_kalan=zimmet_kalan,
                         islem_ilk_dolum=islem_ilk_dolum,
                         islem_kontrol=islem_kontrol,
                         islem_doldurma=islem_doldurma)

# Sistem Yöneticisi Rotaları
@app.route('/otel-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def otel_tanimla():
    otel = Otel.query.first()
    
    if request.method == 'POST':
        try:
            if otel:
                # Güncelle
                otel.ad = request.form['otel_adi']
                otel.adres = request.form['adres']
                otel.telefon = request.form['telefon']
                otel.email = request.form['email']
                otel.vergi_no = request.form['vergi_no']
            else:
                # Yeni oluştur
                otel = Otel(
                    ad=request.form['otel_adi'],
                    adres=request.form['adres'],
                    telefon=request.form['telefon'],
                    email=request.form['email'],
                    vergi_no=request.form['vergi_no']
                )
                db.session.add(otel)
            
            db.session.commit()
            flash('Otel bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('sistem_yoneticisi_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return render_template('sistem_yoneticisi/otel_tanimla.html', otel=otel)

@app.route('/kat-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_tanimla():
    if request.method == 'POST':
        try:
            kat = Kat(
                otel_id=1,  # İlk otel
                kat_adi=request.form['kat_adi'],
                kat_no=int(request.form['kat_no']),
                aciklama=request.form.get('aciklama', '')
            )
            db.session.add(kat)
            db.session.commit()
            flash('Kat başarıyla eklendi.', 'success')
            return redirect(url_for('kat_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    return render_template('sistem_yoneticisi/kat_tanimla.html', katlar=katlar)

@app.route('/kat-duzenle/<int:kat_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_duzenle(kat_id):
    kat = Kat.query.get_or_404(kat_id)
    
    if request.method == 'POST':
        try:
            kat.kat_adi = request.form['kat_adi']
            kat.kat_no = int(request.form['kat_no'])
            kat.aciklama = request.form.get('aciklama', '')
            
            db.session.commit()
            flash('Kat başarıyla güncellendi.', 'success')
            return redirect(url_for('kat_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return render_template('sistem_yoneticisi/kat_duzenle.html', kat=kat)

@app.route('/kat-sil/<int:kat_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_sil(kat_id):
    try:
        kat = Kat.query.get_or_404(kat_id)
        kat.aktif = False
        db.session.commit()
        flash('Kat başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('kat_tanimla'))

@app.route('/oda-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_tanimla():
    if request.method == 'POST':
        try:
            oda = Oda(
                kat_id=int(request.form['kat_id']),
                oda_no=request.form['oda_no'],
                oda_tipi=request.form.get('oda_tipi', ''),
                kapasite=int(request.form['kapasite']) if request.form.get('kapasite') else None
            )
            db.session.add(oda)
            db.session.commit()
            flash('Oda başarıyla eklendi.', 'success')
            return redirect(url_for('oda_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    odalar = Oda.query.filter_by(aktif=True).order_by(Oda.oda_no).all()
    return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=katlar, odalar=odalar)

@app.route('/oda-duzenle/<int:oda_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_duzenle(oda_id):
    oda = Oda.query.get_or_404(oda_id)
    
    if request.method == 'POST':
        try:
            oda.kat_id = int(request.form['kat_id'])
            oda.oda_no = request.form['oda_no']
            oda.oda_tipi = request.form.get('oda_tipi', '')
            oda.kapasite = int(request.form['kapasite']) if request.form.get('kapasite') else None
            
            db.session.commit()
            flash('Oda başarıyla güncellendi.', 'success')
            return redirect(url_for('oda_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    return render_template('sistem_yoneticisi/oda_duzenle.html', oda=oda, katlar=katlar)

@app.route('/oda-sil/<int:oda_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_sil(oda_id):
    try:
        oda = Oda.query.get_or_404(oda_id)
        db.session.delete(oda)
        db.session.commit()
        flash('Oda başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('oda_tanimla'))

# Admin Ata rotaları kaldırıldı - Admin artık tüm yetkilere sahip

# Admin Rotaları
@app.route('/personel-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_tanimla():
    if request.method == 'POST':
        try:
            personel = Kullanici(
                kullanici_adi=request.form['kullanici_adi'],
                ad=request.form['ad'],
                soyad=request.form['soyad'],
                email=request.form.get('email', ''),
                telefon=request.form.get('telefon', ''),
                rol=request.form['rol']
            )
            personel.sifre_belirle(request.form['sifre'])
            db.session.add(personel)
            db.session.commit()
            flash('Kullanıcı başarıyla eklendi.', 'success')
            return redirect(url_for('personel_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            
            # Kullanıcı dostu hata mesajları
            if 'Duplicate entry' in error_msg and 'kullanici_adi' in error_msg:
                flash('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.', 'danger')
            elif 'Duplicate entry' in error_msg and 'email' in error_msg:
                flash('Bu e-posta adresi zaten kullanılıyor. Lütfen farklı bir e-posta adresi seçin.', 'danger')
            else:
                flash(f'Hata oluştu: {error_msg}', 'danger')
    
    personeller = Kullanici.query.filter(
        Kullanici.rol.in_(['admin', 'depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).order_by(Kullanici.olusturma_tarihi.desc()).all()
    return render_template('admin/personel_tanimla.html', personeller=personeller)

@app.route('/personel-duzenle/<int:personel_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_duzenle(personel_id):
    personel = Kullanici.query.get_or_404(personel_id)
    
    if request.method == 'POST':
        try:
            personel.kullanici_adi = request.form['kullanici_adi']
            personel.ad = request.form['ad']
            personel.soyad = request.form['soyad']
            personel.email = request.form.get('email', '')
            personel.telefon = request.form.get('telefon', '')
            personel.rol = request.form['rol']
            
            # Şifre değiştirilmişse
            if request.form.get('yeni_sifre'):
                personel.sifre_belirle(request.form['yeni_sifre'])
            
            db.session.commit()
            flash('Kullanıcı başarıyla güncellendi.', 'success')
            return redirect(url_for('personel_tanimla'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            
            # Kullanıcı dostu hata mesajları
            if 'Duplicate entry' in error_msg and 'kullanici_adi' in error_msg:
                flash('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.', 'danger')
            elif 'Duplicate entry' in error_msg and 'email' in error_msg:
                flash('Bu e-posta adresi zaten kullanılıyor. Lütfen farklı bir e-posta adresi seçin.', 'danger')
            else:
                flash(f'Hata oluştu: {error_msg}', 'danger')
    
    return render_template('admin/personel_duzenle.html', personel=personel)

@app.route('/personel-pasif-yap/<int:personel_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_pasif_yap(personel_id):
    try:
        personel = Kullanici.query.get_or_404(personel_id)
        personel.aktif = False
        db.session.commit()
        flash('Kullanıcı başarıyla pasif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('personel_tanimla'))

@app.route('/personel-aktif-yap/<int:personel_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_aktif_yap(personel_id):
    try:
        personel = Kullanici.query.get_or_404(personel_id)
        personel.aktif = True
        db.session.commit()
        flash('Kullanıcı başarıyla aktif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('personel_tanimla'))

@app.route('/urun-gruplari', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_gruplari():
    if request.method == 'POST':
        try:
            grup = UrunGrup(
                grup_adi=request.form['grup_adi'],
                aciklama=request.form.get('aciklama', '')
            )
            db.session.add(grup)
            db.session.commit()
            flash('Ürün grubu başarıyla eklendi.', 'success')
            return redirect(url_for('urun_gruplari'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    return render_template('admin/urun_gruplari.html', gruplar=gruplar)

@app.route('/grup-duzenle/<int:grup_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def grup_duzenle(grup_id):
    grup = UrunGrup.query.get_or_404(grup_id)
    
    if request.method == 'POST':
        try:
            grup.grup_adi = request.form['grup_adi']
            grup.aciklama = request.form.get('aciklama', '')
            db.session.commit()
            flash('Ürün grubu başarıyla güncellendi.', 'success')
            return redirect(url_for('urun_gruplari'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return render_template('admin/grup_duzenle.html', grup=grup)

@app.route('/grup-sil/<int:grup_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def grup_sil(grup_id):
    try:
        grup = UrunGrup.query.get_or_404(grup_id)
        
        # Gruba ait ürün var mı kontrol et
        urun_sayisi = Urun.query.filter_by(grup_id=grup_id).count()
        if urun_sayisi > 0:
            flash(f'Bu gruba ait {urun_sayisi} ürün bulunmaktadır. Önce ürünleri silin veya başka gruba taşıyın.', 'danger')
            return redirect(url_for('urun_gruplari'))
        
        db.session.delete(grup)
        db.session.commit()
        flash('Ürün grubu başarıyla silindi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urun_gruplari'))

@app.route('/grup-pasif-yap/<int:grup_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def grup_pasif_yap(grup_id):
    try:
        grup = UrunGrup.query.get_or_404(grup_id)
        grup.aktif = False
        db.session.commit()
        flash('Ürün grubu başarıyla pasif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urun_gruplari'))

@app.route('/grup-aktif-yap/<int:grup_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def grup_aktif_yap(grup_id):
    try:
        grup = UrunGrup.query.get_or_404(grup_id)
        grup.aktif = True
        db.session.commit()
        flash('Ürün grubu başarıyla aktif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urun_gruplari'))

@app.route('/urunler', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urunler():
    if request.method == 'POST':
        try:
            barkod = request.form.get('barkod', '').strip()
            urun = Urun(
                grup_id=int(request.form['grup_id']),
                urun_adi=request.form['urun_adi'],
                barkod=barkod if barkod else None,
                birim=request.form.get('birim', 'Adet'),
                kritik_stok_seviyesi=int(request.form.get('kritik_stok_seviyesi', 10))
            )
            db.session.add(urun)
            db.session.commit()
            
            # Log kaydı
            log_islem('ekleme', 'urun', {
                'urun_adi': urun.urun_adi,
                'barkod': urun.barkod,
                'grup_id': urun.grup_id,
                'birim': urun.birim
            })
            
            flash('Ürün başarıyla eklendi.', 'success')
            return redirect(url_for('urunler'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if 'Duplicate entry' in error_msg and 'barkod' in error_msg:
                flash('Bu barkod numarası zaten kullanılıyor. Lütfen farklı bir barkod girin veya boş bırakın.', 'danger')
            else:
                flash(f'Hata oluştu: {error_msg}', 'danger')
    
    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    # Tüm ürünleri getir (aktif ve pasif)
    urunler = Urun.query.order_by(Urun.aktif.desc(), Urun.urun_adi).all()
    return render_template('admin/urunler.html', gruplar=gruplar, urunler=urunler)

@app.route('/urun-duzenle/<int:urun_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_duzenle(urun_id):
    urun = Urun.query.get_or_404(urun_id)
    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    
    if request.method == 'POST':
        try:
            barkod = request.form.get('barkod', '').strip()
            eski_urun_adi = urun.urun_adi
            urun.urun_adi = request.form['urun_adi']
            urun.grup_id = int(request.form['grup_id'])
            urun.barkod = barkod if barkod else None
            urun.birim = request.form.get('birim', 'Adet')
            urun.kritik_stok_seviyesi = int(request.form.get('kritik_stok_seviyesi', 10))
            
            db.session.commit()
            
            # Log kaydı
            log_islem('guncelleme', 'urun', {
                'urun_id': urun.id,
                'eski_urun_adi': eski_urun_adi,
                'yeni_urun_adi': urun.urun_adi,
                'barkod': urun.barkod
            })
            
            flash('Ürün başarıyla güncellendi.', 'success')
            return redirect(url_for('urunler'))
            
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            if 'Duplicate entry' in error_msg and 'barkod' in error_msg:
                flash('Bu barkod numarası zaten kullanılıyor. Lütfen farklı bir barkod girin veya boş bırakın.', 'danger')
            else:
                flash(f'Hata oluştu: {error_msg}', 'danger')
    
    return render_template('admin/urun_duzenle.html', urun=urun, gruplar=gruplar)

@app.route('/urun-sil/<int:urun_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_sil(urun_id):
    try:
        urun = Urun.query.get_or_404(urun_id)
        urun_adi = urun.urun_adi
        
        # Ürüne ait stok hareketi var mı kontrol et
        stok_hareketi = StokHareket.query.filter_by(urun_id=urun_id).first()
        if stok_hareketi:
            flash('Bu ürüne ait stok hareketi bulunmaktadır. Ürün silinemez.', 'danger')
            return redirect(url_for('urunler'))
        
        db.session.delete(urun)
        db.session.commit()
        
        # Log kaydı
        log_islem('silme', 'urun', {
            'urun_id': urun_id,
            'urun_adi': urun_adi
        })
        
        flash('Ürün başarıyla silindi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urunler'))

@app.route('/urun-pasif-yap/<int:urun_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_pasif_yap(urun_id):
    try:
        urun = Urun.query.get_or_404(urun_id)
        urun.aktif = False
        db.session.commit()
        flash('Ürün başarıyla pasif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urunler'))

@app.route('/urun-aktif-yap/<int:urun_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_aktif_yap(urun_id):
    try:
        urun = Urun.query.get_or_404(urun_id)
        urun.aktif = True
        db.session.commit()
        flash('Ürün başarıyla aktif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urunler'))

# Depo Sorumlusu Rotaları
@app.route('/stok-giris', methods=['GET', 'POST'])
@login_required
@role_required('depo_sorumlusu')
def stok_giris():
    if request.method == 'POST':
        try:
            urun_id = int(request.form['urun_id'])
            miktar = int(request.form['miktar'])
            hareket_tipi = request.form['hareket_tipi']
            aciklama = request.form.get('aciklama', '')
            
            urun = Urun.query.get(urun_id)
            stok_hareket = StokHareket(
                urun_id=urun_id,
                hareket_tipi=hareket_tipi,
                miktar=miktar,
                aciklama=aciklama,
                islem_yapan_id=session['kullanici_id']
            )
            db.session.add(stok_hareket)
            db.session.commit()
            
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
    
    urunler = Urun.query.filter_by(aktif=True).order_by(Urun.urun_adi).all()
    
    # Son stok hareketlerini getir
    stok_hareketleri = StokHareket.query.order_by(StokHareket.islem_tarihi.desc()).limit(50).all()
    
    return render_template('depo_sorumlusu/stok_giris.html', 
                         urunler=urunler, 
                         stok_hareketleri=stok_hareketleri)

@app.route('/stok-duzenle/<int:hareket_id>', methods=['GET', 'POST'])
@login_required
@role_required('depo_sorumlusu')
def stok_duzenle(hareket_id):
    hareket = StokHareket.query.get_or_404(hareket_id)
    
    if request.method == 'POST':
        try:
            hareket.miktar = int(request.form['miktar'])
            hareket.hareket_tipi = request.form['hareket_tipi']
            hareket.aciklama = request.form.get('aciklama', '')
            
            db.session.commit()
            
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
    try:
        hareket = StokHareket.query.get_or_404(hareket_id)
        
        # Log kaydı için bilgileri sakla
        urun_adi = hareket.urun.urun_adi if hareket.urun else 'Bilinmeyen'
        hareket_tipi = hareket.hareket_tipi
        miktar = hareket.miktar
        
        # Hareketi sil
        db.session.delete(hareket)
        db.session.commit()
        
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
    if request.method == 'POST':
        try:
            personel_id = int(request.form['personel_id'])
            aciklama = request.form.get('aciklama', '')
            urun_ids = request.form.getlist('urun_ids')
            
            if not urun_ids:
                flash('En az bir ürün seçmelisiniz.', 'warning')
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
            for urun_id in urun_ids:
                miktar = int(request.form.get(f'miktar_{urun_id}', 0))
                if miktar > 0:
                    detay = PersonelZimmetDetay(
                        zimmet_id=zimmet.id,
                        urun_id=int(urun_id),
                        miktar=miktar,
                        kalan_miktar=miktar
                    )
                    db.session.add(detay)
                    
                    # Stok çıkışı kaydet
                    stok_hareket = StokHareket(
                        urun_id=int(urun_id),
                        hareket_tipi='cikis',
                        miktar=miktar,
                        aciklama=f'Zimmet atama - {aciklama}',
                        islem_yapan_id=session['kullanici_id']
                    )
                    db.session.add(stok_hareket)
            
            db.session.commit()
            flash('Zimmet başarıyla atandı.', 'success')
            return redirect(url_for('personel_zimmet'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Hata oluştu: {str(e)}', 'danger')
    
    kat_sorumlulari = Kullanici.query.filter_by(rol='kat_sorumlusu', aktif=True).all()
    urun_gruplari = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    aktif_zimmetler = PersonelZimmet.query.filter_by(durum='aktif').order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
    
    return render_template('depo_sorumlusu/personel_zimmet.html', 
                         kat_sorumlulari=kat_sorumlulari, 
                         urun_gruplari=urun_gruplari, 
                         aktif_zimmetler=aktif_zimmetler)

# AJAX endpoint - Kata göre odaları getir
@app.route('/api/odalar-by-kat/<int:kat_id>')
@login_required
@role_required('kat_sorumlusu', 'sistem_yoneticisi')
def odalar_by_kat(kat_id):
    from flask import jsonify
    odalar = Oda.query.filter_by(kat_id=kat_id, aktif=True).order_by(Oda.oda_no).all()
    return jsonify([{
        'id': oda.id,
        'oda_numarasi': oda.oda_no
    } for oda in odalar])

# AJAX endpoint - Gruba göre ürünleri getir
@app.route('/api/urunler-by-grup/<int:grup_id>')
@login_required
@role_required('depo_sorumlusu', 'kat_sorumlusu')
def urunler_by_grup(grup_id):
    from flask import jsonify
    urunler = Urun.query.filter_by(grup_id=grup_id, aktif=True).order_by(Urun.urun_adi).all()
    return jsonify([{
        'id': urun.id,
        'urun_adi': urun.urun_adi,
        'birim': urun.birim,
        'kritik_stok_seviyesi': urun.kritik_stok_seviyesi
    } for urun in urunler])

# AJAX endpoint - Ürün stok bilgisini getir
@app.route('/api/urun-stok/<int:urun_id>')
@login_required
@role_required('depo_sorumlusu', 'kat_sorumlusu')
def urun_stok(urun_id):
    from flask import jsonify
    urun = Urun.query.get_or_404(urun_id)
    
    # Mevcut stok hesapla
    giris_toplam = db.session.query(db.func.sum(StokHareket.miktar)).filter(
        StokHareket.urun_id == urun_id,
        StokHareket.hareket_tipi.in_(['giris', 'devir', 'sayim'])
    ).scalar() or 0
    
    cikis_toplam = db.session.query(db.func.sum(StokHareket.miktar)).filter(
        StokHareket.urun_id == urun_id,
        StokHareket.hareket_tipi == 'cikis'
    ).scalar() or 0
    
    mevcut_stok = giris_toplam - cikis_toplam
    
    return jsonify({
        'urun_adi': urun.urun_adi,
        'birim': urun.birim,
        'grup_adi': urun.grup.grup_adi,
        'kritik_stok_seviyesi': urun.kritik_stok_seviyesi,
        'mevcut_stok': mevcut_stok,
        'stok_durumu': 'Yeterli' if mevcut_stok > urun.kritik_stok_seviyesi else ('Kritik' if mevcut_stok > 0 else 'Tükendi')
    })

# AJAX endpoint - Kat sorumlusunun zimmet bilgileri
@app.route('/api/zimmetim')
@login_required
@role_required('kat_sorumlusu')
def api_zimmetim():
    from flask import jsonify
    kullanici_id = session['kullanici_id']
    
    # Aktif zimmetlerdeki ürünleri getir
    zimmet_detaylar = db.session.query(
        PersonelZimmetDetay.urun_id,
        Urun.urun_adi,
        Urun.birim,
        db.func.sum(PersonelZimmetDetay.miktar).label('toplam_miktar'),
        db.func.sum(PersonelZimmetDetay.kullanilan_miktar).label('kullanilan_miktar'),
        db.func.sum(PersonelZimmetDetay.kalan_miktar).label('kalan_miktar')
    ).join(Urun, PersonelZimmetDetay.urun_id == Urun.id).join(
        PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
    ).filter(
        PersonelZimmet.personel_id == kullanici_id,
        PersonelZimmet.durum == 'aktif'
    ).group_by(PersonelZimmetDetay.urun_id, Urun.urun_adi, Urun.birim).all()
    
    return jsonify([{
        'urun_id': detay.urun_id,
        'urun_adi': detay.urun_adi,
        'birim': detay.birim,
        'toplam_miktar': float(detay.toplam_miktar or 0),
        'kullanilan_miktar': float(detay.kullanilan_miktar or 0),
        'kalan_miktar': float(detay.kalan_miktar or 0)
    } for detay in zimmet_detaylar])

@app.route('/zimmet-detay/<int:zimmet_id>')
@login_required
@role_required('depo_sorumlusu')
def zimmet_detay(zimmet_id):
    zimmet = PersonelZimmet.query.get_or_404(zimmet_id)
    return render_template('depo_sorumlusu/zimmet_detay.html', zimmet=zimmet)

@app.route('/zimmet-iptal/<int:zimmet_id>', methods=['POST'])
@login_required
@role_required('depo_sorumlusu')
def zimmet_iptal(zimmet_id):
    """Zimmeti tamamen iptal et ve kullanılmayan ürünleri depoya iade et"""
    try:
        zimmet = PersonelZimmet.query.get_or_404(zimmet_id)
        
        # Sadece aktif zimmetler iptal edilebilir
        if zimmet.durum != 'aktif':
            flash('Sadece aktif zimmetler iptal edilebilir.', 'warning')
            return redirect(url_for('personel_zimmet'))
        
        # Tüm zimmet detaylarını kontrol et ve kullanılmayan ürünleri depoya iade et
        for detay in zimmet.detaylar:
            kalan = detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar)
            
            if kalan > 0:
                # Stok hareketi oluştur (depoya giriş)
                stok_hareket = StokHareket(
                    urun_id=detay.urun_id,
                    hareket_tipi='giris',
                    miktar=kalan,
                    aciklama=f'Zimmet iptali - {zimmet.personel.ad} {zimmet.personel.soyad} - Zimmet #{zimmet.id}',
                    islem_yapan_id=current_user.id
                )
                db.session.add(stok_hareket)
                
                # İade edilen miktarı kaydet
                detay.iade_edilen_miktar = (detay.iade_edilen_miktar or 0) + kalan
                detay.kalan_miktar = 0
        
        # Zimmet durumunu güncelle
        zimmet.durum = 'iptal'
        zimmet.iade_tarihi = datetime.utcnow()
        
        db.session.commit()
        flash(f'{zimmet.personel.ad} {zimmet.personel.soyad} adlı personelin zimmeti iptal edildi ve kullanılmayan ürünler depoya iade edildi.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Zimmet iptal edilirken hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('personel_zimmet'))

@app.route('/zimmet-iade/<int:detay_id>', methods=['POST'])
@login_required
@role_required('depo_sorumlusu')
def zimmet_iade(detay_id):
    """Belirli bir ürünü kısmen veya tamamen iade al"""
    try:
        detay = PersonelZimmetDetay.query.get_or_404(detay_id)
        zimmet = detay.zimmet
        
        # Sadece aktif zimmetlerden iade alınabilir
        if zimmet.durum != 'aktif':
            flash('Sadece aktif zimmetlerden ürün iadesi alınabilir.', 'warning')
            return redirect(url_for('zimmet_detay', zimmet_id=zimmet.id))
        
        iade_miktar = int(request.form.get('iade_miktar', 0))
        aciklama = request.form.get('aciklama', '')
        
        if iade_miktar <= 0:
            flash('İade miktarı 0\'dan büyük olmalıdır.', 'warning')
            return redirect(url_for('zimmet_detay', zimmet_id=zimmet.id))
        
        # Kalan miktarı kontrol et
        kalan = detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar)
        
        if iade_miktar > kalan:
            flash(f'İade miktarı kalan miktardan fazla olamaz. Kalan: {kalan}', 'danger')
            return redirect(url_for('zimmet_detay', zimmet_id=zimmet.id))
        
        # Stok hareketi oluştur (depoya giriş)
        stok_hareket = StokHareket(
            urun_id=detay.urun_id,
            hareket_tipi='giris',
            miktar=iade_miktar,
            aciklama=f'Zimmet iadesi - {zimmet.personel.ad} {zimmet.personel.soyad} - {aciklama}',
            islem_yapan_id=current_user.id
        )
        db.session.add(stok_hareket)
        
        # Zimmet detayını güncelle
        detay.iade_edilen_miktar = (detay.iade_edilen_miktar or 0) + iade_miktar
        detay.kalan_miktar = kalan - iade_miktar
        
        db.session.commit()
        flash(f'{detay.urun.urun_adi} ürününden {iade_miktar} adet iade alındı.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'İade işlemi sırasında hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('zimmet_detay', zimmet_id=zimmet.id))

@app.route('/minibar-durumlari')
@login_required
@role_required('depo_sorumlusu')
def minibar_durumlari():
    """Minibar durumları - Kat ve oda seçimine göre minibar içeriğini göster"""
    kat_id = request.args.get('kat_id', type=int)
    oda_id = request.args.get('oda_id', type=int)
    
    # Tüm katları al
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    
    # Seçili kat varsa odaları al
    odalar = []
    if kat_id:
        odalar = Oda.query.filter_by(kat_id=kat_id, aktif=True).order_by(Oda.oda_no).all()
    
    # Seçili oda varsa minibar bilgilerini al
    minibar_bilgisi = None
    son_islem = None
    minibar_urunler = []
    
    if oda_id:
        oda = Oda.query.get(oda_id)
        
        # Son minibar işlemini bul
        son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(
            MinibarIslem.islem_tarihi.desc()
        ).first()
        
        if son_islem:
            # Bu oda için tüm minibar işlemlerini al
            tum_islemler = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(
                MinibarIslem.islem_tarihi.asc()
            ).all()
            
            # Her ürün için toplam hesaplama yap
            urun_toplam = {}
            ilk_dolum_yapildi = set()  # İlk dolum yapılan ürünleri takip et
            
            for islem in tum_islemler:
                for detay in islem.detaylar:
                    urun_id = detay.urun_id
                    if urun_id not in urun_toplam:
                        urun_toplam[urun_id] = {
                            'urun': detay.urun,
                            'toplam_eklenen_ilk_dolum': 0,  # İlk dolumda eklenen (tüketim değil)
                            'toplam_eklenen_doldurma': 0,   # Doldurmalarda eklenen (= tüketim)
                            'toplam_tuketim': 0,
                            'ilk_baslangic': detay.baslangic_stok,
                            'son_bitis': detay.bitis_stok
                        }
                    
                    # İlk dolum mu kontrol et
                    if islem.islem_tipi == 'ilk_dolum' and urun_id not in ilk_dolum_yapildi:
                        urun_toplam[urun_id]['toplam_eklenen_ilk_dolum'] += detay.eklenen_miktar
                        ilk_dolum_yapildi.add(urun_id)
                    elif islem.islem_tipi in ['doldurma', 'kontrol']:
                        # Doldurma veya kontrolde eklenen miktar = tüketim
                        urun_toplam[urun_id]['toplam_eklenen_doldurma'] += detay.eklenen_miktar
                        urun_toplam[urun_id]['toplam_tuketim'] += detay.eklenen_miktar
                    
                    urun_toplam[urun_id]['son_bitis'] = detay.bitis_stok
            
            # Son işlemdeki ürünleri listele (güncel durumda olan ürünler)
            for detay in son_islem.detaylar:
                urun_id = detay.urun_id
                urun_data = urun_toplam.get(urun_id, {})
                
                # Toplam eklenen = İlk dolum + Doldurma
                ilk_dolum_eklenen = urun_data.get('toplam_eklenen_ilk_dolum', 0)
                doldurma_eklenen = urun_data.get('toplam_eklenen_doldurma', 0)
                toplam_eklenen = ilk_dolum_eklenen + doldurma_eklenen
                toplam_tuketim = urun_data.get('toplam_tuketim', 0)
                
                # Mevcut miktar = İlk dolum + Doldurma - Tüketim
                # Ama doldurma = tüketim olduğu için: İlk dolum miktarı kadar olmalı
                mevcut_miktar = urun_data.get('son_bitis', 0)
                
                minibar_urunler.append({
                    'urun': detay.urun,
                    'baslangic_stok': urun_data.get('ilk_baslangic', 0),
                    'bitis_stok': urun_data.get('son_bitis', 0),
                    'eklenen_miktar': toplam_eklenen,
                    'tuketim': toplam_tuketim,
                    'mevcut_miktar': mevcut_miktar
                })
            
            minibar_bilgisi = {
                'oda': oda,
                'son_islem': son_islem,
                'urunler': minibar_urunler,
                'toplam_urun': len(minibar_urunler),
                'toplam_miktar': sum(u['mevcut_miktar'] for u in minibar_urunler)
            }
    
    return render_template('depo_sorumlusu/minibar_durumlari.html',
                         katlar=katlar,
                         odalar=odalar,
                         minibar_bilgisi=minibar_bilgisi,
                         kat_id=kat_id,
                         oda_id=oda_id)

@app.route('/minibar-urun-gecmis/<int:oda_id>/<int:urun_id>')
@login_required
@role_required('depo_sorumlusu')
def minibar_urun_gecmis(oda_id, urun_id):
    """Belirli bir ürünün minibar geçmişini getir"""
    oda = Oda.query.get_or_404(oda_id)
    urun = Urun.query.get_or_404(urun_id)
    
    # Bu oda için tüm minibar işlemlerini al
    gecmis = []
    minibar_islemler = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(
        MinibarIslem.islem_tarihi.desc()
    ).all()
    
    for islem in minibar_islemler:
        # Bu işlemde bu ürün var mı?
        detay = MinibarIslemDetay.query.filter_by(
            islem_id=islem.id,
            urun_id=urun_id
        ).first()
        
        if detay:
            gecmis.append({
                'islem_tarihi': islem.islem_tarihi.strftime('%d.%m.%Y %H:%M'),
                'islem_tipi': islem.islem_tipi,
                'personel': f"{islem.personel.ad} {islem.personel.soyad}",
                'baslangic_stok': detay.baslangic_stok,
                'eklenen_miktar': detay.eklenen_miktar,
                'tuketim': detay.tuketim,
                'bitis_stok': detay.bitis_stok,
                'aciklama': islem.aciklama or '-'
            })
    
    return jsonify({
        'success': True,
        'oda': f"{oda.oda_no}",
        'urun': urun.urun_adi,
        'gecmis': gecmis
    })

@app.route('/depo-raporlar')
@login_required
@role_required('depo_sorumlusu')
def depo_raporlar():
    # Filtreleme parametreleri
    baslangic_tarihi = request.args.get('baslangic_tarihi')
    bitis_tarihi = request.args.get('bitis_tarihi')
    rapor_tipi = request.args.get('rapor_tipi', '')
    urun_grup_id = request.args.get('urun_grup_id', '')
    urun_id = request.args.get('urun_id', '')
    personel_id = request.args.get('personel_id', '')
    hareket_tipi = request.args.get('hareket_tipi', '')
    
    rapor_verisi = None
    rapor_baslik = ""
    
    # Ürün gruplarını ve personelleri filtre için getir
    urun_gruplari = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    urunler = Urun.query.filter_by(aktif=True).order_by(Urun.urun_adi).all()
    personeller = Kullanici.query.filter_by(rol='kat_sorumlusu', aktif=True).order_by(Kullanici.ad, Kullanici.soyad).all()
    
    if rapor_tipi:
        if rapor_tipi == 'stok_durum':
            # Stok Durum Raporu - Tüm ürünler için mevcut stok durumu
            rapor_baslik = "Stok Durum Raporu"
            
            query = Urun.query.filter_by(aktif=True)
            
            if urun_grup_id:
                query = query.filter_by(grup_id=urun_grup_id)
            
            urunler_liste = query.order_by(Urun.urun_adi).all()
            
            rapor_verisi = []
            for urun in urunler_liste:
                mevcut_stok = get_toplam_stok(urun.id)
                rapor_verisi.append({
                    'urun': urun,
                    'mevcut_stok': mevcut_stok
                })
        
        elif rapor_tipi == 'stok_hareket':
            # Stok Hareket Raporu - Detaylı stok hareketleri
            rapor_baslik = "Stok Hareket Raporu"
            
            query = StokHareket.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(StokHareket.islem_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(StokHareket.islem_tarihi < bitis)
            
            if urun_id:
                query = query.filter_by(urun_id=urun_id)
            elif urun_grup_id:
                query = query.join(Urun).filter(Urun.grup_id == urun_grup_id)
            
            if hareket_tipi:
                query = query.filter_by(hareket_tipi=hareket_tipi)
            
            rapor_verisi = query.order_by(StokHareket.islem_tarihi.desc()).all()
            
            # Her hareket için zimmet bilgisini ekleyelim
            for hareket in rapor_verisi:
                # Eğer açıklamada zimmet bilgisi varsa, zimmet personelini bul
                if hareket.aciklama and 'Zimmet' in hareket.aciklama:
                    try:
                        if '#' in hareket.aciklama:
                            zimmet_id = int(hareket.aciklama.split('#')[1].split()[0])
                            zimmet = PersonelZimmet.query.get(zimmet_id)
                            if zimmet and zimmet.personel:
                                hareket.zimmet_personel = f"{zimmet.personel.ad} {zimmet.personel.soyad}"
                            else:
                                hareket.zimmet_personel = None
                        else:
                            hareket.zimmet_personel = None
                    except:
                        hareket.zimmet_personel = None
                else:
                    hareket.zimmet_personel = None
        
        elif rapor_tipi == 'zimmet':
            # Zimmet Raporu - Personel zimmet durumu
            rapor_baslik = "Zimmet Raporu"
            
            query = PersonelZimmet.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter_by(personel_id=personel_id)
            
            rapor_verisi = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
        
        elif rapor_tipi == 'zimmet_detay':
            # Zimmet Detay Raporu - Ürün bazlı zimmet bilgisi
            rapor_baslik = "Ürün Bazlı Zimmet Detay Raporu"
            
            query = db.session.query(
                PersonelZimmetDetay,
                PersonelZimmet,
                Kullanici,
                Urun
            ).join(
                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
            ).join(
                Kullanici, PersonelZimmet.personel_id == Kullanici.id
            ).join(
                Urun, PersonelZimmetDetay.urun_id == Urun.id
            )
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter(PersonelZimmet.personel_id == personel_id)
            
            if urun_id:
                query = query.filter(PersonelZimmetDetay.urun_id == urun_id)
            elif urun_grup_id:
                query = query.filter(Urun.grup_id == urun_grup_id)
            
            rapor_verisi = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
        
        elif rapor_tipi == 'minibar_tuketim':
            # Minibar Tüketim Raporu - Doldurma işlemlerindeki eklenen miktar = tüketim
            rapor_baslik = "Minibar Tüketim Raporu"
            
            query = db.session.query(
                Urun.urun_adi,
                Urun.birim,
                UrunGrup.grup_adi,
                Oda.oda_no,
                Kat.kat_adi,
                MinibarIslem.islem_tarihi,
                MinibarIslem.islem_tipi,
                MinibarIslemDetay.eklenen_miktar,
                Kullanici.ad,
                Kullanici.soyad
            ).select_from(MinibarIslemDetay).join(
                MinibarIslem, MinibarIslemDetay.islem_id == MinibarIslem.id
            ).join(
                Urun, MinibarIslemDetay.urun_id == Urun.id
            ).join(
                UrunGrup, Urun.grup_id == UrunGrup.id
            ).join(
                Oda, MinibarIslem.oda_id == Oda.id
            ).join(
                Kat, Oda.kat_id == Kat.id
            ).join(
                Kullanici, MinibarIslem.personel_id == Kullanici.id
            ).filter(
                # İlk dolum hariç, sadece doldurma ve kontrol işlemlerini al
                MinibarIslem.islem_tipi.in_(['doldurma', 'kontrol']),
                MinibarIslemDetay.eklenen_miktar > 0  # Sadece ekleme yapılan kayıtlar
            )
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(MinibarIslem.islem_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(MinibarIslem.islem_tarihi < bitis)
            
            if urun_id:
                query = query.filter(MinibarIslemDetay.urun_id == urun_id)
            elif urun_grup_id:
                query = query.filter(Urun.grup_id == urun_grup_id)
            
            if personel_id:
                query = query.filter(MinibarIslem.personel_id == personel_id)
            
            rapor_verisi = query.order_by(MinibarIslem.islem_tarihi.desc()).all()
        
        elif rapor_tipi == 'urun_grup':
            # Ürün Grubu Bazlı Rapor
            rapor_baslik = "Ürün Grubu Bazlı Stok Raporu"
            
            query = UrunGrup.query.filter_by(aktif=True)
            
            rapor_verisi = []
            for grup in query.all():
                grup_urunleri = Urun.query.filter_by(grup_id=grup.id, aktif=True).all()
                toplam_stok_degeri = 0
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = get_toplam_stok(urun.id)
                    if mevcut_stok <= urun.kritik_stok_seviyesi:
                        kritik_urun_sayisi += 1
                
                rapor_verisi.append({
                    'grup': grup,
                    'toplam_urun': toplam_urun_sayisi,
                    'kritik_urun': kritik_urun_sayisi
                })
        
        elif rapor_tipi == 'ozet':
            # Özet Rapor - Genel sistem durumu
            rapor_baslik = "Genel Sistem Özet Raporu"
            
            # Toplam ürün sayısı
            toplam_urun = Urun.query.filter_by(aktif=True).count()
            
            # Kritik stok seviyesindeki ürünler
            kritik_urunler = get_kritik_stok_urunler()
            
            # Aktif zimmetler
            aktif_zimmet = PersonelZimmet.query.filter_by(durum='aktif').count()
            
            # Bugünkü stok hareketleri
            bugun = datetime.now().date()
            bugun_baslangic = datetime.combine(bugun, datetime.min.time())
            bugun_bitis = datetime.combine(bugun, datetime.max.time())
            
            bugun_giris = StokHareket.query.filter(
                StokHareket.hareket_tipi == 'giris',
                StokHareket.islem_tarihi.between(bugun_baslangic, bugun_bitis)
            ).count()
            
            bugun_cikis = StokHareket.query.filter(
                StokHareket.hareket_tipi == 'cikis',
                StokHareket.islem_tarihi.between(bugun_baslangic, bugun_bitis)
            ).count()
            
            # Bu ayki zimmet sayısı
            ay_baslangic = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ay_zimmet = PersonelZimmet.query.filter(PersonelZimmet.zimmet_tarihi >= ay_baslangic).count()
            
            rapor_verisi = {
                'toplam_urun': toplam_urun,
                'kritik_urun': len(kritik_urunler),
                'aktif_zimmet': aktif_zimmet,
                'bugun_giris': bugun_giris,
                'bugun_cikis': bugun_cikis,
                'ay_zimmet': ay_zimmet
            }
    
    return render_template('depo_sorumlusu/raporlar.html',
                         rapor_verisi=rapor_verisi,
                         rapor_baslik=rapor_baslik,
                         rapor_tipi=rapor_tipi,
                         urun_gruplari=urun_gruplari,
                         urunler=urunler,
                         personeller=personeller)

# Kat Sorumlusu Rotaları
@app.route('/minibar-kontrol', methods=['GET', 'POST'])
@login_required
@role_required('kat_sorumlusu')
def minibar_kontrol():
    if request.method == 'POST':
        try:
            oda_id = int(request.form['oda_id'])
            islem_tipi = request.form['islem_tipi']
            aciklama = request.form.get('aciklama', '')
            kullanici_id = session['kullanici_id']
            
            # Minibar işlemi oluştur
            islem = MinibarIslem(
                oda_id=oda_id,
                personel_id=kullanici_id,
                islem_tipi=islem_tipi,
                aciklama=aciklama
            )
            db.session.add(islem)
            db.session.flush()  # ID'yi almak için
            
            # Ürün detaylarını işle
            for key, value in request.form.items():
                if key.startswith('miktar_') and value and int(value) > 0:
                    urun_id = int(key.split('_')[1])
                    miktar = int(value)
                    
                    # Sadece ilk_dolum ve doldurma işlemlerinde zimmetten düş
                    if islem_tipi in ['ilk_dolum', 'doldurma']:
                        # Kat sorumlusunun aktif zimmetlerindeki bu ürünü bul (tüm aktif zimmetlerde ara)
                        zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                            PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
                        ).filter(
                            PersonelZimmet.personel_id == kullanici_id,
                            PersonelZimmet.durum == 'aktif',
                            PersonelZimmetDetay.urun_id == urun_id
                        ).all()
                        
                        if not zimmet_detaylar:
                            urun = Urun.query.get(urun_id)
                            urun_adi = urun.urun_adi if urun else 'Bilinmeyen ürün'
                            raise Exception(f'Zimmetinizde bu ürün bulunmuyor: {urun_adi}')
                        
                        # Toplam kalan miktarı hesapla
                        toplam_kalan = sum(detay.miktar - detay.kullanilan_miktar for detay in zimmet_detaylar)
                        
                        if toplam_kalan < miktar:
                            urun = Urun.query.get(urun_id)
                            urun_adi = urun.urun_adi if urun else 'Bilinmeyen ürün'
                            raise Exception(f'Zimmetinizde yeterli ürün yok: {urun_adi}. Kalan: {toplam_kalan}')
                        
                        # Zimmetlerden sırayla düş (FIFO mantığı)
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
                    
                    # Minibar detayı kaydet
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
                    
                    # Sarfiyat oluştur (kontrol ve doldurma işlemlerinde)
                    detay = MinibarIslemDetay(
                        islem_id=islem.id,
                        urun_id=urun_id,
                        baslangic_stok=baslangic,
                        bitis_stok=bitis,
                        tuketim=tuketim
                    )
                    db.session.add(detay)
                    
                    # Doldurma işleminde tüketimi zimmetten düş
                    if islem_tipi == 'doldurma' and tuketim > 0:
                        # Tüm aktif zimmetlerde bu ürünü ara
                        zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
                            PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
                        ).filter(
                            PersonelZimmet.personel_id == kullanici_id,
                            PersonelZimmet.durum == 'aktif',
                            PersonelZimmetDetay.urun_id == urun_id
                        ).all()
                        
                        if zimmet_detaylar:
                            # Toplam kalan miktarı hesapla
                            toplam_kalan = sum(d.miktar - d.kullanilan_miktar for d in zimmet_detaylar)
                            
                            if toplam_kalan >= tuketim:
                                # Zimmetlerden sırayla düş (FIFO mantığı)
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
            flash('Minibar işlemi başarıyla kaydedildi. Zimmetinizden düşürülen ürünler güncellendi.', 'success')
            return redirect(url_for('minibar_kontrol'))
            
        except Exception as e:
            db.session.rollback()
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
        return jsonify({'success': False, 'error': str(e)})

@app.route('/minibar-urunler')
@login_required
@role_required('kat_sorumlusu')
def minibar_urunler():
    """Minibar ürünlerini JSON olarak döndür"""
    try:
        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.grup_id, Urun.urun_adi).all()
        
        urun_listesi = []
        for urun in urunler:
            urun_listesi.append({
                'id': urun.id,
                'ad': urun.urun_adi,
                'grup': urun.grup.grup_adi,
                'birim': urun.birim
            })
        
        return jsonify({'success': True, 'urunler': urun_listesi})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/minibar-icerigi/<int:oda_id>')
@login_required
@role_required('kat_sorumlusu')
def api_minibar_icerigi(oda_id):
    """Odanın mevcut minibar içeriğini döndür (son işleme göre)"""
    try:
        # Son minibar işlemini bul
        son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(MinibarIslem.id.desc()).first()
        
        if not son_islem:
            return jsonify({'success': True, 'urunler': [], 'ilk_dolum': True})
        
        # Son işlemdeki ürünleri ve miktarlarını getir
        urunler = []
        for detay in son_islem.detaylar:
            urun = Urun.query.get(detay.urun_id)
            if urun:
                # Mevcut stok hesaplama:
                # - Eğer bitis_stok girilmişse onu kullan (kontrol/doldurma işlemlerinde)
                # - Yoksa: baslangic_stok + eklenen_miktar - tuketim (ilk dolumda)
                if detay.bitis_stok is not None and detay.bitis_stok >= 0:
                    mevcut_stok = detay.bitis_stok
                else:
                    mevcut_stok = (detay.baslangic_stok or 0) + (detay.eklenen_miktar or 0) - (detay.tuketim or 0)
                
                urunler.append({
                    'urun_id': urun.id,
                    'urun_adi': urun.urun_adi,
                    'grup_adi': urun.grup.grup_adi if urun.grup else '',
                    'birim': urun.birim,
                    'mevcut_stok': mevcut_stok,
                    'son_islem_tarihi': son_islem.islem_tarihi.strftime('%d.%m.%Y %H:%M')
                })
        
        return jsonify({
            'success': True,
            'urunler': urunler,
            'ilk_dolum': False,
            'son_islem_tipi': son_islem.islem_tipi
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/minibar-doldur', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_minibar_doldur():
    """Tek bir ürünü minibar'a doldur"""
    try:
        data = request.get_json()
        oda_id = data.get('oda_id')
        urun_id = data.get('urun_id')
        miktar = int(data.get('miktar', 0))
        islem_tipi = data.get('islem_tipi', 'doldurma')
        kullanici_id = session['kullanici_id']
        
        if not oda_id or not urun_id or miktar <= 0:
            return jsonify({'success': False, 'error': 'Geçersiz parametreler'})
        
        urun = Urun.query.get(urun_id)
        if not urun:
            return jsonify({'success': False, 'error': 'Ürün bulunamadı'})
        
        # Zimmet kontrolü
        zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
            PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
        ).filter(
            PersonelZimmet.personel_id == kullanici_id,
            PersonelZimmet.durum == 'aktif',
            PersonelZimmetDetay.urun_id == urun_id
        ).all()
        
        if not zimmet_detaylar:
            return jsonify({'success': False, 'error': f'Zimmetinizde {urun.urun_adi} bulunmuyor'})
        
        toplam_kalan = sum(d.miktar - d.kullanilan_miktar for d in zimmet_detaylar)
        if toplam_kalan < miktar:
            return jsonify({'success': False, 'error': f'Yetersiz zimmet! Kalan: {toplam_kalan} {urun.birim}'})
        
        # Son işlemi bul
        son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(MinibarIslem.id.desc()).first()
        
        if son_islem:
            # Son işlemdeki bu ürünün stoğunu bul
            son_detay = MinibarIslemDetay.query.filter_by(
                islem_id=son_islem.id,
                urun_id=urun_id
            ).first()
            
            if son_detay:
                baslangic_stok = son_detay.bitis_stok if son_detay.bitis_stok > 0 else (son_detay.baslangic_stok + son_detay.eklenen_miktar - son_detay.tuketim)
            else:
                baslangic_stok = 0
        else:
            baslangic_stok = 0
        
        # Yeni işlem oluştur
        islem = MinibarIslem(
            oda_id=oda_id,
            personel_id=kullanici_id,
            islem_tipi=islem_tipi,
            aciklama=f'{miktar} {urun.birim} {urun.urun_adi} eklendi'
        )
        db.session.add(islem)
        db.session.flush()
        
        # Zimmetten düş (FIFO)
        kalan_miktar = miktar
        kullanilan_zimmet_id = None
        
        for zimmet_detay in zimmet_detaylar:
            if kalan_miktar <= 0:
                break
            
            detay_kalan = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
            if detay_kalan > 0:
                kullanilacak = min(detay_kalan, kalan_miktar)
                zimmet_detay.kullanilan_miktar += kullanilacak
                zimmet_detay.kalan_miktar = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                kalan_miktar -= kullanilacak
                
                if not kullanilan_zimmet_id:
                    kullanilan_zimmet_id = zimmet_detay.id
        
        # Minibar detayı kaydet
        detay = MinibarIslemDetay(
            islem_id=islem.id,
            urun_id=urun_id,
            baslangic_stok=baslangic_stok,
            bitis_stok=baslangic_stok + miktar,
            tuketim=0,
            eklenen_miktar=miktar,
            zimmet_detay_id=kullanilan_zimmet_id
        )
        db.session.add(detay)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{miktar} {urun.birim} {urun.urun_adi} başarıyla eklendi',
            'yeni_stok': baslangic_stok + miktar
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/zimmetim')
@login_required
@role_required('kat_sorumlusu')
def zimmetim():
    kullanici_id = session['kullanici_id']
    
    # Aktif zimmetler
    aktif_zimmetler = PersonelZimmet.query.filter_by(
        personel_id=kullanici_id, 
        durum='aktif'
    ).order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
    
    # Zimmet istatistikleri
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
    # Rapor verilerini hazırla
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
        
    elif rapor_tipi == 'tuketim':
        rapor_baslik = "Tüketim Raporu (Ürün Bazlı)"
        
        # Tüketim raporu - ürün bazlı toplam tüketim
        query = db.session.query(
            Urun,
            db.func.sum(MinibarIslemDetay.tuketim).label('toplam_tuketim'),
            db.func.count(MinibarIslemDetay.id).label('islem_sayisi')
        ).join(MinibarIslemDetay, Urun.id == MinibarIslemDetay.urun_id
        ).join(MinibarIslem, MinibarIslemDetay.islem_id == MinibarIslem.id
        ).filter(MinibarIslem.personel_id == kullanici_id)
        
        if baslangic_tarihi:
            query = query.filter(MinibarIslem.islem_tarihi >= datetime.strptime(baslangic_tarihi, '%Y-%m-%d'))
        if bitis_tarihi:
            query = query.filter(MinibarIslem.islem_tarihi <= datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1))
        
        rapor_verisi = query.group_by(Urun.id).having(db.func.sum(MinibarIslemDetay.tuketim) > 0).all()
        
    elif rapor_tipi == 'oda_bazli':
        rapor_baslik = "Oda Bazlı Rapor"
        
        # Oda bazlı rapor - oda bazlı işlem ve tüketim istatistikleri
        query = db.session.query(
            Oda,
            db.func.count(MinibarIslem.id).label('islem_sayisi'),
            db.func.sum(MinibarIslemDetay.tuketim).label('toplam_tuketim'),
            db.func.max(MinibarIslem.islem_tarihi).label('son_islem')
        ).join(MinibarIslem, Oda.id == MinibarIslem.oda_id
        ).join(MinibarIslemDetay, MinibarIslem.id == MinibarIslemDetay.islem_id
        ).filter(MinibarIslem.personel_id == kullanici_id)
        
        if baslangic_tarihi:
            query = query.filter(MinibarIslem.islem_tarihi >= datetime.strptime(baslangic_tarihi, '%Y-%m-%d'))
        if bitis_tarihi:
            query = query.filter(MinibarIslem.islem_tarihi <= datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1))
        
        rapor_verisi = query.group_by(Oda.id).all()
    
    return render_template('kat_sorumlusu/raporlar.html', 
                         rapor_verisi=rapor_verisi, 
                         rapor_baslik=rapor_baslik,
                         rapor_tipi=rapor_tipi)

# Excel Export
@app.route('/excel-export/<rapor_tipi>')
@login_required
def excel_export(rapor_tipi):
    try:
        # Filtreleme parametrelerini al
        baslangic_tarihi = request.args.get('baslangic_tarihi')
        bitis_tarihi = request.args.get('bitis_tarihi')
        urun_grup_id = request.args.get('urun_grup_id')
        urun_id = request.args.get('urun_id')
        personel_id = request.args.get('personel_id')
        hareket_tipi = request.args.get('hareket_tipi')
        
        # Excel dosyası oluştur
        wb = openpyxl.Workbook()
        ws = wb.active
        
        # Rapor başlığı
        rapor_basliklari = {
            'stok_durum': 'Stok Durum Raporu',
            'stok_hareket': 'Stok Hareket Raporu',
            'zimmet': 'Zimmet Raporu',
            'zimmet_detay': 'Ürün Bazlı Zimmet Detay Raporu',
            'urun_grup': 'Ürün Grubu Bazlı Stok Raporu',
            'ozet': 'Genel Sistem Özet Raporu'
        }
        
        baslik = rapor_basliklari.get(rapor_tipi, 'Rapor')
        ws.title = baslik[:31]  # Excel sheet name limit
        
        # Başlık satırı
        ws['A1'] = baslik
        ws['A1'].font = Font(size=16, bold=True)
        
        # Tarih bilgisi
        ws['A2'] = f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        ws['A2'].font = Font(size=10)
        
        row_num = 4
        
        if rapor_tipi == 'stok_durum':
            # Başlıkları yaz
            headers = ['Ürün Adı', 'Ürün Grubu', 'Birim', 'Mevcut Stok', 'Kritik Seviye', 'Durum']
            ws.merge_cells('A1:F1')
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_num, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            
            # Verileri yaz
            query = Urun.query.filter_by(aktif=True)
            if urun_grup_id:
                query = query.filter_by(grup_id=urun_grup_id)
            
            urunler_liste = query.order_by(Urun.urun_adi).all()
            
            for urun in urunler_liste:
                row_num += 1
                mevcut_stok = get_toplam_stok(urun.id)
                durum = 'KRİTİK' if mevcut_stok <= urun.kritik_stok_seviyesi else 'NORMAL'
                
                ws.cell(row=row_num, column=1, value=urun.urun_adi)
                ws.cell(row=row_num, column=2, value=urun.grup.grup_adi)
                ws.cell(row=row_num, column=3, value=urun.birim)
                ws.cell(row=row_num, column=4, value=mevcut_stok)
                ws.cell(row=row_num, column=5, value=urun.kritik_stok_seviyesi)
                ws.cell(row=row_num, column=6, value=durum)
        
        elif rapor_tipi == 'stok_hareket':
            headers = ['Tarih', 'Ürün Adı', 'Hareket Tipi', 'Miktar', 'Açıklama', 'İşlem Yapan']
            ws.merge_cells('A1:F1')
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_num, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
            
            query = StokHareket.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(StokHareket.islem_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(StokHareket.islem_tarihi < bitis)
            
            if urun_id:
                query = query.filter_by(urun_id=urun_id)
            elif urun_grup_id:
                query = query.join(Urun).filter(Urun.grup_id == urun_grup_id)
            
            if hareket_tipi:
                query = query.filter_by(hareket_tipi=hareket_tipi)
            
            hareketler = query.order_by(StokHareket.islem_tarihi.desc()).all()
            
            for hareket in hareketler:
                row_num += 1
                islem_yapan = f"{hareket.islem_yapan.ad} {hareket.islem_yapan.soyad}" if hareket.islem_yapan else '-'
                
                # Zimmet bilgisini açıklamaya ekle
                aciklama = hareket.aciklama or '-'
                if hareket.aciklama and 'Zimmet' in hareket.aciklama:
                    try:
                        if '#' in hareket.aciklama:
                            zimmet_id = int(hareket.aciklama.split('#')[1].split()[0])
                            zimmet = PersonelZimmet.query.get(zimmet_id)
                            if zimmet and zimmet.personel:
                                aciklama += f" → {zimmet.personel.ad} {zimmet.personel.soyad}"
                    except Exception:
                        pass
                
                ws.cell(row=row_num, column=1, value=hareket.islem_tarihi.strftime('%d.%m.%Y %H:%M'))
                ws.cell(row=row_num, column=2, value=hareket.urun.urun_adi)
                ws.cell(row=row_num, column=3, value=hareket.hareket_tipi.upper())
                ws.cell(row=row_num, column=4, value=hareket.miktar)
                ws.cell(row=row_num, column=5, value=aciklama)
                ws.cell(row=row_num, column=6, value=islem_yapan)
        
        elif rapor_tipi == 'zimmet':
            headers = ['Zimmet No', 'Personel', 'Zimmet Tarihi', 'Ürün Sayısı', 'Toplam Miktar', 'Durum']
            ws.merge_cells('A1:F1')
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_num, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="FFC000", end_color="FFC000", fill_type="solid")
            
            query = PersonelZimmet.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter_by(personel_id=personel_id)
            
            zimmetler = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
            
            for zimmet in zimmetler:
                row_num += 1
                toplam_miktar = sum(d.miktar for d in zimmet.detaylar)
                
                ws.cell(row=row_num, column=1, value=f"#{zimmet.id}")
                ws.cell(row=row_num, column=2, value=f"{zimmet.personel.ad} {zimmet.personel.soyad}")
                ws.cell(row=row_num, column=3, value=zimmet.zimmet_tarihi.strftime('%d.%m.%Y %H:%M'))
                ws.cell(row=row_num, column=4, value=len(zimmet.detaylar))
                ws.cell(row=row_num, column=5, value=toplam_miktar)
                ws.cell(row=row_num, column=6, value=zimmet.durum.upper())
        
        elif rapor_tipi == 'zimmet_detay':
            headers = ['Zimmet No', 'Personel', 'Zimmet Tarihi', 'Ürün Adı', 'Grup', 'Miktar', 'Durum']
            ws.merge_cells('A1:G1')
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_num, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="C55A11", end_color="C55A11", fill_type="solid")
            
            query = db.session.query(
                PersonelZimmetDetay,
                PersonelZimmet,
                Kullanici,
                Urun
            ).join(
                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
            ).join(
                Kullanici, PersonelZimmet.personel_id == Kullanici.id
            ).join(
                Urun, PersonelZimmetDetay.urun_id == Urun.id
            )
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter(PersonelZimmet.personel_id == personel_id)
            
            if urun_id:
                query = query.filter(PersonelZimmetDetay.urun_id == urun_id)
            elif urun_grup_id:
                query = query.filter(Urun.grup_id == urun_grup_id)
            
            detaylar = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).all()
            
            for detay, zimmet, kullanici, urun in detaylar:
                row_num += 1
                
                ws.cell(row=row_num, column=1, value=f"#{zimmet.id}")
                ws.cell(row=row_num, column=2, value=f"{kullanici.ad} {kullanici.soyad}")
                ws.cell(row=row_num, column=3, value=zimmet.zimmet_tarihi.strftime('%d.%m.%Y %H:%M'))
                ws.cell(row=row_num, column=4, value=urun.urun_adi)
                ws.cell(row=row_num, column=5, value=urun.grup.grup_adi)
                ws.cell(row=row_num, column=6, value=detay.miktar)
                ws.cell(row=row_num, column=7, value=zimmet.durum.upper())
        
        elif rapor_tipi == 'urun_grup':
            headers = ['Ürün Grubu', 'Toplam Ürün', 'Kritik Stoklu Ürün']
            ws.merge_cells('A1:C1')
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row_num, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
            
            gruplar = UrunGrup.query.filter_by(aktif=True).all()
            
            for grup in gruplar:
                row_num += 1
                grup_urunleri = Urun.query.filter_by(grup_id=grup.id, aktif=True).all()
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = get_toplam_stok(urun.id)
                    if mevcut_stok <= urun.kritik_stok_seviyesi:
                        kritik_urun_sayisi += 1
                
                ws.cell(row=row_num, column=1, value=grup.grup_adi)
                ws.cell(row=row_num, column=2, value=toplam_urun_sayisi)
                ws.cell(row=row_num, column=3, value=kritik_urun_sayisi)
        
        # Sütun genişliklerini ayarla
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Response oluştur
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename={rapor_tipi}_raporu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
        
    except Exception as e:
        flash(f'Excel export hatası: {str(e)}', 'danger')
        return redirect(url_for('depo_raporlar'))

# PDF Export
@app.route('/pdf-export/<rapor_tipi>')
@login_required
def pdf_export(rapor_tipi):
    try:
        # Türkçe karakter dönüşüm tablosu
        def turkce_ascii(text):
            """Türkçe karakterleri ASCII'ye dönüştür"""
            if not text:
                return ''
            char_map = {
                'ç': 'c', 'Ç': 'C',
                'ğ': 'g', 'Ğ': 'G',
                'ı': 'i', 'İ': 'I',
                'ö': 'o', 'Ö': 'O',
                'ş': 's', 'Ş': 'S',
                'ü': 'u', 'Ü': 'U'
            }
            result = str(text)
            for turkish, ascii_char in char_map.items():
                result = result.replace(turkish, ascii_char)
            return result
        
        # Filtreleme parametrelerini al
        baslangic_tarihi = request.args.get('baslangic_tarihi')
        bitis_tarihi = request.args.get('bitis_tarihi')
        urun_grup_id = request.args.get('urun_grup_id')
        urun_id = request.args.get('urun_id')
        personel_id = request.args.get('personel_id')
        hareket_tipi = request.args.get('hareket_tipi')
        
        # PDF dosyası oluştur
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []
        
        # Rapor başlığı
        rapor_basliklari = {
            'stok_durum': 'Stok Durum Raporu',
            'stok_hareket': 'Stok Hareket Raporu',
            'zimmet': 'Zimmet Raporu',
            'zimmet_detay': 'Urun Bazli Zimmet Detay Raporu',
            'urun_grup': 'Urun Grubu Bazli Stok Raporu',
            'ozet': 'Genel Sistem Ozet Raporu'
        }
        
        baslik = turkce_ascii(rapor_basliklari.get(rapor_tipi, 'Rapor'))
        
        # Başlık
        title = Paragraph(baslik, styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Tarih
        date_text = f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        date_para = Paragraph(date_text, styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 20))
        
        # Tablo verileri
        data = []
        
        if rapor_tipi == 'stok_durum':
            data.append([turkce_ascii(h) for h in ['Urun Adi', 'Urun Grubu', 'Birim', 'Mevcut Stok', 'Kritik Seviye', 'Durum']])
            
            query = Urun.query.filter_by(aktif=True)
            if urun_grup_id:
                query = query.filter_by(grup_id=urun_grup_id)
            
            urunler_liste = query.order_by(Urun.urun_adi).all()
            
            for urun in urunler_liste:
                mevcut_stok = get_toplam_stok(urun.id)
                durum = 'KRITIK' if mevcut_stok <= urun.kritik_stok_seviyesi else 'NORMAL'
                
                data.append([
                    turkce_ascii(urun.urun_adi),
                    turkce_ascii(urun.grup.grup_adi),
                    turkce_ascii(urun.birim),
                    str(mevcut_stok),
                    str(urun.kritik_stok_seviyesi),
                    durum
                ])
        
        elif rapor_tipi == 'stok_hareket':
            data.append([turkce_ascii(h) for h in ['Tarih', 'Urun Adi', 'Hareket', 'Miktar', 'Aciklama']])
            
            query = StokHareket.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(StokHareket.islem_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(StokHareket.islem_tarihi < bitis)
            
            if urun_id:
                query = query.filter_by(urun_id=urun_id)
            elif urun_grup_id:
                query = query.join(Urun).filter(Urun.grup_id == urun_grup_id)
            
            if hareket_tipi:
                query = query.filter_by(hareket_tipi=hareket_tipi)
            
            hareketler = query.order_by(StokHareket.islem_tarihi.desc()).limit(100).all()
            
            for hareket in hareketler:
                # Zimmet bilgisini açıklamaya ekle
                aciklama = hareket.aciklama or '-'
                if hareket.aciklama and 'Zimmet' in hareket.aciklama:
                    try:
                        if '#' in hareket.aciklama:
                            zimmet_id = int(hareket.aciklama.split('#')[1].split()[0])
                            zimmet = PersonelZimmet.query.get(zimmet_id)
                            if zimmet and zimmet.personel:
                                aciklama = f"{aciklama} → {zimmet.personel.ad} {zimmet.personel.soyad}"
                    except Exception:
                        pass
                
                # Açıklamayı kısalt (PDF için)
                aciklama_kisaltilmis = aciklama[:50] if len(aciklama) > 50 else aciklama
                
                data.append([
                    hareket.islem_tarihi.strftime('%d.%m.%Y %H:%M'),
                    turkce_ascii(hareket.urun.urun_adi),
                    turkce_ascii(hareket.hareket_tipi.upper()),
                    str(hareket.miktar),
                    turkce_ascii(aciklama_kisaltilmis)
                ])
        
        elif rapor_tipi == 'zimmet':
            data.append([turkce_ascii(h) for h in ['Zimmet No', 'Personel', 'Tarih', 'Urun Sayisi', 'Toplam', 'Durum']])
            
            query = PersonelZimmet.query
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter_by(personel_id=personel_id)
            
            zimmetler = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).limit(100).all()
            
            for zimmet in zimmetler:
                toplam_miktar = sum(d.miktar for d in zimmet.detaylar)
                
                data.append([
                    f"#{zimmet.id}",
                    turkce_ascii(f"{zimmet.personel.ad} {zimmet.personel.soyad}"),
                    zimmet.zimmet_tarihi.strftime('%d.%m.%Y'),
                    str(len(zimmet.detaylar)),
                    str(toplam_miktar),
                    turkce_ascii(zimmet.durum.upper())
                ])
        
        elif rapor_tipi == 'zimmet_detay':
            data.append([turkce_ascii(h) for h in ['Zimmet', 'Personel', 'Urun', 'Grup', 'Miktar', 'Durum']])
            
            query = db.session.query(
                PersonelZimmetDetay,
                PersonelZimmet,
                Kullanici,
                Urun
            ).join(
                PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
            ).join(
                Kullanici, PersonelZimmet.personel_id == Kullanici.id
            ).join(
                Urun, PersonelZimmetDetay.urun_id == Urun.id
            )
            
            if baslangic_tarihi:
                baslangic = datetime.strptime(baslangic_tarihi, '%Y-%m-%d')
                query = query.filter(PersonelZimmet.zimmet_tarihi >= baslangic)
            
            if bitis_tarihi:
                bitis = datetime.strptime(bitis_tarihi, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PersonelZimmet.zimmet_tarihi < bitis)
            
            if personel_id:
                query = query.filter(PersonelZimmet.personel_id == personel_id)
            
            if urun_id:
                query = query.filter(PersonelZimmetDetay.urun_id == urun_id)
            elif urun_grup_id:
                query = query.filter(Urun.grup_id == urun_grup_id)
            
            detaylar = query.order_by(PersonelZimmet.zimmet_tarihi.desc()).limit(100).all()
            
            for detay, zimmet, kullanici, urun in detaylar:
                data.append([
                    f"#{zimmet.id}",
                    turkce_ascii(f"{kullanici.ad} {kullanici.soyad}"),
                    turkce_ascii(urun.urun_adi),
                    turkce_ascii(urun.grup.grup_adi),
                    str(detay.miktar),
                    turkce_ascii(zimmet.durum.upper())
                ])
        
        elif rapor_tipi == 'urun_grup':
            data.append([turkce_ascii(h) for h in ['Urun Grubu', 'Toplam Urun', 'Kritik Stoklu Urun']])
            
            gruplar = UrunGrup.query.filter_by(aktif=True).all()
            
            for grup in gruplar:
                grup_urunleri = Urun.query.filter_by(grup_id=grup.id, aktif=True).all()
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = get_toplam_stok(urun.id)
                    if mevcut_stok <= urun.kritik_stok_seviyesi:
                        kritik_urun_sayisi += 1
                
                data.append([
                    turkce_ascii(grup.grup_adi),
                    str(toplam_urun_sayisi),
                    str(kritik_urun_sayisi)
                ])
        
        elif rapor_tipi == 'ozet':
            # Özet raporu için özel tablo
            toplam_urun = Urun.query.filter_by(aktif=True).count()
            kritik_urunler = get_kritik_stok_urunler()
            aktif_zimmet = PersonelZimmet.query.filter_by(durum='aktif').count()
            
            bugun = datetime.now().date()
            bugun_baslangic = datetime.combine(bugun, datetime.min.time())
            bugun_bitis = datetime.combine(bugun, datetime.max.time())
            
            bugun_giris = StokHareket.query.filter(
                StokHareket.hareket_tipi == 'giris',
                StokHareket.islem_tarihi.between(bugun_baslangic, bugun_bitis)
            ).count()
            
            bugun_cikis = StokHareket.query.filter(
                StokHareket.hareket_tipi == 'cikis',
                StokHareket.islem_tarihi.between(bugun_baslangic, bugun_bitis)
            ).count()
            
            ay_baslangic = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            ay_zimmet = PersonelZimmet.query.filter(PersonelZimmet.zimmet_tarihi >= ay_baslangic).count()
            
            data = [
                ['Metrik', 'Deger'],
                [turkce_ascii('Toplam Urun Sayisi'), str(toplam_urun)],
                [turkce_ascii('Kritik Stoklu Urun'), str(len(kritik_urunler))],
                [turkce_ascii('Aktif Zimmet'), str(aktif_zimmet)],
                [turkce_ascii('Bugun Stok Giris'), str(bugun_giris)],
                [turkce_ascii('Bugun Stok Cikis'), str(bugun_cikis)],
                [turkce_ascii('Bu Ay Zimmet'), str(ay_zimmet)]
            ]
        
        # Tablo oluştur
        if data:
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F2F2')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')])
            ]))
            
            story.append(table)
        else:
            no_data = Paragraph(turkce_ascii("Bu filtre kriterleri icin veri bulunamadi."), styles['Normal'])
            story.append(no_data)
        
        # PDF'i oluştur
        doc.build(story)
        buffer.seek(0)
        
        # Response oluştur
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename={rapor_tipi}_raporu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        
        return response
        
    except Exception as e:
        flash(f'PDF export hatasi: {str(e)}', 'danger')
        return redirect(url_for('depo_raporlar'))

# Hata yakalama
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

def init_database():
    """Veritabanı ve tabloları otomatik kontrol et ve oluştur"""
    try:
        with app.app_context():
            # Tabloları oluştur (yoksa)
            db.create_all()
            print("✅ Veritabanı tabloları kontrol edildi ve hazır.")
            return True
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        print()
        print("🔧 Lütfen 'python init_db.py' komutunu çalıştırın.")
        return False

if __name__ == '__main__':
    print()
    print("=" * 60)
    print("🏨 OTEL MİNİBAR TAKİP SİSTEMİ")
    print("=" * 60)
    print()
    
    # Veritabanını başlat
    if init_database():
        print()
        print("🚀 Uygulama başlatılıyor...")
        # Railway PORT environment variable desteği
        port = int(os.getenv('PORT', 5014))
        debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
        
        print(f"📍 Adres: http://0.0.0.0:{port}")
        print("🌙 Dark/Light tema: Sağ üstten değiştirilebilir")
        print()
        print("Durdurmak için CTRL+C kullanın")
        print("=" * 60)
        print()
        
        app.run(debug=debug_mode, host='0.0.0.0', port=port)
    else:
        print()
        print("❌ Uygulama başlatılamadı. Lütfen veritabanı ayarlarını kontrol edin.")
        print()
        exit(1)
