"""
Yetkilendirme Helper Fonksiyonları
Otel bazlı erişim kontrolü için yardımcı fonksiyonlar
"""

from models import Kullanici, Otel, KullaniciOtel
from flask import session
import logging

from models import db

logger = logging.getLogger(__name__)


def get_depo_sorumlusu_oteller(kullanici_id):
    """
    Depo sorumlusunun erişebileceği otelleri getir
    
    Args:
        kullanici_id: Kullanıcı ID
        
    Returns:
        List[Otel]: Erişilebilir oteller listesi
    """
    from models import db
    
    try:
        oteller = db.session.query(Otel).join(KullaniciOtel).filter(
            KullaniciOtel.kullanici_id == kullanici_id,
            Otel.aktif == True
        ).order_by(Otel.id).all()
        
        # Debug log
        if not oteller:
            logger.warning(f"Depo sorumlusu {kullanici_id} için otel ataması bulunamadı")
        else:
            logger.info(f"Depo sorumlusu {kullanici_id} için {len(oteller)} otel bulundu: {[o.ad for o in oteller]}")
        
        return oteller
    except Exception as e:
        logger.error(f"Depo sorumlusu otelleri alınırken hata: {e}")
        db.session.rollback()
        return []


def depo_sorumlusu_otel_erisimi(kullanici_id, otel_id):
    """
    Depo sorumlusunun belirli bir otele erişimi var mı kontrol et
    
    Args:
        kullanici_id: Kullanıcı ID
        otel_id: Otel ID
        
    Returns:
        bool: Erişim varsa True, yoksa False
    """
    atama = KullaniciOtel.query.filter_by(
        kullanici_id=kullanici_id,
        otel_id=otel_id
    ).first()
    
    return atama is not None


def get_kat_sorumlusu_otel(kullanici_id):
    """
    Kat sorumlusunun atandığı oteli getir
    
    Args:
        kullanici_id: Kullanıcı ID
        
    Returns:
        Otel: Atandığı otel veya None
    """
    try:
        kullanici = Kullanici.query.get(kullanici_id)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Kat sorumlusu otel okunamadı (kullanici_id={kullanici_id}): {e}")
        return None
    
    if kullanici and kullanici.otel_id:
        return kullanici.otel
    
    return None


def kat_sorumlusu_otel_erisimi(kullanici_id, otel_id):
    """
    Kat sorumlusunun belirli bir otele erişimi var mı kontrol et
    
    Args:
        kullanici_id: Kullanıcı ID
        otel_id: Otel ID
        
    Returns:
        bool: Erişim varsa True, yoksa False
    """
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici:
        return False
    
    return kullanici.otel_id == otel_id


def get_kullanici_otelleri(kullanici_id=None):
    """
    Kullanıcının erişebileceği otelleri getir (rol bazlı)
    
    Args:
        kullanici_id: Kullanıcı ID (None ise session'dan alınır)
        
    Returns:
        List[Otel]: Erişilebilir oteller listesi
    """
    if kullanici_id is None:
        kullanici_id = session.get('kullanici_id')
    
    if not kullanici_id:
        return []
    
    try:
        kullanici = Kullanici.query.get(kullanici_id)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Kullanıcı otelleri okunamadı (kullanici_id={kullanici_id}): {e}")
        return []
    
    if not kullanici:
        return []
    
    # Sistem yöneticisi ve admin tüm otellere erişebilir
    if kullanici.rol in ['sistem_yoneticisi', 'admin']:
        return Otel.query.filter_by(aktif=True).order_by(Otel.id).all()
    
    # Depo sorumlusu - atandığı oteller
    elif kullanici.rol == 'depo_sorumlusu':
        return get_depo_sorumlusu_oteller(kullanici_id)
    
    # Kat sorumlusu - sadece kendi oteli
    elif kullanici.rol == 'kat_sorumlusu':
        otel = get_kat_sorumlusu_otel(kullanici_id)
        return [otel] if otel else []
    
    return []


def kullanici_otel_erisimi(kullanici_id, otel_id):
    """
    Kullanıcının belirli bir otele erişimi var mı kontrol et (rol bazlı)
    
    Args:
        kullanici_id: Kullanıcı ID
        otel_id: Otel ID
        
    Returns:
        bool: Erişim varsa True, yoksa False
    """
    kullanici = Kullanici.query.get(kullanici_id)
    
    if not kullanici:
        return False
    
    # Sistem yöneticisi ve admin tüm otellere erişebilir
    if kullanici.rol in ['sistem_yoneticisi', 'admin']:
        return True
    
    # Depo sorumlusu - atandığı otellere erişebilir
    elif kullanici.rol == 'depo_sorumlusu':
        return depo_sorumlusu_otel_erisimi(kullanici_id, otel_id)
    
    # Kat sorumlusu - sadece kendi oteline erişebilir
    elif kullanici.rol == 'kat_sorumlusu':
        return kat_sorumlusu_otel_erisimi(kullanici_id, otel_id)
    
    return False


def get_otel_filtreleme_secenekleri(kullanici_id=None):
    """
    Kullanıcı için otel filtreleme seçeneklerini getir (dropdown için)
    
    Args:
        kullanici_id: Kullanıcı ID (None ise session'dan alınır)
        
    Returns:
        List[Otel]: Otel objeleri listesi
    """
    return get_kullanici_otelleri(kullanici_id)
