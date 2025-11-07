"""
Oda Kontrol ve Yeniden Dolum Integration Testleri
"""

import pytest
import json
from app import app, db
from models import (
    Kullanici, Kat, Oda, Urun, UrunGrup,
    PersonelZimmet, PersonelZimmetDetay,
    MinibarIslem, MinibarIslemDetay
)


@pytest.fixture
def client():
    """Test client oluştur"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def setup_full_scenario():
    """Tam senaryo için test verileri"""
    # Kullanıcı
    kullanici = Kullanici(
        kullanici_adi='test_kat',
        ad='Test',
        soyad='User',
        rol='kat_sorumlusu',
        aktif=True
    )
    kullanici.sifre_belirle('test123')
    db.session.add(kullanici)
    db.session.flush()
    
    # Kat ve Oda
    kat = Kat(otel_id=1, kat_adi='1. Kat', kat_no=1, aktif=True)
    db.session.add(kat)
    db.session.flush()
    
    oda = Oda(kat_id=kat.id, oda_no='101', aktif=True)
    db.session.add(oda)
    db.session.flush()
    
    # Ürün grubu ve ürünler
    grup = UrunGrup(grup_adi='İçecekler', aktif=True)
    db.session.add(grup)
    db.session.flush()
    
    urun1 = Urun(grup_id=grup.id, urun_adi='Coca Cola', birim='Adet', aktif=True)
    urun2 = Urun(grup_id=grup.id, urun_adi='Fanta', birim='Adet', aktif=True)
    db.session.add_all([urun1, urun2])
    db.session.flush()
    
    # Zimmet
    zimmet = PersonelZimmet(personel_id=kullanici.id, durum='aktif')
    db.session.add(zimmet)
    db.session.flush()
    
    zimmet_detay1 = PersonelZimmetDetay(
        zimmet_id=zimmet.id,
        urun_id=urun1.id,
        miktar=50,
        kullanilan_miktar=0,
        kalan_miktar=50
    )
    zimmet_detay2 = PersonelZimmetDetay(
        zimmet_id=zimmet.id,
        urun_id=urun2.id,
        miktar=30,
        kullanilan_miktar=0,
        kalan_miktar=30
    )
    db.session.add_all([zimmet_detay1, zimmet_detay2])
    
    # İlk dolum
    minibar_islem = MinibarIslem(
        oda_id=oda.id,
        personel_id=kullanici.id,
        islem_tipi='ilk_dolum'
    )
    db.session.add(minibar_islem)
    db.session.flush()
    
    detay1 = MinibarIslemDetay(
        islem_id=minibar_islem.id,
        urun_id=urun1.id,
        baslangic_stok=0,
        bitis_stok=10,
        eklenen_miktar=10,
        zimmet_detay_id=zimmet_detay1.id
    )
    detay2 = MinibarIslemDetay(
        islem_id=minibar_islem.id,
        urun_id=urun2.id,
        baslangic_stok=0,
        bitis_stok=5,
        eklenen_miktar=5,
        zimmet_detay_id=zimmet_detay2.id
    )
    db.session.add_all([detay1, detay2])
    
    db.session.commit()
    
    return {
        'kullanici_id': kullanici.id,
        'oda_id': oda.id,
        'kat_id': kat.id,
        'urun1_id': urun1.id,
        'urun2_id': urun2.id
    }


def test_oda_kontrol_tam_akis(client, setup_full_scenario):
    """Oda seçiminden dolum işlemine kadar tam akış testi"""
    data = setup_full_scenario
    
    # Login
    with client.session_transaction() as sess:
        sess['kullanici_id'] = data['kullanici_id']
        sess['rol'] = 'kat_sorumlusu'
    
    # 1. Oda seç ve ürünleri getir
    response = client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': data['oda_id']}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    urunler_data = json.loads(response.data)
    assert urunler_data['success'] is True
    assert len(urunler_data['data']['urunler']) == 2
    
    # 2. İlk ürüne yeniden dolum yap
    response = client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': data['oda_id'],
            'urun_id': data['urun1_id'],
            'eklenecek_miktar': 5
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    dolum_data = json.loads(response.data)
    assert dolum_data['success'] is True
    assert dolum_data['data']['yeni_miktar'] == 15  # 10 + 5
    
    # 3. Güncel ürün listesini kontrol et
    response = client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': data['oda_id']}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    guncel_data = json.loads(response.data)
    coca_cola = next(u for u in guncel_data['data']['urunler'] if u['urun_id'] == data['urun1_id'])
    assert coca_cola['mevcut_miktar'] == 15
    
    # 4. Stok kontrolü - zimmet düştü mü?
    zimmet_detay = PersonelZimmetDetay.query.filter_by(
        urun_id=data['urun1_id']
    ).first()
    assert zimmet_detay.kalan_miktar == 45  # 50 - 5


def test_coklu_dolum_islemi(client, setup_full_scenario):
    """Çoklu dolum işlemi testi"""
    data = setup_full_scenario
    
    # Login
    with client.session_transaction() as sess:
        sess['kullanici_id'] = data['kullanici_id']
        sess['rol'] = 'kat_sorumlusu'
    
    # Birinci dolum
    client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': data['oda_id'],
            'urun_id': data['urun1_id'],
            'eklenecek_miktar': 3
        }),
        content_type='application/json'
    )
    
    # İkinci dolum
    client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': data['oda_id'],
            'urun_id': data['urun1_id'],
            'eklenecek_miktar': 2
        }),
        content_type='application/json'
    )
    
    # Kontrol
    response = client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': data['oda_id']}),
        content_type='application/json'
    )
    
    data_response = json.loads(response.data)
    coca_cola = next(u for u in data_response['data']['urunler'] if u['urun_id'] == data['urun1_id'])
    assert coca_cola['mevcut_miktar'] == 15  # 10 + 3 + 2
    
    # Zimmet kontrolü
    zimmet_detay = PersonelZimmetDetay.query.filter_by(
        urun_id=data['urun1_id']
    ).first()
    assert zimmet_detay.kalan_miktar == 45  # 50 - 5


def test_stok_tukenmesi_senaryosu(client, setup_full_scenario):
    """Stok tükenmesi senaryosu testi"""
    data = setup_full_scenario
    
    # Login
    with client.session_transaction() as sess:
        sess['kullanici_id'] = data['kullanici_id']
        sess['rol'] = 'kat_sorumlusu'
    
    # Tüm stoğu kullanmaya çalış
    response = client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': data['oda_id'],
            'urun_id': data['urun1_id'],
            'eklenecek_miktar': 50  # Zimmette 50 var
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    # Şimdi daha fazla eklemeye çalış
    response = client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': data['oda_id'],
            'urun_id': data['urun1_id'],
            'eklenecek_miktar': 1
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    error_data = json.loads(response.data)
    assert error_data['success'] is False
    assert 'yeterli' in error_data['message'].lower()
