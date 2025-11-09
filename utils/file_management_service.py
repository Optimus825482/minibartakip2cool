"""
Dosya Yönetim Servisi
Excel dosyalarının yüklenmesi, silinmesi ve temizlenmesi işlemlerini yönetir
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from werkzeug.utils import secure_filename
from models import db, DosyaYukleme, MisafirKayit
from sqlalchemy import and_


class FileManagementService:
    """Dosya yönetimi servisi sınıfı"""
    
    # Konfigürasyon
    UPLOAD_FOLDER = 'uploads/doluluk/'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    FILE_RETENTION_DAYS = 4
    
    @staticmethod
    def save_uploaded_file(file, user_id):
        """
        Yüklenen dosyayı kaydeder
        
        Args:
            file: Werkzeug FileStorage objesi
            user_id: Yükleyen kullanıcı ID
            
        Returns:
            tuple: (success, file_path, islem_kodu, error_message)
        """
        try:
            # Dosya var mı kontrol et
            if not file or file.filename == '':
                return False, None, None, 'Dosya seçilmedi'
            
            # Dosya uzantısı kontrolü
            if not FileManagementService._allowed_file(file.filename):
                return False, None, None, 'Geçersiz dosya formatı. Sadece .xlsx ve .xls dosyaları kabul edilir'
            
            # Dosya boyutu kontrolü (stream'den okumadan önce)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Başa dön
            
            if file_size > FileManagementService.MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                return False, None, None, f'Dosya çok büyük ({size_mb:.1f} MB). Maksimum 10 MB'
            
            # Upload klasörünü oluştur
            FileManagementService._ensure_upload_folder()
            
            # Benzersiz işlem kodu oluştur
            islem_kodu = FileManagementService.generate_islem_kodu()
            
            # Güvenli dosya adı oluştur
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{islem_kodu}.{file_extension}"
            
            # Dosya yolu
            file_path = os.path.join(FileManagementService.UPLOAD_FOLDER, unique_filename)
            
            # Dosyayı kaydet
            file.save(file_path)
            
            # Veritabanı kaydı oluştur
            dosya_yukleme = DosyaYukleme(
                islem_kodu=islem_kodu,
                dosya_adi=original_filename,
                dosya_yolu=file_path,
                dosya_tipi='in_house',  # Başlangıçta varsayılan, sonra güncellenecek
                dosya_boyutu=file_size,
                yukleme_tarihi=datetime.now(timezone.utc),
                durum='yuklendi',
                yuklenen_kullanici_id=user_id
            )
            
            db.session.add(dosya_yukleme)
            db.session.commit()
            
            return True, file_path, islem_kodu, None
            
        except Exception as e:
            db.session.rollback()
            return False, None, None, f'Dosya kaydetme hatası: {str(e)}'
    
    @staticmethod
    def delete_upload_by_islem_kodu(islem_kodu, user_id=None):
        """
        İşlem koduna göre yüklemeyi ve ilgili kayıtları siler
        
        Args:
            islem_kodu: İşlem kodu
            user_id: Silme işlemini yapan kullanıcı ID (audit için)
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Dosya yükleme kaydını bul
            dosya_yukleme = DosyaYukleme.query.filter_by(islem_kodu=islem_kodu).first()
            
            if not dosya_yukleme:
                return False, 'İşlem kodu bulunamadı'
            
            # İlgili misafir kayıtlarını sil
            deleted_count = MisafirKayit.query.filter_by(islem_kodu=islem_kodu).delete()
            
            # Fiziksel dosyayı sil
            if os.path.exists(dosya_yukleme.dosya_yolu):
                try:
                    os.remove(dosya_yukleme.dosya_yolu)
                except Exception as e:
                    print(f"Dosya silme hatası: {str(e)}")
            
            # Dosya yükleme kaydını güncelle
            dosya_yukleme.durum = 'silindi'
            dosya_yukleme.silme_tarihi = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return True, f'{deleted_count} misafir kaydı ve dosya başarıyla silindi'
            
        except Exception as e:
            db.session.rollback()
            return False, f'Silme hatası: {str(e)}'
    
    @staticmethod
    def cleanup_old_files():
        """
        4 günden eski dosyaları otomatik siler
        (Cron job veya scheduler ile çalıştırılacak)
        
        Returns:
            dict: {
                'success': bool,
                'deleted_count': int,
                'message': str
            }
        """
        try:
            # 4 gün önceki tarih
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=FileManagementService.FILE_RETENTION_DAYS)
            
            # Eski dosyaları bul
            old_uploads = DosyaYukleme.query.filter(
                and_(
                    DosyaYukleme.yukleme_tarihi < cutoff_date,
                    DosyaYukleme.durum != 'silindi'
                )
            ).all()
            
            deleted_count = 0
            
            for upload in old_uploads:
                # Fiziksel dosyayı sil
                if os.path.exists(upload.dosya_yolu):
                    try:
                        os.remove(upload.dosya_yolu)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Dosya silme hatası ({upload.dosya_yolu}): {str(e)}")
                
                # Durumu güncelle
                upload.durum = 'silindi'
                upload.silme_tarihi = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'{deleted_count} eski dosya temizlendi'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'deleted_count': 0,
                'message': f'Temizleme hatası: {str(e)}'
            }
    
    @staticmethod
    def generate_islem_kodu():
        """
        Benzersiz işlem kodu oluşturur
        Format: DOLULUK-YYYYMMDD-HHMMSS-RANDOM
        
        Returns:
            str: Benzersiz işlem kodu
        """
        now = datetime.now()
        date_part = now.strftime('%Y%m%d')
        time_part = now.strftime('%H%M%S')
        random_part = str(uuid.uuid4())[:8].upper()
        
        return f"DOLULUK-{date_part}-{time_part}-{random_part}"
    
    @staticmethod
    def _allowed_file(filename):
        """Dosya uzantısı kontrolü"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileManagementService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def _ensure_upload_folder():
        """Upload klasörünü oluştur (yoksa)"""
        if not os.path.exists(FileManagementService.UPLOAD_FOLDER):
            os.makedirs(FileManagementService.UPLOAD_FOLDER, exist_ok=True)
    
    @staticmethod
    def update_dosya_yukleme_status(islem_kodu, durum, **kwargs):
        """
        Dosya yükleme durumunu günceller
        
        Args:
            islem_kodu: İşlem kodu
            durum: Yeni durum
            **kwargs: Ek alanlar (dosya_tipi, toplam_satir, basarili_satir, hatali_satir, hata_detaylari)
        """
        try:
            dosya_yukleme = DosyaYukleme.query.filter_by(islem_kodu=islem_kodu).first()
            
            if dosya_yukleme:
                dosya_yukleme.durum = durum
                
                # Ek alanları güncelle
                if 'dosya_tipi' in kwargs:
                    dosya_yukleme.dosya_tipi = kwargs['dosya_tipi']
                if 'toplam_satir' in kwargs:
                    dosya_yukleme.toplam_satir = kwargs['toplam_satir']
                if 'basarili_satir' in kwargs:
                    dosya_yukleme.basarili_satir = kwargs['basarili_satir']
                if 'hatali_satir' in kwargs:
                    dosya_yukleme.hatali_satir = kwargs['hatali_satir']
                if 'hata_detaylari' in kwargs:
                    dosya_yukleme.hata_detaylari = kwargs['hata_detaylari']
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Durum güncelleme hatası: {str(e)}")
            return False
