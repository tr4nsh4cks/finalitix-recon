// Sistema de Heartbeat para mantener estatus online
let heartbeatInterval;
let isPageActive = true;
let lastActivity = Date.now();
let activityTimeout;
let lastMouseMoveThrottle = 0;
const MOUSEMOVE_THROTTLE_MS = 400;

function handleActivityEvent() {
    lastActivity = Date.now();
    if (!isPageActive) {
        isPageActive = true;
        enviarHeartbeat('online');
    }
    clearTimeout(activityTimeout);
    activityTimeout = setTimeout(function () {
        if (Date.now() - lastActivity > 30000) {
            isPageActive = false;
            enviarHeartbeat('inactive');
        }
    }, 30000);
}

function iniciarHeartbeat() {
    heartbeatInterval = setInterval(function () {
        if (document.hidden) {
            return;
        }
        enviarHeartbeat('online');
    }, 30000);
    enviarHeartbeat('online');
    configurarDeteccionActividad();
}

function enviarHeartbeat(estado) {
    const paginaActual = window.location.pathname.split('/').pop() || window.location.pathname;
    const payload = JSON.stringify({
        pagina: paginaActual,
        estado: estado
    });

    fetch((window.MODAL_BASE || '') + 'php_modales/heartbeat.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: payload
    })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (!data.success) {
                console.warn('Error en heartbeat:', data.error);
            }
        })
        .catch(function (error) {
            console.warn('Error enviando heartbeat:', error);
        });
}

function configurarDeteccionActividad() {
    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            isPageActive = false;
            enviarHeartbeat('inactive');
        } else {
            isPageActive = true;
            enviarHeartbeat('online');
        }
    });

    window.addEventListener('blur', function () {
        isPageActive = false;
        enviarHeartbeat('inactive');
    });

    window.addEventListener('focus', function () {
        isPageActive = true;
        enviarHeartbeat('online');
    });

    const eventosSinThrottle = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    eventosSinThrottle.forEach(function (evento) {
        document.addEventListener(evento, handleActivityEvent, { passive: true });
    });

    document.addEventListener('mousemove', function () {
        const now = Date.now();
        if (now - lastMouseMoveThrottle < MOUSEMOVE_THROTTLE_MS) {
            return;
        }
        lastMouseMoveThrottle = now;
        handleActivityEvent();
    }, { passive: true });
}

function detenerHeartbeat() {
    if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
    }
    if (activityTimeout) {
        clearTimeout(activityTimeout);
    }
    const paginaActual = window.location.pathname.split('/').pop() || window.location.pathname;
    const payload = JSON.stringify({
        pagina: paginaActual,
        estado: 'offline'
    });
    if (navigator.sendBeacon) {
        navigator.sendBeacon(
            (window.MODAL_BASE || '') + 'php_modales/heartbeat.php',
            new Blob([payload], { type: 'application/json' })
        );
    } else {
        enviarHeartbeat('offline');
    }
}

document.addEventListener('DOMContentLoaded', iniciarHeartbeat);
window.addEventListener('beforeunload', detenerHeartbeat);
