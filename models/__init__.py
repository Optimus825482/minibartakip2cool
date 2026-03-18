"""
Modüler Model Yapısı

Bu paket, models.py dosyasını mantıksal modüllere böler.
Geriye dönük uyumluluk için tüm modeller buradan export edilir.

NOT: Şu an için models.py ana kaynak olarak kullanılıyor.
Modüler dosyalar (otel.py, kullanici.py vb.) gelecekte taşınacak.
"""

# Ana models.py'den tüm modelleri import et
from ._models import (
    db, get_kktc_now, KKTC_TZ, JSONType,
    KullaniciRol, HareketTipi, ZimmetDurum, MinibarIslemTipi,
    AuditIslemTipi, RaporTipi, DolumTalebiDurum, QROkutmaTipi,
    GorevDurum, GorevTipi,
    MLMetricType, MLAlertType, MLAlertSeverity,
    Otel, Kat, Oda, OdaTipi, Setup, SetupIcerik, oda_tipi_setup,
    Kullanici, KullaniciOtel,
    UrunGrup, Urun, StokHareket, StokFifoKayit, StokFifoKullanim,
    AnaDepoTedarik, AnaDepoTedarikDetay, OtelZimmetStok, UrunStok,
    PersonelZimmet, PersonelZimmetDetay, ZimmetSablon, ZimmetSablonDetay, PersonelZimmetKullanim,
    MinibarIslem, MinibarIslemDetay, MinibarDolumTalebi,
    GunlukGorev, GorevDetay, GorevDurumLog, YuklemeGorev,
    DNDKontrol, OdaDNDKayit, OdaDNDKontrol, OdaKontrolKaydi,
    MisafirKayit, DosyaYukleme, QRKodOkutmaLog,
    SistemLog, HataLog, AuditLog, SistemAyar, OtomatikRapor,
    EmailAyarlari, EmailLog, DolulukUyariLog,
    KatSorumlusuSiparisTalebi, KatSorumlusuSiparisTalepDetay,
    MLModel, MLMetric, MLAlert, MLTrainingLog, MLFeature, MLPerformanceLog,
    QueryLog, BackupHistory, ConfigAudit, BackgroundJob
)

# Tüm modelleri __all__ ile export et
__all__ = [
    # Base
    'db', 'get_kktc_now', 'KKTC_TZ', 'JSONType',
    # Enum'lar
    'KullaniciRol', 'HareketTipi', 'ZimmetDurum', 'MinibarIslemTipi',
    'AuditIslemTipi', 'RaporTipi', 'DolumTalebiDurum', 'QROkutmaTipi',
    'GorevDurum', 'GorevTipi',
    'MLMetricType', 'MLAlertType', 'MLAlertSeverity',
    # Otel
    'Otel', 'Kat', 'Oda', 'OdaTipi', 'Setup', 'SetupIcerik', 'oda_tipi_setup',
    # Kullanıcı
    'Kullanici', 'KullaniciOtel',
    # Stok
    'UrunGrup', 'Urun', 'StokHareket', 'StokFifoKayit', 'StokFifoKullanim',
    'AnaDepoTedarik', 'AnaDepoTedarikDetay', 'OtelZimmetStok', 'UrunStok',
    # Zimmet
    'PersonelZimmet', 'PersonelZimmetDetay', 'ZimmetSablon', 'ZimmetSablonDetay', 'PersonelZimmetKullanim',
    # Minibar
    'MinibarIslem', 'MinibarIslemDetay', 'MinibarDolumTalebi',
    # Görev
    'GunlukGorev', 'GorevDetay', 'GorevDurumLog', 'YuklemeGorev',
    'DNDKontrol', 'OdaDNDKayit', 'OdaDNDKontrol', 'OdaKontrolKaydi',
    # Doluluk
    'MisafirKayit', 'DosyaYukleme', 'QRKodOkutmaLog',
    # Log
    'SistemLog', 'HataLog', 'AuditLog', 'SistemAyar', 'OtomatikRapor',
    # Email
    'EmailAyarlari', 'EmailLog', 'DolulukUyariLog',
    # Kat Sorumlusu Sipariş (aktif)
    'KatSorumlusuSiparisTalebi', 'KatSorumlusuSiparisTalepDetay',
    # ML
    'MLModel', 'MLMetric', 'MLAlert', 'MLTrainingLog', 'MLFeature', 'MLPerformanceLog',
    # Developer/Sistem
    'QueryLog', 'BackupHistory', 'ConfigAudit', 'BackgroundJob',
]
