/**
 * Minibar Takip Sistemi - Form Validation Modülü
 * Bu modül tüm formlarda kullanılabilecek kapsamlı client-side validation sağlar
 */

class FormValidator {
    constructor(formElement, options = {}) {
        this.form = formElement;
        this.options = {
            showSuccessIcons: true,
            showErrorIcons: true,
            showHelpText: true,
            validateOnInput: true,
            validateOnBlur: true,
            stopOnFirstError: false,
            scrollToError: true,
            focusFirstError: true,
            ...options
        };
        this.validationRules = {};
        this.fieldStates = new Map();
        this.isValid = false;
        this.init();
    }

    /**
     * Form validator'ı başlat
     */
    init() {
        this.setupEventListeners();
        this.updateSubmitButton();
    }

    /**
     * Validation kurallarını tanımla
     */
    setRules(rules) {
        this.validationRules = rules;
    }

    /**
     * Event listener'ları kur
     */
    setupEventListeners() {
        // Input event listeners
        if (this.options.validateOnInput) {
            Object.keys(this.validationRules).forEach(fieldName => {
                const field = this.getField(fieldName);
                if (field) {
                    field.addEventListener('input', (e) => {
                        this.validateField(fieldName);
                        this.updateSubmitButton();
                    });
                }
            });
        }

        // Blur event listeners
        if (this.options.validateOnBlur) {
            Object.keys(this.validationRules).forEach(fieldName => {
                const field = this.getField(fieldName);
                if (field) {
                    field.addEventListener('blur', (e) => {
                        this.validateField(fieldName);
                    });
                }
            });
        }

        // Submit event listener
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm(true)) { // scroll ve focus sadece submit'te
                e.preventDefault();
                return false;
            }
            this.showLoadingState();
            return true;
        });

        // Form değişikliklerini dinle
        this.form.addEventListener('input', () => {
            this.updateSubmitButton();
        });
    }

    /**
     * Field element'ini al
     */
    getField(fieldName) {
        return this.form.querySelector(`[name="${fieldName}"]`) || 
               this.form.querySelector(`#${fieldName}`);
    }

    /**
     * Tek bir field'ı validate et
     */
    validateField(fieldName) {
        const field = this.getField(fieldName);
        if (!field) return { isValid: true };

        const rules = this.validationRules[fieldName];
        if (!rules) return { isValid: true };

        const value = field.value.trim();
        const result = this.applyRules(fieldName, value, rules);
        
        this.updateFieldState(fieldName, result);
        return result;
    }

    /**
     * Validation kurallarını uygula
     */
    applyRules(fieldName, value, rules) {
        // Required check
        if (rules.required && (!value || value.length === 0)) {
            return { isValid: false, message: rules.messages?.required || `${fieldName} is required.` };
        }

        // Optional field with no value
        if (!value || value.length === 0) {
            return { isValid: true };
        }

        // Min length check
        if (rules.minLength && value.length < rules.minLength) {
            return { 
                isValid: false, 
                message: rules.messages?.minLength || `${fieldName} must be at least ${rules.minLength} characters.` 
            };
        }

        // Max length check
        if (rules.maxLength && value.length > rules.maxLength) {
            return { 
                isValid: false, 
                message: rules.messages?.maxLength || `${fieldName} must not exceed ${rules.maxLength} characters.` 
            };
        }

        // Pattern check
        if (rules.pattern && !rules.pattern.test(value)) {
            return { 
                isValid: false, 
                message: rules.messages?.pattern || `${fieldName} format is invalid.` 
            };
        }

        // Custom validation
        if (rules.custom) {
            const customResult = rules.custom(value);
            if (typeof customResult === 'string') {
                return { isValid: false, message: customResult };
            } else if (typeof customResult === 'object' && !customResult.isValid) {
                return customResult;
            }
        }

        // Email validation
        if (rules.email && !this.isValidEmail(value)) {
            return { 
                isValid: false, 
                message: rules.messages?.email || 'Please enter a valid email address.' 
            };
        }

        // Number validation
        if (rules.number) {
            const num = parseFloat(value);
            if (isNaN(num)) {
                return { 
                    isValid: false, 
                    message: rules.messages?.number || 'Please enter a valid number.' 
                };
            }

            if (rules.min !== undefined && num < rules.min) {
                return { 
                    isValid: false, 
                    message: rules.messages?.min || `Value must be at least ${rules.min}.` 
                };
            }

            if (rules.max !== undefined && num > rules.max) {
                return { 
                    isValid: false, 
                    message: rules.messages?.max || `Value must not exceed ${rules.max}.` 
                };
            }
        }

        return { isValid: true };
    }

    /**
     * Email validasyonu
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Field state'ini güncelle
     */
    updateFieldState(fieldName, validationResult) {
        const field = this.getField(fieldName);
        if (!field) return;

        const errorDiv = this.form.querySelector(`#${fieldName}_error`);
        const helpText = this.form.querySelector(`#${fieldName}_help`);
        const validationIcon = field.parentNode.querySelector('.validation-icon');
        const errorIcon = field.parentNode.querySelector('.error-icon');

        // Remove previous state classes
        field.classList.remove(
            'border-green-500', 'border-red-500', 
            'ring-green-500', 'ring-red-500'
        );

        if (validationResult.isValid) {
            // Success state
            field.classList.add('border-green-500', 'ring-green-500');
            
            if (this.options.showSuccessIcons && validationIcon) {
                validationIcon.classList.remove('hidden');
            }
            if (errorIcon) {
                errorIcon.classList.add('hidden');
            }
            if (this.options.showHelpText && helpText) {
                helpText.classList.remove('hidden');
            }
            if (errorDiv) {
                errorDiv.classList.add('hidden');
            }
        } else {
            // Error state
            field.classList.add('border-red-500', 'ring-red-500');
            
            if (validationIcon) {
                validationIcon.classList.add('hidden');
            }
            if (this.options.showErrorIcons && errorIcon) {
                errorIcon.classList.remove('hidden');
            }
            if (helpText) {
                helpText.classList.add('hidden');
            }
            if (errorDiv) {
                errorDiv.classList.remove('hidden');
                const messageElement = errorDiv.querySelector('p');
                if (messageElement) {
                    messageElement.textContent = validationResult.message;
                }
            }
        }

        // Save state
        this.fieldStates.set(fieldName, validationResult);
    }

    /**
     * Tüm formu validate et
     * @param {boolean} scrollAndFocus - Scroll ve focus işlemlerini yap
     */
    validateForm(scrollAndFocus = false) {
        let isValid = true;
        let firstErrorField = null;

        Object.keys(this.validationRules).forEach(fieldName => {
            const result = this.validateField(fieldName);
            if (!result.isValid && isValid) {
                isValid = false;
                if (!firstErrorField) {
                    firstErrorField = this.getField(fieldName);
                }
            }

            if (this.options.stopOnFirstError && !result.isValid) {
                return false;
            }
        });

        // Scroll to first error - sadece scrollAndFocus=true olunca
        if (scrollAndFocus && !isValid && this.options.scrollToError && firstErrorField) {
            firstErrorField.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }

        // Focus first error - sadece scrollAndFocus=true olunca
        if (scrollAndFocus && !isValid && this.options.focusFirstError && firstErrorField) {
            setTimeout(() => firstErrorField.focus(), 300);
        }

        this.isValid = isValid;
        return isValid;
    }

    /**
     * Submit button state'ini güncelle
     */
    updateSubmitButton() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        if (!submitBtn) return;

        const isFormValid = this.validateForm();
        submitBtn.disabled = !isFormValid;

        // Update submit button text
        const submitText = submitBtn.querySelector('#submitText');
        if (submitText) {
            submitText.textContent = isFormValid ? submitText.dataset.originalText || 'Submit' : 'Please fill all required fields';
        }
    }

    /**
     * Loading state'i göster
     */
    showLoadingState() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        const submitText = this.form.querySelector('#submitText');
        const loadingSpinner = this.form.querySelector('#loadingSpinner');

        if (submitBtn) {
            submitBtn.disabled = true;
        }

        if (submitText && !submitText.dataset.originalText) {
            submitText.dataset.originalText = submitText.textContent;
        }

        if (submitText) {
            submitText.textContent = 'Processing...';
        }

        if (loadingSpinner) {
            loadingSpinner.classList.remove('hidden');
        }
    }

    /**
     * Loading state'i gizle
     */
    hideLoadingState() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        const submitText = this.form.querySelector('#submitText');
        const loadingSpinner = this.form.querySelector('#loadingSpinner');

        if (submitBtn) {
            submitBtn.disabled = false;
        }

        if (submitText && submitText.dataset.originalText) {
            submitText.textContent = submitText.dataset.originalText;
        }

        if (loadingSpinner) {
            loadingSpinner.classList.add('hidden');
        }
    }

    /**
     * Tüm field'ları reset et
     */
    reset() {
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.getField(fieldName);
            if (field) {
                field.value = '';
                field.classList.remove(
                    'border-green-500', 'border-red-500', 
                    'ring-green-500', 'ring-red-500'
                );
            }
            
            const errorDiv = this.form.querySelector(`#${fieldName}_error`);
            const helpText = this.form.querySelector(`#${fieldName}_help`);
            const validationIcon = field?.parentNode.querySelector('.validation-icon');
            const errorIcon = field?.parentNode.querySelector('.error-icon');

            if (errorDiv) errorDiv.classList.add('hidden');
            if (helpText) helpText.classList.add('hidden');
            if (validationIcon) validationIcon.classList.add('hidden');
            if (errorIcon) errorIcon.classList.add('hidden');
        });

        this.fieldStates.clear();
        this.updateSubmitButton();
        this.hideLoadingState();
    }
}

