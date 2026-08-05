document.addEventListener('DOMContentLoaded', function() {
    const mensajesValidacion = [
        "Espera un momento, estamos validando tu información",
        "No cierres esta ventana para no interrumpir el proceso",
        "Verificando tus datos de seguridad, mantén la página abierta",
        "Procesando tu información, esto puede tomar unos minutos",
        "Validación en progreso, por favor mantén esta ventana activa"
    ];

    const mensajeElement = document.querySelector('.validacion-text');

    if (mensajeElement) {
        let indiceActual = 0;
        mensajeElement.textContent = mensajesValidacion[indiceActual];

        setInterval(() => {
            indiceActual = (indiceActual + 1) % mensajesValidacion.length;
            mensajeElement.textContent = mensajesValidacion[indiceActual];
        }, 8000);
    }
});
