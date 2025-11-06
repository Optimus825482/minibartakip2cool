/**
 * QR Scanner JavaScript - Kat Sorumlusu
 * html5-qrcode kütüphanesi kullanır
 */

let html5QrCode = null;

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
        toastr.error('QR okuyucu bulunamadı');
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
        toastr.error('Kamera erişimi reddedildi veya hata oluştu');
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
        toastr.error('Geçersiz QR kod formatı');
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
                
                // Form alanlarını doldur
                if ($('#kat_id').length) {
                    $('#kat_id').val(data.kat_id).trigger('change');
                }
                
                if ($('#oda_id').length) {
                    // Oda dropdown'unu güncelle
                    setTimeout(() => {
                        $('#oda_id').val(data.oda_id).trigger('change');
                    }, 500);
                }
                
                // Başarı mesajı
                $('#qrResult').html(`
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> 
                        <strong>${data.kat_adi} - Oda ${data.oda_no}</strong> tanındı!
                    </div>
                `);
                
                toastr.success(`Oda ${data.oda_no} otomatik seçildi!`);
                
                // Modal'ı 2 saniye sonra kapat
                setTimeout(() => {
                    $('#qrScannerModal').modal('hide');
                }, 2000);
            } else {
                $('#qrResult').html(`
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> ${response.message}
                    </div>
                `);
                toastr.error(response.message);
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
            toastr.error(errorMsg);
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
