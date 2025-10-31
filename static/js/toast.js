/**
 * Toast Notification System
 * Modern, animasyonlu bildirim sistemi
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        
        // Toast container oluştur (lazy)
        if (document.getElementById('toast-container')) {
            this.container = document.getElementById('toast-container');
        } else {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none';
            this.container.style.maxWidth = '400px';
            document.body.appendChild(this.container);
        }
        
        this.initialized = true;
    }

    /**
     * Toast göster
     * @param {string} message - Gösterilecek mesaj
     * @param {string} type - success, error, warning, info
     * @param {number} duration - Gösterim süresi (ms)
     */
    show(message, type = 'info', duration = 4000) {
        if (!this.initialized) this.init();
        if (!this.container) return null;
        
        const toast = document.createElement('div');
        toast.className = `
            toast-item
            pointer-events-auto
            bg-white
            shadow-lg
            rounded-lg
            p-4
            mb-3
            flex
            items-start
            gap-3
            transform
            translate-x-full
            transition-all
            duration-300
            ease-out
            border-l-4
            ${this.getTypeClasses(type)}
        `;

        // İkon
        const icon = this.getIcon(type);

        // İçerik
        toast.innerHTML = `
            <div class="flex-shrink-0">
                ${icon}
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-slate-900">${message}</p>
            </div>
            <button class="flex-shrink-0 ml-2 text-slate-400 hover:text-slate-600 transition-colors" onclick="this.parentElement.remove()">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;

        this.container.appendChild(toast);

        // Animasyon başlat
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Otomatik kaldır
        if (duration > 0) {
            setTimeout(() => {
                this.remove(toast);
            }, duration);
        }

        return toast;
    }

    remove(toast) {
        toast.style.transform = 'translateX(150%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }

    getTypeClasses(type) {
        const classes = {
            'success': 'border-green-500',
            'error': 'border-red-500',
            'warning': 'border-yellow-500',
            'info': 'border-blue-500'
        };
        return classes[type] || classes['info'];
    }

    getIcon(type) {
        const icons = {
            'success': `
                <svg class="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            `,
            'error': `
                <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            `,
            'warning': `
                <svg class="w-6 h-6 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
            `,
            'info': `
                <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            `
        };
        return icons[type] || icons['info'];
    }

    // Kısayol metodlar
    success(message, duration = 4000) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration = 4000) {
        return this.show(message, 'info', duration);
    }
}

// Global instance oluştur
window.Toast = new ToastNotification();

// Global fonksiyonlar (kolay kullanım için)
window.showToast = (message, type, duration) => window.Toast.show(message, type, duration);
window.toastSuccess = (message, duration) => window.Toast.success(message, duration);
window.toastError = (message, duration) => window.Toast.error(message, duration);
window.toastWarning = (message, duration) => window.Toast.warning(message, duration);
window.toastInfo = (message, duration) => window.Toast.info(message, duration);
