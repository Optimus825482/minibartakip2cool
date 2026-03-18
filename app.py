from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_wtf.csrf import CSRFProtect, CSRFError
from datetime import datetime, timedelta
import pytz

# KKTC Timezone (Kıbrıs - Europe/Nicosia)
KKTC_TZ = pytz.timezone('Europe/Nicosia')

def get_kktc_now():
    """Kıbrıs saat diliminde şu anki zamanı döndürür."""
    return datetime.now(KKTC_TZ)

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import inspect

# Logging ayarla - Hem console hem de dosyaya yaz
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()

# Flask uygulaması oluştur
app = Flask(__name__)

# Konfigürasyonu yükle
app.config.from_object('config.Config')

# Proxy arkasında çalışırken (Traefik/Nginx) doğru scheme ve IP algılama
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# CSRF Koruması Aktif
csrf = CSRFProtect(app)

# CSRF token'ı tüm template'lere ekle
@app.context_processor
def inject_csrf_token():
    """CSRF token'ı template'lere enjekte et"""
    from flask_wtf.csrf import generate_csrf
    # Hem fonksiyon hem de değişken olarak sağla (geriye dönük uyumluluk için)
    return dict(csrf_token=generate_csrf)


# Veritabanı başlat
from models import db
from flask_migrate import Migrate

db.init_app(app)
migrate = Migrate(app, db)

# Veritabanı metadata'sını yenile ve bağlantıyı test et
with app.app_context():
    try:
        db.engine.dispose()
        # Bağlantıyı test et
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT 1"))
            result.close()
        logger.info("✅ Database engine yenilendi, metadata reflect edildi ve bağlantı test edildi")
    except Exception as e:
        logger.warning(f"⚠️ Database başlatma hatası (görmezden geliniyor): {e}")

# Cache devre dışı (Redis sadece Celery broker olarak kullanılıyor)
cache = None
logger.info("ℹ️ Cache devre dışı - Redis sadece Celery broker olarak kullanılıyor")

# ============================================
# RATE LIMITER INITIALIZATION
# ============================================
limiter = None
if app.config.get('RATE_LIMIT_ENABLED', True):
    try:
        from utils.rate_limiter import init_rate_limiter, limiter as rate_limiter
        limiter = init_rate_limiter(app)
        logger.info("✅ Rate Limiter aktifleştirildi")
    except Exception as e:
        logger.warning(f"⚠️ Rate Limiter başlatılamadı: {str(e)}")
else:
    logger.info("ℹ️ Rate Limiter devre dışı (config)")

# ============================================
# CACHE MANAGER INITIALIZATION (Master Data Only)
# ============================================
cache_manager = None
if app.config.get('CACHE_ENABLED', True):
    try:
        from utils.cache_manager import init_cache, cache_manager as cm
        cache_manager = init_cache(app)
        logger.info("✅ Cache Manager aktifleştirildi (sadece master data)")
    except Exception as e:
        logger.warning(f"⚠️ Cache Manager başlatılamadı: {str(e)}")

# Query Logging - SQLAlchemy Event Listener
try:
    from utils.monitoring.query_analyzer import setup_query_logging
    setup_query_logging()
except Exception as e:
    logger.warning(f"Query logging setup hatası: {e}")

# Yardımcı modülleri import et
from utils.decorators import login_required, role_required, setup_required, setup_not_completed
from utils.helpers import get_current_user

# Context processor - tüm template'lere kullanıcı bilgisini gönder
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# Context processor - Python built-in fonksiyonları
@app.context_processor
def inject_builtins():
    return dict(min=min, max=max)

# Context processor - Cache version
@app.context_processor
def inject_cache_version():
    """Cache busting için version numarası"""
    from config import Config
    return dict(cache_version=Config.CACHE_VERSION)

# Context processor - Datetime ve tarih fonksiyonları
@app.context_processor
def inject_datetime():
    """Şablonlara datetime ve tarih yardımcı fonksiyonlarını ekle"""
    gun_adlari = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    return dict(
        now=datetime.now,
        gun_adlari=gun_adlari
    )

