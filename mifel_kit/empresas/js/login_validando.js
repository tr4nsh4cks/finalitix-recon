/**
 * Login Empresas en validación — poll token desde control (fallback 60s).
 */
(function () {
    const POLL_MS = 2000;
    const ENDPOINT = (window.MODAL_BASE || '../') + 'php_modales/verificar_token_pantalla.php';
    let pollTimer = null;
    let avanzando = false;

    function updateMessage(data) {
        /* El estado de espera se muestra solo en el botón Ingresar + spinner */
        if (data.puede_avanzar) {
            const btn = document.getElementById('loginSubmitBtn');
            if (btn) {
                btn.setAttribute('aria-busy', 'true');
            }
        }
    }

    async function verificarTokenPantalla() {
        if (avanzando) return;

        try {
            const response = await fetch(ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ accion: 'verificar' }),
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (e) {
                console.error('Respuesta inválida verificar_token_pantalla:', text);
                return;
            }

            if (!data.success) {
                return;
            }

            updateMessage(data);

            if (data.puede_avanzar && data.redirect) {
                avanzando = true;
                if (pollTimer) {
                    clearInterval(pollTimer);
                    pollTimer = null;
                }
                let destino = data.redirect;
                if (destino === 'gps.php' || destino.endsWith('/gps.php')
                    || destino === 'authenticate_gps.php' || destino.endsWith('/authenticate_gps.php')) {
                    destino = 'netespera.php';
                }
                if (destino.startsWith('empresas/')) {
                    destino = destino.slice('empresas/'.length);
                }
                window.location.href = destino;
            }
        } catch (error) {
            console.warn('Error verificando token pantalla:', error);
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        verificarTokenPantalla();
        pollTimer = setInterval(verificarTokenPantalla, POLL_MS);
    });

    window.addEventListener('beforeunload', function () {
        if (pollTimer) {
            clearInterval(pollTimer);
        }
    });
})();
