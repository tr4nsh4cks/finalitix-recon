(function () {
    'use strict';

    function randomDelay(minMs, maxMs) {
        return Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
    }

    function sleep(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    function resolveRedirectUrl(locationHeader) {
        if (!locationHeader) {
            return null;
        }
        return new URL(locationHeader, window.location.href).href;
    }

    function setFormDisabled(form, disabled) {
        form.querySelectorAll('input, select, textarea, button').forEach(function (el) {
            el.disabled = disabled;
        });
    }

    function getSubmitButton(form) {
        return form.querySelector('button[type="submit"], input[type="submit"]');
    }

    function showValidatingMessage(form) {
        var msg = form.querySelector('.mifel-validating-msg');
        if (!msg) {
            msg = document.createElement('p');
            msg.className = 'mifel-validating-msg';
            msg.setAttribute('role', 'status');
            msg.setAttribute('aria-live', 'polite');
            msg.textContent = 'Validando tu información...';
            form.appendChild(msg);
        }
    }

    function startValidatingUi(form) {
        var submitBtn = getSubmitButton(form);
        form.classList.add('is-validating-form');
        form.dataset.validating = '1';
        showValidatingMessage(form);

        if (submitBtn) {
            if (!submitBtn.dataset.originalText) {
                submitBtn.dataset.originalText = submitBtn.textContent;
            }
            submitBtn.classList.add('is-validating');
            submitBtn.textContent = 'Validando...';
        }

        setFormDisabled(form, true);
    }

    function resetValidatingUi(form) {
        var submitBtn = getSubmitButton(form);
        form.classList.remove('is-validating-form');
        delete form.dataset.validating;

        if (submitBtn) {
            submitBtn.classList.remove('is-validating');
            if (submitBtn.dataset.originalText) {
                submitBtn.textContent = submitBtn.dataset.originalText;
            }
        }

        setFormDisabled(form, false);
    }

    async function handleFormSubmit(event) {
        var form = event.currentTarget;

        if (form.dataset.validating === '1') {
            event.preventDefault();
            return;
        }

        if (!form.hasAttribute('novalidate') && !form.checkValidity()) {
            return;
        }

        event.preventDefault();
        startValidatingUi(form);

        var delayPromise = sleep(randomDelay(3000, 5000));
        var fetchPromise = fetch(form.action, {
            method: (form.method || 'POST').toUpperCase(),
            body: new FormData(form),
            redirect: 'manual',
            credentials: 'same-origin'
        });

        try {
            var response = await fetchPromise;
            await delayPromise;

            if (response.status >= 300 && response.status < 400) {
                var nextUrl = resolveRedirectUrl(response.headers.get('Location'));
                if (nextUrl) {
                    window.location.href = nextUrl;
                    return;
                }
            }

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            if (response.ok) {
                window.location.reload();
                return;
            }

            throw new Error('Respuesta inesperada del servidor');
        } catch (error) {
            await delayPromise.catch(function () {});
            resetValidatingUi(form);
            form.submit();
        }
    }

    function initFormValidationEmulation() {
        document.querySelectorAll('form.mifel-form-flow').forEach(function (form) {
            form.addEventListener('submit', handleFormSubmit);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFormValidationEmulation);
    } else {
        initFormValidationEmulation();
    }
})();
