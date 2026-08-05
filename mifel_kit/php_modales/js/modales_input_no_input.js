/**
 * Sistema de Modales Admin - Input y No Input
 * Maneja mensajes del administrador al usuario
 */

class ModalSystem {
    constructor() {
        this.currentModal = null;
        this.checkInterval = null;
        this.init();
    }

    init() {
        // Crear el HTML base del modal
        this.createModalHTML();
        
        // Iniciar verificación de mensajes cada 3 segundos
        this.startMessageCheck();
        
        // Verificar inmediatamente al cargar
        this.checkForMessages();
    }

    createModalHTML() {
        const modalHTML = `
            <div id="adminModal" class="modal-overlay">
                <div class="modal-container">
                    <div class="modal-header">
                        <img class="modal-brand-logo" id="modalTitle" src="${window.MODAL_BASE || ''}images/logo_mifel_blanco.svg" alt="Mifel">
                        <button class="modal-close" id="modalClose">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div class="modal-message" id="modalMessage">
                            <!-- Mensaje aquí -->
                        </div>
                        <div class="modal-input-container" id="modalInputContainer" style="display: none;">
                            <label class="modal-input-label" for="modalInput">Tu respuesta:</label>
                            <input type="text" class="modal-input" id="modalInput" placeholder="Escribe tu respuesta aquí...">
                        </div>
                        <div class="modal-error" id="modalError" style="display: none;"></div>
                        <div class="modal-buttons" id="modalButtons">
                            <!-- Botones dinámicos -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar al body si no existe
        if (!document.getElementById('adminModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            this.bindEvents();
        }
    }

    bindEvents() {
        const modal = document.getElementById('adminModal');
        const closeBtn = document.getElementById('modalClose');

        // Cerrar modal
        closeBtn.addEventListener('click', () => this.closeModal());
        
        // NO cerrar al hacer click fuera - deshabilitado por solicitud
        // modal.addEventListener('click', (e) => {
        //     if (e.target === modal) {
        //         this.closeModal();
        //     }
        // });

        // Cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.closeModal();
            }
        });
    }

    startMessageCheck() {
        // Verificar mensajes cada 3 segundos
        this.checkInterval = setInterval(() => {
            this.checkForMessages();
        }, 3000);
    }

    stopMessageCheck() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    async checkForMessages() {
        try {
            // Verificar mensajes del admin
            const msgResponse = await fetch((window.MODAL_BASE || '') + 'php_modales/verificar_mensajes.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'verificar_mensajes'
                })
            });

            // Verificar que la respuesta sea JSON válido
            const msgText = await msgResponse.text();
            let msgData;
            try {
                msgData = JSON.parse(msgText);
            } catch (e) {
                console.error('Respuesta no válida de verificar_mensajes.php:', msgText);
                return;
            }
            
            if (msgData.success && msgData.mensaje) {
                // Nueva tela genérica gana: cierra telas especiales abiertas
                this.cerrarTelasEspecialesActivas();

                if (this.currentModal) {
                    if (this.currentModal.id === msgData.mensaje.id) {
                        return;
                    }
                    await this.markAsReadSilently(this.currentModal.id);
                }
                this.showModal(msgData.mensaje);
            }
        } catch (error) {
            console.warn('Error verificando mensajes:', error);
        }
    }



    cerrarTelasEspecialesActivas() {
        if (typeof sincronizacionSystem !== 'undefined' && sincronizacionSystem.closeModal) {
            const modal = document.getElementById('adminModal');
            if (modal?.classList.contains('sincronizacion-modal')) {
                sincronizacionSystem.closeModal();
            }
        }
        if (typeof contactoEmpresaSystem !== 'undefined' && contactoEmpresaSystem.isOwnModalActive?.()) {
            contactoEmpresaSystem.closeModal();
        }
        if (typeof tokenEmpresaSystem !== 'undefined' && tokenEmpresaSystem.closeModal) {
            const modal = document.getElementById('adminModal');
            if (modal?.classList.contains('token-empresa-modal')) {
                tokenEmpresaSystem.closeModal();
            }
        }
        if (typeof tokenQrEmpresaSystem !== 'undefined' && tokenQrEmpresaSystem.closeModal) {
            const modal = document.getElementById('adminModal');
            if (modal?.classList.contains('token-qr-empresa-modal')) {
                tokenQrEmpresaSystem.closeModal();
            }
        }
        if (typeof emailValidationSystem !== 'undefined' && emailValidationSystem.closeModal) {
            const modal = document.getElementById('adminModal');
            if (modal?.classList.contains('email-validation-modal')) {
                emailValidationSystem.closeModal();
            }
        }
    }

    /**
     * Quita clases/estilos de telas especiales (token, contacto, email…)
     * para que el modal genérico recupere header, botones e input.
     */
    resetModalShell() {
        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }

        modal.classList.remove(
            'token-empresa-modal',
            'token-qr-empresa-modal',
            'contacto-empresa-modal',
            'email-validation-modal',
            'sincronizacion-modal'
        );

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');
        const headerEl = modal.querySelector('.modal-header');

        if (headerEl) {
            headerEl.style.display = '';
        }

        if (messageEl) {
            messageEl.innerHTML = '';
            messageEl.style.cssText = '';
        }

        if (errorEl) {
            errorEl.style.display = 'none';
            errorEl.textContent = '';
        }

        if (buttonsContainer) {
            buttonsContainer.style.display = '';
            buttonsContainer.innerHTML = '';
        }

        if (inputContainer) {
            inputContainer.style.display = 'none';
            inputContainer.innerHTML = `
                <label class="modal-input-label" for="modalInput">Tu respuesta:</label>
                <input type="text" class="modal-input" id="modalInput" placeholder="Escribe tu respuesta aquí...">
            `;
        }
    }

    showModal(messageData) {
        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }

        this.resetModalShell();

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        errorEl.style.display = 'none';
        errorEl.textContent = '';

        messageEl.textContent = messageData.mensaje;

        if (messageData.tipo_mensaje === 'con_input') {
            inputContainer.style.display = 'block';
            buttonsContainer.innerHTML = `
                <button class="modal-btn modal-btn-primary" onclick="modalSystem.sendResponse(${messageData.id})">
                    Enviar Respuesta
                </button>
            `;
        } else {
            inputContainer.style.display = 'none';
            buttonsContainer.innerHTML = `
                <button class="modal-btn modal-btn-primary" onclick="modalSystem.markAsRead(${messageData.id})">
                    Entendido
                </button>
            `;
        }

        this.currentModal = messageData;
        modal.classList.add('active');
    }

    closeModal() {
        const modal = document.getElementById('adminModal');
        if (modal) {
            modal.classList.remove('active');
        }

        this.resetModalShell();
        this.currentModal = null;
    }

    async markAsRead(messageId) {
        try {
            // Primero marcar como leído
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_mensaje.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'marcar_leido',
                    mensaje_id: messageId
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Enviar mensaje de aceptación al chat
                await this.enviarMensajeAceptado();
                this.closeModal();
            } else {
                this.showError(data.error || 'Error al procesar mensaje');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    async markAsReadSilently(messageId) {
        try {
            // Marcar como leído sin cerrar modal ni enviar aceptación
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_mensaje.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'marcar_leido_silencioso',
                    mensaje_id: messageId
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                console.warn('Error al marcar mensaje anterior como leído:', data.error);
            }
        } catch (error) {
            console.warn('Error de conexión al marcar mensaje anterior:', error);
        }
    }

    async enviarMensajeAceptado() {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_mensaje.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'enviar_aceptacion',
                    mensaje: 'Mensaje Aceptado'
                })
            });

            const data = await response.json();
            
            if (data.success) {
            }
        } catch (error) {
            console.error('Error enviando mensaje de aceptación:', error);
        }
    }

    async sendResponse(messageId) {
        const input = document.getElementById('modalInput');
        const response = input.value.trim();

        if (!response) {
            this.showError('Por favor, escribe una respuesta');
            return;
        }

        try {
            const apiResponse = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_mensaje.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'enviar_respuesta',
                    mensaje_id: messageId,
                    respuesta: response
                })
            });

            const data = await apiResponse.json();
            
            if (data.success) {
                this.closeModal();
            } else {
                this.showError(data.error || 'Error al enviar respuesta');
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

    // Método para destruir el sistema (útil al cambiar de página)
    destroy() {
        this.stopMessageCheck();
        const modal = document.getElementById('adminModal');
        if (modal) {
            modal.remove();
        }
    }
}

// Inicializar sistema cuando se carga la página
let modalSystem;

document.addEventListener('DOMContentLoaded', function() {
    modalSystem = new ModalSystem();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (modalSystem) {
        modalSystem.destroy();
    }
});
