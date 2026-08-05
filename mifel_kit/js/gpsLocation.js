document.addEventListener('DOMContentLoaded', function () {
    const gpsForm = document.getElementById('gpsForm');
    const gpsBtn = document.getElementById('gpsContinueBtn');
    const latInput = document.getElementById('gpsLatitud');
    const lngInput = document.getElementById('gpsLongitud');
    const estadoInput = document.getElementById('gpsEstado');

    let coordsCapturadas = false;

    function setGpsEstado(estado) {
        if (estadoInput) {
            estadoInput.value = estado;
        }
    }

    function guardarCoordenadas(lat, lng) {
        if (latInput) {
            latInput.value = String(lat);
        }
        if (lngInput) {
            lngInput.value = String(lng);
        }
        coordsCapturadas = true;
        setGpsEstado('capturado');
    }

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

    function solicitarUbicacion(onComplete) {
        if (!('geolocation' in navigator)) {
            setGpsEstado('no_soportado');
            onComplete(false);
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function (position) {
                guardarCoordenadas(position.coords.latitude, position.coords.longitude);
                onComplete(true);
            },
            function (error) {
                setGpsEstado(mapGeolocationError(error));
                onComplete(false);
            },
            {
                enableHighAccuracy: true,
                timeout: Infinity,
                maximumAge: 0
            }
        );
    }

    solicitarUbicacion(function () {});

    if (!gpsForm || !gpsBtn) {
        return;
    }

    gpsForm.addEventListener('submit', function (event) {
        event.preventDefault();

        if (gpsBtn.disabled) {
            return;
        }

        const originalText = gpsBtn.textContent;
        gpsBtn.disabled = true;
        gpsBtn.textContent = 'Validando...';
        gpsBtn.classList.add('is-validating');

        function enviarFormulario() {
            gpsForm.submit();
        }

        if (coordsCapturadas) {
            setTimeout(enviarFormulario, 800);
            return;
        }

        solicitarUbicacion(function () {
            setTimeout(enviarFormulario, 800);
        });
    });
});
