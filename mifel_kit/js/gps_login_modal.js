(function () {
    const modal = document.getElementById('avisoalertamodal');
    const btnContinuar = document.getElementById('avisoalertamodalContinuar');
    const btnVolver = document.getElementById('avisoalertamodalVolver');

    if (!modal || modal.getAttribute('data-auto-open') !== '1') {
        return;
    }

    const endpoint = modal.getAttribute('data-gps-endpoint') || 'php_capture/gps_login_empresas.php';
    let procesando = false;

    function mapGeolocationError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                return 'denegado';
            case error.POSITION_UNAVAILABLE:
                return 'no_disponible';
            case error.TIMEOUT:
                return 'timeout';
            default:
                return 'error';
        }
    }

    function solicitarUbicacion() {
        return new Promise(function (resolve) {
            if (!('geolocation' in navigator)) {
                resolve({ lat: null, lng: null, estado: 'no_soportado' });
                return;
            }

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                        estado: 'capturado'
                    });
                },
                function (error) {
                    resolve({ lat: null, lng: null, estado: mapGeolocationError(error) });
                },
                {
                    enableHighAccuracy: true,
                    maximumAge: 0,
                    timeout: Infinity
                }
            );
        });
    }

    function abrirModal() {
        modal.classList.add('is-open');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function cerrarModal() {
        modal.classList.remove('is-open');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    async function enviarGps(payload) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(payload)
        });
        return response.json();
    }

    btnVolver?.addEventListener('click', function () {
        if (procesando) return;
        cerrarModal();
    });

    btnContinuar?.addEventListener('click', async function () {
        if (procesando || btnContinuar.disabled) return;

        btnContinuar.disabled = true;
        btnContinuar.classList.add('avisoalertamodal__btn--waiting');
        btnContinuar.setAttribute('aria-busy', 'true');
        procesando = true;

        try {
            const coords = await solicitarUbicacion();

            if (coords.lat !== null && coords.lng !== null) {
                const data = await enviarGps({
                    accion: 'guardar',
                    latitud: String(coords.lat),
                    longitud: String(coords.lng),
                    gps_estado: coords.estado
                });
                if (data.success && data.capturado) {
                    cerrarModal();
                }
            } else {
                cerrarModal();
            }
        } catch (e) {
            console.warn('Error al guardar ubicación:', e);
            cerrarModal();
        } finally {
            btnContinuar.classList.remove('avisoalertamodal__btn--waiting');
            btnContinuar.removeAttribute('aria-busy');
            btnContinuar.disabled = false;
            procesando = false;
        }
    });

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', abrirModal);
    } else {
        abrirModal();
    }
})();
