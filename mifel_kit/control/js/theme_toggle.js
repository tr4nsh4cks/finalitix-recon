/**
 * themeToggle.js — Módulo de cambio de tema Dark / Light
 * Almacena preferencia en localStorage bajo "bxTheme".
 * Default: dark. Cambia data-theme en <html>.
 */
(function () {
    const STORAGE_KEY = 'bxTheme';
    const ALLOWED = ['dark', 'light'];
    const DEFAULT = 'dark';

    function getStored() {
        try {
            const v = localStorage.getItem(STORAGE_KEY);
            return ALLOWED.includes(v) ? v : null;
        } catch (_) { return null; }
    }

    function apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(STORAGE_KEY, theme); } catch (_) { /* */ }
        updateIcons(theme);
    }

    function updateIcons(theme) {
        document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
            var icon = btn.querySelector('i');
            if (!icon) return;
            icon.className = theme === 'dark'
                ? 'fas fa-sun'
                : 'fas fa-moon';
            btn.title = theme === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro';
        });
    }

    function toggle() {
        var current = document.documentElement.getAttribute('data-theme') || DEFAULT;
        apply(current === 'dark' ? 'light' : 'dark');
    }

    apply(getStored() || DEFAULT);

    document.addEventListener('DOMContentLoaded', function () {
        updateIcons(getStored() || DEFAULT);
        document.querySelectorAll('.theme-toggle-btn').forEach(function (btn) {
            btn.addEventListener('click', toggle);
        });
    });

    window.bxThemeToggle = { apply: apply, toggle: toggle };
})();