/**
 * Önceden tanımlanmış validation kuralları
 */
const VALIDATION_RULES = {
    // Kullanıcı adı kuralları
    username: {
        required: true,
        minLength: 3,
        maxLength: 50,
        pattern: /^[a-zA-Z0-9_.-]+$/,
        messages: {
            required: 'Kullanıcı adı zorunludur.',
            minLength: 'Kullanıcı adı en az 3 karakter olmalıdır.',
            maxLength: 'Kullanıcı adı en fazla 50 karakter olmalıdır.',
            pattern: 'Kullanıcı adı sadece harf, rakam ve özel karakterler (_-.) içerebilir.'
        }
    },

    // Şifre kuralları
    password: {
        required: true,
        minLength: 6,
        maxLength: 128,
        messages: {
            required: 'Şifre zorunludur.',
            minLength: 'Şifre en az 6 karakter olmalıdır.',
            maxLength: 'Şifre en fazla 128 karakter olmalıdır.'
        }
    },

    // Güçlü şifre kuralları
    strongPassword: {
        required: true,
        minLength: 8,
        maxLength: 128,
        custom: function(value) {
            const hasUpper = /[A-Z]/.test(value);
            const hasLower = /[a-z]/.test(value);
            const hasNumber = /\d/.test(value);
            const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);

            if (!hasUpper) {
                return { isValid: false, message: 'Şifre en az bir büyük harf içermelidir.' };
            }
            if (!hasLower) {
                return { isValid: false, message: 'Şifre en az bir küçük harf içermelidir.' };
            }
            if (!hasNumber) {
                return { isValid: false, message: 'Şifre en az bir rakam içermelidir.' };
            }
            if (!hasSpecial) {
                return { isValid: false, message: 'Şifre en az bir özel karakter içermelidir.' };
            }
            return true;
        },
        messages: {
            required: 'Şifre zorunludur.',
            minLength: 'Şifre en az 8 karakter olmalıdır.'
        }
    },

    // Email kuralları
    email: {
        email: true,
        maxLength: 100,
        messages: {
            email: 'Geçerli bir e-posta adresi giriniz.',
            maxLength: 'E-posta adresi 100 karakterden uzun olamaz.'
        }
    },

    // Telefon kuralları
    phone: {
        pattern: /^[\d\s\-\+\(\)\.]+$/,
        maxLength: 20,
        messages: {
            pattern: 'Geçerli bir telefon numarası giriniz.',
            maxLength: 'Telefon numarası 20 karakterden uzun olamaz.'
        }
    },

    // Ad soyad kuralları
    name: {
        required: true,
        minLength: 2,
        maxLength: 50,
        pattern: /^[a-zA-ZğüşöçıİĞÜŞÖÇı\s]+$/,
        messages: {
            required: 'Ad zorunludur.',
            minLength: 'Ad en az 2 karakter olmalıdır.',
            maxLength: 'Ad en fazla 50 karakter olmalıdır.',
            pattern: 'Ad sadece harf içerebilir.'
        }
    },

    // Soyad kuralları
    surname: {
        required: true,
        minLength: 2,
        maxLength: 50,
        pattern: /^[a-zA-ZğüşöçıİĞÜŞÖÇı\s]+$/,
        messages: {
            required: 'Soyad zorunludur.',
            minLength: 'Soyad en az 2 karakter olmalıdır.',
            maxLength: 'Soyad en fazla 50 karakter olmalıdır.',
            pattern: 'Soyad sadece harf içerebilir.'
        }
    },

    // Genel metin kuralları
    text: {
        required: true,
        minLength: 2,
        maxLength: 500,
        messages: {
            required: 'Bu alan zorunludur.',
            minLength: 'En az 2 karakter olmalıdır.',
            maxLength: 'En fazla 500 karakter olabilir.'
        }
    },

    // Sayı kuralları
    number: {
        required: true,
        number: true,
        min: 0,
        max: 1000000,
        messages: {
            required: 'Bu alan zorunludur.',
            number: 'Geçerli bir sayı giriniz.',
            min: 'Değer 0\'dan küçük olamaz.',
            max: 'Değer 1.000.000\'dan büyük olamaz.'
        }
    },

    // Miktar kuralları
    quantity: {
        required: true,
        number: true,
        min: 1,
        max: 1000000,
        messages: {
            required: 'Miktar zorunludur.',
            number: 'Geçerli bir miktar giriniz.',
            min: 'Miktar en az 1 olmalıdır.',
            max: 'Miktar en fazla 1.000.000 olabilir.'
        }
    }
};

