"""
Anomaly Detector - ML Anomaly Detection System
Anomali tespit motoru: Z-Score ve Isolation Forest algoritmaları
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy import func
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Anomali tespit motoru"""
    
    def __init__(self, db):
        self.db = db
    
    def calculate_severity(self, deviation_percent):
        """
        Sapma yüzdesine göre önem seviyesi belirle
        Args:
            deviation_percent: Sapma yüzdesi (mutlak değer)
        Returns: 'dusuk', 'orta', 'yuksek', 'kritik'
        """
        abs_deviation = abs(deviation_percent)
        
        if abs_deviation < 30:
            return 'dusuk'
        elif abs_deviation < 50:
            return 'orta'
        elif abs_deviation < 80:
            return 'yuksek'
        else:
            return 'kritik'
    
    def detect_with_zscore(self, values, threshold=3.0):
        """
        Z-Score metodu ile anomali tespiti
        Args:
            values: Değerler listesi
            threshold: Z-score eşik değeri (varsayılan 3.0 = %99.7)
        Returns: (is_anomaly, z_score, mean, std)
        """
        if len(values) < 3:
            return False, 0, 0, 0
        
        values_array = np.array(values)
        mean = np.mean(values_array)
        std = np.std(values_array)
        
        if std == 0:
            return False, 0, mean, 0
        
        current_value = values[-1]
        z_score = abs((current_value - mean) / std)
        
        is_anomaly = z_score > threshold
        
        return is_anomaly, z_score, mean, std
    
    def detect_stok_anomalies(self):
        """
        Stok seviyesi anomalilerini tespit et
        Returns: Oluşturulan alert sayısı
        """
        try:
            from models import MLMetric, MLAlert, Urun
            
            # Son 30 günlük stok metriklerini al
            son_30_gun = datetime.now(timezone.utc) - timedelta(days=30)
            
            # Aktif ürünleri al
            urunler = Urun.query.filter_by(aktif=True).all()
            
            alert_count = 0
            
            for urun in urunler:
                # Bu ürün için son 30 günlük metrikleri al
                metrikler = MLMetric.query.filter(
                    MLMetric.metric_type == 'stok_seviye',
                    MLMetric.entity_type == 'urun',
                    MLMetric.entity_id == urun.id,
                    MLMetric.timestamp >= son_30_gun
                ).order_by(MLMetric.timestamp).all()
                
                if len(metrikler) < 3:
                    continue
                
                values = [m.metric_value for m in metrikler]
                
                # Z-Score ile anomali tespiti
                is_anomaly, z_score, mean, std = self.detect_with_zscore(values)
                
                if is_anomaly:
                    current_value = values[-1]
                    deviation_percent = ((current_value - mean) / mean * 100) if mean > 0 else 0
                    severity = self.calculate_severity(deviation_percent)
                    
                    # Aynı ürün için son 1 saatte alert var mı kontrol et
                    son_1_saat = datetime.now(timezone.utc) - timedelta(hours=1)
                    existing_alert = MLAlert.query.filter(
                        MLAlert.alert_type == 'stok_anomali',
                        MLAlert.entity_type == 'urun',
                        MLAlert.entity_id == urun.id,
                        MLAlert.created_at >= son_1_saat,
                        MLAlert.is_false_positive == False
                    ).first()
                    
                    if not existing_alert:
                        # Mesaj oluştur
                        if current_value < mean:
                            message = f"{urun.urun_adi} stok seviyesi normalden %{abs(deviation_percent):.1f} düşük (Mevcut: {int(current_value)}, Beklenen: {int(mean)})"
                            suggested_action = f"Acil sipariş verin. Kritik seviye: {urun.kritik_stok_seviyesi}"
                        else:
                            message = f"{urun.urun_adi} stok seviyesi normalden %{abs(deviation_percent):.1f} yüksek (Mevcut: {int(current_value)}, Beklenen: {int(mean)})"
                            suggested_action = "Stok kontrolü yapın. Fazla stok olabilir."
                        
                        # Alert oluştur
                        alert = MLAlert(
                            alert_type='stok_anomali',
                            severity=severity,
                            entity_type='urun',
                            entity_id=urun.id,
                            metric_value=current_value,
                            expected_value=mean,
                            deviation_percent=deviation_percent,
                            message=message,
                            suggested_action=suggested_action
                        )
                        self.db.session.add(alert)
                        alert_count += 1
            
            self.db.session.commit()
            
            if alert_count > 0:
                logger.info(f"⚠️  {alert_count} stok anomalisi tespit edildi")
            
            return alert_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Stok anomali tespiti hatası: {str(e)}")
            return 0
    
    def detect_tuketim_anomalies(self):
        """
        Tüketim anomalilerini tespit et (oda bazlı)
        Returns: Oluşturulan alert sayısı
        """
        try:
            from models import MLMetric, MLAlert, Oda
            
            # Son 7 günlük tüketim metriklerini al
            son_7_gun = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Aktif odaları al
            odalar = Oda.query.filter_by(aktif=True).all()
            
            alert_count = 0
            
            for oda in odalar:
                # Bu oda için son 7 günlük metrikleri al
                metrikler = MLMetric.query.filter(
                    MLMetric.metric_type == 'tuketim_miktar',
                    MLMetric.entity_type == 'oda',
                    MLMetric.entity_id == oda.id,
                    MLMetric.timestamp >= son_7_gun
                ).order_by(MLMetric.timestamp).all()
                
                if len(metrikler) < 3:
                    continue
                
                values = [m.metric_value for m in metrikler]
                
                # Z-Score ile anomali tespiti (daha düşük threshold: 2.5)
                is_anomaly, z_score, mean, std = self.detect_with_zscore(values, threshold=2.5)
                
                if is_anomaly:
                    current_value = values[-1]
                    deviation_percent = ((current_value - mean) / mean * 100) if mean > 0 else 0
                    
                    # %40'tan fazla sapma varsa alert oluştur
                    if abs(deviation_percent) >= 40:
                        severity = self.calculate_severity(deviation_percent)
                        
                        # Aynı oda için son 6 saatte alert var mı kontrol et
                        son_6_saat = datetime.now(timezone.utc) - timedelta(hours=6)
                        existing_alert = MLAlert.query.filter(
                            MLAlert.alert_type == 'tuketim_anomali',
                            MLAlert.entity_type == 'oda',
                            MLAlert.entity_id == oda.id,
                            MLAlert.created_at >= son_6_saat,
                            MLAlert.is_false_positive == False
                        ).first()
                        
                        if not existing_alert:
                            # Mesaj oluştur
                            if current_value > mean:
                                message = f"Oda {oda.oda_no} tüketimi normalden %{abs(deviation_percent):.1f} yüksek (Günlük: {int(current_value)}, Ortalama: {int(mean)})"
                                suggested_action = "Minibar kontrolü yapın. Olağandışı tüketim var."
                            else:
                                message = f"Oda {oda.oda_no} tüketimi normalden %{abs(deviation_percent):.1f} düşük (Günlük: {int(current_value)}, Ortalama: {int(mean)})"
                                suggested_action = "Oda boş olabilir veya minibar kullanılmıyor."
                            
                            # Alert oluştur
                            alert = MLAlert(
                                alert_type='tuketim_anomali',
                                severity=severity,
                                entity_type='oda',
                                entity_id=oda.id,
                                metric_value=current_value,
                                expected_value=mean,
                                deviation_percent=deviation_percent,
                                message=message,
                                suggested_action=suggested_action
                            )
                            self.db.session.add(alert)
                            alert_count += 1
            
            self.db.session.commit()
            
            if alert_count > 0:
                logger.info(f"⚠️  {alert_count} tüketim anomalisi tespit edildi")
            
            return alert_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Tüketim anomali tespiti hatası: {str(e)}")
            return 0
    
    def detect_dolum_anomalies(self):
        """
        Dolum süresi anomalilerini tespit et
        Returns: Oluşturulan alert sayısı
        """
        try:
            from models import MLMetric, MLAlert, Kullanici
            
            # Son 7 günlük dolum metriklerini al
            son_7_gun = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Kat sorumluları
            kat_sorumlulari = Kullanici.query.filter_by(
                rol='kat_sorumlusu',
                aktif=True
            ).all()
            
            alert_count = 0
            
            for personel in kat_sorumlulari:
                # Bu personel için son 7 günlük metrikleri al
                metrikler = MLMetric.query.filter(
                    MLMetric.metric_type == 'dolum_sure',
                    MLMetric.entity_type == 'kat_sorumlusu',
                    MLMetric.entity_id == personel.id,
                    MLMetric.timestamp >= son_7_gun
                ).order_by(MLMetric.timestamp).all()
                
                if len(metrikler) < 3:
                    continue
                
                values = [m.metric_value for m in metrikler]
                
                # Z-Score ile anomali tespiti
                is_anomaly, z_score, mean, std = self.detect_with_zscore(values, threshold=2.0)
                
                if is_anomaly:
                    current_value = values[-1]
                    deviation_percent = ((current_value - mean) / mean * 100) if mean > 0 else 0
                    
                    # %50'den fazla uzun sürüyorsa alert oluştur
                    if deviation_percent >= 50:
                        severity = self.calculate_severity(deviation_percent)
                        
                        # Aynı personel için son 12 saatte alert var mı kontrol et
                        son_12_saat = datetime.now(timezone.utc) - timedelta(hours=12)
                        existing_alert = MLAlert.query.filter(
                            MLAlert.alert_type == 'dolum_gecikme',
                            MLAlert.entity_type == 'kat_sorumlusu',
                            MLAlert.entity_id == personel.id,
                            MLAlert.created_at >= son_12_saat,
                            MLAlert.is_false_positive == False
                        ).first()
                        
                        if not existing_alert:
                            # Mesaj oluştur
                            message = f"{personel.ad} {personel.soyad} dolum süresi normalden %{abs(deviation_percent):.1f} uzun (Mevcut: {int(current_value)} dk, Ortalama: {int(mean)} dk)"
                            suggested_action = "Personel ile görüşün. Operasyonel sorun olabilir."
                            
                            # Alert oluştur
                            alert = MLAlert(
                                alert_type='dolum_gecikme',
                                severity=severity,
                                entity_type='kat_sorumlusu',
                                entity_id=personel.id,
                                metric_value=current_value,
                                expected_value=mean,
                                deviation_percent=deviation_percent,
                                message=message,
                                suggested_action=suggested_action
                            )
                            self.db.session.add(alert)
                            alert_count += 1
            
            self.db.session.commit()
            
            if alert_count > 0:
                logger.info(f"⚠️  {alert_count} dolum süresi anomalisi tespit edildi")
            
            return alert_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Dolum süresi anomali tespiti hatası: {str(e)}")
            return 0
    
    def detect_all_anomalies(self):
        """
        Tüm anomali tiplerini tespit et
        Returns: Toplam oluşturulan alert sayısı
        """
        try:
            logger.info("🔍 Anomali tespiti başladı...")
            
            stok_count = self.detect_stok_anomalies()
            tuketim_count = self.detect_tuketim_anomalies()
            dolum_count = self.detect_dolum_anomalies()
            
            total_count = stok_count + tuketim_count + dolum_count
            
            if total_count > 0:
                logger.info(f"⚠️  Toplam {total_count} anomali tespit edildi")
                logger.info(f"   - Stok: {stok_count}")
                logger.info(f"   - Tüketim: {tuketim_count}")
                logger.info(f"   - Dolum: {dolum_count}")
            else:
                logger.info("✅ Anomali tespit edilmedi")
            
            return total_count
            
        except Exception as e:
            logger.error(f"❌ Anomali tespiti hatası: {str(e)}")
            return 0
