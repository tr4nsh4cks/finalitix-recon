<?php
session_start();

// Si ya está logueado, redirigir al dashboard
if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
    header('Location: dashboard.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MifelinS.Control. | Inicio de sesión</title>
    <meta name="robots" content="noindex, nofollow">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/theme_dark.css?v=8">
    <link rel="stylesheet" href="css/theme_light.css?v=7">
    <script src="js/theme_toggle.js?v=1"></script>
</head>
<body class="login-page min-h-screen flex items-center justify-center px-3 py-6 relative overflow-hidden">
    <button type="button" class="theme-toggle-btn fixed top-4 right-4 z-50 px-3 py-2 rounded-lg text-sm shadow-md" title="Cambiar tema" aria-label="Cambiar tema">
        <i class="fas fa-moon" aria-hidden="true"></i>
    </button>
    <div class="login-bg-effects" aria-hidden="true">
        <div class="login-waves-hub">
            <span class="login-wave-ring"></span>
            <span class="login-wave-ring"></span>
            <span class="login-wave-ring"></span>
            <span class="login-wave-ring"></span>
        </div>
        <div class="login-waves-hub login-waves-hub--slow">
            <span class="login-wave-ring login-wave-ring--soft"></span>
            <span class="login-wave-ring login-wave-ring--soft"></span>
        </div>
    </div>
    <div class="login-main relative z-10 flex w-full max-w-xs flex-col items-center">
    <div class="login-card w-full">
        <div class="text-center mb-6">
            <h1 class="login-heading text-base font-semibold leading-snug">TransControl v2.0</h1>
        </div>

        <form action="login.php" method="POST" class="space-y-4">
            <div class="relative login-input-wrap">
                <i class="fas fa-lock login-input-lock absolute left-3 top-1/2 -translate-y-1/2 text-sm pointer-events-none" aria-hidden="true"></i>
                <input type="password"
                       id="clave"
                       name="clave"
                       required
                       autocomplete="current-password"
                       aria-label="Contraseña"
                       class="login-field w-full pl-9 pr-3 py-2 text-sm rounded-lg focus:outline-none"
                       placeholder="Contraseña"
                       autofocus>
            </div>

            <button type="submit"
                    id="login-submit-btn"
                    disabled
                    class="login-submit w-full py-2.5 px-3 text-sm rounded-lg font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-white/35 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent transition-colors">
                <i class="fas fa-sign-in-alt mr-2" aria-hidden="true"></i>Iniciar Sesión
            </button>
        </form>

        <?php if (isset($_GET['error'])): ?>
        <div class="login-alert mt-4 px-3 py-2 rounded-lg text-xs">
            <i class="fas fa-exclamation-triangle mr-2" aria-hidden="true"></i>
            <?php echo htmlspecialchars($_GET['error']); ?>
        </div>
        <?php endif; ?>
    </div>
    <p class="login-tagline" aria-live="polite">
        <span class="login-tagline-row">
            <i class="fas fa-calendar-day" aria-hidden="true"></i>
            <span id="login-tagline-date"></span>
        </span>
        <span class="login-tagline-sep" aria-hidden="true">·</span>
        <span class="login-tagline-row">
            <i class="fas fa-clock" aria-hidden="true"></i>
            <span id="login-tagline-time"></span>
        </span>
    </p>
    </div>
    <script>
    (function () {
        var dateEl = document.getElementById('login-tagline-date');
        var timeEl = document.getElementById('login-tagline-time');
        if (dateEl && timeEl) {
            function updateDateTime() {
                var now = new Date();
                dateEl.textContent = now.toLocaleDateString('es-ES', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });
                timeEl.textContent = now.toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit'
                });
            }
            updateDateTime();
            setInterval(updateDateTime, 1000);
        }

        var input = document.getElementById('clave');
        var btn = document.getElementById('login-submit-btn');
        if (!input || !btn) return;
        function sync() {
            btn.disabled = input.value.trim().length === 0;
        }
        input.addEventListener('input', sync);
        input.addEventListener('paste', function () { setTimeout(sync, 0); });
        sync();
    })();
    </script>
</body>
</html>