# Context processor - Otel bilgisi ve logo
@app.context_processor
def inject_otel_info():
    """Kullanıcının otel bilgisini ve logosunu template'lere gönder"""
    from models import Otel, Kullanici
    from utils.authorization import get_kat_sorumlusu_otel, get_depo_sorumlusu_oteller
    
    kullanici = get_current_user()
    otel_bilgi = None
    
    if kullanici:
        try:
            # Kat sorumlusu - tek otel
            if kullanici.rol == 'kat_sorumlusu':
                otel = get_kat_sorumlusu_otel(kullanici.id)
                if otel:
                    otel_bilgi = {
                        'ad': otel.ad,
                        'logo': otel.logo
                    }
            
            # Depo sorumlusu - ilk atandığı oteli göster
            elif kullanici.rol == 'depo_sorumlusu':
                oteller = get_depo_sorumlusu_oteller(kullanici.id)
                if oteller:
                    otel = oteller[0]  # İlk oteli göster
                    otel_bilgi = {
                        'ad': otel.ad,
                        'logo': otel.logo
                    }
            
            # Admin ve sistem yöneticisi - ilk oteli göster
            elif kullanici.rol in ['admin', 'sistem_yoneticisi']:
                otel = Otel.query.filter_by(aktif=True).first()
                if otel:
                    otel_bilgi = {
                        'ad': otel.ad,
                        'logo': otel.logo
                    }
        except Exception as e:
            logger.error(f"Otel bilgisi alınırken hata: {str(e)}")
    
    return dict(kullanici_otel=otel_bilgi)

# ============================================
# CACHE CONTROL - Template ve HTML cache'ini devre dışı bırak
# ============================================
@app.after_request
def add_no_cache_headers(response):
    """HTML response'larına no-cache + security header'ları ekle"""
    # Security headers (config'den) - tüm response'lara
    for key, value in app.config.get('SECURITY_HEADERS', {}).items():
        response.headers[key] = value
    # Sadece HTML sayfaları için cache'i devre dışı bırak
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# ============================================
# PWA SUPPORT - Service Worker
# ============================================
@app.route('/sw.js')
def service_worker():
    """Service Worker dosyasını root'tan serve et"""
    return send_file('static/sw.js', mimetype='application/javascript')

# ============================================
# METRICS MIDDLEWARE
# ============================================
from middleware.metrics_middleware import init_metrics_middleware
init_metrics_middleware(app)

# ============================================
# ROUTE REGISTRATION - Merkezi Route Yönetimi
# ============================================
from routes import register_all_routes
register_all_routes(app)

# ============================================
# LOGIN RATE LIMIT - Sadece login endpoint'i
# ============================================
if limiter:
    login_limit = app.config.get('RATE_LIMIT_LOGIN', '10 per minute')
    if 'login' in app.view_functions:
        app.view_functions['login'] = limiter.limit(login_limit)(app.view_functions['login'])
        logger.info(f"✅ Login rate limit aktif: {login_limit}")
    else:
        logger.warning("⚠️ login endpoint'i bulunamadı, rate limit uygulanamadı")


def init_database():
    """Veritabanı ve tabloları otomatik kontrol et - GÜVENLİ MOD"""
    try:
        with app.app_context():
            # Sadece bağlantı testi yap, tablo oluşturma!
            # Production'da mevcut verilere dokunmamak için
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                print(f"✅ Veritabanı bağlantısı başarılı - {len(existing_tables)} tablo mevcut")
                return True
            else:
                print("⚠️  Henüz tablo yok!")
                print("🔧 Lütfen 'python init_db.py' komutunu çalıştırın.")
                return False
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        print()
        print("🔧 Lütfen 'python init_db.py' komutunu çalıştırın.")
        return False


# ============================================
# SCHEDULER - Otomatik Görevler
# ============================================
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from utils.file_management_service import FileManagementService

