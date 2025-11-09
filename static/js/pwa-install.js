/**
 * PWA Kurulum Uyarısı
 * Mobil ve tablet cihazlarda otomatik olarak kurulum uyarısı gösterir
 */

(function() {
    'use strict';

    let deferredPrompt;
    let installPromptShown = false;

    // Cihaz tipini kontrol et
    function isMobileOrTablet() {
        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
        
        // Tablet kontrolü - daha kapsamlı
        const isTablet = /(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(userAgent) ||
                        (navigator.maxTouchPoints && navigator.maxTouchPoints > 2 && /MacIntel/.test(navigator.platform));
        
        // Mobil kontrolü
        const isMobile = /Mobile|Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
        
        // Ekran boyutu kontrolü (tablet için)
        const isLargeScreen = window.innerWidth >= 768 && window.innerWidth <= 1366;
        
        return isMobile || isTablet || (isLargeScreen && 'ontouchstart' in window);
    }

    // iOS kontrolü
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }

    // Standalone modda mı kontrol et
    function isInStandaloneMode() {
        return (window.matchMedia('(display-mode: standalone)').matches) || 
               (window.navigator.standalone) || 
               document.referrer.includes('android-app://');
    }

    // Daha önce kurulum uyarısı gösterildi mi?
    function wasPromptShown() {
        const lastShown = localStorage.getItem('pwa-install-prompt-shown');
        if (!lastShown) return false;
        
        // 7 gün geçtiyse tekrar göster
        const daysSinceShown = (Date.now() - parseInt(lastShown)) / (1000 * 60 * 60 * 24);
        return daysSinceShown < 7;
    }

    // Kurulum uyarısını kaydet
    function markPromptShown() {
        localStorage.setItem('pwa-install-prompt-shown', Date.now().toString());
        installPromptShown = true;
    }

    // Android/Chrome PWA kurulum uyarısı
    function showAndroidInstallPrompt() {
        if (!deferredPrompt || installPromptShown) return;

        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.innerHTML = `
            <div style="position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px; box-shadow: 0 -4px 12px rgba(0,0,0,0.15); z-index: 9999; animation: slideUp 0.3s ease-out;">
                <div style="max-width: 600px; margin: 0 auto; display: flex; align-items: center; gap: 12px;">
                    <div style="flex-shrink: 0; width: 48px; height: 48px; background: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                        📱
                    </div>
                    <div style="flex: 1;">
                        <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">Minibar Takip Uygulaması</div>
                        <div style="font-size: 13px; opacity: 0.95;">Ana ekrana ekleyerek daha hızlı erişin</div>
                    </div>
                    <button id="pwa-install-btn" style="background: white; color: #667eea; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; font-size: 14px; cursor: pointer; white-space: nowrap;">
                        Yükle
                    </button>
                    <button id="pwa-close-btn" style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 8px; border-radius: 8px; cursor: pointer; font-size: 18px; line-height: 1; width: 32px; height: 32px;">
                        ✕
                    </button>
                </div>
            </div>
            <style>
                @keyframes slideUp {
                    from { transform: translateY(100%); }
                    to { transform: translateY(0); }
                }
            </style>
        `;

        document.body.appendChild(banner);

        // Yükle butonu
        document.getElementById('pwa-install-btn').addEventListener('click', async () => {
            banner.remove();
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`PWA kurulum sonucu: ${outcome}`);
            deferredPrompt = null;
            markPromptShown();
        });

        // Kapat butonu
        document.getElementById('pwa-close-btn').addEventListener('click', () => {
            banner.remove();
            markPromptShown();
        });
    }

    // iOS Safari kurulum uyarısı
    function showIOSInstallPrompt() {
        if (installPromptShown) return;

        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.innerHTML = `
            <div style="position: fixed; bottom: 0; left: 0; right: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; box-shadow: 0 -4px 12px rgba(0,0,0,0.15); z-index: 9999; animation: slideUp 0.3s ease-out;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px;">
                        <div style="flex-shrink: 0; width: 48px; height: 48px; background: white; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px;">
                            📱
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: bold; font-size: 16px; margin-bottom: 4px;">Minibar Takip Uygulaması</div>
                            <div style="font-size: 13px; opacity: 0.95; line-height: 1.4;">
                                Ana ekrana eklemek için:
                            </div>
                        </div>
                        <button id="pwa-close-btn" style="background: rgba(255,255,255,0.2); color: white; border: none; padding: 8px; border-radius: 8px; cursor: pointer; font-size: 18px; line-height: 1; width: 32px; height: 32px; flex-shrink: 0;">
                            ✕
                        </button>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.6;">
                        1. Aşağıdaki <strong>Paylaş</strong> butonuna <span style="display: inline-block; background: rgba(255,255,255,0.3); padding: 2px 8px; border-radius: 4px; margin: 0 2px;">⬆️</span> dokunun<br>
                        2. <strong>"Ana Ekrana Ekle"</strong> seçeneğini bulun<br>
                        3. <strong>"Ekle"</strong> butonuna dokunun
                    </div>
                </div>
            </div>
            <style>
                @keyframes slideUp {
                    from { transform: translateY(100%); }
                    to { transform: translateY(0); }
                }
            </style>
        `;

        document.body.appendChild(banner);

        document.getElementById('pwa-close-btn').addEventListener('click', () => {
            banner.remove();
            markPromptShown();
        });
    }

    // Sidebar butonlarını göster/gizle (tüm butonlar için)
    function toggleSidebarButton(show) {
        const sidebarBtns = document.querySelectorAll('.pwa-install-button');
        sidebarBtns.forEach(btn => {
            if (show) {
                btn.classList.remove('hidden');
            } else {
                btn.classList.add('hidden');
            }
        });
        console.log(`PWA sidebar butonları ${show ? 'gösterildi' : 'gizlendi'} (${sidebarBtns.length} buton)`);
    }

    // Sidebar butonlarına tıklama event'i (tüm butonlar için)
    function setupSidebarButton() {
        const sidebarBtns = document.querySelectorAll('.pwa-install-button');
        sidebarBtns.forEach(btn => {
            if (btn && deferredPrompt) {
                btn.addEventListener('click', async () => {
                    if (!deferredPrompt) return;
                    
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`PWA kurulum sonucu: ${outcome}`);
                    deferredPrompt = null;
                    toggleSidebarButton(false);
                    markPromptShown();
                });
            }
        });
        console.log(`PWA sidebar butonlarına event listener eklendi (${sidebarBtns.length} buton)`);
    }

    // beforeinstallprompt event'ini yakala (Android/Chrome)
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Sidebar butonunu göster
        toggleSidebarButton(true);
        setupSidebarButton();
        
        // Mobil/tablet ve standalone modda değilse banner göster
        if (isMobileOrTablet() && !isInStandaloneMode() && !wasPromptShown()) {
            // 2 saniye bekle, sonra göster
            setTimeout(() => {
                showAndroidInstallPrompt();
            }, 2000);
        }
    });

    // Sayfa yüklendiğinde iOS kontrolü yap
    window.addEventListener('load', () => {
        console.log('PWA Install: Sayfa yüklendi');
        console.log('iOS:', isIOS());
        console.log('Standalone:', isInStandaloneMode());
        console.log('Mobile/Tablet:', isMobileOrTablet());
        
        // iOS için sidebar butonlarını göster
        if (isIOS() && !isInStandaloneMode()) {
            toggleSidebarButton(true);
            
            // iOS için sidebar butonlarına tıklandığında talimat göster
            const sidebarBtns = document.querySelectorAll('.pwa-install-button');
            sidebarBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    showIOSInstallPrompt();
                });
            });
        }
        
        // iOS ve standalone modda değilse banner göster
        if (isIOS() && !isInStandaloneMode() && !wasPromptShown()) {
            // 3 saniye bekle, sonra göster
            setTimeout(() => {
                showIOSInstallPrompt();
            }, 3000);
        }
    });

    // PWA kurulduğunda
    window.addEventListener('appinstalled', () => {
        console.log('PWA başarıyla kuruldu!');
        deferredPrompt = null;
        
        // Banner varsa kaldır
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.remove();
        }
        
        // Sidebar butonunu gizle
        toggleSidebarButton(false);
    });

})();
