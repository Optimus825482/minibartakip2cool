"""
Alert Manager - ML Anomaly Detection System
Uyarı yönetim servisi: Alert oluşturma, okuma, yanlış pozitif işaretleme
"""

from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class AlertManager:
    """Uyarı yönetim servisi"""
    
    def __init__(self, db):
        self.db = db
    
    def create_alert(self, alert_data):
        """
        Yeni alert oluştur
        Args:
            alert_data: Alert bilgileri (dict)
        Returns: Alert ID veya None
        """
        try:
            from models import MLAlert
            
            alert = MLAlert(**alert_data)
            self.db.session.add(alert)
            self.db.session.commit()
            
            logger.info(f"✅ Alert oluşturuldu: {alert.alert_type} - {alert.severity}")
            
            return alert.id
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Alert oluşturma hatası: {str(e)}")
            return None
    
    def get_active_alerts(self, severity=None, limit=None):
        """
        Aktif alertleri getir
        Args:
            severity: Önem seviyesi filtresi (opsiyonel)
            limit: Maksimum kayıt sayısı (opsiyonel)
        Returns: Alert listesi
        """
        try:
            from models import MLAlert
            
            query = MLAlert.query.filter_by(is_read=False, is_false_positive=False)
            
            if severity:
                query = query.filter_by(severity=severity)
            
            query = query.order_by(
                MLAlert.severity.desc(),
                MLAlert.created_at.desc()
            )
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"❌ Alert getirme hatası: {str(e)}")
            return []
    
    def get_all_alerts(self, days=7, severity=None, alert_type=None):
        """
        Tüm alertleri getir (okunmuş dahil)
        Args:
            days: Son kaç günlük alertler
            severity: Önem seviyesi filtresi
            alert_type: Alert tipi filtresi
        Returns: Alert listesi
        """
        try:
            from models import MLAlert
            from datetime import timedelta
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            query = MLAlert.query.filter(
                MLAlert.created_at >= cutoff_date,
                MLAlert.is_false_positive == False
            )
            
            if severity:
                query = query.filter_by(severity=severity)
            
            if alert_type:
                query = query.filter_by(alert_type=alert_type)
            
            query = query.order_by(MLAlert.created_at.desc())
            
            return query.all()
            
        except Exception as e:
            logger.error(f"❌ Alert getirme hatası: {str(e)}")
            return []
    
    def mark_as_read(self, alert_id, user_id):
        """
        Alert'i okundu olarak işaretle
        Args:
            alert_id: Alert ID
            user_id: Okuyan kullanıcı ID
        Returns: Başarılı mı (bool)
        """
        try:
            from models import MLAlert
            
            alert = MLAlert.query.filter_by(id=alert_id).first()
            
            if not alert:
                logger.warning(f"Alert bulunamadı: {alert_id}")
                return False
            
            alert.is_read = True
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolved_by_id = user_id
            
            self.db.session.commit()
            
            logger.info(f"✅ Alert okundu: {alert_id}")
            
            return True
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Alert okuma hatası: {str(e)}")
            return False
    
    def mark_as_false_positive(self, alert_id, user_id):
        """
        Yanlış pozitif olarak işaretle
        Args:
            alert_id: Alert ID
            user_id: İşaretleyen kullanıcı ID
        Returns: Başarılı mı (bool)
        """
        try:
            from models import MLAlert
            
            alert = MLAlert.query.filter_by(id=alert_id).first()
            
            if not alert:
                logger.warning(f"Alert bulunamadı: {alert_id}")
                return False
            
            alert.is_false_positive = True
            alert.is_read = True
            alert.resolved_at = datetime.now(timezone.utc)
            alert.resolved_by_id = user_id
            
            self.db.session.commit()
            
            logger.info(f"⚠️  Alert yanlış pozitif: {alert_id}")
            
            return True
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Yanlış pozitif işaretleme hatası: {str(e)}")
            return False
    
    def get_alert_statistics(self, days=30):
        """
        Alert istatistiklerini getir
        Args:
            days: Son kaç günlük istatistikler
        Returns: İstatistik dict'i
        """
        try:
            from models import MLAlert
            from datetime import timedelta
            from sqlalchemy import func
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Toplam alert sayısı
            total_alerts = MLAlert.query.filter(
                MLAlert.created_at >= cutoff_date
            ).count()
            
            # Okunmamış alert sayısı
            unread_alerts = MLAlert.query.filter(
                MLAlert.created_at >= cutoff_date,
                MLAlert.is_read == False,
                MLAlert.is_false_positive == False
            ).count()
            
            # Yanlış pozitif sayısı
            false_positives = MLAlert.query.filter(
                MLAlert.created_at >= cutoff_date,
                MLAlert.is_false_positive == True
            ).count()
            
            # Severity dağılımı
            severity_dist = self.db.session.query(
                MLAlert.severity,
                func.count(MLAlert.id)
            ).filter(
                MLAlert.created_at >= cutoff_date,
                MLAlert.is_false_positive == False
            ).group_by(MLAlert.severity).all()
            
            # Alert tipi dağılımı
            type_dist = self.db.session.query(
                MLAlert.alert_type,
                func.count(MLAlert.id)
            ).filter(
                MLAlert.created_at >= cutoff_date,
                MLAlert.is_false_positive == False
            ).group_by(MLAlert.alert_type).all()
            
            return {
                'total_alerts': total_alerts,
                'unread_alerts': unread_alerts,
                'false_positives': false_positives,
                'false_positive_rate': (false_positives / total_alerts * 100) if total_alerts > 0 else 0,
                'severity_distribution': {s: c for s, c in severity_dist},
                'type_distribution': {t: c for t, c in type_dist}
            }
            
        except Exception as e:
            logger.error(f"❌ İstatistik hesaplama hatası: {str(e)}")
            return {}
    
    def send_notification(self, alert):
        """
        Bildirim gönder (email, SMS, push)
        Args:
            alert: MLAlert objesi
        Returns: Başarılı mı (bool)
        """
        # TODO: Email/SMS/Push notification implementasyonu
        # Şimdilik sadece log
        logger.info(f"📧 Bildirim gönderilecek: {alert.message}")
        return True
    
    def cleanup_old_alerts(self, days=90):
        """
        Eski alertleri temizle
        Args:
            days: Kaç günden eski alertler silinecek
        Returns: Silinen kayıt sayısı
        """
        try:
            from models import MLAlert
            from datetime import timedelta
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            deleted_count = MLAlert.query.filter(
                MLAlert.created_at < cutoff_date,
                MLAlert.is_read == True
            ).delete()
            
            self.db.session.commit()
            
            if deleted_count > 0:
                logger.info(f"🗑️  {deleted_count} eski alert silindi ({days} günden eski)")
            
            return deleted_count
            
        except Exception as e:
            self.db.session.rollback()
            logger.error(f"❌ Alert temizleme hatası: {str(e)}")
            return 0
