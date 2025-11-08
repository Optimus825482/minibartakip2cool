from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy import Numeric, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PG_ENUM
import enum
import os

db = SQLAlchemy()

# Database type detection
DB_TYPE = os.getenv('DB_TYPE', 'mysql')
IS_POSTGRESQL = DB_TYPE == 'postgresql'

# Use JSONB for PostgreSQL, Text for MySQL
JSONType = JSONB if IS_POSTGRESQL else Text

# DateTime helper
def get_datetime_column():
    """Get DateTime column based on database type"""
    return db.DateTime(timezone=IS_POSTGRESQL)

def get_datetime_default():
    """Get datetime default based on database type"""
    return lambda: datetime.now(timezone.utc) if IS_POSTGRESQL else datetime.utcnow

# PostgreSQL ENUM Types
# Bu enum'lar hem MySQL hem PostgreSQL ile uyumlu çalışır
class KullaniciRol(str, enum.Enum):
    SISTEM_YONETICISI = 'sistem_yoneticisi'
    ADMIN = 'admin'
    DEPO_SORUMLUSU = 'depo_sorumlusu'
    KAT_SORUMLUSU = 'kat_sorumlusu'

class HareketTipi(str, enum.Enum):
    GIRIS = 'giris'
    CIKIS = 'cikis'
    DEVIR = 'devir'
    SAYIM = 'sayim'

class ZimmetDurum(str, enum.Enum):
    AKTIF = 'aktif'
    TAMAMLANDI = 'tamamlandi'
    IPTAL = 'iptal'

class MinibarIslemTipi(str, enum.Enum):
    ILK_DOLUM = 'ilk_dolum'
    KONTROL = 'kontrol'
    DOLDURMA = 'doldurma'
    EK_DOLUM = 'ek_dolum'

