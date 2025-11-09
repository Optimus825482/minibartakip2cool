"""
Data Collector - ML Anomaly Detection System
Veri toplama servisi: Stok, tüketim ve dolum metriklerini toplar
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """Veri toplama servisi"""
    
    def __init__(self, db):
        self.db = db
    
    def collect_stok_metrics(self):
        """
        Tüm ürünler için stok seviyelerini topla
        Returns: Toplanan metrik sayısı
        """
        try:
            from models import Urun, StokHareket, MLMetric
            
            # Aktif ürünleri al
            urunler = Urun.query.filter_by(aktif=True).all()
            
            collected_count = 0
            timestamp = datetime.now(timezone.utc)
            
            for urun in urunler:
                # Stok seviyesini hesapla
                giris_toplam = self.db.session.query(
                    func.coalesce(func.sum(StokHareket.miktar), 0)
                ).filter(
                    StokHareket.urun_id == urun.id,
                    StokHareket.hareket_tipi == 'giris'
                ).scalar()
                
                cikis_toplam = self.db.session.query(
                    func.coalesce(func.sum(StokHareket.miktar), 0)
                ).filter(
                    StokHareket.urun_id == urun.id,
                    StokHareket.hareket_tipi == 'cikis'
                ).scalar()
                
                mevcut_stok = giris_toplam - cikis_toplam
                
                # Metrik kaydı oluştur
                metric = MLMetric(
                    metric_type='stok_seviye',
                    entity_type='urun',
                    entity_id=urun.id,
                    metric_value=float(mevcut_stok),
                    timestamp=timestamp,
                    extra_data={
                        'urun_adi': urun.urun_adi,
                        'kritik_seviye': urun.kritik_stok_seviyesi,
                        'grup': urun.grup.grup_adi if urun.grup else None
                    }
                )
                self.db.session.add(metric)
                collected_count += 1
            
            self.db.session.commit()
            logger.info(f"✅ Stok metrikleri toplandı: {collected_count} ürün")
            return collected_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Stok metrik toplama hatası: {str(e)}")
            return 0
    
    def collect_tuketim_metrics(self):
        """
        Oda bazlı tüketim verilerini topla (son 24 saat)
        Returns: Toplanan metrik sayısı
        """
        try:
            from models import Oda, MinibarIslem, MinibarIslemDetay, MLMetric
            
            # Son 24 saatlik verileri al
            son_24_saat = datetime.now(timezone.utc) - timedelta(hours=24)
            
            # Aktif odaları al
            odalar = Oda.query.filter_by(aktif=True).all()
            
            collected_count = 0
            timestamp = datetime.now(timezone.utc)
            
            for oda in odalar:
                # Son 24 saatteki tüketimi hesapla
                tuketim_toplam = self.db.session.query(
                    func.coalesce(func.sum(MinibarIslemDetay.tuketim), 0)
                ).join(
                    MinibarIslem
                ).filter(
                    MinibarIslem.oda_id == oda.id,
                    MinibarIslem.islem_tarihi >= son_24_saat,
                    MinibarIslem.islem_tipi.in_(['kontrol', 'doldurma'])
                ).scalar()
                
                # Sadece tüketim varsa kaydet
                if tuketim_toplam > 0:
                    metric = MLMetric(
                        metric_type='tuketim_miktar',
                        entity_type='oda',
                        entity_id=oda.id,
                        metric_value=float(tuketim_toplam),
                        timestamp=timestamp,
                        extra_data={
                            'oda_no': oda.oda_no,
                            'oda_tipi': oda.oda_tipi,
                            'kat': oda.kat.kat_adi if oda.kat else None
                        }
                    )
                    self.db.session.add(metric)
                    collected_count += 1
            
            self.db.session.commit()
            logger.info(f"✅ Tüketim metrikleri toplandı: {collected_count} oda")
            return collected_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Tüketim metrik toplama hatası: {str(e)}")
            return 0
    
    def collect_dolum_metrics(self):
        """
        Dolum süresi metriklerini topla (son 7 gün)
        Returns: Toplanan metrik sayısı
        """
        try:
            from models import Kullanici, MinibarIslem, MLMetric
            
            # Son 7 günlük verileri al
            son_7_gun = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Kat sorumluları
            kat_sorumlulari = Kullanici.query.filter_by(
                rol='kat_sorumlusu',
                aktif=True
            ).all()
            
            collected_count = 0
            timestamp = datetime.now(timezone.utc)
            
            for personel in kat_sorumlulari:
                # Son 7 gündeki dolum işlemlerini al
                dolum_islemleri = MinibarIslem.query.filter(
                    MinibarIslem.personel_id == personel.id,
                    MinibarIslem.islem_tarihi >= son_7_gun,
                    MinibarIslem.islem_tipi.in_(['ilk_dolum', 'doldurma', 'yeniden_dolum'])
                ).order_by(MinibarIslem.islem_tarihi).all()
                
                if len(dolum_islemleri) >= 2:
                    # Ortalama dolum süresini hesapla (işlemler arası süre)
                    sureler = []
                    for i in range(1, len(dolum_islemleri)):
                        onceki = dolum_islemleri[i-1].islem_tarihi
                        sonraki = dolum_islemleri[i].islem_tarihi
                        sure_dakika = (sonraki - onceki).total_seconds() / 60
                        sureler.append(sure_dakika)
                    
                    if sureler:
                        ortalama_sure = sum(sureler) / len(sureler)
                        
                        metric = MLMetric(
                            metric_type='dolum_sure',
                            entity_type='kat_sorumlusu',
                            entity_id=personel.id,
                            metric_value=float(ortalama_sure),
                            timestamp=timestamp,
                            extra_data={
                                'personel_adi': f"{personel.ad} {personel.soyad}",
                                'islem_sayisi': len(dolum_islemleri),
                                'otel': personel.otel.ad if personel.otel else None
                            }
                        )
                        self.db.session.add(metric)
                        collected_count += 1
            
            self.db.session.commit()
            logger.info(f"✅ Dolum süresi metrikleri toplandı: {collected_count} personel")
            return collected_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Dolum süresi metrik toplama hatası: {str(e)}")
            return 0
    
    def collect_all_metrics(self):
        """
        Tüm metrikleri topla
        Returns: Toplam toplanan metrik sayısı
        """
        try:
            logger.info("🔄 Veri toplama başladı...")
            
            stok_count = self.collect_stok_metrics()
            tuketim_count = self.collect_tuketim_metrics()
            dolum_count = self.collect_dolum_metrics()
            
            total_count = stok_count + tuketim_count + dolum_count
            
            logger.info(f"✅ Toplam {total_count} metrik toplandı")
            logger.info(f"   - Stok: {stok_count}")
            logger.info(f"   - Tüketim: {tuketim_count}")
            logger.info(f"   - Dolum: {dolum_count}")
            
            return total_count
            
        except Exception as e:
            logger.error(f"❌ Veri toplama hatası: {str(e)}")
            return 0
    
    def cleanup_old_metrics(self, days=90):
        """
        Eski metrikleri temizle (90 günden eski)
        Args:
            days: Kaç günden eski veriler silinecek
        Returns: Silinen kayıt sayısı
        """
        try:
            from models import MLMetric
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            deleted_count = MLMetric.query.filter(
                MLMetric.timestamp < cutoff_date
            ).delete()
            
            self.db.session.commit()
            
            if deleted_count > 0:
                logger.info(f"🗑️  {deleted_count} eski metrik silindi ({days} günden eski)")
            
            return deleted_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Metrik temizleme hatası: {str(e)}")
            return 0
