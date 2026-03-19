"""
Executive Dashboard Data Service
Üst yönetici paneli için veri toplama ve analiz servisi
"""

from datetime import datetime, timedelta, date
from sqlalchemy import func, desc, cast, Date, extract, case, and_, or_, text
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text as sql_text
from models import (
    db, Kullanici, Otel, Oda, Urun, UrunGrup, Kat,
    MinibarIslem, MinibarIslemDetay, StokHareket,
    PersonelZimmet, PersonelZimmetDetay,
    AuditLog, SistemLog, GunlukGorev, GorevDetay,
    OdaKontrolKaydi, MinibarIslemTipi, KullaniciRol,
    GorevDurum, GorevTipi, HareketTipi,
    OdaDNDKayit, OdaDNDKontrol
)
import logging
from utils.helpers import get_excluded_user_ids

logger = logging.getLogger(__name__)


def get_kktc_now():
    """KKTC saatini döndür"""
    from pytz import timezone
    kktc_tz = timezone('Europe/Nicosia')
    return datetime.now(kktc_tz).replace(tzinfo=None)


def get_date_range(period='today'):
    """Zaman periyoduna göre başlangıç-bitiş tarihi döndür"""
    now = get_kktc_now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if period == 'today':
        return today_start, now
    elif period == 'yesterday':
        yesterday = today_start - timedelta(days=1)
        return yesterday, today_start
    elif period == 'this_week':
        week_start = today_start - timedelta(days=now.weekday())
        return week_start, now
    elif period == 'last_week':
        this_week_start = today_start - timedelta(days=now.weekday())
        return this_week_start - timedelta(days=7), this_week_start
    elif period == 'this_month':
        month_start = today_start.replace(day=1)
        return month_start, now
    elif period == 'last_month':
        this_month_start = today_start.replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return last_month_start, this_month_start
    else:  # all
        return datetime(2020, 1, 1), now


