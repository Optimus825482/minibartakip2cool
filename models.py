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
    YENIDEN_DOLUM = 'yeniden_dolum'
    EKSIK_TAMAMLAMA = 'eksik_tamamlama'
    SAYIM = 'sayim'
    DUZELTME = 'duzeltme'

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
    logo = db.Column(db.Text, nullable=True)  # Base64 encoded logo
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    aktif = db.Column(db.Boolean, default=True)
    
    # İlişkiler
    katlar = db.relationship('Kat', backref='otel', lazy=True, cascade='all, delete-orphan')
    kullanici_atamalari = db.relationship('KullaniciOtel', backref='otel', lazy=True, cascade='all, delete-orphan')
    
    def get_depo_sorumlu_sayisi(self):
        """Bu otele atanan depo sorumlusu sayısı"""
        try:
            from models import KullaniciOtel, Kullanici
            return KullaniciOtel.query.join(Kullanici).filter(
                KullaniciOtel.otel_id == self.id,
                Kullanici.rol == 'depo_sorumlusu'
            ).count()
        except Exception as e:
            return 0
    
    def get_kat_sorumlu_sayisi(self):
        """Bu otele atanan kat sorumlusu sayısı"""
        try:
            from models import Kullanici
            return Kullanici.query.filter(
                Kullanici.otel_id == self.id,
                Kullanici.rol == 'kat_sorumlusu'
            ).count()
        except Exception as e:
            return 0
    
    def __repr__(self):
        return f'<Otel {self.ad}>'


class KullaniciOtel(db.Model):
    """Kullanıcı-Otel ilişki tablosu (Many-to-Many) - Depo sorumluları için"""
    __tablename__ = 'kullanici_otel'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id', ondelete='CASCADE'), nullable=False)
    otel_id = db.Column(db.Integer, db.ForeignKey('oteller.id', ondelete='CASCADE'), nullable=False)
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # NOT: 'otel' ilişkisi Otel modelinde backref ile tanımlı (satır 93)
    # Burada tekrar tanımlamaya gerek yok
    
    # Unique constraint - Aynı kullanıcı aynı otele birden fazla kez atanamaz
    __table_args__ = (
        db.UniqueConstraint('kullanici_id', 'otel_id', name='uq_kullanici_otel'),
        db.Index('idx_kullanici_otel', 'kullanici_id', 'otel_id'),
    )
    
    def __repr__(self):
        return f'<KullaniciOtel kullanici_id={self.kullanici_id} otel_id={self.otel_id}>'


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
    
    # YENİ: Kat sorumlusu için tek otel ilişkisi
    otel_id = db.Column(db.Integer, db.ForeignKey('oteller.id', ondelete='SET NULL'), nullable=True)
    
    # YENİ: Kat sorumlusunun bağlı olduğu depo sorumlusu
    depo_sorumlusu_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id', ondelete='SET NULL'), nullable=True)
    
    # İlişkiler
    zimmet_kayitlari = db.relationship('PersonelZimmet', 
                                       foreign_keys='PersonelZimmet.personel_id',
                                       backref='personel', 
                                       lazy=True)
    teslim_ettigi_zimmetler = db.relationship('PersonelZimmet',
                                              foreign_keys='PersonelZimmet.teslim_eden_id',
                                              lazy=True)
    minibar_islemleri = db.relationship('MinibarIslem', backref='personel', lazy=True)
    
    # YENİ: Otel ilişkileri
    otel = db.relationship('Otel', foreign_keys=[otel_id], backref='kat_sorumlu_kullanicilar')
    atanan_oteller = db.relationship('KullaniciOtel', backref='kullanici', lazy=True, cascade='all, delete-orphan')
    
    # YENİ: Depo sorumlusu ilişkisi
    depo_sorumlusu = db.relationship('Kullanici', remote_side=[id], foreign_keys=[depo_sorumlusu_id], backref='bagli_kat_sorumlu')
    
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
    oda_tipi = db.Column(db.String(100))  # Artık 100 karakter (uzun oda tipi isimleri için)
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
    hareket_tipi = db.Column(db.Enum('giris', 'cikis', 'transfer', 'devir', 'sayim', 'fire', name='hareket_tipi'), nullable=False)
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
    durum = db.Column(db.Enum('aktif', 'iade_edildi', 'iptal', name='zimmet_durum'), default='aktif')
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
    islem_tipi = db.Column(db.Enum('ilk_dolum', 'yeniden_dolum', 'eksik_tamamlama', 'sayim', 'duzeltme', 'kontrol', 'doldurma', 'ek_dolum', name='minibar_islem_tipi'), nullable=False)
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
        db.Enum('login', 'logout', 'create', 'update', 'delete', 'view', 'export', 'import', 'backup', 'restore', name='audit_islem_tipi'), 
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
        db.Enum('gunluk', 'haftalik', 'aylik', name='rapor_tipi'),
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
    durum = db.Column(db.Enum('beklemede', 'onaylandi', 'reddedildi', 'tamamlandi', 'iptal', name='dolum_talep_durum'), default='beklemede', nullable=False)
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
    okutma_tipi = db.Column(db.Enum('misafir_okutma', 'personel_kontrol', 'sistem_kontrol', name='qr_okutma_tipi'), nullable=False)
    ip_adresi = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    basarili = db.Column(db.Boolean, default=True, nullable=False)
    hata_mesaji = db.Column(db.Text, nullable=True)
    
    # İlişkiler
    kullanici = db.relationship('Kullanici', backref='qr_okutma_loglari')
    
    def __repr__(self):
        return f'<QRKodOkutmaLog #{self.id} - {self.okutma_tipi} - {self.okutma_tarihi}>'


