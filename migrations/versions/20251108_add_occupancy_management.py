"""Add occupancy management tables

Revision ID: 20251108_occupancy
Revises: 20251108_083857
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251108_occupancy'
down_revision = '20251108_083857'
depends_on = None


def upgrade():
    """
    Otel doluluk yönetimi için gerekli tabloları oluştur
    """
    
    # 1. Enum tiplerini oluştur
    op.execute("CREATE TYPE misafir_kayit_tipi AS ENUM ('in_house', 'arrival')")
    op.execute("CREATE TYPE dosya_tipi AS ENUM ('in_house', 'arrivals')")
    op.execute("CREATE TYPE yukleme_durum AS ENUM ('yuklendi', 'isleniyor', 'tamamlandi', 'hata', 'silindi')")
    
    # 2. MisafirKayit tablosunu oluştur
    op.create_table(
        'misafir_kayitlari',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('oda_id', sa.Integer(), nullable=False),
        sa.Column('islem_kodu', sa.String(50), nullable=False),
        sa.Column('misafir_sayisi', sa.Integer(), nullable=False),
        sa.Column('giris_tarihi', sa.Date(), nullable=False),
        sa.Column('giris_saati', sa.Time(), nullable=True),
        sa.Column('cikis_tarihi', sa.Date(), nullable=False),
        sa.Column('kayit_tipi', postgresql.ENUM('in_house', 'arrival', name='misafir_kayit_tipi'), nullable=False),
        sa.Column('olusturma_tarihi', sa.DateTime(timezone=True), nullable=False),
        sa.Column('olusturan_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['oda_id'], ['odalar.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['olusturan_id'], ['kullanicilar.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # MisafirKayit indeksleri
    op.create_index('idx_misafir_islem_kodu', 'misafir_kayitlari', ['islem_kodu'])
    op.create_index('idx_misafir_oda_tarih', 'misafir_kayitlari', ['oda_id', 'giris_tarihi', 'cikis_tarihi'])
    op.create_index('idx_misafir_giris', 'misafir_kayitlari', ['giris_tarihi'])
    op.create_index('idx_misafir_cikis', 'misafir_kayitlari', ['cikis_tarihi'])
    
    # 3. DosyaYukleme tablosunu oluştur
    op.create_table(
        'dosya_yuklemeleri',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('islem_kodu', sa.String(50), nullable=False),
        sa.Column('dosya_adi', sa.String(255), nullable=False),
        sa.Column('dosya_yolu', sa.String(500), nullable=False),
        sa.Column('dosya_tipi', postgresql.ENUM('in_house', 'arrivals', name='dosya_tipi'), nullable=False),
        sa.Column('dosya_boyutu', sa.Integer(), nullable=True),
        sa.Column('yukleme_tarihi', sa.DateTime(timezone=True), nullable=False),
        sa.Column('silme_tarihi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('durum', postgresql.ENUM('yuklendi', 'isleniyor', 'tamamlandi', 'hata', 'silindi', name='yukleme_durum'), nullable=False),
        sa.Column('toplam_satir', sa.Integer(), default=0),
        sa.Column('basarili_satir', sa.Integer(), default=0),
        sa.Column('hatali_satir', sa.Integer(), default=0),
        sa.Column('hata_detaylari', postgresql.JSONB(), nullable=True),
        sa.Column('yuklenen_kullanici_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['yuklenen_kullanici_id'], ['kullanicilar.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('islem_kodu', name='uq_dosya_islem_kodu')
    )
    
    # DosyaYukleme indeksleri
    op.create_index('idx_dosya_islem_kodu', 'dosya_yuklemeleri', ['islem_kodu'])
    op.create_index('idx_dosya_yukleme_tarihi', 'dosya_yuklemeleri', ['yukleme_tarihi'])
    op.create_index('idx_dosya_silme_tarihi', 'dosya_yuklemeleri', ['silme_tarihi'])
    
    print("✅ Occupancy management tables created successfully!")


def downgrade():
    """
    Otel doluluk yönetimi tablolarını kaldır
    """
    # Tabloları sil
    op.drop_table('dosya_yuklemeleri')
    op.drop_table('misafir_kayitlari')
    
    # Enum tiplerini sil
    op.execute("DROP TYPE IF EXISTS yukleme_durum")
    op.execute("DROP TYPE IF EXISTS dosya_tipi")
    op.execute("DROP TYPE IF EXISTS misafir_kayit_tipi")
    
    print("✅ Occupancy management tables dropped successfully!")