class ExecutiveDashboardService:
    """Executive Dashboard veri servisi"""

    @staticmethod
    def get_kpi_summary(period='today', use_cache=True):
        """Ana KPI kartları için özet veriler - OPTIMIZED: 7 query → 3 query"""
        try:
            from utils.cache_manager import cache_manager
            cache_key = f'exec_dash_kpi_{period}'
            if cache_manager.enabled:
                cached = cache_manager.get(cache_key)
                if cached is not None:
                    return cached

            start_date, end_date = get_date_range(period)
            excluded = get_excluded_user_ids()

            # QUERY 1: Master data counts — basit ayrı count'lar (combined query unreliable)
            toplam_otel = Otel.query.filter_by(aktif=True).count()
            toplam_oda = Oda.query.filter_by(aktif=True).count()
            toplam_urun = Urun.query.filter_by(aktif=True).count()
            toplam_kullanici = Kullanici.query.filter_by(aktif=True).count()

            # QUERY 2: Period-based metrics combined (kontrol + tuketim + audit stats)
            kontrol = OdaKontrolKaydi.query.filter(
                OdaKontrolKaydi.kontrol_tarihi >= start_date,
                OdaKontrolKaydi.kontrol_tarihi < end_date,
                ~OdaKontrolKaydi.personel_id.in_(excluded)
            ).count()

            tuketim = db.session.query(
                func.coalesce(func.sum(MinibarIslemDetay.tuketim), 0)
            ).join(MinibarIslem).filter(
                MinibarIslem.islem_tarihi >= start_date,
                MinibarIslem.islem_tarihi < end_date,
                MinibarIslemDetay.tuketim > 0,
                ~MinibarIslem.personel_id.in_(excluded)
            ).scalar() or 0

            # Audit stats: aktif kullanıcı + toplam işlem in single query
            audit_stats = db.session.query(
                func.count(func.distinct(AuditLog.kullanici_id)).label('aktif_kullanici'),
                func.count(AuditLog.id).label('toplam_islem')
            ).filter(
                AuditLog.islem_tarihi >= start_date,
                AuditLog.islem_tarihi < end_date,
                ~AuditLog.kullanici_id.in_(excluded)
            ).first()
            aktif_kullanici = audit_stats.aktif_kullanici if audit_stats else 0
            toplam_islem = audit_stats.toplam_islem if audit_stats else 0

            # QUERY 3: Görev tamamlanma — TEK sorgu ile toplam ve tamamlanan
            gorev_stats = db.session.query(
                func.count(func.distinct(GunlukGorev.id)).label('toplam'),
                func.count(func.distinct(case(
                    (GunlukGorev.durum == GorevDurum.COMPLETED, GunlukGorev.id), else_=None
                ))).label('tamamlanan')
            ).join(
                GorevDetay, GorevDetay.gorev_id == GunlukGorev.id
            ).filter(
                GunlukGorev.gorev_tarihi >= start_date.date(),
                GunlukGorev.gorev_tarihi <= end_date.date(),
                GorevDetay.misafir_kayit_id.isnot(None)
            ).first()

            toplam_gorev = gorev_stats.toplam if gorev_stats else 0
            tamamlanan_gorev = gorev_stats.tamamlanan if gorev_stats else 0
            gorev_oran = round((tamamlanan_gorev / toplam_gorev * 100) if toplam_gorev > 0 else 0)

            result = {
                'toplam_otel': toplam_otel,
                'toplam_oda': toplam_oda,
                'toplam_urun': toplam_urun,
                'toplam_kullanici': toplam_kullanici,
                'bugun_kontrol': kontrol,
                'bugun_tuketim': int(tuketim),
                'gorev_oran': gorev_oran,
                'tamamlanan_gorev': tamamlanan_gorev,
                'toplam_gorev': toplam_gorev,
                'aktif_kullanici': aktif_kullanici,
                'bugun_islem': toplam_islem
            }

            # Cache'e kaydet
            if use_cache:
                from utils.executive_cache_service import ExecutiveCacheService
                ExecutiveCacheService.set_kpi_summary(result, period)

            return result
        except Exception as e:
            logger.error(f"KPI summary hatası: {e}")
            return {
                'toplam_otel': 0, 'toplam_oda': 0, 'toplam_urun': 0,
                'toplam_kullanici': 0, 'bugun_kontrol': 0, 'bugun_tuketim': 0,
                'gorev_oran': 0, 'tamamlanan_gorev': 0, 'toplam_gorev': 0,
                'aktif_kullanici': 0, 'bugun_islem': 0
            }

    @staticmethod
    def get_user_activity_stats():
        """Kullanıcı bazlı aktivite istatistikleri (executive dashboard - superadmin dahil)"""
        try:
            now = get_kktc_now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)

            users = Kullanici.query.filter(
                Kullanici.aktif == True
            ).options(joinedload(Kullanici.otel)).all()

            today_counts = dict(
                db.session.query(
                    AuditLog.kullanici_id,
                    func.count(AuditLog.id)
                ).filter(
                    AuditLog.islem_tarihi >= today_start
                ).group_by(AuditLog.kullanici_id).all()
            )

            weekly_counts = dict(
                db.session.query(
                    AuditLog.kullanici_id,
                    func.count(AuditLog.id)
                ).filter(
                    AuditLog.islem_tarihi >= week_start
                ).group_by(AuditLog.kullanici_id).all()
            )

            last_activities = dict(
                db.session.query(
                    AuditLog.kullanici_id,
                    func.max(AuditLog.islem_tarihi)
                ).group_by(AuditLog.kullanici_id).all()
            )

            user_stats = []
            for user in users:
                bugun_islem = today_counts.get(user.id, 0)
                haftalik_islem = weekly_counts.get(user.id, 0)
                son_aktivite = last_activities.get(user.id)
                otel_ad = user.otel.ad if user.otel else 'Genel'

                user_stats.append({
                    'id': user.id,
                    'ad_soyad': user.ad_soyad,
                    'rol': user.rol,
                    'otel': otel_ad,
                    'bugun_islem': bugun_islem,
                    'haftalik_islem': haftalik_islem,
                    'son_aktivite': son_aktivite.strftime('%d.%m.%Y %H:%M') if son_aktivite else '-',
                    'aktif_mi': bugun_islem > 0
                })

            user_stats.sort(key=lambda x: x['bugun_islem'], reverse=True)
            return user_stats
        except Exception as e:
            logger.error(f"User activity stats hatası: {e}")
            return []

    @staticmethod
    def get_hotel_comparison(period='today', use_cache=True):
        """
        Otel bazlı karşılaştırma verileri
        
        Optimizasyon:
        - 4 ayrı query yerine tek query ile tüm metrikler alınır
        - Görev query'si optimize edildi (distinct yerine subquery)
        - Redis cache ile 60 saniye TTL
        """
        # Cache kontrolü
        if use_cache:
            from utils.executive_cache_service import ExecutiveCacheService
            cached = ExecutiveCacheService.get_hotel_comparison(period)
            if cached:
                return cached
        
        try:
            start_date, end_date = get_date_range(period)
            oteller = Otel.query.filter_by(aktif=True).order_by(Otel.id).all()
            otel_ids = [o.id for o in oteller]
            excluded = get_excluded_user_ids()

            # Tek query ile tüm metrikleri al
            metrics = db.session.execute(sql_text("""
                WITH otel_metrics AS (
                    SELECT 
                        k.otel_id,
                        COUNT(DISTINCT o.id) as oda_sayisi,
                        COUNT(DISTINCT okk.id) as kontrol_sayisi,
                        COALESCE(SUM(mid.tuketim), 0) as toplam_tuketim
                    FROM katlar k
                    LEFT JOIN odalar o ON o.kat_id = k.id AND o.aktif = true
                    LEFT JOIN oda_kontrol_kaydi okk ON okk.oda_id = o.id 
                        AND okk.kontrol_tarihi >= :start_date 
                        AND okk.kontrol_tarihi < :end_date
                        AND okk.personel_id NOT IN :excluded
                    LEFT JOIN minibar_islem mi ON mi.oda_id = o.id 
                        AND mi.islem_tarihi >= :start_date 
                        AND mi.islem_tarihi < :end_date
                        AND mi.personel_id NOT IN :excluded
                    LEFT JOIN minibar_islem_detay mid ON mid.islem_id = mi.id AND mid.tuketim > 0
                    WHERE k.otel_id = ANY(:otel_ids)
                    GROUP BY k.otel_id
                )
                SELECT * FROM otel_metrics
            """), {
                'start_date': start_date,
                'end_date': end_date,
                'excluded': tuple(excluded) if excluded else (0,),
                'otel_ids': otel_ids
            }).fetchall()

            # Metrikleri dict'e çevir
            metrics_dict = {
                row[0]: {
                    'oda_sayisi': row[1],
                    'kontrol': row[2],
                    'tuketim': int(row[3])
                } for row in metrics
            }

            # Görev query'si (optimize edilmiş)
            gorevler = GunlukGorev.query.join(
                GorevDetay, GorevDetay.gorev_id == GunlukGorev.id
            ).filter(
                GunlukGorev.otel_id.in_(otel_ids),
                GunlukGorev.gorev_tarihi >= start_date.date(),
                GunlukGorev.gorev_tarihi <= end_date.date(),
                GorevDetay.misafir_kayit_id.isnot(None)
            ).distinct().all()

            gorev_by_otel = {}
            for g in gorevler:
                gorev_by_otel.setdefault(g.otel_id, []).append(g)

            hotel_data = []
            for otel in oteller:
                m = metrics_dict.get(otel.id, {'oda_sayisi': 0, 'kontrol': 0, 'tuketim': 0})
                otel_gorevler = gorev_by_otel.get(otel.id, [])
                toplam_g = len(otel_gorevler)
                tamamlanan_g = sum(1 for g in otel_gorevler if g.durum == GorevDurum.COMPLETED)

                hotel_data.append({
                    'id': otel.id,
                    'ad': otel.ad,
                    'oda_sayisi': m['oda_sayisi'],
                    'bugun_kontrol': m['kontrol'],
                    'bugun_tuketim': m['tuketim'],
                    'gorev_toplam': toplam_g,
                    'gorev_tamamlanan': tamamlanan_g,
                    'gorev_oran': round((tamamlanan_g / toplam_g * 100) if toplam_g > 0 else 0)
                })

            # Cache'e kaydet
            if use_cache:
                from utils.executive_cache_service import ExecutiveCacheService
                ExecutiveCacheService.set_hotel_comparison(hotel_data, period)

            return hotel_data
        except Exception as e:
            logger.error(f"Hotel comparison hatası: {e}")
            return []

    @staticmethod
    def get_consumption_trends(period='today', days=None):
        """Tüketim trend verileri (günlük)"""
        try:
            from utils.cache_manager import cache_manager
            cache_key = f'exec_dash_cons_trends_{period}_{days}'
            if cache_manager.enabled:
                cached = cache_manager.get(cache_key)
                if cached is not None:
                    return cached

            start_date, end_date = get_date_range(period)
            if days:
                now = get_kktc_now()
                start_date = now - timedelta(days=days)
                end_date = now

            delta = (end_date - start_date).days
            if delta < 1:
                delta = 1

            results = db.session.query(
                cast(MinibarIslem.islem_tarihi, Date).label('gun'),
                func.coalesce(func.sum(MinibarIslemDetay.tuketim), 0).label('toplam')
            ).join(MinibarIslem).filter(
                MinibarIslem.islem_tarihi >= start_date,
                MinibarIslem.islem_tarihi < end_date,
                MinibarIslemDetay.tuketim > 0,
                ~MinibarIslem.personel_id.in_(get_excluded_user_ids())
            ).group_by('gun').order_by('gun').all()

            result_dict = {r.gun: int(r.toplam) for r in results}

            labels = []
            values = []
            for i in range(delta):
                day = (start_date + timedelta(days=i)).date() if isinstance(start_date, datetime) else start_date + timedelta(days=i)
                labels.append(day.strftime('%d.%m'))
                values.append(result_dict.get(day, 0))

            result = {'labels': labels, 'values': values}

            if cache_manager.enabled:
                cache_manager.set(cache_key, result, 120)

            return result
        except Exception as e:
            logger.error(f"Consumption trends hatası: {e}")
            return {'labels': [], 'values': []}

    @staticmethod
    def get_top_consumed_products(limit=10, period='this_month'):
        """En çok tüketilen ürünler"""
        try:
            from utils.cache_manager import cache_manager
            cache_key = f'exec_dash_top_prods_{limit}_{period}'
            if cache_manager.enabled:
                cached = cache_manager.get(cache_key)
                if cached is not None:
                    return cached

            start_date, end_date = get_date_range(period)

            results = db.session.query(
                Urun.urun_adi,
                func.sum(MinibarIslemDetay.tuketim).label('toplam')
            ).join(MinibarIslemDetay, Urun.id == MinibarIslemDetay.urun_id
            ).join(MinibarIslem, MinibarIslemDetay.islem_id == MinibarIslem.id
            ).filter(
                MinibarIslem.islem_tarihi >= start_date,
                MinibarIslem.islem_tarihi < end_date,
                MinibarIslemDetay.tuketim > 0,
                ~MinibarIslem.personel_id.in_(get_excluded_user_ids())
            ).group_by(Urun.urun_adi
            ).order_by(desc('toplam')
            ).limit(limit).all()

            result = {
                'labels': [r[0] for r in results],
                'values': [int(r[1]) for r in results]
            }

            if cache_manager.enabled:
                cache_manager.set(cache_key, result, 120)

            return result
        except Exception as e:
            logger.error(f"Top consumed products hatası: {e}")
            return {'labels': [], 'values': []}

    @staticmethod
    def get_room_control_stats(period='today', days=None):
        """Oda kontrol istatistikleri (günlük)"""
        try:
            from utils.cache_manager import cache_manager
            cache_key = f'exec_dash_room_ctrl_{period}_{days}'
            if cache_manager.enabled:
                cached = cache_manager.get(cache_key)
                if cached is not None:
                    return cached

            start_date, end_date = get_date_range(period)
            if days:
                now = get_kktc_now()
                start_date = now - timedelta(days=days)
                end_date = now

            delta = (end_date - start_date).days
            if delta < 1:
                delta = 1

            results = db.session.query(
                cast(OdaKontrolKaydi.kontrol_tarihi, Date).label('gun'),
                func.count(OdaKontrolKaydi.id).label('sayi')
            ).filter(
                OdaKontrolKaydi.kontrol_tarihi >= start_date,
                OdaKontrolKaydi.kontrol_tarihi < end_date,
                ~OdaKontrolKaydi.personel_id.in_(get_excluded_user_ids())
            ).group_by('gun').order_by('gun').all()

            result_dict = {r.gun: r.sayi for r in results}

            labels = []
            values = []
            for i in range(delta):
                day = (start_date + timedelta(days=i)).date() if isinstance(start_date, datetime) else start_date + timedelta(days=i)
                labels.append(day.strftime('%d.%m'))
                values.append(result_dict.get(day, 0))

            result = {'labels': labels, 'values': values}

            if cache_manager.enabled:
                cache_manager.set(cache_key, result, 120)

            return result
        except Exception as e:
            logger.error(f"Room control stats hatası: {e}")
            return {'labels': [], 'values': []}

    @staticmethod
    def get_recent_activity(limit=50):
        """
        Son aktiviteler (real-time feed - executive dashboard, superadmin dahil)
        
        Optimizasyon:
        - AuditLog'dan sadece son N kayıt alınır (index: islem_tarihi DESC)
        - Kullanıcı bilgileri tek query'de joinedload ile yüklenir
        """
        try:
            from sqlalchemy.orm import joinedload
            from utils.executive_cache_service import ExecutiveCacheService
            cached = ExecutiveCacheService.get_activity_feed(limit)
            if cached is not None:
                return cached
            
            # AuditLog'dan son N kayıt + kullanıcı bilgisi (tek query)
            activities = AuditLog.query.options(
                joinedload(AuditLog.kullanici)
            ).order_by(
                desc(AuditLog.islem_tarihi)
            ).limit(limit).all()

            result = []
            for a in activities:
                kullanici = a.kullanici if hasattr(a, 'kullanici') and a.kullanici else None
                result.append({
                    'id': a.id,
                    'zaman': a.islem_tarihi.strftime('%H:%M:%S') if a.islem_tarihi else '',
                    'tarih': a.islem_tarihi.strftime('%d.%m.%Y') if a.islem_tarihi else '',
                    'kullanici': kullanici.ad_soyad if kullanici else 'Sistem',
                    'rol': kullanici.rol if kullanici else '-',
                    'islem': a.islem_tipi.value if hasattr(a.islem_tipi, 'value') else str(a.islem_tipi),
                    'detay': a.aciklama or '',
                    'tablo': a.tablo_adi or ''
                })

            ExecutiveCacheService.set_activity_feed(result, limit)
            return result
        except Exception as e:
            logger.error(f"Recent activity hatası: {e}")
            return []

    @staticmethod
    def get_task_completion_by_hotel(period='today'):
        """
        Otel bazlı görev tamamlanma oranları
        (sadece doluluk bilgisi yüklendikten sonra oluşturulan görevler)
        
        Optimizasyon:
        - Tek query ile tüm otel görev istatistikleri alınır
        """
        try:
            from utils.executive_cache_service import ExecutiveCacheService
            cached = ExecutiveCacheService.get_task_completion(period)
            if cached is not None:
                return cached

            start_date, end_date = get_date_range(period)
            oteller = Otel.query.filter_by(aktif=True).order_by(Otel.id).all()
            otel_ids = [o.id for o in oteller]

            # Tek query ile tüm otel görev istatistiklerini al
            stats = db.session.execute(sql_text("""
                SELECT 
                    gg.otel_id,
                    COUNT(DISTINCT gg.id) as toplam,
                    COUNT(DISTINCT CASE WHEN gg.durum = 'COMPLETED' THEN gg.id END) as tamamlanan
                FROM gunluk_gorevler gg
                INNER JOIN gorev_detaylari gd ON gd.gorev_id = gg.id
                WHERE gg.otel_id = ANY(:otel_ids)
                  AND gg.gorev_tarihi >= :start_date
                  AND gg.gorev_tarihi <= :end_date
                  AND gd.misafir_kayit_id IS NOT NULL
                GROUP BY gg.otel_id
            """), {
                'otel_ids': otel_ids,
                'start_date': start_date.date(),
                'end_date': end_date.date()
            }).fetchall()

            # Stats'ı dict'e çevir
            stats_dict = {row[0]: {'toplam': row[1], 'tamamlanan': row[2]} for row in stats}

            data = []
            for otel in oteller:
                s = stats_dict.get(otel.id, {'toplam': 0, 'tamamlanan': 0})
                toplam = s['toplam']
                tamamlanan = s['tamamlanan']
                oran = round((tamamlanan / toplam * 100) if toplam > 0 else 0)
                data.append({
                    'otel': otel.ad,
                    'toplam': toplam,
                    'tamamlanan': tamamlanan,
                    'oran': oran
                })

            ExecutiveCacheService.set_task_completion(data, period)
            return data
        except Exception as e:
            logger.error(f"Task completion by hotel hatası: {e}")
            return []

    @staticmethod
    def get_hourly_activity(period='today'):
        """Saatlik aktivite dağılımı"""
        try:
            start_date, end_date = get_date_range(period)

            results = db.session.query(
                extract('hour', AuditLog.islem_tarihi).label('saat'),
                func.count(AuditLog.id).label('sayi')
            ).filter(
                AuditLog.islem_tarihi >= start_date,
                AuditLog.islem_tarihi < end_date,
                ~AuditLog.kullanici_id.in_(get_excluded_user_ids())
            ).group_by('saat').order_by('saat').all()

            hours = {int(r.saat): r.sayi for r in results}
            labels = [f'{h:02d}:00' for h in range(24)]
            values = [hours.get(h, 0) for h in range(24)]

            return {'labels': labels, 'values': values}
        except Exception as e:
            logger.error(f"Hourly activity hatası: {e}")
            return {'labels': [], 'values': []}

    @staticmethod
    def get_weekly_summary():
        """Seçilen döneme göre dinamik özet kartları:
        - Görev Tamamlanma (tamamlanan/toplam)
        - Ort. Tüketim/İşlem (sadece tüketim kaydı olan işlemler)
        - Bugünkü DND Sayısı
        """
        try:
            from utils.cache_manager import cache_manager
            cache_key = 'exec_dash_weekly'
            if cache_manager.enabled:
                cached = cache_manager.get(cache_key)
                if cached is not None:
                    return cached

            now = get_kktc_now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            # --- Görev Tamamlanma (bugün, sadece misafir kayıtlı) ---
            gorevler = GunlukGorev.query.join(
                GorevDetay, GorevDetay.gorev_id == GunlukGorev.id
            ).filter(
                GunlukGorev.gorev_tarihi == today_start.date(),
                GorevDetay.misafir_kayit_id.isnot(None)
            ).distinct().all()
            toplam_gorev = len(gorevler)
            tamamlanan_gorev = sum(1 for g in gorevler if g.durum == GorevDurum.COMPLETED)

            # --- Ort. Tüketim/İşlem (sadece tüketim kaydı olan işlemler) ---
            # Tüketim kaydı olan işlem = MinibarIslem where en az 1 detayda tuketim > 0
            tuketim_islem_q = db.session.query(
                func.count(func.distinct(MinibarIslem.id)).label('islem_sayisi'),
                func.coalesce(func.sum(MinibarIslemDetay.tuketim), 0).label('toplam_tuketim')
            ).join(MinibarIslemDetay).filter(
                MinibarIslem.islem_tarihi >= today_start,
                MinibarIslem.islem_tarihi < today_end,
                MinibarIslemDetay.tuketim > 0,
                ~MinibarIslem.personel_id.in_(get_excluded_user_ids())
            ).first()

            tuketimli_islem_sayisi = tuketim_islem_q.islem_sayisi if tuketim_islem_q else 0
            toplam_tuketim = int(tuketim_islem_q.toplam_tuketim) if tuketim_islem_q else 0
            ort_tuketim_islem = round(toplam_tuketim / tuketimli_islem_sayisi, 2) if tuketimli_islem_sayisi > 0 else 0

            # --- Bugünkü DND Sayısı ---
            bugun_dnd = OdaDNDKayit.query.filter(
                OdaDNDKayit.kayit_tarihi == today_start.date(),
                OdaDNDKayit.durum == 'aktif'
            ).count()

            # Ayrıca GorevDetay'daki DND'ler (görev sistemi üzerinden)
            gorev_dnd = GorevDetay.query.join(GunlukGorev).filter(
                GunlukGorev.gorev_tarihi == today_start.date(),
                GorevDetay.durum == 'dnd_pending',
                GorevDetay.misafir_kayit_id.isnot(None)
            ).count()

            toplam_dnd = bugun_dnd + gorev_dnd

            result = {
                'gorev_tamamlanan': tamamlanan_gorev,
                'gorev_toplam': toplam_gorev,
                'ort_tuketim_islem': ort_tuketim_islem,
                'tuketimli_islem': tuketimli_islem_sayisi,
                'toplam_tuketim': toplam_tuketim,
                'bugun_dnd': toplam_dnd
            }

            if cache_manager.enabled:
                cache_manager.set(cache_key, result, 60)

            return result
        except Exception as e:
            logger.error(f"Weekly summary hatası: {e}")
            return {
                'gorev_tamamlanan': 0, 'gorev_toplam': 0,
                'ort_tuketim_islem': 0, 'tuketimli_islem': 0,
                'toplam_tuketim': 0, 'bugun_dnd': 0
            }


def invalidate_executive_dashboard_cache():
    """Executive dashboard cache'ini temizle"""
    from utils.cache_manager import cache_manager
    if cache_manager.enabled:
        for prefix in ['exec_dash_kpi', 'exec_dash_cons_trends', 'exec_dash_room_ctrl', 'exec_dash_top_prods', 'exec_dash_weekly']:
            cache_manager.invalidate(prefix)
