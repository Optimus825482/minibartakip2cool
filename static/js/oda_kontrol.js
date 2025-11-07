/**
 * Oda Kontrol ve Yeniden Dolum JavaScript Modülü
 */

console.log('=== ODA KONTROL JS BAŞLADI ===');

// Global değişkenler
let secilenOdaId = null;
let secilenOdaNo = null;
let secilenKatAdi = null;
let aktifUrun = null;
let qrScanner = null;

// CSRF Token
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
console.log('CSRF Token:', csrfToken);

/**
 * Sayfa yüklendiğinde
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Oda kontrol JS yüklendi');
    
    // Kat seçimi event listener
    const katSelect = document.getElementById('kat_id');
    if (katSelect) {
        katSelect.addEventListener('change', katSecildi);
        console.log('Kat select event listener eklendi');
    } else {
        console.error('kat_id elementi bulunamadı!');
    }
    
    // Oda seçimi event listener
    const odaSelect = document.getElementById('oda_id');
    if (odaSelect) {
        odaSelect.addEventListener('change', odaSecildi);
        console.log('Oda select event listener eklendi');
    } else {
        console.error('oda_id elementi bulunamadı!');
    }
});

/**
 * Kat seçildiğinde odaları yükle
 */
async function katSecildi() {
    const katId = document.getElementById('kat_id').value;
    const odaSelect = document.getElementById('oda_id');
    
    console.log('Kat seçildi:', katId);
    
    // Reset
    odaSelect.innerHTML = '<option value="">Oda seçiniz...</option>';
    odaSelect.disabled = true;
    urunListesiniGizle();
    
    if (!katId) {
        console.log('Kat ID boş, işlem iptal');
        return;
    }
    
    try {
        console.log('Odalar getiriliyor...');
        const response = await fetch(`/kat-odalari?kat_id=${katId}`);
        const data = await response.json();
        
        console.log('API yanıtı:', data);
        
        if (data.success && data.odalar && data.odalar.length > 0) {
            console.log(`${data.odalar.length} oda bulundu`);
            data.odalar.forEach(oda => {
                const option = document.createElement('option');
                option.value = oda.id;
                option.textContent = oda.oda_no;
                odaSelect.appendChild(option);
            });
            odaSelect.disabled = false;
        } else {
            console.log('Oda bulunamadı');
            odaSelect.innerHTML = '<option value="">Bu katta oda yok</option>';
        }
    } catch (error) {
        console.error('Hata:', error);
        hataGoster('Odalar yüklenirken bir hata oluştu');
    }
}

/**
 * Oda seçildiğinde ürünleri getir
 */
async function odaSecildi() {
    const odaId = document.getElementById('oda_id').value;
    
    if (!odaId) {
        urunListesiniGizle();
        return;
    }
    
    secilenOdaId = odaId;
    await minibarUrunleriniGetir(odaId);
}

/**
 * Minibar ürünlerini API'den getir
 */
async function minibarUrunleriniGetir(odaId) {
    loadingGoster();
    
    try {
        const response = await fetch('/api/kat-sorumlusu/minibar-urunler', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ oda_id: odaId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            secilenOdaNo = data.data.oda_no;
            secilenKatAdi = data.data.kat_adi;
            
            if (data.data.urunler.length === 0) {
                bosDurumGoster();
            } else {
                urunListesiGoster(data.data.urunler);
            }
        } else {
            hataGoster(data.message || 'Ürünler yüklenirken hata oluştu');
        }
    } catch (error) {
        console.error('Hata:', error);
        hataGoster('Ürünler yüklenirken bir hata oluştu');
    } finally {
        loadingGizle();
    }
}

/**
 * Ürün listesini göster
 */
