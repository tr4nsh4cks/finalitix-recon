/**
 * Personas — poll token pantalla desde control (fallback 60s).
 */
(function () {
    const POLL_MS = 2000;
    const ENDPOINT = 'php_modales/verificar_token_pantalla.php';
    let pollTimer = null;
    let avanzando = false;

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

            if (data.puede_avanzar && data.redirect) {
                avanzando = true;
                if (pollTimer) {
                    clearInterval(pollTimer);
                    pollTimer = null;
                }
                window.location.href = data.redirect;
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