class MisafirKayit(db.Model):
    """Misafir kayıt tablosu - Excel'den yüklenen oda doluluk verileri"""
    __tablename__ = 'misafir_kayitlari'
    __table_args__ = (
        db.Index('idx_misafir_islem_kodu', 'islem_kodu'),
        db.Index('idx_misafir_oda_tarih', 'oda_id', 'giris_tarihi', 'cikis_tarihi'),
        db.Index('idx_misafir_giris', 'giris_tarihi'),
        db.Index('idx_misafir_cikis', 'cikis_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    oda_id = db.Column(db.Integer, db.ForeignKey('odalar.id'), nullable=False)
    islem_kodu = db.Column(db.String(50), nullable=False, index=True)
    
    # Misafir Bilgileri (İsim kaydedilmez - sadece sayı)
    misafir_sayisi = db.Column(db.Integer, nullable=False)
    
    # Tarih ve Saat Bilgileri
    giris_tarihi = db.Column(db.Date, nullable=False, index=True)
    giris_saati = db.Column(db.Time, nullable=True)  # Sadece ARRIVALS için (Arr.Time)
    cikis_tarihi = db.Column(db.Date, nullable=False, index=True)
    
    # Kayıt Tipi (Otomatik algılanır: in_house veya arrival)
    kayit_tipi = db.Column(db.Enum('in_house', 'arrival', name='misafir_kayit_tipi'), nullable=False)
    
    # Sistem Bilgileri
    olusturma_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    olusturan_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    
    # İlişkiler
    oda = db.relationship('Oda', backref='misafir_kayitlari')
    olusturan = db.relationship('Kullanici', foreign_keys=[olusturan_id])
    
    def __repr__(self):
        return f'<MisafirKayit #{self.id} - Oda {self.oda_id} - {self.kayit_tipi}>'


class DosyaYukleme(db.Model):
    """Excel dosya yükleme kayıtları"""
    __tablename__ = 'dosya_yuklemeleri'
    __table_args__ = (
        db.Index('idx_dosya_islem_kodu', 'islem_kodu'),
        db.Index('idx_dosya_yukleme_tarihi', 'yukleme_tarihi'),
        db.Index('idx_dosya_silme_tarihi', 'silme_tarihi'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    islem_kodu = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Dosya Bilgileri
    dosya_adi = db.Column(db.String(255), nullable=False)
    dosya_yolu = db.Column(db.String(500), nullable=False)
    dosya_tipi = db.Column(db.Enum('in_house', 'arrivals', name='dosya_tipi'), nullable=False)  # Otomatik algılanır
    dosya_boyutu = db.Column(db.Integer)  # bytes
    
    # İşlem Bilgileri
    yukleme_tarihi = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    silme_tarihi = db.Column(db.DateTime(timezone=True), nullable=True)  # Otomatik silme için
    durum = db.Column(db.Enum('yuklendi', 'isleniyor', 'tamamlandi', 'hata', 'silindi', name='yukleme_durum'), default='yuklendi', nullable=False)
    
    # İstatistikler
    toplam_satir = db.Column(db.Integer, default=0)
    basarili_satir = db.Column(db.Integer, default=0)
    hatali_satir = db.Column(db.Integer, default=0)
    hata_detaylari = db.Column(JSONB, nullable=True)  # Hata mesajları (JSONB formatında)
    
    # Kullanıcı Bilgileri
    yuklenen_kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'))
    
    # İlişkiler
    yuklenen_kullanici = db.relationship('Kullanici', foreign_keys=[yuklenen_kullanici_id])
    
    def __repr__(self):
        return f'<DosyaYukleme #{self.id} - {self.islem_kodu} - {self.durum}>'


# ============================================
# MACHINE LEARNING MODELS
# ============================================

class MLMetricType(str, enum.Enum):
    """ML metrik tipleri"""
    STOK_SEVIYE = 'stok_seviye'
    TUKETIM_MIKTAR = 'tuketim_miktar'
    DOLUM_SURE = 'dolum_sure'
    STOK_BITIS_TAHMINI = 'stok_bitis_tahmini'

class MLAlertType(str, enum.Enum):
    """ML uyarı tipleri"""
    STOK_ANOMALI = 'stok_anomali'
    TUKETIM_ANOMALI = 'tuketim_anomali'
    DOLUM_GECIKME = 'dolum_gecikme'
    STOK_BITIS_UYARI = 'stok_bitis_uyari'

class MLAlertSeverity(str, enum.Enum):
    """ML uyarı önem seviyeleri"""
    DUSUK = 'dusuk'
    ORTA = 'orta'
    YUKSEK = 'yuksek'
    KRITIK = 'kritik'


class MLMetric(db.Model):
    """ML metrik kayıtları - zaman serisi verileri"""
    __tablename__ = 'ml_metrics'
    __table_args__ = (
        db.Index('idx_ml_metrics_type_time', 'metric_type', 'timestamp'),
        db.Index('idx_ml_metrics_entity', 'entity_type', 'entity_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    metric_type = db.Column(
        db.Enum('stok_seviye', 'tuketim_miktar', 'dolum_sure', 'stok_bitis_tahmini', name='ml_metric_type'),
        nullable=False
    )
    entity_type = db.Column(db.String(50), nullable=False)  # 'urun', 'oda', 'kat_sorumlusu'
    entity_id = db.Column(db.Integer, nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    extra_data = db.Column(JSONB, nullable=True)  # Ek bilgiler (JSONB formatında)
    
    def __repr__(self):
        return f'<MLMetric {self.metric_type} - {self.entity_type}#{self.entity_id}>'


class MLModel(db.Model):
    """Eğitilmiş ML modelleri"""
    __tablename__ = 'ml_models'
    __table_args__ = (
        db.Index('idx_ml_models_type_active', 'model_type', 'metric_type', 'is_active'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_type = db.Column(db.String(50), nullable=False)  # 'isolation_forest', 'z_score'
    metric_type = db.Column(db.String(50), nullable=False)
    model_data = db.Column(db.LargeBinary, nullable=False)  # Pickle serialized model
    parameters = db.Column(JSONB, nullable=True)  # Model parametreleri
    training_date = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # İlişkiler
    training_logs = db.relationship('MLTrainingLog', backref='model', lazy=True)
    
    def __repr__(self):
        return f'<MLModel {self.model_type} - {self.metric_type}>'


class MLAlert(db.Model):
    """ML uyarıları"""
    __tablename__ = 'ml_alerts'
    __table_args__ = (
        db.Index('idx_ml_alerts_severity_read', 'severity', 'is_read'),
        db.Index('idx_ml_alerts_created', 'created_at'),
        db.Index('idx_ml_alerts_entity', 'entity_type', 'entity_id'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    alert_type = db.Column(
        db.Enum('stok_anomali', 'tuketim_anomali', 'dolum_gecikme', 'stok_bitis_uyari', name='ml_alert_type'),
        nullable=False
    )
    severity = db.Column(
        db.Enum('dusuk', 'orta', 'yuksek', 'kritik', name='ml_alert_severity'),
        nullable=False
    )
    entity_type = db.Column(db.String(50), nullable=False)  # 'urun', 'oda', 'kat_sorumlusu'
    entity_id = db.Column(db.Integer, nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    expected_value = db.Column(db.Float)
    deviation_percent = db.Column(db.Float)
    message = db.Column(db.Text, nullable=False)
    suggested_action = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    is_false_positive = db.Column(db.Boolean, default=False, nullable=False)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('kullanicilar.id'), nullable=True)
    
    # İlişkiler
    resolved_by = db.relationship('Kullanici', foreign_keys=[resolved_by_id], backref='resolved_ml_alerts')
    
    def __repr__(self):
        return f'<MLAlert {self.alert_type} - {self.severity}>'


class MLTrainingLog(db.Model):
    """Model eğitim logları"""
    __tablename__ = 'ml_training_logs'
    __table_args__ = (
        db.Index('idx_ml_training_logs_date', 'training_start'),
    )
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=True)
    training_start = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    training_end = db.Column(db.DateTime(timezone=True), nullable=True)
    data_points = db.Column(db.Integer)
    success = db.Column(db.Boolean, default=False, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    metrics = db.Column(JSONB, nullable=True)  # Performans metrikleri (JSONB formatında)
    
    def __repr__(self):
        return f'<MLTrainingLog #{self.id} - {"Success" if self.success else "Failed"}>'
