"""
Oda Kontrol ve Yeniden Dolum Unit Testleri
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
def auth_client(client):
    """Giriş yapmış test client"""
    # Test kullanıcısı oluştur
    kullanici = Kullanici(
        kullanici_adi='test_kat_sorumlusu',
        ad='Test',
        soyad='Kat Sorumlusu',
        rol='kat_sorumlusu',
        aktif=True
    )
    kullanici.sifre_belirle('test123')
    db.session.add(kullanici)
    db.session.commit()
    
    # Login
    with client.session_transaction() as sess:
        sess['kullanici_id'] = kullanici.id
        sess['kullanici_adi'] = kullanici.kullanici_adi
        sess['rol'] = kullanici.rol
    
    return client


@pytest.fixture
def test_data():
    """Test verileri oluştur"""
    # Kat oluştur
    kat = Kat(otel_id=1, kat_adi='1. Kat', kat_no=1, aktif=True)
    db.session.add(kat)
    db.session.flush()
    
    # Oda oluştur
    oda = Oda(kat_id=kat.id, oda_no='101', aktif=True)
    db.session.add(oda)
    db.session.flush()
    
    # Ürün grubu oluştur
    grup = UrunGrup(grup_adi='İçecekler', aktif=True)
    db.session.add(grup)
    db.session.flush()
    
    # Ürün oluştur
    urun = Urun(
        grup_id=grup.id,
        urun_adi='Coca Cola',
        birim='Adet',
        aktif=True
    )
    db.session.add(urun)
    db.session.flush()
    
    # Kullanıcı zimmet oluştur
    kullanici = Kullanici.query.filter_by(kullanici_adi='test_kat_sorumlusu').first()
    zimmet = PersonelZimmet(
        personel_id=kullanici.id,
        durum='aktif'
    )
    db.session.add(zimmet)
    db.session.flush()
    
    # Zimmet detay oluştur
    zimmet_detay = PersonelZimmetDetay(
        zimmet_id=zimmet.id,
        urun_id=urun.id,
        miktar=100,
        kullanilan_miktar=0,
        kalan_miktar=100
    )
    db.session.add(zimmet_detay)
    
    # Minibar işlem oluştur (ilk dolum)
    minibar_islem = MinibarIslem(
        oda_id=oda.id,
        personel_id=kullanici.id,
        islem_tipi='ilk_dolum'
    )
    db.session.add(minibar_islem)
    db.session.flush()
    
    # Minibar detay oluştur
    minibar_detay = MinibarIslemDetay(
        islem_id=minibar_islem.id,
        urun_id=urun.id,
        baslangic_stok=0,
        bitis_stok=5,
        eklenen_miktar=5,
        zimmet_detay_id=zimmet_detay.id
    )
    db.session.add(minibar_detay)
    
    db.session.commit()
    
    return {
        'oda_id': oda.id,
        'urun_id': urun.id,
        'zimmet_detay_id': zimmet_detay.id
    }


def test_minibar_urunler_basarili(auth_client, test_data):
    """Oda ürünlerini başarıyla getirme testi"""
    response = auth_client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': test_data['oda_id']}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['data']['urunler']) > 0
    assert data['data']['urunler'][0]['urun_adi'] == 'Coca Cola'


def test_minibar_urunler_bos(auth_client):
    """Boş minibar durumu testi"""
    # Boş oda oluştur
    kat = Kat(otel_id=1, kat_adi='2. Kat', kat_no=2, aktif=True)
    db.session.add(kat)
    db.session.flush()
    
    oda = Oda(kat_id=kat.id, oda_no='201', aktif=True)
    db.session.add(oda)
    db.session.commit()
    
    response = auth_client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': oda.id}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert len(data['data']['urunler']) == 0
    assert 'henüz ürün bulunmamaktadır' in data['message']


def test_minibar_urunler_gecersiz_oda(auth_client):
    """Geçersiz oda_id testi"""
    response = auth_client.post(
        '/api/kat-sorumlusu/minibar-urunler',
        data=json.dumps({'oda_id': 99999}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['success'] is False


def test_yeniden_dolum_basarili(auth_client, test_data):
    """Başarılı yeniden dolum testi"""
    response = auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': 3
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert data['data']['yeni_miktar'] == 8  # 5 + 3


def test_yeniden_dolum_yetersiz_stok(auth_client, test_data):
    """Yetersiz stok hatası testi"""
    response = auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': 200  # Zimmette 100 var
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = json.loads(response.data)
    assert data['success'] is False
    assert 'yeterli' in data['message'].lower()


def test_yeniden_dolum_gecersiz_miktar(auth_client, test_data):
    """Geçersiz miktar validasyonu testi"""
    # Negatif miktar
    response = auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': -5
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
    
    # Sıfır miktar
    response = auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': 0
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False


def test_zimmet_dusus_hesaplama(auth_client, test_data):
    """Zimmet düşüş hesaplaması testi"""
    # Başlangıç zimmet miktarı
    zimmet_detay = db.session.get(PersonelZimmetDetay, test_data['zimmet_detay_id'])
    baslangic_kalan = zimmet_detay.kalan_miktar
    
    # Yeniden dolum yap
    eklenecek = 10
    auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': eklenecek
        }),
        content_type='application/json'
    )
    
    # Zimmet kontrolü
    db.session.refresh(zimmet_detay)
    assert zimmet_detay.kalan_miktar == baslangic_kalan - eklenecek
    assert zimmet_detay.kullanilan_miktar == eklenecek


def test_minibar_miktar_guncelleme(auth_client, test_data):
    """Minibar miktar güncelleme testi"""
    # Yeniden dolum yap
    eklenecek = 5
    response = auth_client.post(
        '/api/kat-sorumlusu/yeniden-dolum',
        data=json.dumps({
            'oda_id': test_data['oda_id'],
            'urun_id': test_data['urun_id'],
            'eklenecek_miktar': eklenecek
        }),
        content_type='application/json'
    )
    
    # Yeni minibar işlemini kontrol et
    son_islem = MinibarIslem.query.filter_by(
        oda_id=test_data['oda_id']
    ).order_by(MinibarIslem.id.desc()).first()
    
    assert son_islem is not None
    assert son_islem.islem_tipi == 'doldurma'
    
    # Detayı kontrol et
    detay = MinibarIslemDetay.query.filter_by(
        islem_id=son_islem.id,
        urun_id=test_data['urun_id']
    ).first()
    
    assert detay is not None
    assert detay.baslangic_stok == 5
    assert detay.eklenen_miktar == eklenecek
    assert detay.bitis_stok == 10  # 5 + 5
