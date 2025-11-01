from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify, send_file
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta, timezone
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

# CSRF Koruması Aktif
csrf = CSRFProtect(app)

# Rate Limiting Aktif
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Production'da Redis kullanılmalı
    strategy="fixed-window"
)

# Veritabanı başlat
from models import db
db.init_app(app)

# Yardımcı modülleri import et
from utils.decorators import login_required, role_required, setup_required, setup_not_completed
from utils.helpers import (
    get_current_user, get_kritik_stok_urunler, get_stok_toplamlari,
    log_islem, get_son_loglar, get_kullanici_loglari, get_modul_loglari,
    log_hata, get_son_hatalar, get_cozulmemis_hatalar, hata_cozuldu_isaretle,
    get_stok_durumu, get_tum_urunler_stok_durumlari
)
from utils.audit import (
    audit_create, audit_update, audit_delete,
    audit_login, audit_logout, serialize_model
)

# Modelleri import et
from models import (
    Otel, Kullanici, Kat, Oda, UrunGrup, Urun, StokHareket, 
    PersonelZimmet, PersonelZimmetDetay, MinibarIslem, MinibarIslemDetay, 
    SistemAyar, SistemLog, HataLog, OtomatikRapor
)

# Rate Limit Error Handler
@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit aşıldığında gösterilecek hata sayfası"""
    # Audit Trail - Rate limit ihlali
    from utils.audit import log_audit
    log_audit(
        islem_tipi='view',
        tablo_adi='rate_limit',
        aciklama=f'Rate limit aşıldı: {request.endpoint}',
        basarili=False,
        hata_mesaji=str(e)
    )

    return render_template('errors/429.html', error=e), 429


# CSRF error handler - record and inform user
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    try:
        # Log the CSRF error for diagnostics
        log_hata(e, modul='csrf', extra_info={'path': request.path, 'method': request.method})
    except Exception:
        # If logging fails, swallow to avoid masking the original error
        pass

    # Inform the user and redirect back
    flash('Form doğrulaması başarısız oldu (CSRF). Lütfen sayfayı yenileyip tekrar deneyin.', 'danger')
    return redirect(request.referrer or url_for('index'))

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
    
    # Giriş yapmış kullanıcı varsa panele yönlendir
    if 'kullanici_id' in session:
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))

# Setup sayfası
@app.route('/setup', methods=['GET', 'POST'])
@setup_not_completed
@limiter.limit("10 per hour")  # Rate limit: 10 deneme/saat
def setup():
    from forms import SetupForm
    from sqlalchemy.exc import IntegrityError, OperationalError

    form = SetupForm()

    if form.validate_on_submit():
        try:
            # Otel bilgileri
            otel = Otel(
                ad=form.otel_adi.data,
                adres=form.adres.data,
                telefon=form.telefon.data,
                email=form.email.data,
                vergi_no=form.vergi_no.data or ''
            )
            db.session.add(otel)
            db.session.flush()  # ID'yi almak için

            # Sistem yöneticisi oluştur
            sistem_yoneticisi = Kullanici(
                kullanici_adi=form.kullanici_adi.data,
                ad=form.ad.data,
                soyad=form.soyad.data,
                email=form.admin_email.data,
                telefon=form.admin_telefon.data or '',
                rol='sistem_yoneticisi'
            )
            sistem_yoneticisi.sifre_belirle(form.sifre.data)
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

        except IntegrityError:
            db.session.rollback()
            flash('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı deneyin.', 'danger')
            log_hata(Exception('Setup IntegrityError'), modul='setup')
        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='setup')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='setup', extra_info={'form_data': form.data})

    # Eğer POST yapıldı fakat form doğrulama başarısızsa, hata detaylarını loglayalım
    if request.method == 'POST' and not form.validate_on_submit():
        try:
            # form.errors JSON-serializable olmayabilir, bu yüzden güvenli hale getir
            errors = {k: v for k, v in (form.errors or {}).items()}
            form_data = request.form.to_dict()
            log_hata(Exception('Setup validation failed'), modul='setup', extra_info={'errors': errors, 'form_data': form_data})
            flash('Form doğrulama hatası. Girdi alanlarını kontrol edin ve tekrar deneyin.', 'danger')
        except Exception as e:
            # Log kaydında da hata olursa yakala ama işlemi bozma
            log_hata(e, modul='setup', extra_info={'note': 'logging_failed_on_validation'})

    return render_template('setup.html', form=form)

# Login sayfası
@app.route('/login', methods=['GET', 'POST'])
@setup_required
@limiter.limit("5 per minute")  # Rate limit: 5 deneme/dakika (Brute force koruması)
def login():
    from forms import LoginForm

    form = LoginForm()

    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(
            kullanici_adi=form.kullanici_adi.data,
            aktif=True
        ).first()

        if kullanici and kullanici.sifre_kontrol(form.sifre.data):
            session.clear()
            session.permanent = form.remember_me.data

            session['kullanici_id'] = kullanici.id
            session['kullanici_adi'] = kullanici.kullanici_adi
            session['ad'] = kullanici.ad
            session['soyad'] = kullanici.soyad
            session['rol'] = kullanici.rol

            # Son giriş tarihini güncelle
            try:
                kullanici.son_giris = datetime.now(timezone.utc)
                db.session.commit()
            except Exception as e:
                # Son giriş güncelleme hatası login'i engellemez
                log_hata(e, modul='login', extra_info={'action': 'son_giris_guncelleme'})

            # Log kaydı
            log_islem('giris', 'sistem', {
                'kullanici_adi': kullanici.kullanici_adi,
                'ad_soyad': f'{kullanici.ad} {kullanici.soyad}',
                'rol': kullanici.rol
            })

            # Audit Trail
            audit_login(
                kullanici_id=kullanici.id,
                kullanici_adi=kullanici.kullanici_adi,
                kullanici_rol=kullanici.rol,
                basarili=True
            )

            flash(f'Hoş geldiniz, {kullanici.ad} {kullanici.soyad}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Başarısız login denemesini logla
            audit_login(
                kullanici_id=None,
                kullanici_adi=form.kullanici_adi.data,
                kullanici_rol='unknown',
                basarili=False,
                hata_mesaji='Geçersiz kullanıcı adı veya şifre'
            )
            flash('Kullanıcı adı veya şifre hatalı!', 'danger')

    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
def logout():
    # Log kaydı (session temizlenmeden önce)
    kullanici_id = session.get('kullanici_id')
    if kullanici_id:
        kullanici = db.session.get(Kullanici, kullanici_id)
        if kullanici:
            log_islem('cikis', 'sistem', {
                'kullanici_adi': kullanici.kullanici_adi,
                'ad_soyad': f'{kullanici.ad} {kullanici.soyad}',
                'rol': kullanici.rol
            })
            
            # Audit Trail
            audit_logout()
    
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('login'))

# Panel - rol bazlı yönlendirme
@app.route('/dashboard')
@login_required
def dashboard():
    rol = session.get('rol')
    
    if rol == 'sistem_yoneticisi':
        return redirect(url_for('sistem_yoneticisi_dashboard'))
    elif rol == 'admin':
        return redirect(url_for('sistem_yoneticisi_dashboard'))  # Admin de sistem yöneticisi panelini kullanır
    elif rol == 'depo_sorumlusu':
        return redirect(url_for('depo_dashboard'))
    elif rol == 'kat_sorumlusu':
        return redirect(url_for('kat_sorumlusu_dashboard'))
    else:
        flash('Geçersiz kullanıcı rolü!', 'danger')
        return redirect(url_for('logout'))

# Sistem Yöneticisi Panel
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
    
    # Gelişmiş stok durumları
    stok_durumlari = get_tum_urunler_stok_durumlari()
    
    # Son eklenen personeller (admin için)
    son_personeller = Kullanici.query.filter(
        Kullanici.rol.in_(['depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).order_by(Kullanici.olusturma_tarihi.desc()).limit(5).all()
    
    # Son eklenen ürünler (admin için)
    son_urunler = Urun.query.filter_by(aktif=True).order_by(Urun.olusturma_tarihi.desc()).limit(5).all()
    
    # Ürün bazlı tüketim verileri (Son 30 günün en çok tüketilen ürünleri)
    from datetime import datetime, timedelta
    bugun = datetime.now().date()
    otuz_gun_once = bugun - timedelta(days=30)
    
    # Minibar işlemlerinden en çok tüketilen ürünleri al
    urun_tuketim = db.session.query(
        Urun.urun_adi,
        db.func.sum(MinibarIslemDetay.tuketim).label('toplam_tuketim')
    ).join(
        MinibarIslemDetay, MinibarIslemDetay.urun_id == Urun.id
    ).join(
        MinibarIslem, MinibarIslem.id == MinibarIslemDetay.islem_id
    ).filter(
        db.func.date(MinibarIslem.islem_tarihi) >= otuz_gun_once,
        MinibarIslemDetay.tuketim > 0
    ).group_by(
        Urun.id, Urun.urun_adi
    ).order_by(
        db.desc('toplam_tuketim')
    ).limit(10).all()
    
    urun_labels = [u[0] for u in urun_tuketim]
    urun_tuketim_miktarlari = [float(u[1] or 0) for u in urun_tuketim]
    
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
                         stok_durumlari=stok_durumlari,
                         son_personeller=son_personeller,
                         son_urunler=son_urunler,
                         urun_labels=urun_labels,
                         urun_tuketim_miktarlari=urun_tuketim_miktarlari)

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

# Admin paneli kaldırıldı - Sistem Yöneticisi paneli kullanılıyor

# Depo Sorumlusu Panel
@app.route('/depo')
@login_required
@role_required('depo_sorumlusu')
def depo_dashboard():
    # İstatistikler
    toplam_urun = Urun.query.filter_by(aktif=True).count()
    kritik_urunler = get_kritik_stok_urunler()
    aktif_zimmetler = PersonelZimmet.query.filter_by(durum='aktif').count()
    
    # Gelişmiş stok durumları
    stok_durumlari = get_tum_urunler_stok_durumlari()
    
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
    
    # Ürün bazlı tüketim verileri (Son 30 günün en çok tüketilen ürünleri)
    otuz_gun_once = bugun - timedelta(days=30)
    
    # Minibar işlemlerinden en çok tüketilen ürünleri al
    urun_tuketim = db.session.query(
        Urun.urun_adi,
        db.func.sum(MinibarIslemDetay.tuketim).label('toplam_tuketim')
    ).join(
        MinibarIslemDetay, MinibarIslemDetay.urun_id == Urun.id
    ).join(
        MinibarIslem, MinibarIslem.id == MinibarIslemDetay.islem_id
    ).filter(
        db.func.date(MinibarIslem.islem_tarihi) >= otuz_gun_once,
        MinibarIslemDetay.tuketim > 0
    ).group_by(
        Urun.id, Urun.urun_adi
    ).order_by(
        db.desc('toplam_tuketim')
    ).limit(10).all()
    
    urun_labels = [u[0] for u in urun_tuketim]
    urun_tuketim_miktarlari = [float(u[1] or 0) for u in urun_tuketim]
    
    return render_template('depo_sorumlusu/dashboard.html',
                         toplam_urun=toplam_urun,
                         kritik_urunler=kritik_urunler,
                         stok_durumlari=stok_durumlari,
                         aktif_zimmetler=aktif_zimmetler,
                         toplam_iade_edilen=toplam_iade_edilen,
                         bu_ay_iadeler=bu_ay_iadeler,
                         iptal_zimmetler=iptal_zimmetler,
                         son_hareketler=son_hareketler,
                         grup_labels=grup_labels,
                         grup_stok_miktarlari=grup_stok_miktarlari,
                         gun_labels=gun_labels,
                         giris_verileri=giris_verileri,
                         cikis_verileri=cikis_verileri,
                         urun_labels=urun_labels,
                         urun_tuketim_miktarlari=urun_tuketim_miktarlari)

# Kat Sorumlusu Panel
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
    from forms import OtelForm
    from sqlalchemy.exc import OperationalError

    otel = Otel.query.first()
    form = OtelForm()
    
    # GET request - formu otel bilgileriyle doldur
    if request.method == 'GET' and otel:
        form.otel_adi.data = otel.ad
        form.adres.data = otel.adres
        form.telefon.data = otel.telefon
        form.email.data = otel.email

    if form.validate_on_submit():
        try:
            if otel:
                # Güncelle - eski değerleri kaydet (audit için)
                eski_deger = serialize_model(otel)

                otel.ad = form.otel_adi.data
                otel.adres = form.adres.data
                otel.telefon = form.telefon.data
                otel.email = form.email.data

                db.session.commit()

                # Audit Trail
                audit_update('oteller', otel.id, eski_deger, otel)
            else:
                # Yeni oluştur
                otel = Otel(
                    ad=form.otel_adi.data,
                    adres=form.adres.data,
                    telefon=form.telefon.data,
                    email=form.email.data
                )
                db.session.add(otel)
                db.session.commit()

                # Audit Trail
                audit_create('oteller', otel.id, otel)

            flash('Otel bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('sistem_yoneticisi_dashboard'))

        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='otel_tanimla')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='otel_tanimla', extra_info={'form_data': form.data})

    return render_template('sistem_yoneticisi/otel_tanimla.html', otel=otel, form=form)

@app.route('/kat-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_tanimla():
    from forms import KatForm
    from sqlalchemy.exc import IntegrityError, OperationalError

    form = KatForm()

    if form.validate_on_submit():
        try:
            kat = Kat(
                otel_id=1,  # İlk otel
                kat_adi=form.kat_adi.data,
                kat_no=form.kat_no.data,
                aciklama=form.aciklama.data or ''
            )
            db.session.add(kat)
            db.session.commit()

            # Audit Trail
            audit_create('kat', kat.id, kat)

            flash('Kat başarıyla eklendi.', 'success')
            return redirect(url_for('kat_tanimla'))

        except IntegrityError:
            db.session.rollback()
            flash('Bu kat numarası zaten mevcut.', 'danger')
            log_hata(Exception('Kat IntegrityError'), modul='kat_tanimla')
        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='kat_tanimla')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='kat_tanimla', extra_info={'form_data': form.data})

    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    return render_template('sistem_yoneticisi/kat_tanimla.html', katlar=katlar, form=form)

@app.route('/kat-duzenle/<int:kat_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_duzenle(kat_id):
    from forms import KatForm
    from sqlalchemy.exc import IntegrityError, OperationalError

    kat = Kat.query.get_or_404(kat_id)
    form = KatForm(obj=kat)

    if form.validate_on_submit():
        try:
            # Eski değerleri kaydet
            eski_deger = serialize_model(kat)

            kat.kat_adi = form.kat_adi.data
            kat.kat_no = form.kat_no.data
            kat.aciklama = form.aciklama.data or ''

            db.session.commit()

            # Audit Trail
            audit_update('kat', kat.id, eski_deger, kat)

            flash('Kat başarıyla güncellendi.', 'success')
            return redirect(url_for('kat_tanimla'))

        except IntegrityError:
            db.session.rollback()
            flash('Bu kat numarası başka bir kat tarafından kullanılıyor.', 'danger')
            log_hata(Exception('Kat Duzenle IntegrityError'), modul='kat_duzenle')
        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='kat_duzenle')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='kat_duzenle', extra_info={'kat_id': kat_id, 'form_data': form.data})

    return render_template('sistem_yoneticisi/kat_duzenle.html', kat=kat, form=form)

@app.route('/kat-sil/<int:kat_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def kat_sil(kat_id):
    try:
        kat = Kat.query.get_or_404(kat_id)
        eski_deger = serialize_model(kat)
        kat.aktif = False
        db.session.commit()
        
        # Audit Trail
        audit_update('kat', kat.id, eski_deger, kat)
        
        flash('Kat başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('kat_tanimla'))

@app.route('/oda-tanimla', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_tanimla():
    from forms import OdaForm
    from sqlalchemy.exc import IntegrityError, OperationalError

    # Kat seçeneklerini doldur (form oluşturmadan önce)
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    kat_choices = [(k.id, f'{k.kat_adi} (Kat {k.kat_no})') for k in katlar]
    
    form = OdaForm()
    form.kat_id.choices = kat_choices

    if form.validate_on_submit():
        try:
            oda = Oda(
                kat_id=form.kat_id.data,
                oda_no=form.oda_no.data,
                oda_tipi=form.oda_tipi.data,
                kapasite=form.kapasite.data
            )
            db.session.add(oda)
            db.session.commit()

            # Audit Trail
            audit_create('oda', oda.id, oda)

            flash('Oda başarıyla eklendi.', 'success')
            return redirect(url_for('oda_tanimla'))

        except IntegrityError:
            db.session.rollback()
            flash('Bu oda numarası zaten mevcut.', 'danger')
            log_hata(Exception('Oda IntegrityError'), modul='oda_tanimla')
        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='oda_tanimla')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='oda_tanimla', extra_info={'form_data': form.data})

    odalar = Oda.query.filter_by(aktif=True).order_by(Oda.oda_no).all()
    return render_template('sistem_yoneticisi/oda_tanimla.html', katlar=katlar, odalar=odalar, form=form)

@app.route('/oda-duzenle/<int:oda_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_duzenle(oda_id):
    from forms import OdaForm
    from sqlalchemy.exc import IntegrityError, OperationalError

    oda = Oda.query.get_or_404(oda_id)
    
    # Kat seçeneklerini doldur (form oluşturmadan önce)
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    kat_choices = [(k.id, f'{k.kat_adi} (Kat {k.kat_no})') for k in katlar]
    
    form = OdaForm(obj=oda)
    form.kat_id.choices = kat_choices

    if form.validate_on_submit():
        try:
            # Eski değerleri kaydet
            eski_deger = serialize_model(oda)

            oda.kat_id = form.kat_id.data
            oda.oda_no = form.oda_no.data
            oda.oda_tipi = form.oda_tipi.data
            oda.kapasite = form.kapasite.data

            db.session.commit()

            # Audit Trail
            audit_update('oda', oda.id, eski_deger, oda)

            flash('Oda başarıyla güncellendi.', 'success')
            return redirect(url_for('oda_tanimla'))

        except IntegrityError:
            db.session.rollback()
            flash('Bu oda numarası başka bir oda tarafından kullanılıyor.', 'danger')
            log_hata(Exception('Oda Duzenle IntegrityError'), modul='oda_duzenle')
        except OperationalError as e:
            db.session.rollback()
            flash('Veritabanı bağlantı hatası. Lütfen daha sonra tekrar deneyin.', 'danger')
            log_hata(e, modul='oda_duzenle')
        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Sistem yöneticisine bildirildi.', 'danger')
            log_hata(e, modul='oda_duzenle', extra_info={'oda_id': oda_id, 'form_data': form.data})

    return render_template('sistem_yoneticisi/oda_duzenle.html', oda=oda, katlar=katlar, form=form)

@app.route('/oda-sil/<int:oda_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def oda_sil(oda_id):
    try:
        oda = Oda.query.get_or_404(oda_id)
        eski_deger = serialize_model(oda)
        db.session.delete(oda)
        db.session.commit()
        
        # Audit Trail
        audit_delete('oda', oda_id, eski_deger)
        
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
    from forms import PersonelForm
    from sqlalchemy.exc import IntegrityError

    form = PersonelForm()

    if form.validate_on_submit():
        try:
            personel = Kullanici(
                kullanici_adi=form.kullanici_adi.data,
                ad=form.ad.data,
                soyad=form.soyad.data,
                email=form.email.data or '',
                telefon=form.telefon.data or '',
                rol=form.rol.data
            )
            personel.sifre_belirle(form.sifre.data)
            db.session.add(personel)
            db.session.commit()

            # Audit Trail
            audit_create('kullanici', personel.id, personel)

            flash('Kullanıcı başarıyla eklendi.', 'success')
            return redirect(url_for('personel_tanimla'))

        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e)

            # Kullanıcı dostu hata mesajları
            if 'kullanici_adi' in error_msg:
                flash('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.', 'danger')
            elif 'email' in error_msg:
                flash('Bu e-posta adresi zaten kullanılıyor. Lütfen farklı bir e-posta adresi seçin.', 'danger')
            else:
                flash('Kayıt sırasında bir hata oluştu.', 'danger')
            log_hata(e, modul='personel_tanimla')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='personel_tanimla')

    personeller = Kullanici.query.filter(
        Kullanici.rol.in_(['admin', 'depo_sorumlusu', 'kat_sorumlusu']),
        Kullanici.aktif.is_(True)
    ).order_by(Kullanici.olusturma_tarihi.desc()).all()
    return render_template('admin/personel_tanimla.html', form=form, personeller=personeller)

@app.route('/personel-duzenle/<int:personel_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_duzenle(personel_id):
    from forms import PersonelDuzenleForm
    from sqlalchemy.exc import IntegrityError
    from utils.audit import serialize_model

    personel = Kullanici.query.get_or_404(personel_id)
    form = PersonelDuzenleForm(obj=personel)

    if form.validate_on_submit():
        try:
            # Eski değerleri kaydet
            eski_deger = serialize_model(personel)

            personel.kullanici_adi = form.kullanici_adi.data
            personel.ad = form.ad.data
            personel.soyad = form.soyad.data
            personel.email = form.email.data or ''
            personel.telefon = form.telefon.data or ''
            personel.rol = form.rol.data

            # Şifre değiştirilmişse
            if form.yeni_sifre.data:
                personel.sifre_belirle(form.yeni_sifre.data)

            db.session.commit()

            # Audit Trail
            audit_update('kullanici', personel.id, eski_deger, personel)

            flash('Kullanıcı başarıyla güncellendi.', 'success')
            return redirect(url_for('personel_tanimla'))

        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e)

            # Kullanıcı dostu hata mesajları
            if 'kullanici_adi' in error_msg:
                flash('Bu kullanıcı adı zaten kullanılıyor. Lütfen farklı bir kullanıcı adı seçin.', 'danger')
            elif 'email' in error_msg:
                flash('Bu e-posta adresi zaten kullanılıyor. Lütfen farklı bir e-posta adresi seçin.', 'danger')
            else:
                flash('Güncelleme sırasında bir hata oluştu.', 'danger')
            log_hata(e, modul='personel_duzenle')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='personel_duzenle')

    return render_template('admin/personel_duzenle.html', form=form, personel=personel)

@app.route('/personel-pasif-yap/<int:personel_id>', methods=['POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def personel_pasif_yap(personel_id):
    try:
        personel = Kullanici.query.get_or_404(personel_id)
        eski_deger = serialize_model(personel)
        personel.aktif = False
        db.session.commit()
        
        # Audit Trail
        audit_update('kullanici', personel.id, eski_deger, personel)
        
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
        eski_deger = serialize_model(personel)
        personel.aktif = True
        db.session.commit()
        
        # Audit Trail
        audit_update('kullanici', personel.id, eski_deger, personel)
        
        flash('Kullanıcı başarıyla aktif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('personel_tanimla'))

@app.route('/urun-gruplari', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_gruplari():
    from forms import UrunGrupForm
    from sqlalchemy.exc import IntegrityError

    form = UrunGrupForm()

    if form.validate_on_submit():
        try:
            grup = UrunGrup(
                grup_adi=form.grup_adi.data,
                aciklama=form.aciklama.data or ''
            )
            db.session.add(grup)
            db.session.commit()

            # Audit Trail
            audit_create('urun_grup', grup.id, grup)

            flash('Ürün grubu başarıyla eklendi.', 'success')
            return redirect(url_for('urun_gruplari'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Bu grup adı zaten kullanılıyor. Lütfen farklı bir ad girin.', 'danger')
            log_hata(e, modul='urun_gruplari')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='urun_gruplari')

    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    return render_template('admin/urun_gruplari.html', form=form, gruplar=gruplar)

@app.route('/grup-duzenle/<int:grup_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def grup_duzenle(grup_id):
    from forms import UrunGrupForm
    from sqlalchemy.exc import IntegrityError

    grup = UrunGrup.query.get_or_404(grup_id)
    form = UrunGrupForm(obj=grup)

    if form.validate_on_submit():
        try:
            eski_deger = serialize_model(grup)
            grup.grup_adi = form.grup_adi.data
            grup.aciklama = form.aciklama.data or ''
            db.session.commit()

            # Audit Trail
            audit_update('urun_grup', grup.id, eski_deger, grup)

            flash('Ürün grubu başarıyla güncellendi.', 'success')
            return redirect(url_for('urun_gruplari'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Bu grup adı zaten kullanılıyor. Lütfen farklı bir ad girin.', 'danger')
            log_hata(e, modul='grup_duzenle')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='grup_duzenle')

    return render_template('admin/grup_duzenle.html', form=form, grup=grup)

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
        
        eski_deger = serialize_model(grup)
        db.session.delete(grup)
        db.session.commit()
        
        # Audit Trail
        audit_delete('urun_grup', grup_id, eski_deger)
        
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
        eski_deger = serialize_model(grup)
        grup.aktif = False
        db.session.commit()
        
        # Audit Trail
        audit_update('urun_grup', grup.id, eski_deger, grup)
        
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
        eski_deger = serialize_model(grup)
        grup.aktif = True
        db.session.commit()
        
        # Audit Trail
        audit_update('urun_grup', grup.id, eski_deger, grup)
        
        flash('Ürün grubu başarıyla aktif yapıldı.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Hata oluştu: {str(e)}', 'danger')
    
    return redirect(url_for('urun_gruplari'))

@app.route('/urunler', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urunler():
    from forms import UrunForm
    from sqlalchemy.exc import IntegrityError

    # Grup seçeneklerini doldur (form oluşturmadan önce)
    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    grup_choices = [(g.id, g.grup_adi) for g in gruplar]
    
    form = UrunForm()
    form.grup_id.choices = grup_choices

    if form.validate_on_submit():
        try:
            urun = Urun(
                grup_id=form.grup_id.data,
                urun_adi=form.urun_adi.data,
                barkod=form.barkod.data or None,
                birim=form.birim.data or 'Adet',
                kritik_stok_seviyesi=form.kritik_stok_seviyesi.data or 10
            )
            db.session.add(urun)
            db.session.commit()

            # Audit Trail
            audit_create('urun', urun.id, urun)

            # Log kaydı
            log_islem('ekleme', 'urun', {
                'urun_adi': urun.urun_adi,
                'barkod': urun.barkod,
                'grup_id': urun.grup_id,
                'birim': urun.birim
            })

            flash('Ürün başarıyla eklendi.', 'success')
            return redirect(url_for('urunler'))

        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e)
            if 'barkod' in error_msg:
                flash('Bu barkod numarası zaten kullanılıyor. Lütfen farklı bir barkod girin veya boş bırakın.', 'danger')
            else:
                flash('Kayıt sırasında bir hata oluştu.', 'danger')
            log_hata(e, modul='urunler')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='urunler')

    # Tüm ürünleri getir (aktif ve pasif)
    urunler = Urun.query.order_by(Urun.aktif.desc(), Urun.urun_adi).all()
    return render_template('admin/urunler.html', form=form, gruplar=gruplar, urunler=urunler)

@app.route('/urun-duzenle/<int:urun_id>', methods=['GET', 'POST'])
@login_required
@role_required('sistem_yoneticisi', 'admin')
def urun_duzenle(urun_id):
    from forms import UrunForm
    from sqlalchemy.exc import IntegrityError
    from utils.audit import serialize_model

    urun = Urun.query.get_or_404(urun_id)
    gruplar = UrunGrup.query.filter_by(aktif=True).order_by(UrunGrup.grup_adi).all()
    grup_choices = [(g.id, g.grup_adi) for g in gruplar]

    form = UrunForm(obj=urun)
    form.grup_id.choices = grup_choices

    if form.validate_on_submit():
        try:
            # Eski değerleri kaydet
            eski_deger = serialize_model(urun)
            eski_urun_adi = urun.urun_adi

            urun.urun_adi = form.urun_adi.data
            urun.grup_id = form.grup_id.data
            urun.barkod = form.barkod.data or None
            urun.birim = form.birim.data or 'Adet'
            urun.kritik_stok_seviyesi = form.kritik_stok_seviyesi.data or 10

            db.session.commit()

            # Audit Trail
            audit_update('urun', urun.id, eski_deger, urun)

            # Log kaydı
            log_islem('guncelleme', 'urun', {
                'urun_id': urun.id,
                'eski_urun_adi': eski_urun_adi,
                'yeni_urun_adi': urun.urun_adi,
                'barkod': urun.barkod
            })

            flash('Ürün başarıyla güncellendi.', 'success')
            return redirect(url_for('urunler'))

        except IntegrityError as e:
            db.session.rollback()
            error_msg = str(e)
            if 'barkod' in error_msg:
                flash('Bu barkod numarası zaten kullanılıyor. Lütfen farklı bir barkod girin veya boş bırakın.', 'danger')
            else:
                flash('Güncelleme sırasında bir hata oluştu.', 'danger')
            log_hata(e, modul='urun_duzenle')

        except Exception as e:
            db.session.rollback()
            flash('Beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.', 'danger')
            log_hata(e, modul='urun_duzenle')

    return render_template('admin/urun_duzenle.html', form=form, urun=urun, gruplar=gruplar)

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
        
        # Eski değerleri kaydet (silme öncesi)
        from utils.audit import serialize_model
        eski_deger = serialize_model(urun)
        
        db.session.delete(urun)
        db.session.commit()
        
        # Audit Trail
        audit_delete('urun', urun_id, eski_deger)
        
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
        eski_deger = serialize_model(urun)
        urun.aktif = False
        db.session.commit()
        
        # Audit Trail
        audit_update('urun', urun.id, eski_deger, urun)
        
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
        eski_deger = serialize_model(urun)
        urun.aktif = True
        db.session.commit()
        
        # Audit Trail
        audit_update('urun', urun.id, eski_deger, urun)
        
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
    
    # Son stok hareketlerini getir
    stok_hareketleri = StokHareket.query.order_by(StokHareket.islem_tarihi.desc()).limit(50).all()
    
    return render_template('depo_sorumlusu/stok_giris.html', 
                         gruplar=gruplar,
                         urunler=urunler, 
                         stok_hareketleri=stok_hareketleri)

@app.route('/stok-duzenle/<int:hareket_id>', methods=['GET', 'POST'])
@login_required
@role_required('depo_sorumlusu')
def stok_duzenle(hareket_id):
    hareket = StokHareket.query.get_or_404(hareket_id)
    
    if request.method == 'POST':
        try:
            # Eski değerleri kaydet
            from utils.audit import serialize_model
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
        islem_yapan = get_current_user()
        if not islem_yapan:
            flash('Kullanıcı oturumu bulunamadı. Lütfen tekrar giriş yapın.', 'danger')
            return redirect(url_for('logout'))
        
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
                    islem_yapan_id=islem_yapan.id
                )
                db.session.add(stok_hareket)
                
                # İade edilen miktarı kaydet
                detay.iade_edilen_miktar = (detay.iade_edilen_miktar or 0) + kalan
                detay.kalan_miktar = 0
        
        # Zimmet durumunu güncelle
        zimmet.durum = 'iptal'
        zimmet.iade_tarihi = datetime.now(timezone.utc)
        
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
        islem_yapan = get_current_user()
        if not islem_yapan:
            flash('Kullanıcı oturumu bulunamadı. Lütfen tekrar giriş yapın.', 'danger')
            return redirect(url_for('logout'))
        
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
            islem_yapan_id=islem_yapan.id
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
        oda = db.session.get(Oda, oda_id)
        
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
            stok_map = get_stok_toplamlari([urun.id for urun in urunler_liste])
            
            rapor_verisi = []
            for urun in urunler_liste:
                mevcut_stok = stok_map.get(urun.id, 0)
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
                            zimmet = db.session.get(PersonelZimmet, zimmet_id)
                            if zimmet and zimmet.personel:
                                hareket.zimmet_personel = f"{zimmet.personel.ad} {zimmet.personel.soyad}"
                            else:
                                hareket.zimmet_personel = None
                        else:
                            hareket.zimmet_personel = None
                    except Exception:
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
            # Minibar Tüketim Raporu - SADECE minibar kontrol sırasındaki tüketim
            rapor_baslik = "Minibar Tüketim Raporu"
            
            query = db.session.query(
                Urun.urun_adi,
                Urun.birim,
                UrunGrup.grup_adi,
                Oda.oda_no,
                Kat.kat_adi,
                MinibarIslem.islem_tarihi,
                MinibarIslem.islem_tipi,
                MinibarIslemDetay.tuketim,  # Tüketim sütununu kullan
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
                # Kontrol ve doldurma işlemlerini al (ilk_dolum hariç - çünkü ilk dolumda tüketim yok)
                MinibarIslem.islem_tipi.in_(['kontrol', 'doldurma']),
                MinibarIslemDetay.tuketim > 0  # Sadece tüketim olan kayıtlar
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
            aktif_urunler = Urun.query.filter_by(aktif=True).all()
            stok_map = get_stok_toplamlari([urun.id for urun in aktif_urunler])
            urunler_by_grup = {}
            for urun in aktif_urunler:
                urunler_by_grup.setdefault(urun.grup_id, []).append(urun)
            
            rapor_verisi = []
            for grup in query.all():
                grup_urunleri = urunler_by_grup.get(grup.id, [])
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = stok_map.get(urun.id, 0)
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
            
            # KONTROL İŞLEMİNDE KAYIT OLUŞTURMA - Sadece Görüntüleme
            if islem_tipi == 'kontrol':
                flash('Kontrol işlemi tamamlandı. (Sadece görüntüleme - kayıt oluşturulmadı)', 'info')
                
                # Kontrol için sistem logu
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
                            urun = db.session.get(Urun, urun_id)
                            urun_adi = urun.urun_adi if urun else 'Bilinmeyen ürün'
                            raise Exception(f'Zimmetinizde bu ürün bulunmuyor: {urun_adi}')
                        
                        # Toplam kalan miktarı hesapla
                        toplam_kalan = sum(detay.miktar - detay.kullanilan_miktar for detay in zimmet_detaylar)
                        
                        if toplam_kalan < miktar:
                            urun = db.session.get(Urun, urun_id)
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
            
            # Audit Trail
            audit_create('minibar_islem', islem.id, islem)
            
            flash('Minibar işlemi başarıyla kaydedildi. Zimmetinizden düşürülen ürünler güncellendi.', 'success')
            
            # İşlem logu
            log_islem(
                kullanici_id=kullanici_id,
                modul='minibar',
                islem_tipi=islem_tipi,
                aciklama=f'Oda {oda_id} - {islem_tipi} işlemi'
            )
            
            return redirect(url_for('minibar_kontrol'))
            
        except Exception as e:
            db.session.rollback()
            
            # Hatayı logla
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
        return jsonify({'success': False, 'error': str(e)})

@app.route('/minibar-urunler')
@login_required
@role_required('kat_sorumlusu')
def minibar_urunler():
    """Minibar ürünlerini JSON olarak döndür"""
    try:
        urunler = Urun.query.filter_by(aktif=True).order_by(Urun.grup_id, Urun.urun_adi).all()
        
        # Kullanıcının zimmet bilgilerini getir - aktif zimmetler
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
            urun = db.session.get(Urun, detay.urun_id)
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
    """Tek bir ürünü minibar'a doldur - YENİ VERSİYON: Gerçek stok girişi ile"""
    try:
        data = request.get_json()
        oda_id = data.get('oda_id')
        urun_id = data.get('urun_id')
        gercek_mevcut_stok = float(data.get('gercek_mevcut_stok', 0))
        eklenen_miktar = float(data.get('eklenen_miktar', 0))
        islem_tipi = data.get('islem_tipi', 'doldurma')
        kullanici_id = session['kullanici_id']
        
        # Validasyon
        if not oda_id or not urun_id:
            return jsonify({'success': False, 'error': 'Geçersiz parametreler'})
        
        if gercek_mevcut_stok < 0:
            return jsonify({'success': False, 'error': 'Mevcut stok negatif olamaz'})
            
        if eklenen_miktar <= 0:
            return jsonify({'success': False, 'error': 'Eklenecek miktar 0\'dan büyük olmalı'})
        
        urun = db.session.get(Urun, urun_id)
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
        if toplam_kalan < eklenen_miktar:
            return jsonify({'success': False, 'error': f'Yetersiz zimmet! Kalan: {toplam_kalan} {urun.birim}'})
        
        # Son işlemi bul
        son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(MinibarIslem.id.desc()).first()
        
        if not son_islem:
            return jsonify({'success': False, 'error': 'Bu odada henüz işlem yapılmamış. Önce ilk dolum yapınız.'})
        
        # Son işlemdeki kayıtlı stok
        son_detay = MinibarIslemDetay.query.filter_by(
            islem_id=son_islem.id,
            urun_id=urun_id
        ).first()
        
        if not son_detay:
            return jsonify({'success': False, 'error': 'Bu ürün için kayıt bulunamadı'})
        
        kayitli_stok = son_detay.bitis_stok if son_detay.bitis_stok is not None else 0
        
        # TÜKETİM HESAPLAMA (Gerçek sayım ile)
        tuketim = max(0, kayitli_stok - gercek_mevcut_stok)
        
        # Yeni stok
        yeni_stok = gercek_mevcut_stok + eklenen_miktar
        
        # Yeni işlem oluştur
        islem = MinibarIslem(
            oda_id=oda_id,
            personel_id=kullanici_id,
            islem_tipi=islem_tipi,
            aciklama=f'Gerçek Sayım: {gercek_mevcut_stok}, Eklenen: {eklenen_miktar}, Tüketim: {tuketim} {urun.birim} {urun.urun_adi}'
        )
        db.session.add(islem)
        db.session.flush()
        
        # ÖNEMLİ: Diğer ürünleri kopyala (değişmeden)
        if son_islem:
            for son_detay_item in son_islem.detaylar:
                if son_detay_item.urun_id != urun_id:
                    mevcut = son_detay_item.bitis_stok if son_detay_item.bitis_stok is not None else 0
                    
                    yeni_detay = MinibarIslemDetay(
                        islem_id=islem.id,
                        urun_id=son_detay_item.urun_id,
                        baslangic_stok=mevcut,
                        bitis_stok=mevcut,
                        tuketim=0,
                        eklenen_miktar=0,
                        zimmet_detay_id=None
                    )
                    db.session.add(yeni_detay)
        
        # Zimmetten düş (FIFO)
        kalan_miktar = eklenen_miktar
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
        
        # Eklenen ürün için minibar detayı kaydet
        detay = MinibarIslemDetay(
            islem_id=islem.id,
            urun_id=urun_id,
            baslangic_stok=gercek_mevcut_stok,  # Gerçek sayım
            bitis_stok=yeni_stok,  # Gerçek + eklenen
            tuketim=tuketim,  # Kayıtlı - gerçek
            eklenen_miktar=eklenen_miktar,
            zimmet_detay_id=kullanilan_zimmet_id
        )
        db.session.add(detay)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'✅ Başarılı!\n\nTüketim: {tuketim} {urun.birim}\nEklenen: {eklenen_miktar} {urun.birim}\nYeni Stok: {yeni_stok} {urun.birim}',
            'yeni_stok': yeni_stok,
            'tuketim': tuketim
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# TOPLU İŞLEM ÖZELLİKLERİ
# ============================================================================

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

