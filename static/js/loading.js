/**
 * Loading & Progress Indicator System
 * Yükleme göstergeleri ve progress bar sistemi
 */

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.progressBar = null;
        this.overlay = null;
        this.initialized = false;
    }

    /**
     * Lazy initialization - sadece gerektiğinde DOM elementleri oluştur
     */
    init() {
        if (this.initialized) return;
        
        // Progress bar container
        this.createProgressBar();
        
        // Global loading overlay
        this.createLoadingOverlay();
        
        this.initialized = true;
    }

    /**
     * Sayfa üstünde ince progress bar oluştur
     */
    createProgressBar() {
        if (document.getElementById('global-progress-bar')) {
            this.progressBar = document.getElementById('global-progress-bar');
            return;
        }
        
        const progressBar = document.createElement('div');
        progressBar.id = 'global-progress-bar';
        progressBar.className = 'fixed top-0 left-0 right-0 h-1 bg-blue-500 z-[9999] transition-all duration-300 origin-left';
        progressBar.style.transform = 'scaleX(0)';
        progressBar.style.opacity = '0';
        document.body.appendChild(progressBar);
        this.progressBar = progressBar;
    }

    /**
     * Tam sayfa loading overlay oluştur
     */
    createLoadingOverlay() {
        if (document.getElementById('global-loading-overlay')) {
            this.overlay = document.getElementById('global-loading-overlay');
            return;
        }
        
        const overlay = document.createElement('div');
        overlay.id = 'global-loading-overlay';
        overlay.className = 'fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-[9998] hidden items-center justify-center';
        overlay.innerHTML = `
            <div class="bg-white dark:bg-slate-800 rounded-lg shadow-2xl p-8 flex flex-col items-center gap-4">
                <div class="relative">
                    <div class="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                </div>
                <p class="text-slate-700 dark:text-slate-300 font-medium" id="loading-message">Yükleniyor...</p>
            </div>
        `;
        document.body.appendChild(overlay);
        this.overlay = overlay;
    }

    /**
     * Progress bar göster ve animate et
     * @param {number} progress - 0-100 arası değer
     */
    showProgress(progress = 0) {
        if (!this.initialized) this.init();
        if (!this.progressBar) return;
        
        this.progressBar.style.opacity = '1';
        this.progressBar.style.transform = `scaleX(${progress / 100})`;
        
        if (progress >= 100) {
            setTimeout(() => {
                this.progressBar.style.opacity = '0';
                setTimeout(() => {
                    this.progressBar.style.transform = 'scaleX(0)';
                }, 300);
            }, 300);
        }
    }

    /**
     * Progress bar'ı otomatik animate et (belirsiz yükleme için)
     */
    startProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            this.showProgress(progress);
            
            if (!this.activeLoaders.size) {
                clearInterval(interval);
                this.showProgress(100);
            }
        }, 200);
        
        return interval;
    }

    /**
     * Tam sayfa loading overlay göster
     * @param {string} message - Gösterilecek mesaj
     */
    showOverlay(message = 'Yükleniyor...') {
        if (!this.initialized) this.init();
        if (!this.overlay) return;
        
        const messageEl = this.overlay.querySelector('#loading-message');
        if (messageEl) messageEl.textContent = message;
        
        this.overlay.classList.remove('hidden');
        this.overlay.classList.add('flex');
    }

    /**
     * Loading overlay'i gizle
     */
    hideOverlay() {
        if (!this.initialized || !this.overlay) return;
        
        this.overlay.classList.add('hidden');
        this.overlay.classList.remove('flex');
    }

    /**
     * Belirli bir element için inline loading göster
     * @param {HTMLElement} element - Loading gösterilecek element
     * @param {string} size - small, medium, large
     * @returns {HTMLElement} Loading spinner element
     */
    showInline(element, size = 'medium') {
        if (!element) return null;
        
        const sizes = {
            small: 'w-4 h-4 border-2',
            medium: 'w-8 h-8 border-3',
            large: 'w-12 h-12 border-4'
        };
        
        const spinner = document.createElement('div');
        spinner.className = `inline-loading-spinner ${sizes[size] || sizes.medium} border-blue-200 border-t-blue-600 rounded-full animate-spin`;
        spinner.dataset.loadingSpinner = 'true';
        
        // Element'in içeriğini sakla
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        
        // Loading spinner ekle
        element.innerHTML = '';
        element.appendChild(spinner);
        element.disabled = true;
        
        return spinner;
    }

    /**
     * Inline loading'i kaldır ve orijinal içeriği geri yükle
     * @param {HTMLElement} element - Loading kaldırılacak element
     */
    hideInline(element) {
        if (!element) return;
        
        const originalContent = element.dataset.originalContent;
        if (originalContent) {
            element.innerHTML = originalContent;
            delete element.dataset.originalContent;
        }
        
        element.disabled = false;
    }

    /**
     * Fetch istekleri için otomatik loading
     * @param {Promise} promise - Fetch promise
     * @param {Object} options - Loading options
     */
    async withLoading(promise, options = {}) {
        const {
            showProgress = true,
            showOverlay = false,
            overlayMessage = 'Yükleniyor...',
            element = null
        } = options;
        
        const loaderId = Math.random().toString(36).substr(2, 9);
        this.activeLoaders.add(loaderId);
        
        try {
            // Loading göstergeleri başlat
            let progressInterval = null;
            if (showProgress) {
                progressInterval = this.startProgress();
            }
            
            if (showOverlay) {
                this.showOverlay(overlayMessage);
            }
            
            if (element) {
                this.showInline(element);
            }
            
            // Promise'i bekle
            const result = await promise;
            
            // Loading göstergeleri kapat
            this.activeLoaders.delete(loaderId);
            
            if (progressInterval) {
                clearInterval(progressInterval);
            }
            
            if (showProgress) {
                this.showProgress(100);
            }
            
            if (showOverlay) {
                this.hideOverlay();
            }
            
            if (element) {
                this.hideInline(element);
            }
            
            return result;
        } catch (error) {
            this.activeLoaders.delete(loaderId);
            
            if (showOverlay) {
                this.hideOverlay();
            }
            
            if (element) {
                this.hideInline(element);
            }
            
            throw error;
        }
    }
}

// Global instance
window.Loading = new LoadingManager();

// Kısayol fonksiyonlar
window.showLoading = (message) => window.Loading.showOverlay(message);
window.hideLoading = () => window.Loading.hideOverlay();
window.showProgress = (progress) => window.Loading.showProgress(progress);

// Fetch wrapper - otomatik loading ile
window.fetchWithLoading = async (url, options = {}) => {
    const loadingOptions = options.loading || {};
    delete options.loading;
    
    return window.Loading.withLoading(
        fetch(url, options),
        loadingOptions
    );
};
