/**
 * Sistema de Tooltips Dinámicos - TransControl
 * Maneja la creación y gestión de tooltips para botones del dashboard
 */

class TooltipManager {
    constructor() {
        this.tooltips = new Map();
        this.init();
    }

    init() {
        // Inicializar tooltips después de que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeTooltips());
        } else {
            this.initializeTooltips();
        }
    }

    initializeTooltips() {
        // Definir tooltips para cada botón según la página
        const tooltipConfig = {
            // Botones de control principal (dashboard)
            'button[onclick="togglePolling()"]': {
                text: 'Pausar/Reanudar actualización automática',
                position: 'top'
            },
            'button[onclick="toggleAudioNotifications()"]': {
                text: 'Activar/Desactivar notificaciones de audio',
                position: 'top'
            },
            'button[onclick="vaciarRegistros()"]': {
                text: 'Vaciar todos los registros',
                position: 'top'
            },
            'button[onclick="exportData()"]': {
                text: 'Exportar datos a CSV',
                position: 'top'
            },
            '#resultsPerPageBtn': {
                text: 'Cambiar resultados por página',
                position: 'top'
            },

            // Botones del header (todas las páginas)
            'header a[href="dashboard.php"]': {
                text: 'Ir al Dashboard',
                position: 'bottom'
            },
            'a[href="user_bx.php"]': {
                text: 'Gestión de Administradores',
                position: 'bottom'
            },
            'a[href="mensaje_rapido.php"]': {
                text: 'Editor de Mensajes Rápidos',
                position: 'bottom'
            },
            'button[onclick="showColumnConfig()"]': {
                text: 'Configurar Columnas',
                position: 'bottom'
            },
            'button[onclick="logout()"]': {
                text: 'Cerrar Sesión',
                position: 'bottom'
            },

            // Botones específicos de userBX.php - ELIMINADOS según solicitud
            // No se incluyen tooltips para: editUser, deleteUser, submit (crear usuario)

            // Botones específicos de mensaje_rapido.php - ELIMINADOS según solicitud  
            // No se incluyen tooltips para: addMessage, removeMessage, submit (guardar), cancelar
        };

        // Aplicar tooltips a cada elemento
        Object.entries(tooltipConfig).forEach(([selector, config]) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                this.addTooltip(element, config.text, config.position);
            });
        });

        // Tooltips dinámicos para botones de acción en la tabla
        this.initializeTableTooltips();
    }

    addTooltip(element, text, position = 'top') {
        if (!element || this.tooltips.has(element)) return;

        // Crear contenedor tooltip si no existe
        if (!element.classList.contains('tooltip-container')) {
            element.classList.add('tooltip-container');
        }

        // Crear elemento tooltip
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${position}`;
        tooltip.textContent = text;

        // Añadir tooltip al elemento
        element.appendChild(tooltip);
        
        // Guardar referencia
        this.tooltips.set(element, tooltip);

        // Añadir eventos para mejor control
        element.addEventListener('mouseenter', () => this.showTooltip(element));
        element.addEventListener('mouseleave', () => this.hideTooltip(element));
    }

    initializeTableTooltips() {
        // Observer para tooltips dinámicos en la tabla
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.addTableButtonTooltips(node);
                        }
                    });
                }
            });
        });

        // Observar cambios en el tbody de la tabla
        const tableBody = document.getElementById('tableBody');
        if (tableBody) {
            observer.observe(tableBody, { childList: true, subtree: true });
            // Inicializar tooltips existentes
            this.addTableButtonTooltips(tableBody);
        }
    }

    addTableButtonTooltips(container) {
        // Tooltips para botones de acción en la tabla
        // Excluimos "Abrir panel de control" y "Eliminar registro" como solicitado
        
        const editButtons = container.querySelectorAll('button[onclick*="editarComentario"]');
        editButtons.forEach(button => {
            if (!this.tooltips.has(button)) {
                this.addTooltip(button, 'Editar comentario', 'top');
            }
        });

        // Los botones de "openPopup" y "deleteRecord" no tendrán tooltips
    }

    showTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.style.opacity = '1';
            tooltip.style.visibility = 'visible';
        }
    }

    hideTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.style.opacity = '0';
            tooltip.style.visibility = 'hidden';
        }
    }

    updateTooltipText(element, newText) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.textContent = newText;
        }
    }

    removeTooltip(element) {
        const tooltip = this.tooltips.get(element);
        if (tooltip) {
            tooltip.remove();
            this.tooltips.delete(element);
            element.classList.remove('tooltip-container');
        }
    }

    // Método para actualizar tooltips dinámicamente
    updatePollingTooltip(isActive) {
        const pollingBtn = document.querySelector('button[onclick="togglePolling()"]');
        if (pollingBtn) {
            const text = isActive ? 'Pausar actualización automática' : 'Reanudar actualización automática';
            this.updateTooltipText(pollingBtn, text);
        }
    }

    updateAudioTooltip(isEnabled) {
        const audioBtn = document.querySelector('button[onclick="toggleAudioNotifications()"]');
        if (audioBtn) {
            const text = isEnabled ? 'Desactivar notificaciones de audio' : 'Activar notificaciones de audio';
            this.updateTooltipText(audioBtn, text);
        }
    }
}

// Inicializar el sistema de tooltips
const tooltipManager = new TooltipManager();

// Exportar para uso global
window.tooltipManager = tooltipManager;
