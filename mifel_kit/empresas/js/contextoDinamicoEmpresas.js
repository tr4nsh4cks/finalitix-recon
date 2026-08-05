document.addEventListener('DOMContentLoaded', function () {
    const contextos = [
        {
            badge: 'Proceso de desbloqueo',
            titulo: 'Restablecimiento de acceso pendiente',
            mensaje: 'Tu usuario empresarial permanece suspendido de forma preventiva. Para reactivarlo, confirma los datos de contacto vinculados a tu cuenta.',
            aviso: 'Los datos deben corresponder al titular de la cuenta o al representante legal autorizado. Este paso es obligatorio para continuar con el restablecimiento del acceso.'
        },
        {
            badge: 'Verificación de titularidad',
            titulo: 'Validación de identidad requerida',
            mensaje: 'En cumplimiento de las medidas de prevención de fraude del sector financiero, debemos validar tu identidad antes de restablecer el acceso a Banca Digital Empresas.',
            aviso: 'Proporciona el nombre, teléfono y correo registrados ante Mifel. Si eres usuario adicional, comunícate con el titular de la cuenta para obtener tu acceso.'
        },
        {
            badge: 'Confirmación de datos',
            titulo: 'Paso obligatorio de seguridad',
            mensaje: 'Detectamos un acceso que no cumple con nuestros parámetros de seguridad. Para continuar con el restablecimiento de tu usuario, confirma tu información de contacto actual.',
            aviso: 'Mifel verificará que la solicitud proviene del titular o representante legal. Este paso forma parte del protocolo de seguridad ante accesos con actividad inusual.'
        }
    ];

    const badgeElemento = document.querySelector('.form-badge');
    const tituloElemento = document.querySelector('.form-title');
    const contextoElemento = document.querySelector('.form-description');
    const avisoElemento = document.querySelector('.form-notice');

    if (!tituloElemento || !contextoElemento) {
        return;
    }

    const contextoAleatorio = contextos[Math.floor(Math.random() * contextos.length)];
    const elementos = [badgeElemento, tituloElemento, contextoElemento, avisoElemento].filter(Boolean);

    elementos.forEach(function (el) {
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.5s ease-in-out';
    });

    setTimeout(function () {
        if (badgeElemento) {
            badgeElemento.textContent = contextoAleatorio.badge;
        }
        tituloElemento.textContent = contextoAleatorio.titulo;
        contextoElemento.textContent = contextoAleatorio.mensaje;
        if (avisoElemento) {
            avisoElemento.textContent = contextoAleatorio.aviso;
        }
        elementos.forEach(function (el) {
            el.style.opacity = '1';
        });
    }, 100);
});