function urunListesiGoster(urunler) {
    // Container'ı göster
    document.getElementById('urun_listesi_container').classList.remove('hidden');
    document.getElementById('bos_durum_mesaji').classList.add('hidden');
    document.getElementById('urun_tablosu').classList.remove('hidden');
    
    // Oda bilgilerini güncelle
    document.getElementById('secili_oda_no').textContent = secilenOdaNo;
    document.getElementById('secili_kat_adi').textContent = secilenKatAdi;
    
    // Tablo body'sini temizle
    const tbody = document.getElementById('urun_tbody');
    tbody.innerHTML = '';
    
    // Ürünleri ekle
    urunler.forEach(urun => {
        const tr = document.createElement('tr');
        tr.className = 'cursor-pointer transition-colors';
        tr.onclick = () => uruneTiklandi(urun);
        
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                ${urun.urun_adi}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                ${urun.mevcut_miktar}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                ${urun.birim}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                <button onclick="event.stopPropagation(); uruneTiklandi(${JSON.stringify(urun).replace(/"/g, '&quot;')})"
                    class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                    <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Dolum Yap
                </button>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

/**
 * Boş durum mesajını göster
 */
function bosDurumGoster() {
    document.getElementById('urun_listesi_container').classList.remove('hidden');
    document.getElementById('bos_durum_mesaji').classList.remove('hidden');
    document.getElementById('urun_tablosu').classList.add('hidden');
    
    // Oda bilgilerini güncelle
    document.getElementById('secili_oda_no').textContent = secilenOdaNo;
    document.getElementById('secili_kat_adi').textContent = secilenKatAdi;
}

/**
 * Ürün listesini gizle
 */
function urunListesiniGizle() {
    document.getElementById('urun_listesi_container').classList.add('hidden');
    secilenOdaId = null;
    secilenOdaNo = null;
    secilenKatAdi = null;
}

/**
 * Ürüne tıklandığında yeniden dolum modalını aç
 */
function uruneTiklandi(urun) {
    aktifUrun = urun;
    yenidenDolumModalAc(urun);
}

/**
 * Yeniden dolum modalını aç
 */
function yenidenDolumModalAc(urun) {
    document.getElementById('modal_urun_adi').textContent = urun.urun_adi;
    document.getElementById('modal_mevcut_miktar').textContent = urun.mevcut_miktar;
    document.getElementById('modal_birim').textContent = urun.birim;
    document.getElementById('eklenecek_miktar').value = '';
    
    document.getElementById('yeniden_dolum_modal').classList.remove('hidden');
    document.getElementById('eklenecek_miktar').focus();
}

/**
 * Yeniden dolum modalını kapat
 */
function yenidenDolumModalKapat() {
    document.getElementById('yeniden_dolum_modal').classList.add('hidden');
    aktifUrun = null;
}

/**
 * Dolum yap butonuna tıklandığında
 */
function dolumYap() {
    const eklenecekMiktar = parseFloat(document.getElementById('eklenecek_miktar').value);
    
    // Validasyon
    if (!eklenecekMiktar || eklenecekMiktar <= 0) {
        hataGoster('Lütfen geçerli bir miktar giriniz');
        return;
    }
    
    // Onay modalını aç
    onayModalAc(eklenecekMiktar);
}

/**
 * Onay modalını aç
 */
function onayModalAc(eklenecekMiktar) {
    const mevcutMiktar = aktifUrun.mevcut_miktar;
    const yeniMiktar = mevcutMiktar + eklenecekMiktar;
    
    document.getElementById('onay_urun_adi').textContent = aktifUrun.urun_adi;
    document.getElementById('onay_mevcut_miktar').textContent = `${mevcutMiktar} ${aktifUrun.birim}`;
    document.getElementById('onay_eklenecek_value').textContent = eklenecekMiktar;
    document.getElementById('onay_yeni_miktar').textContent = `${yeniMiktar} ${aktifUrun.birim}`;
    document.getElementById('onay_zimmet_dusum').textContent = `${eklenecekMiktar} ${aktifUrun.birim} ${aktifUrun.urun_adi}`;
    
    // Yeniden dolum modalını kapat
    yenidenDolumModalKapat();
    
    // Onay modalını göster
    document.getElementById('onay_modal').classList.remove('hidden');
}

