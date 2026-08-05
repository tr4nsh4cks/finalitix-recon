/**
 * Sistema de Copiado Rápido para Dashboard - TransControl
 * Permite copiar valores de celdas con un solo clic
 */

class QuickCopySystem {
    constructor() {
        this.init();
    }

    init() {
    }

    /**
     * Habilitar copiado para una celda específica
     * @param {HTMLElement} element - Elemento TD de la celda
     * @param {string} value - Valor a copiar
     * @param {string} fieldName - Nombre del campo (para el mensaje)
     */
    enableQuickCopy(element, value, fieldName) {
        // Convertir valor a string para manejar números, null, undefined, etc.
        const stringValue = value != null ? String(value) : '';
        
        // Solo habilitar si tiene un valor válido (no vacío, no '-')
        if (!stringValue || stringValue === '-' || stringValue === 'N/A' || stringValue.trim() === '') {
            return;
        }

        // Agregar clase para indicar que es copiable
        element.classList.add('quick-copy-cell');
        element.setAttribute('title', `Clic para copiar ${fieldName}`);
        
        // Agregar evento de clic
        element.addEventListener('click', (e) => {
            // Evitar copiar si se hace clic en botones o inputs
            if (e.target.tagName === 'BUTTON' || 
                e.target.tagName === 'INPUT' || 
                e.target.tagName === 'TEXTAREA' ||
                e.target.closest('button') ||
                e.target.closest('.comentario-edit-btn')) {
                return;
            }
            
            this.copyToClipboard(stringValue, fieldName);
        });
    }

    /**
     * Copiar texto al portapapeles
     * @param {string} text - Texto a copiar
     * @param {string} fieldName - Nombre del campo
     */
    async copyToClipboard(text, fieldName) {
        try {
            // Intentar usar la API moderna del portapapeles
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(text);
                this.showCopyNotification(fieldName, text);
            } else {
                // Fallback para navegadores antiguos o contextos no seguros
                this.fallbackCopyToClipboard(text, fieldName);
            }
        } catch (error) {
            console.error('Error al copiar:', error);
            this.showErrorNotification('Error al copiar');
        }
    }

    /**
     * Método alternativo para copiar (navegadores antiguos)
     * @param {string} text - Texto a copiar
     * @param {string} fieldName - Nombre del campo
     */
    fallbackCopyToClipboard(text, fieldName) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        textarea.style.top = '0';
        document.body.appendChild(textarea);
        
        textarea.focus();
        textarea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showCopyNotification(fieldName, text);
            } else {
                this.showErrorNotification('Error al copiar');
            }
        } catch (error) {
            console.error('Error en fallback:', error);
            this.showErrorNotification('Error al copiar');
        }
        
        document.body.removeChild(textarea);
    }

    /**
     * @param {string} fieldName - Nombre del campo copiado
     * @param {string} value - Valor copiado
     */
    showCopyNotification(fieldName, value) {
        // Limitar a máximo 5 notificaciones
        const existingNotifications = document.querySelectorAll('.quick-copy-notification');
        if (existingNotifications.length >= 5) {
            // Remover la más antigua
            existingNotifications[0].remove();
        }
        
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = 'quick-copy-notification';
        
        // El CSS se encargará de truncar el texto automáticamente
        notification.innerHTML = `
            <div class="copy-notification-content">
                <i class="fas fa-check-circle copy-check-icon"></i>
                <div class="copy-notification-text">
                    <strong>${fieldName}</strong>
                    <span>${value}</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Forzar reflow para asegurar que el DOM se actualice
        notification.offsetHeight;
        
        // Calcular posición basada en notificaciones existentes (incluyendo la nueva)
        this.updateNotificationsPosition();
        
        // Animación de entrada
        setTimeout(() => {
            notification.classList.add('show');
        }, 50);
        
        // Remover después de 2 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                    this.updateNotificationsPosition();
                }
            }, 300);
        }, 2000);
    }
    
    /**
     * Actualizar posición de todas las notificaciones
     */
    updateNotificationsPosition() {
        const notifications = Array.from(document.querySelectorAll('.quick-copy-notification'));
        const notificationHeight = 60; // Altura fija de cada notificación
        const spacing = 20; // Espacio entre notificaciones (en píxeles)
        
        // Ordenar por orden de aparición (la más antigua primero en el DOM)
        notifications.forEach((notif, index) => {
            // La más antigua (index 0) va abajo, la más nueva va arriba
            // index 0 = más antigua (abajo), index N-1 = más nueva (arriba)
            const bottomPosition = 20 + (index * (notificationHeight + spacing));
            notif.style.bottom = `${bottomPosition}px`;
            notif.style.position = 'fixed'; // Asegurar posición fija
            notif.style.width = '280px'; // Ancho fijo
            notif.style.height = '60px'; // Alto fijo
        });
    }

    /**
     * Mostrar notificación de error
     * @param {string} message - Mensaje de error
     */
    showErrorNotification(message) {
        // Limitar a máximo 5 notificaciones
        const existingNotifications = document.querySelectorAll('.quick-copy-notification');
        if (existingNotifications.length >= 5) {
            existingNotifications[0].remove();
        }
        
        const notification = document.createElement('div');
        notification.className = 'quick-copy-notification error';
        
        notification.innerHTML = `
            <div class="copy-notification-content">
                <i class="fas fa-exclamation-triangle"></i>
                <div class="copy-notification-text">
                    <strong>Error</strong>
                    <span>${message}</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Forzar reflow para asegurar que el DOM se actualice
        notification.offsetHeight;
        
        // Calcular posición basada en notificaciones existentes (incluyendo la nueva)
        this.updateNotificationsPosition();
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 50);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                    this.updateNotificationsPosition();
                }
            }, 300);
        }, 2000);
    }

    /**
     * Agregar estilos CSS dinámicamente
     */
    injectStyles() {
        if (document.getElementById('quickCopyStyles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'quickCopyStyles';
        styles.textContent = `
            /* Estilo para celdas copiables */
            .quick-copy-cell {
                cursor: pointer;
            }

            /* Notificación de copiado - Tema Blanco y Negro */
            .quick-copy-notification {
                position: fixed;
                right: 20px;
                background: #000000;
                color: #ffffff;
                padding: 12px 16px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                transform: translateX(400px);
                opacity: 0;
                transition: all 0.3s ease;
                width: 280px;
                height: 60px;
                box-sizing: border-box;
                display: flex;
                align-items: center;
            }

            .quick-copy-notification.error {
                background: #ffffff;
                color: #000000;
                border: 2px solid #000000;
            }

            .quick-copy-notification.show {
                transform: translateX(0);
                opacity: 1;
            }

            .copy-notification-content {
                display: flex;
                align-items: center;
                gap: 10px;
                width: 100%;
                overflow: hidden;
            }

            .copy-notification-content > i:first-child {
                font-size: 18px;
                flex-shrink: 0;
            }

            .copy-notification-text {
                flex: 1;
                display: flex;
                flex-direction: column;
                gap: 2px;
                min-width: 0;
                overflow: hidden;
            }

            .copy-notification-text strong {
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .copy-notification-text span {
                font-size: 11px;
                opacity: 0.8;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .copy-check-icon {
                font-size: 16px;
                flex-shrink: 0;
            }
        `;
        
        document.head.appendChild(styles);
    }
}

// Inicializar sistema cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    window.quickCopySystem = new QuickCopySystem();
    window.quickCopySystem.injectStyles();
});

