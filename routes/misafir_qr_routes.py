"""
Misafir QR Kod Route'ları
"""

from flask import jsonify, request, render_template, session
from models import db, Oda, MinibarDolumTalebi
from utils.qr_service import QRKodService
from utils.rate_limiter import QRRateLimiter
from utils.helpers import log_islem, log_hata
from flask_wtf.csrf import CSRFProtect
import bleach


def register_misafir_qr_routes(app):
    """Misafir QR route'larını kaydet"""
    
    @app.route('/qr/<token>')
    def qr_redirect(token):
        """QR kod yönlendirme - Akıllı routing"""
        try:
            # Rate limit kontrolü
            ip = request.remote_addr
            if not QRRateLimiter.check_qr_scan_limit(ip):
                return render_template('errors/429.html'), 429
            
            # Token'ı doğrula
            oda = QRKodService.validate_token(token)
            
            if not oda:
                # Geçersiz token logu
                QRKodService.log_qr_scan(
                    oda_id=None,
                    okutma_tipi='misafir',
                    kullanici_id=None,
                    basarili=False,
                    hata_mesaji='Geçersiz token'
                )
                return render_template('errors/404.html', 
                                     message='Geçersiz QR kod'), 404
            
            # Kullanıcı kat sorumlusu mu kontrol et
            if 'kullanici_id' in session and session.get('rol') == 'kat_sorumlusu':
                # Kat sorumlusu - minibar işlemleri sayfasına yönlendir
                return render_template('kat_sorumlusu/qr_redirect.html',
                                     oda=oda,
                                     token=token)
            else:
                # Misafir - dolum talebi sayfasına yönlendir
                return render_template('misafir_dolum_talebi.html',
                                     oda=oda,
                                     token=token)
                
        except Exception as e:
            log_hata(e, modul='qr_redirect', extra_info={'token': token[:10]})
            return render_template('errors/500.html'), 500
    
    
    @app.route('/misafir/dolum-talebi/<token>', methods=['GET', 'POST'])
    def misafir_dolum_talebi(token):
        """Misafir dolum talebi sayfası"""
        try:
            # Rate limit kontrolü
            ip = request.remote_addr
            if not QRRateLimiter.check_qr_scan_limit(ip):
                return jsonify({
                    'success': False,
                    'message': 'Çok fazla deneme. Lütfen 1 dakika bekleyin.'
                }), 429
            
            # Token'ı doğrula
            oda = QRKodService.validate_token(token)
            
            if not oda:
                return jsonify({
                    'success': False,
                    'message': 'Geçersiz QR kod'
                }), 404
            
            if request.method == 'POST':
                # Dolum talebi kaydet
                notlar = request.form.get('notlar', '').strip()
                
                # Input sanitization
                if notlar:
                    notlar = bleach.clean(notlar, tags=[], strip=True)
                    if len(notlar) > 500:
                        return jsonify({
                            'success': False,
                            'message': 'Not maksimum 500 karakter olabilir'
                        }), 400
                
                # Talep oluştur
                talep = MinibarDolumTalebi(
                    oda_id=oda.id,
                    durum='beklemede',
                    notlar=notlar if notlar else None
                )
                db.session.add(talep)
                db.session.commit()
                
                # QR okutma logu
                QRKodService.log_qr_scan(
                    oda_id=oda.id,
                    okutma_tipi='misafir',
                    kullanici_id=None,
                    basarili=True
                )
                
                # Log kaydı
                log_islem('ekleme', 'dolum_talebi', {
                    'oda_id': oda.id,
                    'oda_no': oda.oda_no,
                    'talep_id': talep.id
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Dolum talebiniz başarıyla gönderildi!'
                })
            
            else:  # GET
                return render_template('misafir_dolum_talebi.html',
                                     oda=oda,
                                     token=token)
                
        except Exception as e:
            db.session.rollback()
            log_hata(e, modul='misafir_dolum_talebi', extra_info={'token': token[:10]})
            return jsonify({
                'success': False,
                'message': 'Talep gönderilirken hata oluştu'
            }), 500