/**
 * Yardımcı fonksiyonlar
 */
const FormValidationHelpers = {
    /**
     * Password visibility toggle
     */
    togglePassword: function(toggleBtn, passwordInput) {
        if (!toggleBtn || !passwordInput) return;

        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            const svg = this.querySelector('svg');
            if (svg) {
                svg.innerHTML = type === 'password'
                    ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>'
                    : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>';
            }
        });
    },

    /**
     * Input mask for numbers
     */
    numberMask: function(input, allowDecimals = false, maxDecimals = 2) {
        if (!input) return;

        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/[^\d.,]/g, '');
            
            if (!allowDecimals) {
                value = value.replace(/[.,]/g, '');
            } else {
                // Sadece ilk decimal separator'ı allow et
                const firstComma = value.indexOf(',');
                const firstDot = value.indexOf('.');
                
                if (firstComma !== -1 && firstDot !== -1) {
                    const firstSep = Math.min(firstComma, firstDot);
                    value = value.substring(0, firstSep) + 
                           value.substring(firstSep).replace(/[.,]/g, '');
                }
                
                // Decimal kısmını sınırla
                const decimalIndex = value.search(/[.,]/);
                if (decimalIndex !== -1) {
                    const integerPart = value.substring(0, decimalIndex);
                    const decimalPart = value.substring(decimalIndex + 1);
                    value = integerPart + (decimalPart ? '.' + decimalPart.substring(0, maxDecimals) : '');
                }
            }
            
            e.target.value = value;
        });
    },

    /**
     * Character counter
     */
    characterCounter: function(input, counterElement, maxLength) {
        if (!input || !counterElement) return;

        function updateCounter() {
            const currentLength = input.value.length;
            counterElement.textContent = `${currentLength}/${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counterElement.classList.add('text-orange-600');
            } else {
                counterElement.classList.remove('text-orange-600');
            }
            
            if (currentLength >= maxLength) {
                counterElement.classList.add('text-red-600');
                counterElement.classList.remove('text-orange-600');
            } else {
                counterElement.classList.remove('text-red-600');
            }
        }

        input.addEventListener('input', updateCounter);
        updateCounter();
    }
};

/**
 * Auto-initialize forms with data-validate attribute
 */
document.addEventListener('DOMContentLoaded', function() {
    const formsToValidate = document.querySelectorAll('form[data-validate]');
    
    formsToValidate.forEach(form => {
        const rules = JSON.parse(form.getAttribute('data-validation-rules') || '{}');
        const validator = new FormValidator(form);
        validator.setRules(rules);
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormValidator, VALIDATION_RULES, FormValidationHelpers };
}
