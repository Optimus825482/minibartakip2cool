"""
Excel İşleme Servisi
Otel doluluk Excel dosyalarını işler ve veritabanına kaydeder
"""

import openpyxl
from datetime import datetime, date, time
from models import db, MisafirKayit, DosyaYukleme, Oda, Kat
from sqlalchemy import and_
import traceback


class ExcelProcessingService:
    """Excel dosyalarını işleyen servis sınıfı"""
    
    # Beklenen sütun adları
    IN_HOUSE_COLUMNS = ['Name', 'Room no', 'R.Type', 'Arrival', 'Departure', 'Adult']
    ARRIVALS_COLUMNS = ['Name', 'Room no', 'R.Type', 'Hsk.St.', 'Arr.Time', 'Arrival', 'Departure', 'Adult']
    
    @staticmethod
    def detect_file_type(headers):
        """
        Excel sütun başlıklarından dosya tipini otomatik algılar
        
        Args:
            headers: Excel'in ilk satırındaki sütun başlıkları (list)
            
        Returns:
            str: 'arrivals' veya 'in_house'
        
        Logic:
            - Eğer 'Hsk.St.' veya 'Arr.Time' varsa -> 'arrivals'
            - Yoksa -> 'in_house'
        """
        headers_str = [str(h).strip() if h else '' for h in headers]
        
        # ARRIVALS dosyası için özel sütunlar
        if 'Hsk.St.' in headers_str or 'Arr.Time' in headers_str:
            return 'arrivals'
        
        return 'in_house'
    
    @staticmethod
    def process_excel_file(file_path, islem_kodu, user_id, otel_id=None):
        """
        Excel dosyasını işler ve veritabanına kaydeder
        
        Args:
            file_path: Dosya yolu
            islem_kodu: Benzersiz işlem kodu
            user_id: Yükleyen kullanıcı ID
            otel_id: Otel ID (opsiyonel, filtreleme için)
            
        Returns:
            dict: {
                'success': bool,
                'dosya_tipi': str,
                'toplam_satir': int,
                'basarili_satir': int,
                'hatali_satir': int,
                'hatalar': list
            }
        """
        try:
            # Excel dosyasını aç
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            sheet = workbook.active
            
            # İlk satırdan başlıkları al
            headers = []
            for cell in sheet[1]:
                headers.append(cell.value)
            
            # Dosya tipini algıla
            dosya_tipi = ExcelProcessingService.detect_file_type(headers)
            kayit_tipi = 'arrival' if dosya_tipi == 'arrivals' else 'in_house'
            
            # Sütun indekslerini bul
            col_indices = ExcelProcessingService._get_column_indices(headers)
            
            if not col_indices:
                return {
                    'success': False,
                    'error': 'Gerekli sütunlar bulunamadı',
                    'dosya_tipi': dosya_tipi,
                    'toplam_satir': 0,
                    'basarili_satir': 0,
                    'hatali_satir': 0,
                    'hatalar': ['Gerekli sütunlar (Room no, Arrival, Departure, Adult) bulunamadı']
                }
            
            # Satırları işle
            toplam_satir = 0
            basarili_satir = 0
            hatali_satir = 0
            hatalar = []
            
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                toplam_satir += 1
                
                try:
                    # Satır verilerini çıkar
                    row_data = ExcelProcessingService._extract_row_data(
                        row, col_indices, dosya_tipi
                    )
                    
                    # Veriyi doğrula
                    is_valid, error_msg = ExcelProcessingService.validate_row(row_data)
                    
                    if not is_valid:
                        hatali_satir += 1
                        hatalar.append(f"Satır {row_idx}: {error_msg}")
                        continue
                    
                    # Odayı bul veya oluştur
                    oda = ExcelProcessingService.get_or_create_oda(
                        row_data['oda_no'], otel_id
                    )
                    
                    if not oda:
                        hatali_satir += 1
                        hatalar.append(f"Satır {row_idx}: Oda '{row_data['oda_no']}' bulunamadı veya oluşturulamadı")
                        continue
                    
                    # MisafirKayit oluştur
                    misafir_kayit = MisafirKayit(
                        oda_id=oda.id,
                        islem_kodu=islem_kodu,
                        misafir_sayisi=row_data['misafir_sayisi'],
                        giris_tarihi=row_data['giris_tarihi'],
                        giris_saati=row_data.get('giris_saati'),
                        cikis_tarihi=row_data['cikis_tarihi'],
                        kayit_tipi=kayit_tipi,
                        olusturan_id=user_id
                    )
                    
                    db.session.add(misafir_kayit)
                    basarili_satir += 1
                    
                except Exception as e:
                    hatali_satir += 1
                    hatalar.append(f"Satır {row_idx}: {str(e)}")
                    continue
            
            # Toplu kaydet
            db.session.commit()
            
            return {
                'success': True,
                'dosya_tipi': dosya_tipi,
                'toplam_satir': toplam_satir,
                'basarili_satir': basarili_satir,
                'hatali_satir': hatali_satir,
                'hatalar': hatalar[:50]  # İlk 50 hatayı döndür
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Excel işleme hatası: {str(e)}',
                'dosya_tipi': None,
                'toplam_satir': 0,
                'basarili_satir': 0,
                'hatali_satir': 0,
                'hatalar': [str(e), traceback.format_exc()]
            }
    
    @staticmethod
    def _get_column_indices(headers):
        """Sütun başlıklarından indeksleri bul"""
        indices = {}
        
        for idx, header in enumerate(headers):
            header_str = str(header).strip() if header else ''
            
            if header_str == 'Room no':
                indices['oda_no'] = idx
            elif header_str == 'Arrival':
                indices['giris_tarihi'] = idx
            elif header_str == 'Departure':
                indices['cikis_tarihi'] = idx
            elif header_str == 'Adult':
                indices['misafir_sayisi'] = idx
            elif header_str == 'Arr.Time':
                indices['giris_saati'] = idx
        
        # Zorunlu sütunlar var mı kontrol et
        required = ['oda_no', 'giris_tarihi', 'cikis_tarihi', 'misafir_sayisi']
        if all(key in indices for key in required):
            return indices
        
        return None
    
    @staticmethod
    def _extract_row_data(row, col_indices, dosya_tipi):
        """Satırdan veri çıkar"""
        data = {
            'oda_no': str(row[col_indices['oda_no']]).strip() if row[col_indices['oda_no']] else None,
            'giris_tarihi': row[col_indices['giris_tarihi']],
            'cikis_tarihi': row[col_indices['cikis_tarihi']],
            'misafir_sayisi': row[col_indices['misafir_sayisi']],
        }
        
        # ARRIVALS için giriş saati
        if dosya_tipi == 'arrivals' and 'giris_saati' in col_indices:
            data['giris_saati'] = row[col_indices['giris_saati']]
        
        return data
    
    @staticmethod
    def validate_row(row_data):
        """
        Satır verilerini doğrular
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Oda numarası kontrolü
        if not row_data.get('oda_no'):
            return False, "Oda numarası boş"
        
        # Giriş tarihi kontrolü
        giris_tarihi = ExcelProcessingService.parse_date(row_data.get('giris_tarihi'))
        if not giris_tarihi:
            return False, "Geçersiz giriş tarihi"
        
        # Çıkış tarihi kontrolü
        cikis_tarihi = ExcelProcessingService.parse_date(row_data.get('cikis_tarihi'))
        if not cikis_tarihi:
            return False, "Geçersiz çıkış tarihi"
        
        # Tarih sırası kontrolü
        if giris_tarihi >= cikis_tarihi:
            return False, "Giriş tarihi çıkış tarihinden önce olmalı"
        
        # Misafir sayısı kontrolü
        try:
            misafir_sayisi = int(row_data.get('misafir_sayisi', 0))
            if misafir_sayisi <= 0:
                return False, "Misafir sayısı pozitif olmalı"
            row_data['misafir_sayisi'] = misafir_sayisi
        except (ValueError, TypeError):
            return False, "Geçersiz misafir sayısı"
        
        # Tarihleri güncelle
        row_data['giris_tarihi'] = giris_tarihi
        row_data['cikis_tarihi'] = cikis_tarihi
        
        # Giriş saati kontrolü (varsa)
        if 'giris_saati' in row_data and row_data['giris_saati']:
            giris_saati = ExcelProcessingService.parse_time(row_data['giris_saati'])
            row_data['giris_saati'] = giris_saati
        
        return True, None
    
    @staticmethod
    def parse_date(date_value):
        """Tarih değerini parse eder"""
        if not date_value:
            return None
        
        # Zaten date objesi ise
        if isinstance(date_value, date):
            return date_value
        
        # datetime objesi ise
        if isinstance(date_value, datetime):
            return date_value.date()
        
        # String ise parse et
        if isinstance(date_value, str):
            date_value = date_value.strip()
            
            # Yaygın tarih formatları
            formats = [
                '%Y-%m-%d',
                '%d.%m.%Y',
                '%d/%m/%Y',
                '%d-%m-%Y',
                '%Y/%m/%d',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def parse_time(time_value):
        """Saat değerini parse eder"""
        if not time_value:
            return None
        
        # Zaten time objesi ise
        if isinstance(time_value, time):
            return time_value
        
        # datetime objesi ise
        if isinstance(time_value, datetime):
            return time_value.time()
        
        # String ise parse et
        if isinstance(time_value, str):
            time_value = time_value.strip()
            
            # Yaygın saat formatları
            formats = [
                '%H:%M',
                '%H:%M:%S',
                '%I:%M %p',  # 12 saat formatı (AM/PM)
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_value, fmt).time()
                except ValueError:
                    continue
        
        return None
    
    @staticmethod
    def get_or_create_oda(oda_no, otel_id=None):
        """
        Oda numarasına göre oda kaydını getirir veya oluşturur
        
        Args:
            oda_no: Oda numarası
            otel_id: Otel ID (opsiyonel)
            
        Returns:
            Oda: Oda objesi veya None
        """
        try:
            # Önce odayı bul
            query = Oda.query.filter_by(oda_no=oda_no)
            
            # Otel filtresi varsa ekle
            if otel_id:
                query = query.join(Kat).filter(Kat.otel_id == otel_id)
            
            oda = query.first()
            
            if oda:
                return oda
            
            # Oda bulunamadı - uyarı ver ama None döndür
            # (Oda oluşturma işlemi manuel yapılmalı)
            return None
            
        except Exception as e:
            print(f"Oda arama hatası: {str(e)}")
            return None
