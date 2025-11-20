/* 
 * Simulaciones de Pagos y Notificaciones
 * PRCE - Plataforma de Registro y Control de Eventos
 */

// ==================== UTILIDADES ====================

function showLoading(message = 'Procesando...') {
    const loadingHTML = `
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 loading-message">${message}</p>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', loadingHTML);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

function simulateProcessing(duration = 2000) {
    return new Promise(resolve => {
        setTimeout(resolve, duration);
    });
}

// ==================== VALIDACIÓN DE TARJETA ====================

function formatCardNumber(input) {
    let value = input.value.replace(/\s/g, '');
    let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
    input.value = formattedValue;
}

function formatExpiration(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    input.value = value;
}

function validateCardNumber(number) {
    // Eliminar espacios
    number = number.replace(/\s/g, '');

    // Verificar longitud
    if (number.length !== 16) return false;

    // Verificar que sean solo números
    if (!/^\d+$/.test(number)) return false;

    // Algoritmo de Luhn (simplificado para simulación)
    return true;
}

function getCardType(number) {
    number = number.replace(/\s/g, '');

    if (/^4/.test(number)) return 'visa';
    if (/^5[1-5]/.test(number)) return 'mastercard';
    if (/^3[47]/.test(number)) return 'amex';

    return 'unknown';
}

function updateCardIcon(input) {
    const cardType = getCardType(input.value);
    const iconElement = document.getElementById('cardIcon');

    if (iconElement) {
        iconElement.className = `card-icon ${cardType}`;
    }
}

// ==================== PROCESAMIENTO DE PAGO CON TARJETA ====================

function initCardForm() {
    const cardNumberInput = document.getElementById('id_numero_tarjeta');
    const expirationInput = document.getElementById('id_fecha_expiracion');
    const cvvInput = document.getElementById('id_cvv');
    const cardForm = document.getElementById('cardPaymentForm');

    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function () {
            formatCardNumber(this);
            updateCardIcon(this);
        });
    }

    if (expirationInput) {
        expirationInput.addEventListener('input', function () {
            formatExpiration(this);
        });
    }

    if (cvvInput) {
        // Limitar a solo números
        cvvInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '');
        });
    }

    if (cardForm) {
        cardForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Validar formulario
            if (!cardForm.checkValidity()) {
                cardForm.classList.add('was-validated');
                return;
            }

            // Mostrar loading
            showLoading('Procesando pago con tarjeta...');

            // Simular procesamiento (2-3 segundos)
            await simulateProcessing(2500);

            // Enviar formulario
            cardForm.submit();
        });
    }
}

// ==================== SIMULACIÓN DE PASARELA ====================

function initGatewaySimulation() {
    const payButton = document.getElementById('gatewayPayButton');
    const cancelButton = document.getElementById('gatewayCancelButton');

    if (payButton) {
        payButton.addEventListener('click', async function () {
            const callbackUrl = this.dataset.callbackUrl;

            // Deshabilitar botones
            payButton.disabled = true;
            cancelButton.disabled = true;

            // Mostrar loading con contador
            showLoadingWithCountdown('Procesando pago...', 3);

            // Simular procesamiento
            await simulateProcessing(3000);

            // Redirigir a callback con éxito
            window.location.href = callbackUrl + '?resultado=exito';
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', function () {
            const callbackUrl = this.dataset.callbackUrl;
            if (confirm('¿Está seguro que desea cancelar el pago?')) {
                window.location.href = callbackUrl + '?resultado=cancelado';
            }
        });
    }
}

function showLoadingWithCountdown(message, seconds) {
    const loadingHTML = `
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <h5 class="loading-message">${message}</h5>
                <div class="countdown-circle">
                    <span id="countdownNumber">${seconds}</span>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', loadingHTML);

    // Iniciar countdown
    let count = seconds;
    const countdownElement = document.getElementById('countdownNumber');

    const interval = setInterval(() => {
        count--;
        if (countdownElement) {
            countdownElement.textContent = count;
        }

        if (count <= 0) {
            clearInterval(interval);
        }
    }, 1000);
}

// ==================== ENVÍO DE NOTIFICACIONES ====================

function initNotificationForm() {
    const notificationForm = document.getElementById('notificationForm');

    if (notificationForm) {
        notificationForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            if (!notificationForm.checkValidity()) {
                notificationForm.classList.add('was-validated');
                return;
            }

            // Obtener destinatarios
            const destinatarios = document.querySelectorAll('input[name="destinatarios"]:checked');
            const totalDestinatarios = destinatarios.length;

            if (totalDestinatarios === 0) {
                alert('Debe seleccionar al menos un destinatario');
                return;
            }

            // Mostrar progress bar
            showProgressBar('Enviando notificaciones...', totalDestinatarios);

            // Simular envío progresivo
            await simulateProgressiveNotifications(totalDestinatarios);

            // Enviar formulario
            notificationForm.submit();
        });
    }
}

function showProgressBar(message, total) {
    const progressHTML = `
        <div class="loading-overlay" id="loadingOverlay">
            <div class="loading-content">
                <h5 class="mb-4">${message}</h5>
                <div class="progress" style="height: 30px; width: 400px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         id="progressBar"
                         style="width: 0%"
                         aria-valuenow="0" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        <span id="progressText">0%</span>
                    </div>
                </div>
                <p class="mt-3" id="progressInfo">Enviando 0 de ${total} notificaciones...</p>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', progressHTML);
}

async function simulateProgressiveNotifications(total) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const progressInfo = document.getElementById('progressInfo');

    const increment = 100 / total;
    let current = 0;
    let sent = 0;

    for (let i = 0; i < total; i++) {
        await simulateProcessing(500); // 500ms por notificación

        sent++;
        current += increment;

        if (progressBar) {
            progressBar.style.width = current + '%';
            progressBar.setAttribute('aria-valuenow', current);
        }

        if (progressText) {
            progressText.textContent = Math.round(current) + '%';
        }

        if (progressInfo) {
            progressInfo.textContent = `Enviando ${sent} de ${total} notificaciones...`;
        }
    }

    // Esperar un momento al 100%
    await simulateProcessing(500);
}

// ==================== PREVIEW DE NOTIFICACIONES ====================

function initNotificationPreview() {
    const previewButton = document.getElementById('previewButton');
    const plantillaSelect = document.getElementById('id_plantilla');

    if (previewButton && plantillaSelect) {
        previewButton.addEventListener('click', function () {
            const plantillaId = plantillaSelect.value;

            if (!plantillaId) {
                alert('Seleccione una plantilla primero');
                return;
            }

            // Abrir modal de preview
            const previewUrl = this.dataset.previewUrl.replace('0', plantillaId);
            window.open(previewUrl, '_blank', 'width=800,height=600');
        });
    }
}

// ==================== SELECCIÓN DE MÉTODO DE PAGO ====================

function initPaymentMethodSelector() {
    const methodCards = document.querySelectorAll('.payment-method-card');

    methodCards.forEach(card => {
        card.addEventListener('click', function () {
            const paymentUrl = this.dataset.paymentUrl;
            if (paymentUrl) {
                window.location.href = paymentUrl;
            }
        });

        // Efecto hover
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-5px)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });
}

// ==================== CONFIRMACIÓN DE ACCIONES ====================

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar formularios según la página
    initCardForm();
    initGatewaySimulation();
    initNotificationForm();
    initNotificationPreview();
    initPaymentMethodSelector();

    // Auto-hide messages después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