@app.route('/api/toplu-oda-mevcut-durum', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_toplu_oda_mevcut_durum():
    """Seçilen odalardaki belirli bir ürünün mevcut stok durumunu döndür"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz JSON verisi'}), 400
        
        oda_ids = data.get('oda_ids', [])
        urun_id = data.get('urun_id')
        
        if not oda_ids or not urun_id:
            return jsonify({'success': False, 'error': 'Eksik parametreler'}), 400
        
        # Tip dönüşümü yap
        try:
            urun_id = int(urun_id)
            oda_ids = [int(oid) for oid in oda_ids]
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Geçersiz parametre tipi: {str(e)}'}), 400
        
        durum_listesi = []
        
        for oda_id in oda_ids:
            oda = db.session.get(Oda, oda_id)
            if not oda:
                continue
            
            # Son işlemi bul
            son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(
                MinibarIslem.id.desc()
            ).first()
            
            mevcut_stok = 0
            if son_islem:
                son_detay = next((d for d in son_islem.detaylar if d.urun_id == urun_id), None)
                if son_detay:
                    mevcut_stok = son_detay.bitis_stok if son_detay.bitis_stok is not None else 0
            
            durum_listesi.append({
                'oda_id': oda_id,
                'oda_no': oda.oda_no,
                'mevcut_stok': mevcut_stok
            })
        
        return jsonify({'success': True, 'durum': durum_listesi})
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Mevcut durum hatası: {error_detail}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/toplu-oda-doldur', methods=['POST'])
@login_required
@role_required('kat_sorumlusu')
def api_toplu_oda_doldur():
    """Seçilen odalara toplu olarak ürün doldur - Direkt stok ekleme (tüketim takibi yok)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Geçersiz JSON verisi'}), 400
        
        oda_ids = data.get('oda_ids', [])  # Seçilen oda ID'leri
        urun_id = data.get('urun_id')
        eklenen_miktar = data.get('eklenen_miktar')
        kullanici_id = session.get('kullanici_id')
        
        if not kullanici_id:
            return jsonify({'success': False, 'error': 'Kullanıcı oturumu bulunamadı'}), 401

        # Validasyon ve tip dönüşümü
        if not oda_ids or not urun_id or not eklenen_miktar:
            return jsonify({'success': False, 'error': 'Eksik parametreler'}), 400
        
        try:
            urun_id = int(urun_id)
            oda_ids = [int(oid) for oid in oda_ids]
            eklenen_miktar = float(eklenen_miktar)
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Geçersiz parametre tipi: {str(e)}'}), 400
        
        if eklenen_miktar <= 0:
            return jsonify({'success': False, 'error': 'Eklenecek miktar 0\'dan büyük olmalıdır'}), 400

        # Ürün bilgisi
        urun = db.session.get(Urun, urun_id)
        if not urun:
            return jsonify({'success': False, 'error': 'Ürün bulunamadı'})

        # Zimmetten toplam gereken miktar
        toplam_gerekli = eklenen_miktar * len(oda_ids)

        # Kullanıcının zimmetini kontrol et
        zimmet_detaylar = db.session.query(PersonelZimmetDetay).join(
            PersonelZimmet, PersonelZimmetDetay.zimmet_id == PersonelZimmet.id
        ).filter(
            PersonelZimmet.personel_id == kullanici_id,
            PersonelZimmet.durum == 'aktif',
            PersonelZimmetDetay.urun_id == urun_id
        ).order_by(PersonelZimmet.zimmet_tarihi).all()

        # Toplam kalan zimmet
        toplam_kalan = sum(detay.miktar - detay.kullanilan_miktar for detay in zimmet_detaylar)

        if toplam_kalan < toplam_gerekli:
            return jsonify({
                'success': False,
                'error': f'Zimmetinizde yeterli ürün yok! Gereken: {toplam_gerekli} {urun.birim}, Mevcut: {toplam_kalan} {urun.birim}'
            })

        # Her oda için işlem oluştur
        basarili_odalar = []
        hatali_odalar = []

        for oda_id in oda_ids:
            try:
                oda = db.session.get(Oda, oda_id)
                if not oda:
                    hatali_odalar.append({'oda_id': oda_id, 'hata': 'Oda bulunamadı'})
                    continue

                # Son işlemi bul
                son_islem = MinibarIslem.query.filter_by(oda_id=oda_id).order_by(
                    MinibarIslem.id.desc()
                ).first()

                # Mevcut stok (bu ürün için)
                mevcut_stok = 0
                if son_islem:
                    son_detay = next((d for d in son_islem.detaylar if d.urun_id == urun_id), None)
                    if son_detay:
                        mevcut_stok = son_detay.bitis_stok if son_detay.bitis_stok is not None else 0

                # Yeni stok = Mevcut + Eklenen (tüketim takibi yok)
                yeni_stok = mevcut_stok + eklenen_miktar

                # Yeni işlem oluştur
                islem = MinibarIslem(
                    oda_id=oda_id,
                    personel_id=kullanici_id,
                    islem_tipi='doldurma',
                    aciklama=f'TOPLU DOLDURMA - Mevcut: {mevcut_stok}, Eklenen: {eklenen_miktar} {urun.birim} {urun.urun_adi}'
                )
                db.session.add(islem)
                db.session.flush()

                # Diğer ürünleri kopyala (değişmeden)
                if son_islem:
                    for son_detay_item in son_islem.detaylar:
                        if son_detay_item.urun_id != urun_id:
                            mevcut = son_detay_item.bitis_stok if son_detay_item.bitis_stok is not None else 0
                            yeni_detay = MinibarIslemDetay(
                                islem_id=islem.id,
                                urun_id=son_detay_item.urun_id,
                                baslangic_stok=mevcut,
                                bitis_stok=mevcut,
                                tuketim=0,
                                eklenen_miktar=0,
                                zimmet_detay_id=son_detay_item.zimmet_detay_id
                            )
                            db.session.add(yeni_detay)

                # Doldurma detayını ekle (tüketim = 0, sadece ekleme)
                doldurma_detay = MinibarIslemDetay(
                    islem_id=islem.id,
                    urun_id=urun_id,
                    baslangic_stok=mevcut_stok,
                    bitis_stok=yeni_stok,
                    tuketim=0,  # Tüketim takibi yok
                    eklenen_miktar=eklenen_miktar,
                    zimmet_detay_id=None
                )
                db.session.add(doldurma_detay)

                # Zimmetten düş (FIFO) - Sadece eklenen miktar kadar
                kalan_miktar = eklenen_miktar
                for zimmet_detay in zimmet_detaylar:
                    if kalan_miktar <= 0:
                        break
                    detay_kalan = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                    if detay_kalan > 0:
                        kullanilacak = min(detay_kalan, kalan_miktar)
                        zimmet_detay.kullanilan_miktar += kullanilacak
                        zimmet_detay.kalan_miktar = zimmet_detay.miktar - zimmet_detay.kullanilan_miktar
                        kalan_miktar -= kullanilacak

                        if not doldurma_detay.zimmet_detay_id:
                            doldurma_detay.zimmet_detay_id = zimmet_detay.id

                basarili_odalar.append({'oda_id': oda_id, 'oda_no': oda.oda_no})

            except Exception as oda_hata:
                hatali_odalar.append({'oda_id': oda_id, 'hata': str(oda_hata)})
                db.session.rollback()
                continue

        # Tüm işlemleri kaydet
        if basarili_odalar:
            db.session.commit()
            
            # Audit Trail - Toplu doldurma işlemi
            audit_create('minibar_toplu_doldurma', None, {
                'urun_id': urun_id,
                'urun_adi': urun.urun_adi,
                'eklenen_miktar': eklenen_miktar,
                'oda_sayisi': len(basarili_odalar),
                'toplam_miktar': toplam_gerekli,
                'basarili_odalar': [o['oda_no'] for o in basarili_odalar],
                'islem_tipi': 'toplu_doldurma'
            })

        return jsonify({
            'success': True,
            'basarili_sayisi': len(basarili_odalar),
            'hatali_sayisi': len(hatali_odalar),
            'basarili_odalar': basarili_odalar,
            'hatali_odalar': hatali_odalar,
            'mesaj': f'{len(basarili_odalar)} odaya başarıyla ürün eklendi!'
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        error_detail = traceback.format_exc()
        print(f"Toplu doldurma hatası: {error_detail}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/kat-bazli-rapor', methods=['GET'])
@login_required
@role_required('kat_sorumlusu', 'admin', 'depo_sorumlusu')
def kat_bazli_rapor():
    """Kat bazlı tüketim raporu sayfası"""
    katlar = Kat.query.filter_by(aktif=True).order_by(Kat.kat_no).all()
    return render_template('raporlar/kat_bazli_rapor.html', katlar=katlar)

@app.route('/api/kat-rapor-veri', methods=['GET'])
@login_required
@role_required('kat_sorumlusu', 'admin', 'depo_sorumlusu')
def api_kat_rapor_veri():
    """Kat bazlı rapor verilerini getir"""
    try:
        kat_id = request.args.get('kat_id', type=int)
        baslangic_tarih = request.args.get('baslangic_tarih')
        bitis_tarih = request.args.get('bitis_tarih')

        if not kat_id:
            return jsonify({'success': False, 'error': 'Kat ID gerekli'})

        # Kat bilgisi
        kat = db.session.get(Kat, kat_id)
        if not kat:
            return jsonify({'success': False, 'error': 'Kat bulunamadı'})

        # Kattaki odalar
        odalar = Oda.query.filter_by(kat_id=kat_id, aktif=True).order_by(Oda.oda_no).all()

        if not odalar:
            return jsonify({'success': True, 'kat_adi': kat.kat_adi, 'odalar': [], 'urun_ozeti': []})

        # Tarih filtresi oluştur
        query_filter = []
        if baslangic_tarih:
            query_filter.append(MinibarIslem.islem_tarihi >= baslangic_tarih)
        if bitis_tarih:
            from datetime import datetime, timedelta
            bitis_dt = datetime.strptime(bitis_tarih, '%Y-%m-%d') + timedelta(days=1)
            query_filter.append(MinibarIslem.islem_tarihi < bitis_dt)

        # Her oda için rapor verisi
        oda_raporlari = []
        urun_toplam_tuketim = {}  # {urun_id: {'urun_adi': '', 'birim': '', 'toplam': 0}}

        for oda in odalar:
            # Son işlem
            son_islem_query = MinibarIslem.query.filter_by(oda_id=oda.id)
            if query_filter:
                son_islem_query = son_islem_query.filter(*query_filter)
            son_islem = son_islem_query.order_by(MinibarIslem.id.desc()).first()

            oda_veri = {
                'oda_no': oda.oda_no,
                'oda_id': oda.id,
                'son_islem_tarih': son_islem.islem_tarihi.strftime('%d.%m.%Y %H:%M') if son_islem else '-',
                'urunler': [],
                'toplam_tuketim_adedi': 0
            }

            if son_islem:
                for detay in son_islem.detaylar:
                    urun = detay.urun
                    oda_veri['urunler'].append({
                        'urun_adi': urun.urun_adi,
                        'mevcut_stok': detay.bitis_stok or 0,
                        'tuketim': detay.tuketim or 0,
                        'birim': urun.birim
                    })
                    oda_veri['toplam_tuketim_adedi'] += (detay.tuketim or 0)

                    # Ürün toplam tüketim
                    if urun.id not in urun_toplam_tuketim:
                        urun_toplam_tuketim[urun.id] = {
                            'urun_adi': urun.urun_adi,
                            'birim': urun.birim,
                            'toplam': 0
                        }
                    urun_toplam_tuketim[urun.id]['toplam'] += (detay.tuketim or 0)

            oda_raporlari.append(oda_veri)

        # Ürün özeti listesi
        urun_ozeti = [
            {
                'urun_adi': v['urun_adi'],
                'toplam_tuketim': v['toplam'],
                'birim': v['birim']
            }
            for v in urun_toplam_tuketim.values()
        ]

        # Toplam tüketim özeti sırala
        urun_ozeti.sort(key=lambda x: x['toplam_tuketim'], reverse=True)

        return jsonify({
            'success': True,
            'kat_adi': kat.kat_adi,
            'oda_sayisi': len(odalar),
            'odalar': oda_raporlari,
            'urun_ozeti': urun_ozeti
        })

    except Exception as e:
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
            stok_map = get_stok_toplamlari([urun.id for urun in urunler_liste])
            
            for urun in urunler_liste:
                row_num += 1
                mevcut_stok = stok_map.get(urun.id, 0)
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
                            zimmet = db.session.get(PersonelZimmet, zimmet_id)
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
            aktif_urunler = Urun.query.filter_by(aktif=True).all()
            stok_map = get_stok_toplamlari([urun.id for urun in aktif_urunler])
            urun_gruplari_map = {}
            for urun in aktif_urunler:
                urun_gruplari_map.setdefault(urun.grup_id, []).append(urun)
            
            for grup in gruplar:
                row_num += 1
                grup_urunleri = urun_gruplari_map.get(grup.id, [])
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = stok_map.get(urun.id, 0)
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
                except Exception:
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
            stok_map = get_stok_toplamlari([urun.id for urun in urunler_liste]) if urunler_liste else {}
            
            for urun in urunler_liste:
                mevcut_stok = stok_map.get(urun.id, 0)
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
                            zimmet = db.session.get(PersonelZimmet, zimmet_id)
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
            aktif_urunler = Urun.query.filter_by(aktif=True).all()
            stok_map = get_stok_toplamlari([urun.id for urun in aktif_urunler]) if aktif_urunler else {}

            grup_urunleri_map = {}
            for urun in aktif_urunler:
                grup_urunleri_map.setdefault(urun.grup_id, []).append(urun)

            for grup in gruplar:
                grup_urunleri = grup_urunleri_map.get(grup.id, [])
                toplam_urun_sayisi = len(grup_urunleri)
                kritik_urun_sayisi = 0
                
                for urun in grup_urunleri:
                    mevcut_stok = stok_map.get(urun.id, 0)
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

# ============================================================================
# API: DASHBOARD WIDGET'LARI
# ============================================================================

@app.route('/api/son-aktiviteler')
@login_required
@role_required(['sistem_yoneticisi', 'admin'])
def api_son_aktiviteler():
    """Son kullanıcı aktivitelerini döndür"""
    try:
        limit = request.args.get('limit', 10, type=int)

        # Son aktiviteleri çek (sadece önemli işlemler)
        aktiviteler = SistemLog.query\
            .filter(SistemLog.islem_tipi.in_(['ekleme', 'guncelleme', 'silme']))\
            .order_by(SistemLog.islem_tarihi.desc())\
            .limit(limit)\
            .all()

        data = []
        for log in aktiviteler:
            # Kullanıcı bilgisi
            kullanici_adi = 'Sistem'
            if log.kullanici:
                kullanici_adi = f"{log.kullanici.ad} {log.kullanici.soyad}"

            # İşlem detayını parse et
            import json
            detay = {}
            if log.islem_detay:
                try:
                    detay = json.loads(log.islem_detay) if isinstance(log.islem_detay, str) else log.islem_detay
                except Exception:
                    detay = {'aciklama': log.islem_detay}

            # Zaman farkı hesapla
            # islem_tarihi timezone-aware mi kontrol et
            if log.islem_tarihi.tzinfo is None:
                # Naive datetime ise, UTC olarak kabul et
                islem_tarihi = log.islem_tarihi.replace(tzinfo=timezone.utc)
            else:
                islem_tarihi = log.islem_tarihi
            
            zaman_farki = datetime.now(timezone.utc) - islem_tarihi

            if zaman_farki < timedelta(minutes=1):
                zaman_str = "Az önce"
            elif zaman_farki < timedelta(hours=1):
                dakika = int(zaman_farki.total_seconds() / 60)
                zaman_str = f"{dakika} dakika önce"
            elif zaman_farki < timedelta(days=1):
                saat = int(zaman_farki.total_seconds() / 3600)
                zaman_str = f"{saat} saat önce"
            else:
                gun = zaman_farki.days
                zaman_str = f"{gun} gün önce"

            data.append({
                'id': log.id,
                'kullanici': kullanici_adi,
                'islem_tipi': log.islem_tipi,
                'modul': log.modul,
                'detay': detay,
                'zaman': zaman_str,
                'tam_tarih': log.islem_tarihi.strftime('%d.%m.%Y %H:%M')
            })

        return jsonify({'success': True, 'aktiviteler': data})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tuketim-trendleri')
@login_required
@role_required(['sistem_yoneticisi', 'admin', 'depo_sorumlusu'])
def api_tuketim_trendleri():
    """Günlük/haftalık tüketim trendlerini döndür"""
    try:
        from sqlalchemy import func

        gun_sayisi = request.args.get('gun', 7, type=int)  # Varsayılan 7 gün

        # Son N günün tüketim verilerini al
        baslangic = datetime.now(timezone.utc) - timedelta(days=gun_sayisi)

        # Günlük tüketim toplamı (MinibarIslemDetay'dan)
        gunluk_tuketim = db.session.query(
            func.date(MinibarIslem.islem_tarihi).label('tarih'),
            func.sum(MinibarIslemDetay.tuketim).label('toplam_tuketim'),
            func.count(MinibarIslemDetay.id).label('islem_sayisi')
        ).join(MinibarIslemDetay, MinibarIslemDetay.islem_id == MinibarIslem.id)\
         .filter(MinibarIslem.islem_tarihi >= baslangic)\
         .group_by(func.date(MinibarIslem.islem_tarihi))\
         .order_by(func.date(MinibarIslem.islem_tarihi))\
         .all()

        # Tüm günleri doldur (veri olmayan günler için 0)
        tum_gunler = {}
        for i in range(gun_sayisi):
            tarih = (datetime.now(timezone.utc) - timedelta(days=gun_sayisi-i-1)).date()
            tum_gunler[str(tarih)] = {'tuketim': 0, 'islem_sayisi': 0}

        # Veri olanları güncelle
        for row in gunluk_tuketim:
            tarih_str = str(row.tarih)
            tum_gunler[tarih_str] = {
                'tuketim': int(row.toplam_tuketim or 0),
                'islem_sayisi': int(row.islem_sayisi or 0)
            }

        # Chart.js formatına çevir
        labels = []
        tuketim_data = []
        islem_data = []

        for tarih_str in sorted(tum_gunler.keys()):
            # Tarih formatla (DD/MM)
            tarih_obj = datetime.strptime(tarih_str, '%Y-%m-%d')
            labels.append(tarih_obj.strftime('%d/%m'))
            tuketim_data.append(tum_gunler[tarih_str]['tuketim'])
            islem_data.append(tum_gunler[tarih_str]['islem_sayisi'])

        return jsonify({
            'success': True,
            'labels': labels,
            'datasets': [
                {
                    'label': 'Toplam Tüketim',
                    'data': tuketim_data,
                    'borderColor': 'rgb(239, 68, 68)',
                    'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                    'tension': 0.3
                },
                {
                    'label': 'İşlem Sayısı',
                    'data': islem_data,
                    'borderColor': 'rgb(59, 130, 246)',
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'tension': 0.3
                }
            ]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================
# AUDIT TRAIL ROUTE'LARI
# ==========================

@app.route('/sistem-yoneticisi/audit-trail')
@login_required
@role_required('sistem_yoneticisi')
def audit_trail():
    """Audit Trail - Denetim İzi Sayfası"""
    from models import AuditLog, Kullanici
    from datetime import datetime, timedelta
    
    # Sayfalama
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Filtreler
    kullanici_id = request.args.get('kullanici_id', type=int)
    islem_tipi = request.args.get('islem_tipi')
    tablo_adi = request.args.get('tablo_adi')
    tarih_baslangic = request.args.get('tarih_baslangic')
    tarih_bitis = request.args.get('tarih_bitis')
    
    # Base query
    query = AuditLog.query
    
    # Filtreleme
    if kullanici_id:
        query = query.filter_by(kullanici_id=kullanici_id)
    if islem_tipi:
        query = query.filter_by(islem_tipi=islem_tipi)
    if tablo_adi:
        query = query.filter_by(tablo_adi=tablo_adi)
    if tarih_baslangic:
        tarih_baslangic_dt = datetime.strptime(tarih_baslangic, '%Y-%m-%d')
        query = query.filter(AuditLog.islem_tarihi >= tarih_baslangic_dt)
    if tarih_bitis:
        tarih_bitis_dt = datetime.strptime(tarih_bitis, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(AuditLog.islem_tarihi < tarih_bitis_dt)
    
    # Sıralama ve sayfalama
    query = query.order_by(AuditLog.islem_tarihi.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # İstatistikler
    bugun = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    bu_hafta = bugun - timedelta(days=bugun.weekday())
    bu_ay = bugun.replace(day=1)
    
    stats = {
        'today': AuditLog.query.filter(AuditLog.islem_tarihi >= bugun).count(),
        'week': AuditLog.query.filter(AuditLog.islem_tarihi >= bu_hafta).count(),
        'month': AuditLog.query.filter(AuditLog.islem_tarihi >= bu_ay).count()
    }
    
    # Filtre için kullanıcı listesi
    users = Kullanici.query.filter_by(aktif=True).order_by(Kullanici.kullanici_adi).all()
    
    # Filtre için tablo listesi (unique)
    tables = db.session.query(AuditLog.tablo_adi).distinct().order_by(AuditLog.tablo_adi).all()
    tables = [t[0] for t in tables]
    
    return render_template('sistem_yoneticisi/audit_trail.html',
                         logs=pagination.items,
                         pagination=pagination,
                         users=users,
                         tables=tables,
                         stats=stats)


@app.route('/sistem-yoneticisi/audit-trail/<int:log_id>')
@login_required
@role_required('sistem_yoneticisi')
def audit_trail_detail(log_id):
    """Audit Log Detay API"""
    from models import AuditLog
    
    log = AuditLog.query.get_or_404(log_id)
    
    return jsonify({
        'id': log.id,
        'kullanici_id': log.kullanici_id,
        'kullanici_adi': log.kullanici_adi,
        'kullanici_rol': log.kullanici_rol,
        'islem_tipi': log.islem_tipi,
        'tablo_adi': log.tablo_adi,
        'kayit_id': log.kayit_id,
        'eski_deger': log.eski_deger,
        'yeni_deger': log.yeni_deger,
        'degisiklik_ozeti': log.degisiklik_ozeti,
        'http_method': log.http_method,
        'url': log.url,
        'endpoint': log.endpoint,
        'ip_adresi': log.ip_adresi,
        'user_agent': log.user_agent,
        'islem_tarihi': log.islem_tarihi.strftime('%d.%m.%Y %H:%M:%S'),
        'aciklama': log.aciklama,
        'basarili': log.basarili,
        'hata_mesaji': log.hata_mesaji
    })


@app.route('/sistem-yoneticisi/audit-trail/export')
@login_required
@role_required('sistem_yoneticisi')
def audit_trail_export():
    """Audit Trail Excel Export"""
    from models import AuditLog
    from io import BytesIO
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from datetime import datetime
    
    # Filtreleri al
    kullanici_id = request.args.get('kullanici_id', type=int)
    islem_tipi = request.args.get('islem_tipi')
    tablo_adi = request.args.get('tablo_adi')
    tarih_baslangic = request.args.get('tarih_baslangic')
    tarih_bitis = request.args.get('tarih_bitis')
    
    # Query oluştur
    query = AuditLog.query
    
    if kullanici_id:
        query = query.filter_by(kullanici_id=kullanici_id)
    if islem_tipi:
        query = query.filter_by(islem_tipi=islem_tipi)
    if tablo_adi:
        query = query.filter_by(tablo_adi=tablo_adi)
    if tarih_baslangic:
        tarih_baslangic_dt = datetime.strptime(tarih_baslangic, '%Y-%m-%d')
        query = query.filter(AuditLog.islem_tarihi >= tarih_baslangic_dt)
    if tarih_bitis:
        tarih_bitis_dt = datetime.strptime(tarih_bitis, '%Y-%m-%d')
        query = query.filter(AuditLog.islem_tarihi <= tarih_bitis_dt)
    
    logs = query.order_by(AuditLog.islem_tarihi.desc()).limit(10000).all()
    
    # Excel oluştur
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Audit Trail"
    
    # Başlıklar
    headers = ['ID', 'Tarih', 'Kullanıcı', 'Rol', 'İşlem', 'Tablo', 'Kayıt ID', 
               'Değişiklik', 'IP', 'URL', 'Başarılı']
    
    # Başlık satırını formatla
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        cell.alignment = Alignment(horizontal='center')
    
    # Verileri ekle
    for row, log in enumerate(logs, 2):
        ws.cell(row=row, column=1, value=log.id)
        ws.cell(row=row, column=2, value=log.islem_tarihi.strftime('%d.%m.%Y %H:%M'))
        ws.cell(row=row, column=3, value=log.kullanici_adi)
        ws.cell(row=row, column=4, value=log.kullanici_rol)
        ws.cell(row=row, column=5, value=log.islem_tipi)
        ws.cell(row=row, column=6, value=log.tablo_adi)
        ws.cell(row=row, column=7, value=log.kayit_id)
        ws.cell(row=row, column=8, value=log.degisiklik_ozeti or '')
        ws.cell(row=row, column=9, value=log.ip_adresi or '')
        ws.cell(row=row, column=10, value=log.url or '')
        ws.cell(row=row, column=11, value='Evet' if log.basarili else 'Hayır')
    
    # Sütun genişliklerini ayarla
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 20
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 20
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 50
    ws.column_dimensions['I'].width = 15
    ws.column_dimensions['J'].width = 40
    ws.column_dimensions['K'].width = 10
    
    # Excel dosyasını kaydet
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    filename = f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Audit export işlemini logla
    from utils.audit import audit_export
    audit_export('audit_logs', f'Excel export: {len(logs)} kayıt')
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


# ============================================================================
# SİSTEM SIFIRLAMA - ÖZEL ŞİFRE İLE KORUMALI
# ============================================================================

RESET_PASSWORD = "518518Erkan!"  # Özel sistem sıfırlama şifresi

@app.route('/resetsystem', methods=['GET', 'POST'])
@csrf.exempt  # CSRF korumasını kaldır (kendi validasyonumuz var)
def reset_system():
    """Sistem sıfırlama sayfası - Özel şifre ile korumalı"""
    
    if request.method == 'GET':
        # Şifre giriş sayfasını göster
        return render_template('reset_system.html', show_stats=False)
    
    # POST işlemi
    action = request.form.get('action')
    reset_password = request.form.get('reset_password', '')
    
    # Şifre kontrolü
    if reset_password != RESET_PASSWORD:
        flash('❌ Hatalı sistem sıfırlama şifresi!', 'error')
        return render_template('reset_system.html', show_stats=False)
    
    # İstatistikleri göster
    if action == 'check':
        try:
            stats = {
                'kullanici_sayisi': Kullanici.query.count(),
                'otel_sayisi': Otel.query.count(),
                'kat_sayisi': Kat.query.count(),
                'oda_sayisi': Oda.query.count(),
                'urun_grubu_sayisi': UrunGrup.query.count(),
                'urun_sayisi': Urun.query.count(),
                'stok_hareket_sayisi': StokHareket.query.count(),
                'zimmet_sayisi': PersonelZimmet.query.count(),
                'zimmet_detay_sayisi': PersonelZimmetDetay.query.count(),
                'minibar_islem_sayisi': MinibarIslem.query.count(),
                'minibar_detay_sayisi': MinibarIslemDetay.query.count(),
                'log_sayisi': SistemLog.query.count(),
                'hata_sayisi': HataLog.query.count(),
                'audit_sayisi': db.session.execute(db.text("SELECT COUNT(*) FROM audit_logs")).scalar() or 0
            }
            
            return render_template('reset_system.html', 
                                 show_stats=True, 
                                 stats=stats,
                                 password=reset_password)
        
        except Exception as e:
            flash(f'❌ İstatistikler alınırken hata: {str(e)}', 'error')
            return render_template('reset_system.html', show_stats=False)
    
    # Sistem sıfırlama işlemi
    elif action == 'reset':
        # Onay checkbox kontrolü
        if not request.form.get('confirm_reset'):
            flash('❌ Sıfırlama onayı verilmedi!', 'error')
            return redirect(url_for('reset_system'))
        
        try:
            # Tüm tabloları temizle (sıralama önemli - foreign key kısıtları)
            print("\n" + "="*60)
            print("🔴 SİSTEM SIFIRLAMA BAŞLADI")
            print("="*60)
            
            # 1. MinibarIslemDetay (foreign key: minibar_islemleri)
            count = db.session.execute(db.text("DELETE FROM minibar_islem_detay")).rowcount
            print(f"✓ MinibarIslemDetay silindi: {count} kayıt")
            
            # 2. MinibarIslem
            count = db.session.execute(db.text("DELETE FROM minibar_islemleri")).rowcount
            print(f"✓ MinibarIslem silindi: {count} kayıt")
            
            # 3. PersonelZimmetDetay (foreign key: personel_zimmet)
            count = db.session.execute(db.text("DELETE FROM personel_zimmet_detay")).rowcount
            print(f"✓ PersonelZimmetDetay silindi: {count} kayıt")
            
            # 4. PersonelZimmet
            count = db.session.execute(db.text("DELETE FROM personel_zimmet")).rowcount
            print(f"✓ PersonelZimmet silindi: {count} kayıt")
            
            # 5. StokHareket
            count = db.session.execute(db.text("DELETE FROM stok_hareketleri")).rowcount
            print(f"✓ StokHareket silindi: {count} kayıt")
            
            # 6. Urun (foreign key: urun_gruplari)
            count = db.session.execute(db.text("DELETE FROM urunler")).rowcount
            print(f"✓ Urun silindi: {count} kayıt")
            
            # 7. UrunGrup
            count = db.session.execute(db.text("DELETE FROM urun_gruplari")).rowcount
            print(f"✓ UrunGrup silindi: {count} kayıt")
            
            # 8. Oda (foreign key: katlar)
            count = db.session.execute(db.text("DELETE FROM odalar")).rowcount
            print(f"✓ Oda silindi: {count} kayıt")
            
            # 9. Kat (foreign key: oteller)
            count = db.session.execute(db.text("DELETE FROM katlar")).rowcount
            print(f"✓ Kat silindi: {count} kayıt")
            
            # 10. LOG VE AUDIT TABLOLARI ÖNCE SİLİNMELİ (foreign key: kullanicilar)
            # SistemLog
            count = db.session.execute(db.text("DELETE FROM sistem_loglari")).rowcount
            print(f"✓ SistemLog silindi: {count} kayıt")
            
            # HataLog
            count = db.session.execute(db.text("DELETE FROM hata_loglari")).rowcount
            print(f"✓ HataLog silindi: {count} kayıt")
            
            # AuditLog (kullanıcılara foreign key var!)
            count = db.session.execute(db.text("DELETE FROM audit_logs")).rowcount
            print(f"✓ AuditLog silindi: {count} kayıt")
            
            # 11. OtomatikRapor (kullanıcılara foreign key olabilir)
            count = db.session.execute(db.text("DELETE FROM otomatik_raporlar")).rowcount
            print(f"✓ OtomatikRapor silindi: {count} kayıt")
            
            # 12. ARTIK KULLANICILARı SİLEBİLİRİZ
            # Kullanici (foreign key: oteller)
            count = db.session.execute(db.text("DELETE FROM kullanicilar")).rowcount
            print(f"✓ Kullanici silindi: {count} kayıt")
            
            # 13. Otel
            count = db.session.execute(db.text("DELETE FROM oteller")).rowcount
            print(f"✓ Otel silindi: {count} kayıt")
            
            # 14. SistemAyar - setup_tamamlandi'yi sıfırla
            db.session.execute(db.text("DELETE FROM sistem_ayarlari WHERE anahtar = 'setup_tamamlandi'"))
            print(f"✓ Setup ayarı sıfırlandı")
            
            # Auto-increment değerlerini sıfırla
            tables = [
                'minibar_islem_detay', 'minibar_islemleri',
                'personel_zimmet_detay', 'personel_zimmet',
                'stok_hareketleri', 'urunler', 'urun_gruplari',
                'odalar', 'katlar', 'kullanicilar', 'oteller',
                'sistem_loglari', 'hata_loglari', 'audit_logs', 'otomatik_raporlar'
            ]
            
            for table in tables:
                try:
                    db.session.execute(db.text(f"ALTER TABLE {table} AUTO_INCREMENT = 1"))
                except:
                    pass  # Bazı tablolar primary key olmayabilir
            
            print(f"✓ Auto-increment değerleri sıfırlandı")
            
            # Commit
            db.session.commit()
            
            print("="*60)
            print("✅ SİSTEM SIFIRLAMA TAMAMLANDI")
            print("="*60)
            print()
            
            # Session'ı temizle
            session.clear()
            
            # Başarı mesajı ve yönlendirme
            flash('✅ Sistem başarıyla sıfırlandı! Tüm veriler silindi ve sistem ilk kurulum aşamasına döndü.', 'success')
            flash('🔄 Şimdi ilk kurulum sayfasına yönlendiriliyorsunuz...', 'info')
            
            return redirect(url_for('setup'))
        
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ HATA: {str(e)}\n")
            flash(f'❌ Sistem sıfırlanırken hata oluştu: {str(e)}', 'error')
            return redirect(url_for('reset_system'))
    
    # Geçersiz action
    flash('❌ Geçersiz işlem!', 'error')
    return redirect(url_for('reset_system'))


# Hata yakalama
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(400)
def bad_request(error):
    """CSRF ve diğer 400 hatalarını yakala"""
    if request.is_json:
        return jsonify({'success': False, 'error': str(error)}), 400
    return render_template('errors/404.html'), 400

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
