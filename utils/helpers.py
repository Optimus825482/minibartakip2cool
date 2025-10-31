from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from flask import session, request
from models import Kullanici, StokHareket, Urun, SistemLog, HataLog, db
from sqlalchemy import case
import json
import traceback
import logging

# Logging yapılandırması
logging.basicConfig(
    filename='minibar_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_current_user():
    """Oturumdaki kullanıcıyı getir"""
    if 'kullanici_id' in session:
        return Kullanici.query.get(session['kullanici_id'])
    return None


def get_stok_toplamlari(urun_ids=None):
    """Belirtilen ürünler için stok toplamlarını tek sorguda getir."""
    net_miktar = db.func.sum(
        case(
            (StokHareket.hareket_tipi.in_(['giris', 'devir', 'sayim']), StokHareket.miktar),
            (StokHareket.hareket_tipi == 'cikis', -StokHareket.miktar),
            else_=0
        )
    )

    query = db.session.query(StokHareket.urun_id, net_miktar.label('net'))

    if urun_ids:
        query = query.filter(StokHareket.urun_id.in_(urun_ids))

    stoklar = {row.urun_id: int(row.net or 0) for row in query.group_by(StokHareket.urun_id)}

    if urun_ids:
        for uid in urun_ids:
            stoklar.setdefault(uid, 0)

    return stoklar


def get_toplam_stok(urun_id):
    """Ürün için toplam stok miktarını hesapla"""
    return get_stok_toplamlari([urun_id]).get(urun_id, 0)


def get_kritik_stok_urunler():
    """Kritik stok seviyesinin altındaki ürünleri getir"""
    urunler = Urun.query.filter_by(aktif=True).all()
    stok_map = get_stok_toplamlari([urun.id for urun in urunler])
    kritik_urunler = []
    
    for urun in urunler:
        mevcut_stok = stok_map.get(urun.id, 0)
        if mevcut_stok <= urun.kritik_stok_seviyesi:
            kritik_urunler.append({
                'urun': urun,
                'mevcut_stok': mevcut_stok,
                'kritik_seviye': urun.kritik_stok_seviyesi
            })
    
    return kritik_urunler


def get_stok_durumu(urun_id, stok_cache=None):
    """
    Ürün stok durumunu kategorize et ve badge bilgisi döndür
    
    Returns:
        dict: {
            'durum': 'kritik' | 'dikkat' | 'normal',
            'badge_class': Tailwind CSS class,
            'badge_text': Görünecek metin,
            'icon': SVG icon HTML,
            'mevcut_stok': int,
            'kritik_seviye': int,
            'yuzde': float (stok doluluk yüzdesi)
        }
    """
    urun = Urun.query.get(urun_id)
    if not urun:
        return None
    
    if stok_cache is None:
        mevcut_stok = get_toplam_stok(urun_id)
    else:
        mevcut_stok = stok_cache.get(urun_id, 0)
    kritik_seviye = urun.kritik_stok_seviyesi
    
    # Kritik seviyenin %150'si dikkat eşiği
    dikkat_esigi = kritik_seviye * 1.5
    
    # Yüzde hesaplama (kritik seviyeye göre)
    if kritik_seviye > 0:
        yuzde = (mevcut_stok / kritik_seviye) * 100
    else:
        yuzde = 100 if mevcut_stok > 0 else 0
    
    if mevcut_stok <= kritik_seviye:
        # KRİTİK - Kırmızı
        return {
            'durum': 'kritik',
            'badge_class': 'bg-red-100 text-red-800 border border-red-300',
            'badge_text': 'Kritik Stok',
            'icon': '''<svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                      </svg>''',
            'mevcut_stok': mevcut_stok,
            'kritik_seviye': kritik_seviye,
            'yuzde': yuzde
        }
    elif mevcut_stok <= dikkat_esigi:
        # DİKKAT - Sarı
        return {
            'durum': 'dikkat',
            'badge_class': 'bg-yellow-100 text-yellow-800 border border-yellow-300',
            'badge_text': 'Dikkat',
            'icon': '''<svg class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                      </svg>''',
            'mevcut_stok': mevcut_stok,
            'kritik_seviye': kritik_seviye,
            'yuzde': yuzde
        }
    else:
        # NORMAL - Yeşil
        return {
            'durum': 'normal',
            'badge_class': 'bg-green-100 text-green-800 border border-green-300',
            'badge_text': 'Yeterli',
            'icon': '''<svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                      </svg>''',
            'mevcut_stok': mevcut_stok,
            'kritik_seviye': kritik_seviye,
            'yuzde': yuzde
        }


def get_tum_urunler_stok_durumlari():
    """
    Tüm aktif ürünlerin stok durumlarını kategorize et
    
    Returns:
        dict: {
            'kritik': [],    # Kritik stokta olan ürünler
            'dikkat': [],    # Dikkat gerektiren ürünler
            'normal': [],    # Normal stokta olan ürünler
            'istatistik': {
                'toplam': int,
                'kritik_sayi': int,
                'dikkat_sayi': int,
                'normal_sayi': int
            }
        }
    """
    urunler = Urun.query.filter_by(aktif=True).all()
    stok_map = get_stok_toplamlari([urun.id for urun in urunler])
    
    kategoriler = {
        'kritik': [],
        'dikkat': [],
        'normal': []
    }
    
    for urun in urunler:
        durum = get_stok_durumu(urun.id, stok_cache=stok_map)
        if durum:
            durum['urun'] = urun
            kategoriler[durum['durum']].append(durum)
    
    return {
        'kritik': sorted(kategoriler['kritik'], key=lambda x: x['mevcut_stok']),
        'dikkat': sorted(kategoriler['dikkat'], key=lambda x: x['mevcut_stok']),
        'normal': sorted(kategoriler['normal'], key=lambda x: x['urun'].urun_adi),
        'istatistik': {
            'toplam': len(urunler),
            'kritik_sayi': len(kategoriler['kritik']),
            'dikkat_sayi': len(kategoriler['dikkat']),
            'normal_sayi': len(kategoriler['normal'])
        }
    }


def excel_export_stok_raporu():
    """Stok durumu Excel raporu oluştur"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Stok Raporu"
    
    # Başlık stili
    baslik_font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
    baslik_fill = PatternFill(start_color='475569', end_color='475569', fill_type='solid')
    baslik_alignment = Alignment(horizontal='center', vertical='center')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Başlıklar
    headers = ['Ürün Kodu', 'Ürün Adı', 'Grup', 'Birim', 'Mevcut Stok', 'Kritik Seviye', 'Durum']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = baslik_font
        cell.fill = baslik_fill
        cell.alignment = baslik_alignment
        cell.border = border
    
    # Veri satırları
    urunler = Urun.query.filter_by(aktif=True).all()
    stok_map = get_stok_toplamlari([urun.id for urun in urunler])

    for row_num, urun in enumerate(urunler, 2):
        mevcut_stok = stok_map.get(urun.id, 0)
        durum = 'KRİTİK' if mevcut_stok <= urun.kritik_stok_seviyesi else 'NORMAL'
        
        data = [
            urun.id,
            urun.urun_adi,
            urun.grup.grup_adi,
            urun.birim,
            mevcut_stok,
            urun.kritik_stok_seviyesi,
            durum
        ]
        
        for col_num, value in enumerate(data, 1):
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center')
            
            if durum == 'KRİTİK' and col_num == 7:
                cell.fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                cell.font = Font(color='DC2626', bold=True)
    
    # Sütun genişlikleri
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 12
    
    # BytesIO'ya kaydet
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output


def excel_export_zimmet_raporu(personel_id):
    """Personel zimmet Excel raporu oluştur"""
    from models import PersonelZimmet, PersonelZimmetDetay
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Zimmet Raporu"
    
    # Stil tanımlamaları
    baslik_font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
    baslik_fill = PatternFill(start_color='475569', end_color='475569', fill_type='solid')
    baslik_alignment = Alignment(horizontal='center', vertical='center')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Başlıklar
    headers = ['Zimmet No', 'Ürün Adı', 'Teslim Edilen', 'Kullanılan', 'Kalan', 'Tarih', 'Durum']
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = baslik_font
        cell.fill = baslik_fill
        cell.alignment = baslik_alignment
        cell.border = border
    
    # Veri satırları
    zimmetler = PersonelZimmet.query.filter_by(personel_id=personel_id).all()
    row_num = 2
    
    for zimmet in zimmetler:
        for detay in zimmet.detaylar:
            data = [
                zimmet.id,
                detay.urun.urun_adi,
                detay.miktar,
                detay.kullanilan_miktar,
                detay.kalan_miktar or (detay.miktar - detay.kullanilan_miktar),
                zimmet.zimmet_tarihi.strftime('%d.%m.%Y'),
                zimmet.durum.upper()
            ]
            
            for col_num, value in enumerate(data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.border = border
                cell.alignment = Alignment(horizontal='left', vertical='center')
            
            row_num += 1
    
    # Sütun genişlikleri
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 12
    
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    return output


def pdf_export_stok_raporu():
    """Stok durumu PDF raporu oluştur"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elements = []
    
    # Stil tanımlamaları
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=30,
        alignment=1
    )
    
    # Başlık
    title = Paragraph("STOK DURUM RAPORU", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Tablo verileri
    data = [['Ürün Kodu', 'Ürün Adı', 'Grup', 'Birim', 'Mevcut Stok', 'Kritik Seviye', 'Durum']]
    
    urunler = Urun.query.filter_by(aktif=True).all()
    stok_map = get_stok_toplamlari([urun.id for urun in urunler]) if urunler else {}
    for urun in urunler:
        mevcut_stok = stok_map.get(urun.id, 0)
        durum = 'KRİTİK' if mevcut_stok <= urun.kritik_stok_seviyesi else 'NORMAL'
        
        data.append([
            str(urun.id),
            urun.urun_adi[:30],
            urun.grup.grup_adi[:20],
            urun.birim,
            str(mevcut_stok),
            str(urun.kritik_stok_seviyesi),
            durum
        ])
    
    # Tablo oluştur
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#475569')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    
    # PDF oluştur
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def format_tarih(tarih):
    """Tarih formatla"""
    if not tarih:
        return ''
    return tarih.strftime('%d.%m.%Y %H:%M')


def format_para(tutar):
    """Para formatla"""
    if not tutar:
        return '0,00 ₺'
    return f'{tutar:,.2f} ₺'.replace(',', 'X').replace('.', ',').replace('X', '.')


def log_islem(islem_tipi, modul, islem_detay=None):
    """
    Sistem işlemlerini logla
    
    Args:
        islem_tipi: giris, cikis, ekleme, guncelleme, silme, goruntuleme
        modul: urun, stok, zimmet, oda, kat, personel vb.
        islem_detay: İşlem detayları (dict veya string)
    """
    try:
        kullanici_id = session.get('kullanici_id')
        
        # İşlem detayını JSON'a çevir
        if isinstance(islem_detay, dict):
            detay_json = json.dumps(islem_detay, ensure_ascii=False)
        else:
            detay_json = str(islem_detay) if islem_detay else None
        
        # IP adresi ve tarayıcı bilgisi
        ip_adresi = request.remote_addr if request else None
        tarayici = request.headers.get('User-Agent', '')[:200] if request else None
        
        # Log kaydı oluştur
        log = SistemLog(
            kullanici_id=kullanici_id,
            islem_tipi=islem_tipi,
            modul=modul,
            islem_detay=detay_json,
            ip_adresi=ip_adresi,
            tarayici=tarayici
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        # Log hatası uygulamayı durdurmamalı
        print(f'Log hatası: {str(e)}')
        try:
            db.session.rollback()
        except Exception:
            pass


def get_son_loglar(limit=50):
    """Son log kayıtlarını getir"""
    return SistemLog.query.order_by(SistemLog.islem_tarihi.desc()).limit(limit).all()


def get_kullanici_loglari(kullanici_id, limit=50):
    """Belirli bir kullanıcının log kayıtlarını getir"""
    return SistemLog.query.filter_by(kullanici_id=kullanici_id).order_by(
        SistemLog.islem_tarihi.desc()
    ).limit(limit).all()


def get_modul_loglari(modul, limit=50):
    """Belirli bir modülün log kayıtlarını getir"""
    return SistemLog.query.filter_by(modul=modul).order_by(
        SistemLog.islem_tarihi.desc()
    ).limit(limit).all()


def log_hata(exception, modul=None, extra_info=None):
    """
    Hataları hem dosyaya hem de veritabanına logla
    
    Args:
        exception: Exception objesi
        modul: Hangi modülde oluştu (örn: 'minibar', 'stok', 'zimmet')
        extra_info: Ek bilgiler (dict)
    
    Returns:
        HataLog objesi
    """
    try:
        kullanici_id = session.get('kullanici_id')
        
        # Exception bilgileri
        hata_tipi = type(exception).__name__
        hata_mesaji = str(exception)
        hata_detay = traceback.format_exc()
        
        # Request bilgileri
        url = request.url if request else None
        method = request.method if request else None
        ip_adresi = request.remote_addr if request else None
        tarayici = request.headers.get('User-Agent', '')[:200] if request else None
        
        # Ek bilgileri JSON'a çevir
        if extra_info:
            hata_detay += f"\n\nEk Bilgiler:\n{json.dumps(extra_info, ensure_ascii=False, indent=2)}"
        
        # Dosyaya logla
        logging.error(
            f"Hata: {hata_tipi} - {hata_mesaji}\n"
            f"Modül: {modul}\n"
            f"URL: {url}\n"
            f"Kullanıcı: {kullanici_id}\n"
            f"Detay:\n{hata_detay}"
        )
        
        # Veritabanına logla
        hata_log = HataLog(
            kullanici_id=kullanici_id,
            hata_tipi=hata_tipi,
            hata_mesaji=hata_mesaji[:500],  # İlk 500 karakter
            hata_detay=hata_detay,
            modul=modul,
            url=url[:500] if url else None,
            method=method,
            ip_adresi=ip_adresi,
            tarayici=tarayici
        )
        
        db.session.add(hata_log)
        db.session.commit()
        
        return hata_log
        
    except Exception as e:
        # Hata loglama hatası uygulamayı durdurmamalı
        print(f'HATA LOGLAMA HATASI: {str(e)}')
        logging.error(f'Hata loglama hatası: {str(e)}')
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


def get_son_hatalar(limit=50):
    """Son hata kayıtlarını getir"""
    return HataLog.query.order_by(HataLog.olusturma_tarihi.desc()).limit(limit).all()


def get_cozulmemis_hatalar():
    """Çözülmemiş hataları getir"""
    return HataLog.query.filter_by(cozuldu=False).order_by(HataLog.olusturma_tarihi.desc()).all()


def hata_cozuldu_isaretle(hata_id, cozum_notu=None):
    """Hatayı çözüldü olarak işaretle"""
    try:
        hata = HataLog.query.get(hata_id)
        if hata:
            hata.cozuldu = True
            hata.cozum_notu = cozum_notu
            db.session.commit()
            return True
    except Exception as e:
        logging.error(f'Hata çözüldü işaretleme hatası: {str(e)}')
        db.session.rollback()
    return False

