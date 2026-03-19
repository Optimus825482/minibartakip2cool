"""Performans optimizasyonu - Eksik index'ler ekleme

Revision ID: 20260319_performance_indexes
Revises: None
Create Date: 2026-03-19

Sorun: Ort. yanıt 2.7s, P95 16s — CPU %2.4 boşta.
Kök neden: Sık sorgulanan kolonlarda composite index eksikliği.
"""
from alembic import op
from sqlalchemy import text


revision = '20260319_performance_indexes'
down_revision = None  # Manuel olarak son migration'a bağla
branch_labels = None
depends_on = None


def upgrade():
    # Raw SQL ile index oluştur — IF NOT EXISTS ile güvenli
    indexes = [
        # MisafirKayit - son çıkış sorguları (boş oda detayı)
        "CREATE INDEX IF NOT EXISTS idx_misafir_oda_cikis_desc ON misafir_kayitlari (oda_id, cikis_tarihi DESC)",
        
        # MisafirKayit - giris/cikis aralık sorguları (doluluk kontrolü)
        "CREATE INDEX IF NOT EXISTS idx_misafir_oda_giris_cikis ON misafir_kayitlari (oda_id, giris_tarihi, cikis_tarihi)",
        
        # GorevDetay - misafir_kayit_id NOT NULL partial index (executive dashboard)
        "CREATE INDEX IF NOT EXISTS idx_gorev_detay_misafir_not_null ON gorev_detaylari (gorev_id) WHERE misafir_kayit_id IS NOT NULL",
        
        # AuditLog - islem_tipi + tarih composite (aktivite sorguları)
        "CREATE INDEX IF NOT EXISTS idx_audit_islem_tipi_tarih ON audit_logs (islem_tipi, islem_tarihi)",
        
        # MinibarIslemDetay - islem_id + tuketim (SUM sorguları)
        "CREATE INDEX IF NOT EXISTS idx_minibar_detay_islem_tuketim ON minibar_islem_detay (islem_id, tuketim)",
        
        # OdaKontrolKaydi - sadece tarih (tarih aralığı filtresi)
        "CREATE INDEX IF NOT EXISTS idx_oda_kontrol_tarih ON oda_kontrol_kayitlari (kontrol_tarihi)",
        
        # GunlukGorev - tarih + durum composite (dashboard sorguları)
        "CREATE INDEX IF NOT EXISTS idx_gunluk_gorev_tarih_durum ON gunluk_gorevler (gorev_tarihi, durum)",
        
        # GunlukGorev - otel + tarih (otel bazlı dashboard sorguları)
        "CREATE INDEX IF NOT EXISTS idx_gunluk_gorev_otel_tarih ON gunluk_gorevler (otel_id, gorev_tarihi)",
        
        # MinibarIslem - personel + tarih (kat sorumlusu dashboard)
        "CREATE INDEX IF NOT EXISTS idx_minibar_islem_personel_tarih ON minibar_islemleri (personel_id, islem_tarihi DESC)",
        
        # MinibarIslem - personel + islem_tipi (islem tipi dağılımı)
        "CREATE INDEX IF NOT EXISTS idx_minibar_islem_personel_tipi ON minibar_islemleri (personel_id, islem_tipi)",
        
        # PersonelZimmet - personel + durum (aktif zimmet sorguları)
        "CREATE INDEX IF NOT EXISTS idx_personel_zimmet_personel_durum ON personel_zimmet (personel_id, durum)",
        
        # QueryLog - timestamp ve execution_time (cleanup + analiz)
        "CREATE INDEX IF NOT EXISTS idx_query_log_timestamp ON query_logs (timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_query_log_exec_time ON query_logs (execution_time DESC)",
        
        # OdaDNDKayit - tarih + durum (DND sorguları)
        "CREATE INDEX IF NOT EXISTS idx_oda_dnd_tarih_durum ON oda_dnd_kayitlari (kayit_tarihi, durum)",
        
        # DNDKontrol - gorev_detay_id (batch DND lookup)
        "CREATE INDEX IF NOT EXISTS idx_dnd_kontrol_gorev_detay ON dnd_kontroller (gorev_detay_id)",
    ]
    
    for sql in indexes:
        op.execute(text(sql))


def downgrade():
    drops = [
        "DROP INDEX IF EXISTS idx_dnd_kontrol_gorev_detay",
        "DROP INDEX IF EXISTS idx_oda_dnd_tarih_durum",
        "DROP INDEX IF EXISTS idx_query_log_exec_time",
        "DROP INDEX IF EXISTS idx_query_log_timestamp",
        "DROP INDEX IF EXISTS idx_personel_zimmet_personel_durum",
        "DROP INDEX IF EXISTS idx_minibar_islem_personel_tipi",
        "DROP INDEX IF EXISTS idx_minibar_islem_personel_tarih",
        "DROP INDEX IF EXISTS idx_gunluk_gorev_otel_tarih",
        "DROP INDEX IF EXISTS idx_gunluk_gorev_tarih_durum",
        "DROP INDEX IF EXISTS idx_oda_kontrol_tarih",
        "DROP INDEX IF EXISTS idx_minibar_detay_islem_tuketim",
        "DROP INDEX IF EXISTS idx_audit_islem_tipi_tarih",
        "DROP INDEX IF EXISTS idx_gorev_detay_misafir_not_null",
        "DROP INDEX IF EXISTS idx_misafir_oda_giris_cikis",
        "DROP INDEX IF EXISTS idx_misafir_oda_cikis_desc",
    ]
    
    for sql in drops:
        op.execute(text(sql))
