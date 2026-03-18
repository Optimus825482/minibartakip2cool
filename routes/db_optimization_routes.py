"""
Database Optimizasyon Route'ları
Fiyatlandırma ve Karlılık Sistemi için veritabanı optimizasyon endpoint'leri

Erkan için - Database Performance Management
"""

from flask import Blueprint, jsonify, render_template, request
from utils.decorators import login_required, role_required
from utils.db_optimization import DatabaseOptimizer
from utils.audit import log_audit
import logging

logger = logging.getLogger(__name__)

db_optimization_bp = Blueprint('db_optimization', __name__, url_prefix='/api/v1/db')


@db_optimization_bp.route('/health', methods=['GET'])
@login_required
@role_required(['sistem_yoneticisi'])
def check_health():
    """
    Veritabanı sağlık kontrolü
    
    Returns:
        JSON: Sağlık durumu
    """
    try:
        result = DatabaseOptimizer.check_database_health()
        
        log_audit(
            islem_tipi='execute',
            tablo_adi='db_health',
            aciklama='Database health check yapıldı'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Health check hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/indexes/check', methods=['GET'])
@login_required
@role_required(['sistem_yoneticisi'])
def check_indexes():
    """
    Eksik index'leri kontrol et
    
    Returns:
        JSON: Eksik index listesi
    """
    try:
        result = DatabaseOptimizer.check_missing_indexes()
        
        log_audit(
            islem_tipi='execute',
            tablo_adi='db_index',
            aciklama=f'{result.get("missing_count", 0)} eksik index tespit edildi'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Index check hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/indexes/create', methods=['POST'])
@login_required
@role_required(['sistem_yoneticisi'])
def create_indexes():
    """
    Eksik index'leri oluştur
    
    Returns:
        JSON: Oluşturma sonucu
    """
    try:
        result = DatabaseOptimizer.create_missing_indexes()
        
        log_audit(
            islem_tipi='update',
            tablo_adi='db_index',
            aciklama=f'{result.get("created_count", 0)} index oluşturuldu'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Index creation hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/performance/analyze', methods=['GET'])
@login_required
@role_required(['sistem_yoneticisi'])
def analyze_performance():
    """
    Query performansını analiz et
    
    Returns:
        JSON: Performans analizi
    """
    try:
        result = DatabaseOptimizer.analyze_query_performance()
        
        log_audit(
            islem_tipi='execute',
            tablo_adi='db_performance',
            aciklama='Query performans analizi yapıldı'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Performance analysis hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/tables/optimize', methods=['POST'])
@login_required
@role_required(['sistem_yoneticisi'])
def optimize_tables():
    """
    Tabloları optimize et (ANALYZE)
    
    Returns:
        JSON: Optimizasyon sonucu
    """
    try:
        result = DatabaseOptimizer.optimize_tables()
        
        log_audit(
            islem_tipi='update',
            tablo_adi='db_tables',
            aciklama=f'{result.get("optimized_count", 0)} tablo optimize edildi'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Table optimization hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/pool/stats', methods=['GET'])
@login_required
@role_required(['sistem_yoneticisi'])
def pool_stats():
    """
    Connection pool istatistikleri
    
    Returns:
        JSON: Pool stats
    """
    try:
        result = DatabaseOptimizer.get_connection_pool_stats()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Pool stats hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@db_optimization_bp.route('/optimize/full', methods=['POST'])
@login_required
@role_required(['sistem_yoneticisi'])
def full_optimization():
    """
    Tam optimizasyon paketi çalıştır
    
    Returns:
        JSON: Tüm optimizasyon sonuçları
    """
    try:
        result = DatabaseOptimizer.run_full_optimization()
        
        log_audit(
            islem_tipi='update',
            tablo_adi='database',
            aciklama='Full database optimization yapıldı'
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Full optimization hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# UI Route
@db_optimization_bp.route('/dashboard', methods=['GET'])
@login_required
@role_required(['sistem_yoneticisi'])
def optimization_dashboard():
    """
    Database optimizasyon dashboard'u
    
    Returns:
        HTML: Dashboard sayfası
    """
    try:
        return render_template('admin/db_optimization_dashboard.html')
        
    except Exception as e:
        logger.error(f"Dashboard render hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def register_db_optimization_routes(app):
    """Database optimizasyon route'larını kaydet"""
    app.register_blueprint(db_optimization_bp)