class AuditIslemTipi(str, enum.Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    LOGIN = 'login'
    LOGOUT = 'logout'
    VIEW = 'view'
    EXPORT = 'export'
    IMPORT = 'import'

class RaporTipi(str, enum.Enum):
    GUNLUK_STOK = 'gunluk_stok'
    STOK_KONTROLU = 'stok_kontrolu'
    ZIMMET_OZETI = 'zimmet_ozeti'
    MINIBAR_TUKETIM = 'minibar_tuketim'

class DolumTalebiDurum(str, enum.Enum):
    BEKLEMEDE = 'beklemede'
    TAMAMLANDI = 'tamamlandi'
    IPTAL = 'iptal'

class QROkutmaTipi(str, enum.Enum):
    KAT_SORUMLUSU = 'kat_sorumlusu'
    MISAFIR = 'misafir'

class Otel(db.Model):
    """Otel bilgileri tablosu"""
    __tablename__ = 'oteller'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ad = db.Column(db.String(200), nullable=False)
    adres = db.Column(db.Text)
    telefon = db.Column(db.String(20))
    email = db.Column(db.String(100))
    vergi_no = db.Column(db.String(50))
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    aktif = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    katlar = db.relationship('Kat', backref='otel', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Otel {self.ad}>'


class Kullanici(db.Model):
    """Kullanıcılar tablosu - Tüm roller"""
    __tablename__ = 'kullanicilar'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(255), nullable=False)
    ad = db.Column(db.String(100), nullable=False)
    soyad = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefon = db.Column(db.String(20))
    rol = db.Column(db.Enum('sistem_yoneticisi', 'admin', 'depo_sorumlusu', 'kat_sorumlusu', name='kullanici_rol'), nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    son_giris = db.Column(db.DateTime(timezone=True))
    
    # İlişkiler
    zimmet_kayitlari = db.relationship('PersonelZimmet', 
                                       foreign_keys='PersonelZimmet.personel_id',
                                       backref='personel', 
                                       lazy=True)
    teslim_ettigi_zimmetler = db.relationship('PersonelZimmet',
                                              foreign_keys='PersonelZimmet.teslim_eden_id',
                                              lazy=True)
    minibar_islemleri = db.relationship('MinibarIslem', backref='personel', lazy=True)
    
    def sifre_belirle(self, sifre):
        """Şifreyi hashleyerek kaydet"""
        self.sifre_hash = generate_password_hash(sifre)
    
    def sifre_kontrol(self, sifre):
        """Şifre kontrolü"""
        return check_password_hash(self.sifre_hash, sifre)
    
    def __repr__(self):
        return f'<Kullanici {self.kullanici_adi} ({self.rol})>'


class Kat(db.Model):
    """Katlar tablosu"""
    __tablename__ = 'katlar'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    otel_id = db.Column(db.Integer, db.ForeignKey('oteller.id'), nullable=False)
    kat_adi = db.Column(db.String(50), nullable=False)
    kat_no = db.Column(db.Integer, nullable=False)
    aciklama = db.Column(db.Text)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    odalar = db.relationship('Oda', backref='kat', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Kat {self.kat_adi}>'


class Oda(db.Model):
    """Odalar tablosu"""
    __tablename__ = 'odalar'
    __table_args__ = (
        db.Index('idx_qr_token', 'qr_kod_token'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kat_id = db.Column(db.Integer, db.ForeignKey('katlar.id'), nullable=False)
    oda_no = db.Column(db.String(20), nullable=False, unique=True)
    oda_tipi = db.Column(db.String(50))
    kapasite = db.Column(db.Integer)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # QR Kod Alanları
    qr_kod_token = db.Column(db.String(64), unique=True, nullable=True)
    qr_kod_gorsel = db.Column(db.Text, nullable=True)  # Base64 encoded PNG
    qr_kod_olusturma_tarihi = db.Column(db.DateTime(timezone=True), nullable=True)
    misafir_mesaji = db.Column(db.String(500), nullable=True)
    
    # İlişkiler
    minibar_islemleri = db.relationship('MinibarIslem', backref='oda', lazy=True)
    dolum_talepleri = db.relationship('MinibarDolumTalebi', backref='oda', lazy=True)
    qr_okutma_loglari = db.relationship('QRKodOkutmaLog', backref='oda', lazy=True)
    
    def __repr__(self):
        return f'<Oda {self.oda_no}>'


class UrunGrup(db.Model):
    """Ürün grupları tablosu"""
    __tablename__ = 'urun_gruplari'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grup_adi = db.Column(db.String(100), nullable=False, unique=True)
    aciklama = db.Column(db.Text)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    urunler = db.relationship('Urun', backref='grup', lazy=True)
    
    def __repr__(self):
        return f'<UrunGrup {self.grup_adi}>'


class Urun(db.Model):
    """Ürünler tablosu"""
    __tablename__ = 'urunler'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grup_id = db.Column(db.Integer, db.ForeignKey('urun_gruplari.id'), nullable=False)
    urun_adi = db.Column(db.String(200), nullable=False)
    barkod = db.Column(db.String(50), unique=True)
    birim = db.Column(db.String(20), default='Adet')
    kritik_stok_seviyesi = db.Column(db.Integer, default=10)
    aktif = db.Column(db.Boolean, default=True)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # İlişkiler
    stok_hareketleri = db.relationship('StokHareket', backref='urun', lazy=True)
    zimmet_detaylari = db.relationship('PersonelZimmetDetay', backref='urun', lazy=True)
    minibar_detaylari = db.relationship('MinibarIslemDetay', backref='urun', lazy=True)
    
    def __repr__(self):
        return f'<Urun {self.urun_adi}>'


class StokHareket(db.Model):
    """Stok hareketleri tablosu - Depo giriş/çıkış"""
    __tablename__ = 'stok_hareketleri'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    hareket_tipi = db.Column(db.Enum('giris', 'cikis', 'devir', 'sayim', name='hareket_tipi'), nullable=False)
    miktar = db.Column(db.Integer, nullable=False)
    aciklama = db.Column(db.Text)
    islem_yapan_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    islem_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # İlişki
    islem_yapan = db.relationship('Kullanici', foreign_keys=[islem_yapan_id])
    
    def __repr__(self):
        return f'<StokHareket {self.hareket_tipi} - {self.miktar}>'


class PersonelZimmet(db.Model):
    """Personel zimmet tablosu - Kat sorumlusu zimmet başlık"""
    __tablename__ = 'personel_zimmet'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    personel_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    zimmet_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    iade_tarihi = db.Column(db.DateTime(timezone=True), nullable=True)
    teslim_eden_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    durum = db.Column(db.Enum('aktif', 'tamamlandi', 'iptal', name='zimmet_durum'), default='aktif')
    aciklama = db.Column(db.Text)
    
    # İlişkiler
    teslim_eden = db.relationship('Kullanici', 
                                  foreign_keys=[teslim_eden_id],
                                  overlaps="teslim_ettigi_zimmetler")
    detaylar = db.relationship('PersonelZimmetDetay', backref='zimmet', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PersonelZimmet #{self.id}>'


class PersonelZimmetDetay(db.Model):
    """Personel zimmet detay tablosu"""
    __tablename__ = 'personel_zimmet_detay'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zimmet_id = db.Column(db.Integer, db.ForeignKey('personel_zimmet.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    miktar = db.Column(db.Integer, nullable=False)
    kullanilan_miktar = db.Column(db.Integer, default=0)
    kalan_miktar = db.Column(db.Integer)
    iade_edilen_miktar = db.Column(db.Integer, default=0)
    kritik_stok_seviyesi = db.Column(db.Integer, nullable=True)  # Kat sorumlusu tarafından belirlenen kritik seviye
    
    def __repr__(self):
        return f'<PersonelZimmetDetay #{self.id}>'


class MinibarIslem(db.Model):
    """Minibar işlemleri tablosu - Kontrol ve tüketim başlık"""
    __tablename__ = 'minibar_islemleri'
    __table_args__ = (
        db.Index('idx_oda_tarih', 'oda_id', 'islem_tarihi'),
        db.Index('idx_personel_tarih', 'personel_id', 'islem_tarihi'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    personel_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=False)
    islem_tipi = db.Column(db.Enum('ilk_dolum', 'kontrol', 'doldurma', 'ek_dolum', name='minibar_islem_tipi'), nullable=False)
    islem_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    aciklama = db.Column(db.Text)
    
    # İlişkiler
    detaylar = db.relationship('MinibarIslemDetay', backref='islem', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MinibarIslem #{self.id} - {self.islem_tipi}>'


class MinibarIslemDetay(db.Model):
    """Minibar işlem detay tablosu"""
    __tablename__ = 'minibar_islem_detay'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    islem_id = db.Column(db.Integer, db.ForeignKey('minibar_islemleri.id'), nullable=False)
    urun_id = db.Column(db.Integer, db.ForeignKey('urunler.id'), nullable=False)
    baslangic_stok = db.Column(db.Integer, default=0)
    bitis_stok = db.Column(db.Integer, default=0)
    tuketim = db.Column(db.Integer, default=0)
    eklenen_miktar = db.Column(db.Integer, default=0)
    zimmet_detay_id = db.Column(db.Integer, db.ForeignKey('personel_zimmet_detay.id'), nullable=True)  # Hangi zimmetten kullanıldığı
    
    # İlişkiler
    zimmet_detay = db.relationship('PersonelZimmetDetay', foreign_keys=[zimmet_detay_id])
    
    def __repr__(self):
        return f'<MinibarIslemDetay #{self.id}>'


class SistemAyar(db.Model):
    """Sistem ayarları tablosu"""
    __tablename__ = 'sistem_ayarlari'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    anahtar = db.Column(db.String(100), unique=True, nullable=False)
    deger = db.Column(db.Text)
    aciklama = db.Column(db.Text)
    
    def __repr__(self):
        return f'<SistemAyar {self.anahtar}>'


class SistemLog(db.Model):
    """Sistem log kayıtları tablosu"""
    __tablename__ = 'sistem_loglari'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    islem_tipi = db.Column(db.String(50), nullable=False)  # giris, cikis, ekleme, guncelleme, silme, goruntuleme
    modul = db.Column(db.String(100), nullable=False)  # urun, stok, zimmet, oda, kat vb.
    islem_detay = db.Column(JSONB, nullable=True)  # İşlem detayları (JSONB formatında - PostgreSQL)
    ip_adresi = db.Column(db.String(50))
    tarayici = db.Column(db.String(200))
    islem_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # İlişki
    kullanici = db.relationship('Kullanici', foreign_keys=[kullanici_id], backref='log_kayitlari')
    
    def __repr__(self):
        return f'<SistemLog {self.islem_tipi} - {self.modul}>'


class HataLog(db.Model):
    """Hata log kayıtları tablosu"""
    __tablename__ = 'hata_loglari'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    hata_tipi = db.Column(db.String(100), nullable=False)  # Exception tipi
    hata_mesaji = db.Column(db.Text, nullable=False)  # Hata mesajı
    hata_detay = db.Column(db.Text)  # Stack trace ve detaylar
    modul = db.Column(db.String(100))  # Hangi modülde oluştu
    url = db.Column(db.String(500))  # Hangi URL'de oluştu
    method = db.Column(db.String(10))  # HTTP method (GET, POST, etc.)
    ip_adresi = db.Column(db.String(50))
    tarayici = db.Column(db.String(200))
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    cozuldu = db.Column(db.Boolean, default=False)  # Hata çözüldü mü?
    cozum_notu = db.Column(db.Text)  # Çözüm notu
    
    # İlişki
    kullanici = db.relationship('Kullanici', foreign_keys=[kullanici_id], backref='hata_kayitlari')
    
    def __repr__(self):
        return f'<HataLog {self.hata_tipi} - {self.olusturma_tarihi}>'


class AuditLog(db.Model):
    """Audit Trail - Denetim İzi Kayıtları"""
    __tablename__ = 'audit_logs'
    __table_args__ = (
        db.Index('idx_tablo_kayit', 'tablo_adi', 'kayit_id'),
        db.Index('idx_kullanici_tarih', 'kullanici_id', 'islem_tarihi'),
        db.Index('idx_tarih', 'islem_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Kullanıcı ve İşlem Bilgileri
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)  # Nullable - sistem/script işlemleri için
    kullanici_adi = db.Column(db.String(100), nullable=False)  # Denormalize - kullanıcı silinse bile kayıt kalır
    kullanici_rol = db.Column(db.String(50), nullable=False)
    
    # İşlem Detayları
    islem_tipi = db.Column(
        db.Enum('create', 'update', 'delete', 'login', 'logout', 'view', 'export', 'import', name='audit_islem_tipi'), 
        nullable=False
    )
    tablo_adi = db.Column(db.String(100), nullable=False)  # Hangi tablo etkilendi
    kayit_id = db.Column(db.Integer)  # Etkilenen kayıt ID'si
    
    # Veri Değişiklikleri
    eski_deger = db.Column(JSONB, nullable=True)  # JSONB formatında eski değerler (PostgreSQL)
    yeni_deger = db.Column(JSONB, nullable=True)  # JSONB formatında yeni değerler (PostgreSQL)
    degisiklik_ozeti = db.Column(db.Text)  # Okunabilir değişiklik özeti
    
    # HTTP İstek Bilgileri
    http_method = db.Column(db.String(10))  # GET, POST, PUT, DELETE
    url = db.Column(db.String(500))  # İstek URL'i
    endpoint = db.Column(db.String(200))  # Flask endpoint adı
    
    # Ağ Bilgileri
    ip_adresi = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))  # Tarayıcı bilgisi
    
    # Zaman Bilgisi
    islem_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Ek Bilgiler
    aciklama = db.Column(db.Text)  # Ek açıklama
    basarili = db.Column(db.Boolean, default=True)  # İşlem başarılı mı?
    hata_mesaji = db.Column(db.Text)  # Hata varsa mesajı
    
    # İlişki
    kullanici = db.relationship('Kullanici', foreign_keys=[kullanici_id], backref='audit_kayitlari')
    
    def __repr__(self):
        return f'<AuditLog {self.islem_tipi} - {self.tablo_adi} #{self.kayit_id}>'


class OtomatikRapor(db.Model):
    """Otomatik Oluşturulan Raporlar (Günlük Stok Raporu vb.)"""
    __tablename__ = 'otomatik_raporlar'
    __table_args__ = (
        db.Index('idx_rapor_tipi_tarih', 'rapor_tipi', 'olusturma_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Rapor Bilgileri
    rapor_tipi = db.Column(
        db.Enum('gunluk_stok', 'stok_kontrolu', 'zimmet_ozeti', 'minibar_tuketim', name='rapor_tipi'),
        nullable=False
    )
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text)
    
    # Rapor İçeriği (JSONB formatında - PostgreSQL)
    rapor_verisi = db.Column(JSONB, nullable=False)  # JSONB
    
    # Özet İstatistikler (Hızlı erişim için)
    toplam_urun = db.Column(db.Integer)
    kritik_stok_sayisi = db.Column(db.Integer)
    toplam_deger = db.Column(Numeric(10, 2))
    
    # Ek Bilgiler
    olusturan = db.Column(db.String(100), default='Sistem')  # Sistem veya kullanıcı adı
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f'<OtomatikRapor {self.rapor_tipi} - {self.olusturma_tarihi}>'



class MinibarDolumTalebi(db.Model):
    """Misafir dolum talepleri tablosu"""
    __tablename__ = 'minibar_dolum_talepleri'
    __table_args__ = (
        db.Index('idx_oda_durum', 'oda_id', 'durum'),
        db.Index('idx_talep_tarihi', 'talep_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    talep_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    durum = db.Column(db.Enum('beklemede', 'tamamlandi', 'iptal', name='dolum_talep_durum'), default='beklemede', nullable=False)
    tamamlanma_tarihi = db.Column(db.DateTime(timezone=True), nullable=True)
    notlar = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<MinibarDolumTalebi #{self.id} - Oda {self.oda_id} - {self.durum}>'


class QRKodOkutmaLog(db.Model):
    """QR kod okutma geçmişi tablosu"""
    __tablename__ = 'qr_kod_okutma_loglari'
    __table_args__ = (
        db.Index('idx_oda_tarih', 'oda_id', 'okutma_tarihi'),
        db.Index('idx_kullanici_tarih', 'kullanici_id', 'okutma_tarihi'),
        db.Index('idx_okutma_tipi', 'okutma_tipi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    okutma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    okutma_tipi = db.Column(db.Enum('kat_sorumlusu', 'misafir', name='qr_okutma_tipi'), nullable=False)
    ip_adresi = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    basarili = db.Column(db.Boolean, default=True, nullable=False)
    hata_mesaji = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    kullanici = db.relationship('Kullanici', backref='qr_okutma_loglari')
    
    def __repr__(self):
        return f'<QRKodOkutmaLog #{self.id} - {self.okutma_tipi} - {self.okutma_tarihi}>'
