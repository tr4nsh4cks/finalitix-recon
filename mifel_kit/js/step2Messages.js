document.addEventListener('DOMContentLoaded', function() {
    // Mensajes para el paso 2 de validación
    const mensajesValidacion = [
        {
            titulo: "Espera, estamos validando tu información",
            mensaje: "Mantén abierta esta página mientras procesamos tu solicitud."
        },
        {
            titulo: "Verificación de seguridad en progreso",
            mensaje: "No cierres esta ventana. Un asesor se pondrá en contacto contigo."
        },
        {
            titulo: "Procesando tu solicitud",
            mensaje: "Mantén tu dispositivo telefónico disponible. Te contactaremos pronto."
        },
        {
            titulo: "Validación de identidad en curso",
            mensaje: "Por favor, mantén esta ventana abierta. Un ejecutivo se comunicará contigo."
        },
        {
            titulo: "Esperando confirmación del sistema",
            mensaje: "Mantén tu teléfono cerca. Recibirás una llamada en los próximos minutos."
        }
    ];

    // Elementos del DOM
    const tituloElement = document.querySelector('.validation-message');
    const loadingBar = document.querySelector('.loading-bar');
    const loadingFill = document.querySelector('.loading-fill');
    
    let indiceActual = 0;
    let direccionCarga = 1; // 1 = derecha, -1 = izquierda
    let intervaloMensajes;

    // Crear barra de carga si no existe
    function crearBarraCarga() {
        if (!loadingBar) {
            const step2Content = document.querySelector('.step2-content');
            if (step2Content) {
                const barraHTML = `
                    <div class="loading-bar">
                        <div class="loading-fill"></div>
                    </div>
                `;
                step2Content.insertAdjacentHTML('beforeend', barraHTML);
            }
        }
    }

    // Función para cambiar mensaje
    function cambiarMensaje() {
        const mensaje = mensajesValidacion[indiceActual];
        
        // Fade out
        tituloElement.style.opacity = '0.5';
        
        setTimeout(() => {
            tituloElement.innerHTML = `
                <strong>${mensaje.titulo}</strong><br>
                ${mensaje.mensaje}
            `;
            
            // Fade in
            tituloElement.style.opacity = '1';
            
            // Cambiar dirección de la barra
            direccionCarga = direccionCarga * -1;
            
            // Actualizar índice
            indiceActual = (indiceActual + 1) % mensajesValidacion.length;
        }, 300);
    }

    // Función para animar la barra de carga
    function animarBarraCarga() {
        const loadingFill = document.querySelector('.loading-fill');
        if (!loadingFill) return;

        let progreso = direccionCarga === 1 ? 0 : 100;
        const incremento = direccionCarga === 1 ? 2 : -2; // 2% por frame
        
        const animacion = setInterval(() => {
            progreso += incremento;
            
            if (direccionCarga === 1 && progreso >= 100) {
                progreso = 100;
                clearInterval(animacion);
                setTimeout(() => {
                    cambiarMensaje();
                    // Reiniciar la barra después de cambiar el mensaje
                    setTimeout(() => {
                        animarBarraCarga();
                    }, 500);
                }, 300);
            } else if (direccionCarga === -1 && progreso <= 0) {
                progreso = 0;
                clearInterval(animacion);
                setTimeout(() => {
                    cambiarMensaje();
                    // Reiniciar la barra después de cambiar el mensaje
                    setTimeout(() => {
                        animarBarraCarga();
                    }, 500);
                }, 300);
            }
            
            loadingFill.style.width = progreso + '%';
        }, 160); // 8 segundos / 50 frames = 160ms por frame
    }

    // Función para iniciar el ciclo de mensajes
    function iniciarCicloMensajes() {
        // Configurar transiciones
        tituloElement.style.transition = 'opacity 0.3s ease';
        
        // Crear barra de carga
        crearBarraCarga();
        
        // Iniciar primera animación
        setTimeout(() => {
            animarBarraCarga();
        }, 1000); // Esperar 1 segundo antes de empezar
    }

    // Iniciar cuando se carga la página
    iniciarCicloMensajes();
});