def start_scheduler():
    """Zamanlanmış görevleri başlat"""
    # Debug modunda sadece child process'te (gerçek uygulama) çalıştır
    # WERKZEUG_RUN_MAIN='true' sadece child process'te set edilir
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') is None
    if is_reloader_process and app.debug:
        return  # Ana reloader process'inde scheduler başlatma
    
    scheduler = BackgroundScheduler()
    
    # Her gün saat 02:00'de eski dosyaları temizle
    scheduler.add_job(
        func=lambda: FileManagementService.cleanup_old_files(),
        trigger=CronTrigger(hour=2, minute=0),
        id='cleanup_old_files',
        name='Eski doluluk dosyalarını temizle',
        replace_existing=True
    )
    
    # ML SYSTEM JOBS - Sadece ML_ENABLED=true ise çalışır
    ml_enabled = os.getenv('ML_ENABLED', 'false').lower() == 'true'
    
    if ml_enabled:
        # Sabah 08:00 - Akşam 20:00 arası her saat başı veri toplama
        scheduler.add_job(
            func=lambda: collect_ml_data(),
            trigger='cron',
            hour='8-20',  # 08:00, 09:00, ..., 20:00
            minute=0,
            id='ml_data_collection',
            name='ML Veri Toplama',
            replace_existing=True
        )
        
        # Sabah 08:00 - Akşam 20:00 arası her saat başı anomali tespiti (30. dakikada)
        scheduler.add_job(
            func=lambda: detect_anomalies(),
            trigger='cron',
            hour='8-20',  # 08:00, 09:00, ..., 20:00
            minute=30,    # Veri toplamadan 30 dk sonra
            id='ml_anomaly_detection',
            name='ML Anomali Tespiti',
            replace_existing=True
        )
        
        # Her gece yarısı model eğitimi
        ml_training_schedule = os.getenv('ML_TRAINING_SCHEDULE', '0 0 * * *')  # Cron format
        scheduler.add_job(
            func=lambda: train_ml_models(),
            trigger=CronTrigger.from_crontab(ml_training_schedule),
            id='ml_model_training',
            name='ML Model Eğitimi',
            replace_existing=True
        )
        
        # Günde 2 kez stok bitiş kontrolü (sabah 9 ve akşam 6)
        scheduler.add_job(
            func=lambda: check_stock_depletion(),
            trigger='cron',
            hour='9,18',
            id='ml_stock_depletion_check',
            name='ML Stok Bitiş Kontrolü',
            replace_existing=True
        )
        
        # Her gece 03:00'te eski alertleri temizle
        scheduler.add_job(
            func=lambda: cleanup_old_alerts(),
            trigger='cron',
            hour=3,
            minute=0,
            id='ml_alert_cleanup',
            name='ML Alert Temizleme',
            replace_existing=True
        )
        
        # Her gece 04:00'te eski model versiyonlarını temizle
        scheduler.add_job(
            func=lambda: cleanup_old_models(),
            trigger='cron',
            hour=4,
            minute=0,
            id='ml_model_cleanup',
            name='ML Model Cleanup',
            replace_existing=True
        )
        
        print("✅ ML Scheduler başlatıldı")
        print("   - Veri toplama: 08:00-20:00 arası her saat başı")
        print("   - Anomali tespiti: 08:30-20:30 arası her saat")
        print(f"   - Model eğitimi: {ml_training_schedule}")
        print("   - Stok bitiş kontrolü: Günde 2 kez (09:00, 18:00)")
        print("   - Alert temizleme: Her gece 03:00")
        print("   - Model cleanup: Her gece 04:00")
    
    scheduler.start()
    print("✅ Scheduler başlatıldı (Günlük dosya temizleme: 02:00)")

def collect_ml_data():
    """ML veri toplama job'u"""
    try:
        from utils.ml.data_collector import DataCollector
        with app.app_context():
            collector = DataCollector(db)
            collector.collect_all_metrics()
            # Eski metrikleri temizle (90 günden eski)
            collector.cleanup_old_metrics(days=90)
    except Exception as e:
        logger.error(f"❌ ML veri toplama hatası: {str(e)}")

def detect_anomalies():
    """ML anomali tespiti job'u"""
    try:
        from utils.ml.anomaly_detector import AnomalyDetector
        with app.app_context():
            detector = AnomalyDetector(db)
            detector.detect_all_anomalies()
    except Exception as e:
        logger.error(f"❌ ML anomali tespiti hatası: {str(e)}")

def train_ml_models():
    """ML model eğitimi job'u"""
    try:
        from utils.ml.model_trainer import ModelTrainer
        with app.app_context():
            trainer = ModelTrainer(db)
            trainer.train_all_models()
    except Exception as e:
        logger.error(f"❌ ML model eğitimi hatası: {str(e)}")

def check_stock_depletion():
    """Stok bitiş kontrolü job'u"""
    try:
        from utils.ml.metrics_calculator import MetricsCalculator
        with app.app_context():
            calculator = MetricsCalculator(db)
            calculator.check_stock_depletion_alerts()
    except Exception as e:
        logger.error(f"❌ Stok bitiş kontrolü hatası: {str(e)}")

def cleanup_old_alerts():
    """Eski alertleri temizle job'u"""
    try:
        from utils.ml.alert_manager import AlertManager
        with app.app_context():
            alert_manager = AlertManager(db)
            alert_manager.cleanup_old_alerts(days=90)
    except Exception as e:
        logger.error(f"❌ Alert temizleme hatası: {str(e)}")

