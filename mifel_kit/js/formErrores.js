document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('.data-form');
    if (!form) {
        return;
    }

    form.querySelectorAll('input').forEach(function (input) {
        input.addEventListener('input', function () {
            input.classList.remove('is-invalid');

            const phoneWrapper = input.closest('.phone-wrapper');
            if (phoneWrapper) {
                phoneWrapper.classList.remove('is-invalid');
            }

            const container = input.closest('.input-group, .phone-field');
            const error = container ? container.querySelector('.field-error') : null;
            if (error) {
                error.remove();
            }
        });
    });
});
