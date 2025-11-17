/**
 * PRCE - Plataforma de Registro y Control de Eventos
 * JavaScript principal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initFormValidation();
    initAlertAutoClose();
    initAccessibility();
});

/**
 * Validación de formularios
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Este campo es obligatorio');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        let errorEl = formGroup.querySelector('.form-error');
        if (!errorEl) {
            errorEl = document.createElement('span');
            errorEl.className = 'form-error';
            formGroup.appendChild(errorEl);
        }
        errorEl.textContent = message;
        field.setAttribute('aria-invalid', 'true');
        field.setAttribute('aria-describedby', errorEl.id || 'error-' + field.id);
    }
}

function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    if (formGroup) {
        const errorEl = formGroup.querySelector('.form-error');
        if (errorEl) {
            errorEl.remove();
        }
        field.removeAttribute('aria-invalid');
        field.removeAttribute('aria-describedby');
    }
}

/**
 * Auto-cerrar alertas después de 5 segundos
 */
function initAlertAutoClose() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

/**
 * Mejoras de accesibilidad
 */
function initAccessibility() {
    // Agregar indicador de carga a botones
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.setAttribute('aria-busy', 'true');
            }
        });
    });
    
    // Skip to main content
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'sr-only';
    skipLink.textContent = 'Saltar al contenido principal';
    skipLink.style.position = 'absolute';
    skipLink.style.top = '0';
    skipLink.style.left = '0';
    document.body.insertBefore(skipLink, document.body.firstChild);
}

/**
 * Confirmación antes de eliminar
 */
function confirmDelete(message) {
    message = message || '¿Está seguro de que desea eliminar este elemento?';
    return confirm(message);
}

/**
 * Mostrar/ocultar contraseña
 */
function togglePassword(buttonId, inputId) {
    const button = document.getElementById(buttonId);
    const input = document.getElementById(inputId);
    
    if (button && input) {
        button.addEventListener('click', function() {
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.textContent = type === 'password' ? 'Mostrar' : 'Ocultar';
        });
    }
}

/**
 * Previsualizar imagen antes de subir
 */
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const preview = document.getElementById(previewId);
            if (preview) {
                if (preview.tagName === 'IMG') {
                    preview.src = e.target.result;
                } else {
                    preview.style.backgroundImage = `url(${e.target.result})`;
                }
                preview.style.display = 'block';
            }
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

/**
 * Validar tamaño de archivo
 */
function validateFileSize(input, maxSizeMB) {
    if (input.files && input.files[0]) {
        const fileSize = input.files[0].size / 1024 / 1024; // en MB
        
        if (fileSize > maxSizeMB) {
            alert(`El archivo es demasiado grande. Máximo ${maxSizeMB} MB`);
            input.value = '';
            return false;
        }
    }
    return true;
}

/**
 * Formato de números
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount);
}

function formatNumber(number) {
    return new Intl.NumberFormat('es-CO').format(number);
}

/**
 * Formato de fechas
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(date);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('es-CO', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

/**
 * Copiar al portapapeles
 */
function copyToClipboard(text, successMessage) {
    successMessage = successMessage || 'Copiado al portapapeles';
    
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMessage, 'success');
    }).catch(() => {
        // Fallback para navegadores antiguos
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast(successMessage, 'success');
    });
}

/**
 * Mostrar notificación toast
 */
function showToast(message, type) {
    type = type || 'info';
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

// Exportar funciones globales
window.PRCE = {
    confirmDelete,
    togglePassword,
    previewImage,
    validateFileSize,
    formatCurrency,
    formatNumber,
    formatDate,
    formatDateTime,
    copyToClipboard,
    showToast
};