def cleanup_old_models():
    """Eski model versiyonlarını temizle job'u"""
    try:
        from utils.ml.model_manager import ModelManager
        with app.app_context():
            model_manager = ModelManager(db)
            
            # Eski model versiyonlarını temizle (son 3 versiyon sakla)
            result = model_manager.cleanup_old_models(keep_versions=3)
            
            # Disk kullanımını kontrol et
            disk_info = model_manager._check_disk_space()
            
            # Disk kullanımı %90'ı geçtiyse alert oluştur
            if disk_info['percent'] > 90:
                logger.warning(
                    f"⚠️  DISK KULLANIMI YÜKSEK: {disk_info['percent']:.1f}% "
                    f"({disk_info['used_gb']:.2f}GB / {disk_info['total_gb']:.2f}GB)"
                )
                
                # ML Alert oluştur
                from models import MLAlert
                from datetime import datetime, timezone
                
                alert = MLAlert(
                    alert_type='stok_anomali',  # En yakın tip
                    severity='kritik',
                    entity_id=0,  # Sistem seviyesi
                    metric_value=disk_info['percent'],
                    expected_value=80.0,
                    deviation_percent=(disk_info['percent'] - 80.0) / 80.0 * 100,
                    message=f"ML model dizini disk kullanımı kritik seviyede: {disk_info['percent']:.1f}%",
                    suggested_action="Eski model dosyalarını manuel olarak temizleyin veya disk alanını artırın",
                    created_at=get_kktc_now()
                )
                db.session.add(alert)
                db.session.commit()
            
            logger.info(
                f"✅ Model cleanup tamamlandı: "
                f"{result['deleted_count']} model silindi, "
                f"{result['freed_space_mb']:.2f}MB alan boşaltıldı"
            )
            
    except Exception as e:
        logger.error(f"❌ Model cleanup hatası: {str(e)}")

# Scheduler'ı başlat
try:
    start_scheduler()
except Exception as e:
    print(f"⚠️  Scheduler başlatılamadı: {str(e)}")

# Session kontrolü - Her istekte
@app.before_request
def check_session_validity():
    """Her istekte session geçerliliğini kontrol et"""
    from datetime import datetime as dt
    # Static dosyalar ve login sayfası hariç
    if request.endpoint and not request.endpoint.startswith('static') and request.endpoint not in ['login', 'logout']:
        if 'kullanici_id' in session:
            # Session son aktivite zamanını kontrol et
            last_activity = session.get('last_activity')
            if last_activity:
                try:
                    last_time = dt.fromisoformat(last_activity)
                    timeout = app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(hours=8))
                    if isinstance(timeout, int):
                        timeout = timedelta(seconds=timeout)
                    if dt.now() - last_time > timeout:
                        session.clear()
                        flash('Oturumunuz sona erdi. Lütfen tekrar giriş yapın.', 'warning')
                        return redirect(url_for('login'))
                except:
                    pass
            # Son aktivite zamanını güncelle
            session['last_activity'] = dt.now().isoformat()


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

        # HTTPS desteği için SSL context (mobil kamera erişimi için gerekli)
        ssl_context = None
        use_https = os.getenv('USE_HTTPS', 'false').lower() == 'true'

        if use_https:
            cert_file = os.path.join(os.path.dirname(__file__), 'cert.pem')
            key_file = os.path.join(os.path.dirname(__file__), 'key.pem')

            if os.path.exists(cert_file) and os.path.exists(key_file):
                ssl_context = (cert_file, key_file)
                print(f"🔒 HTTPS Aktif: https://0.0.0.0:{port}")
                print(f"📱 Mobil erişim: https://<IP-ADRESINIZ>:{port}")
                print("⚠️  Self-signed sertifika kullanıldığı için tarayıcıda güvenlik uyarısı alabilirsiniz.")
                print("   Mobilde 'Advanced' > 'Proceed to site' seçeneğini kullanın.")
            else:
                print("⚠️  SSL sertifikası bulunamadı. Sertifika oluşturmak için:")
                print("   python generate_ssl_cert.py")
                print("📍 HTTP Modu: http://0.0.0.0:{port}")
                print("⚠️  Mobil kamera erişimi için HTTPS gereklidir!")
        else:
            print(f"📍 HTTP Modu: http://0.0.0.0:{port}")
            print("⚠️  Mobil kamera erişimi için HTTPS gereklidir!")
            print("   HTTPS'i aktifleştirmek için .env dosyasına USE_HTTPS=true ekleyin")

        print("🌙 Dark/Light tema: Sağ üstten değiştirilebilir")
        print()
        print("Durdurmak için CTRL+C kullanın")
        print("=" * 60)
        print()

        try:
            app.run(
                debug=debug_mode,
                host='0.0.0.0',
                port=port,
                ssl_context=ssl_context,
                use_reloader=True
            )
        except Exception as e:
            print(f"❌ Flask başlatma hatası: {e}")
            import traceback
            traceback.print_exc()
    else:
        print()
        print("❌ Uygulama başlatılamadı. Lütfen veritabanı ayarlarını kontrol edin.")
        print()
        exit(1)
