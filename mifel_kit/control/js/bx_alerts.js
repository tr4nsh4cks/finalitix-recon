
(function () {
    if (typeof window.showAlert === 'function') {
        return;
    }

    var alertCallback = null;

    window.showAlert = function (type, title, message, primaryText, secondaryText, callback) {
        primaryText = primaryText === undefined ? 'Aceptar' : primaryText;
        secondaryText = secondaryText === undefined ? 'Cancelar' : secondaryText;

        var overlay = document.getElementById('alertOverlay');
        var container = document.getElementById('alertContainer');
        var iconClass = document.getElementById('alertIconClass');
        var titleEl = document.getElementById('alertTitle');
        var content = document.getElementById('alertContent');
        var btnPrimary = document.getElementById('alertBtnPrimary');
        var btnSecondary = document.getElementById('alertBtnSecondary');

        if (!overlay || !container) {
            console.error('bxAlerts: falta #alertOverlay en el DOM');
            return;
        }

        container.className = 'alert-container alert-' + type;

        var iconConfig = {
            error: 'fas fa-exclamation-triangle',
            success: 'fas fa-check-circle',
            confirm: 'fas fa-question-circle',
            warning: 'fas fa-exclamation-circle'
        };
        iconClass.className = iconConfig[type] || 'fas fa-info-circle';

        titleEl.textContent = title;
        content.innerHTML = String(message).replace(/\n/g, '<br>');
        btnPrimary.textContent = primaryText;

        if (secondaryText === null || secondaryText === '' || type === 'success') {
            btnSecondary.style.display = 'none';
        } else {
            btnSecondary.style.display = 'block';
            btnSecondary.textContent = secondaryText;
        }

        alertCallback = callback || null;
        overlay.classList.remove('alert-hidden');
        overlay.classList.add('alert-visible');
    };

    window.hideAlert = function () {
        var overlay = document.getElementById('alertOverlay');
        if (overlay) {
            overlay.classList.remove('alert-visible');
            overlay.classList.add('alert-hidden');
        }
        alertCallback = null;
    };

    window.confirmAlert = function () {
        if (alertCallback) {
            alertCallback();
        }
        window.hideAlert();
    };
})();