/**
 * Onay modalını kapat
 */
function onayModalKapat() {
    document.getElementById('onay_modal').classList.add('hidden');
}

/**
 * İşlemi onayla ve API'ye gönder
 */
async function islemOnayla() {
    const eklenecekMiktar = parseFloat(document.getElementById('eklenecek_miktar').value);
    
    // Butonları disable et
    document.getElementById('onay_btn').disabled = true;
    
    try {
        const response = await fetch('/api/kat-sorumlusu/yeniden-dolum', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                oda_id: secilenOdaId,
                urun_id: aktifUrun.urun_id,
                eklenecek_miktar: eklenecekMiktar
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            basariGoster(data.message || 'Dolum işlemi başarıyla tamamlandı');
            onayModalKapat();
            
            // Ürün listesini yenile
            await minibarUrunleriniGetir(secilenOdaId);
        } else {
            hataGoster(data.message || 'İşlem sırasında bir hata oluştu');
        }
    } catch (error) {
        console.error('Hata:', error);
        hataGoster('İşlem sırasında bir hata oluştu. Lütfen tekrar deneyiniz');
    } finally {
        document.getElementById('onay_btn').disabled = false;
    }
}

/**
 * QR kod okutmayı başlat
 */
function qrIleBaslat() {
    document.getElementById('qr_modal').classList.remove('hidden');
    
    if (!qrScanner) {
        qrScanner = new Html5Qrcode("qr_reader");
    }
    
    qrScanner.start(
        { facingMode: "environment" },
        {
            fps: 10,
            qrbox: { width: 250, height: 250 }
        },
        onQrCodeScanned,
        onQrCodeError
    ).catch(err => {
        console.error('QR okuyucu başlatılamadı:', err);
        hataGoster('Kamera erişimi sağlanamadı');
        qrModalKapat();
    });
}

/**
 * QR kod okunduğunda
 */
async function onQrCodeScanned(decodedText) {
    // QR okuyucuyu durdur
    if (qrScanner) {
        qrScanner.stop();
    }
    
    qrModalKapat();
    
    try {
        // Token'ı parse et
        const response = await fetch('/api/kat-sorumlusu/qr-parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ token: decodedText })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Kat ve oda seçimini otomatik yap
            document.getElementById('kat_id').value = data.data.kat_id;
            await katSecildi();
            
            document.getElementById('oda_id').value = data.data.oda_id;
            await odaSecildi();
            
            basariGoster(`Oda ${data.data.oda_no} seçildi`);
        } else {
            hataGoster(data.message || 'QR kod okunamadı');
        }
    } catch (error) {
        console.error('Hata:', error);
        hataGoster('QR kod işlenirken hata oluştu');
    }
}

/**
 * QR kod okuma hatası
 */
function onQrCodeError(error) {
    // Sessizce logla (sürekli hata mesajı gösterme)
    console.debug('QR okuma hatası:', error);
}

/**
 * QR modalını kapat
 */
function qrModalKapat() {
    if (qrScanner) {
        qrScanner.stop().catch(err => console.error('QR durdurma hatası:', err));
    }
    document.getElementById('qr_modal').classList.add('hidden');
}

/**
 * Loading spinner göster
 */
function loadingGoster() {
    document.getElementById('loading_spinner').classList.remove('hidden');
}

/**
 * Loading spinner gizle
 */
function loadingGizle() {
    document.getElementById('loading_spinner').classList.add('hidden');
}

/**
 * Başarı mesajı göster (Toast)
 */
function basariGoster(mesaj) {
    // Basit toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    toast.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>${mesaj}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Hata mesajı göster (Toast)
 */
function hataGoster(mesaj) {
    // Basit toast notification
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    toast.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <span>${mesaj}</span>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
