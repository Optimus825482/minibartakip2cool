/**
 * QR Scanner JavaScript - Kat Sorumlusu
 * html5-qrcode kütüphanesi kullanır
 */

let html5QrCode = null;
let secilenOdaId = null; // Global variable tanımı

// jQuery kontrolü
if (typeof $ === 'undefined' || typeof jQuery === 'undefined') {
    console.error('jQuery yüklenmemiş! QR Scanner çalışmayacak.');
}

// QR ile başlat
function qrIleBaslat() {
    $('#qrScannerModal').modal('show');
    startQRScanner();
}

// Manuel seçim
function manuelBaslat() {
    $('#qrScannerModal').modal('hide');
    // Manuel form zaten sayfada var
}

// QR Scanner başlat
function startQRScanner() {
    const qrReaderDiv = document.getElementById("qrReader");
    
    if (!qrReaderDiv) {
        if (window.Toast) {
            window.Toast.error('QR okuyucu bulunamadı');
        } else {
            console.error('QR okuyucu bulunamadı');
        }
        return;
    }
    
    html5QrCode = new Html5Qrcode("qrReader");
    
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 }
    };
    
    html5QrCode.start(
        { facingMode: "environment" }, // Arka kamera
        config,
        (decodedText, decodedResult) => {
            // QR kod başarıyla okundu
            onQRCodeScanned(decodedText);
            stopQRScanner();
        },
        (errorMessage) => {
            // Hata (sessizce yoksay - sürekli okuma denemeleri)
        }
    ).catch((err) => {
        console.error('QR Scanner başlatma hatası:', err);
        if (window.Toast) {
            window.Toast.error('Kamera erişimi reddedildi veya hata oluştu');
        }
        $('#qrScannerModal').modal('hide');
    });
}

// QR Scanner durdur
function stopQRScanner() {
    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            html5QrCode.clear();
            html5QrCode = null;
        }).catch((err) => {
            console.error('QR Scanner durdurma hatası:', err);
        });
    }
}

// QR kod okunduğunda
function onQRCodeScanned(qrUrl) {
    // URL'den token'ı çıkar
    const urlParts = qrUrl.split('/');
    const token = urlParts[urlParts.length - 1];
    
    if (!token) {
        if (window.Toast) {
            window.Toast.error('Geçersiz QR kod formatı');
        }
        return;
    }
    
    // Loading göster
    $('#qrResult').html('<i class="fas fa-spinner fa-spin"></i> QR kod işleniyor...').show();
    
    // API'ye gönder
    $.ajax({
        url: '/api/kat-sorumlusu/qr-parse',
        method: 'POST',
        contentType: 'application/json',
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        },
        data: JSON.stringify({ token: token }),
        success: function(response) {
            if (response.success) {
                const data = response.data;
                
                // 1. Önce kat seç
                if ($('#kat_id').length) {
                    $('#kat_id').val(data.kat_id);
                    
                    // 2. Kat change eventini manuel tetikle ve odaları yükle
                    const katId = data.kat_id;
                    const odaSelect = $('#oda_id');
                    
                    // Oda dropdown'unu temizle ve loading göster
                    odaSelect.html('<option value="">Yükleniyor...</option>');
                    odaSelect.prop('disabled', true);
                    
                    // Odaları yükle
                    $.ajax({
                        url: `/kat-odalari?kat_id=${katId}`,
                        method: 'GET',
                        success: function(odaData) {
                            if (odaData.success && odaData.odalar.length > 0) {
                                // Oda dropdown'unu doldur
                                odaSelect.html('<option value="">Oda seçiniz...</option>');
                                odaData.odalar.forEach(oda => {
                                    odaSelect.append(`<option value="${oda.id}">${oda.oda_no}</option>`);
                                });
                                
                                // Dropdown'u aktif et
                                odaSelect.prop('disabled', false);
                                
                                // 3. Şimdi odayı seç
                                odaSelect.val(data.oda_id);
                                
                                // 4. Oda seçimini tetikle ve işlem tipi dropdown'unu güncelle
                                secilenOdaId = data.oda_id;
                                const islemTipiSelect = $('#islem_tipi');
                                
                                // İşlem tipi dropdown'unu aktif et ve placeholder'ı güncelle
                                islemTipiSelect.html(`
                                    <option value="">İşlem tipi seçiniz...</option>
                                    <option value="ilk_dolum">İlk Dolum</option>
                                    <option value="kontrol">Kontrol</option>
                                    <option value="doldurma">Doldurma</option>
                                `);
                                islemTipiSelect.prop('disabled', false);
                                
                                // Başarı mesajı
                                $('#qrResult').html(`
                                    <div class="alert alert-success">
                                        <i class="fas fa-check-circle"></i> 
                                        <strong>${data.kat_adi} - Oda ${data.oda_no}</strong> tanındı!
                                    </div>
                                `);
                                
                                if (window.Toast) {
                                    window.Toast.success(`Oda ${data.oda_no} otomatik seçildi!`);
                                }
                                
                                // Modal'ı 2 saniye sonra kapat
                                setTimeout(() => {
                                    $('#qrScannerModal').modal('hide');
                                }, 2000);
                            } else {
                                odaSelect.html('<option value="">Bu katta oda yok</option>');
                                if (window.Toast) {
                                    window.Toast.error('Bu katta oda bulunamadı');
                                }
                            }
                        },
                        error: function() {
                            odaSelect.html('<option value="">Hata oluştu</option>');
                            if (window.Toast) {
                                window.Toast.error('Odalar yüklenirken hata oluştu');
                            }
                        }
                    });
                }
            } else {
                $('#qrResult').html(`
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> ${response.message}
                    </div>
                `);
                if (window.Toast) {
                    window.Toast.error(response.message);
                }
            }
        },
        error: function(xhr) {
            let errorMsg = 'QR kod okunamadı';
            
            if (xhr.status === 429) {
                errorMsg = 'Çok fazla deneme. Lütfen 1 dakika bekleyin.';
            } else if (xhr.status === 404) {
                errorMsg = 'Geçersiz QR kod';
            }
            
            $('#qrResult').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-times-circle"></i> ${errorMsg}
                </div>
            `);
            if (window.Toast) {
                window.Toast.error(errorMsg);
            }
        }
    });
}

// Modal kapatıldığında scanner'ı durdur
$(document).ready(function() {
    $('#qrScannerModal').on('hidden.bs.modal', function () {
        stopQRScanner();
        $('#qrResult').hide();
    });
});
