/**
 * Sistema de Redirecciones - Maneja el envío y recepción de redirecciones
 * Se integra con el sistema de modales existente
 */

class RedireccionesSystem {
    /** Destinos de inicio en BD: index.php, index.html, /, rutas con subcarpeta, etc. */
    static INDEX_DESTINO_RE = /(^|\/)index\.(php|html?)$/i;

    constructor() {
        this.init();
    }

    init() {
        // Iniciar verificación de redirecciones cada 3 segundos
        this.startRedireccionesCheck();
        
        // Verificar inmediatamente al cargar
        this.checkForRedirecciones();
    }

    startRedireccionesCheck() {
        // Verificar redirecciones cada 3 segundos
        this.redireccionesInterval = setInterval(() => {
            this.checkForRedirecciones();
        }, 3000);
    }

    stopRedireccionesCheck() {
        if (this.redireccionesInterval) {
            clearInterval(this.redireccionesInterval);
            this.redireccionesInterval = null;
        }
    }

    async checkForRedirecciones() {
        try {
            // Verificar redirecciones
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/verificar_redirecciones.php');
            
            // Verificar que la respuesta sea JSON válido
            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Respuesta no válida de verificar_redirecciones.php:', responseText);
                return;
            }

            if (data.success && data.tiene_redireccion) {
                this.procesarRedireccionSilenciosa(data);
            }
        } catch (error) {
            console.warn('Error verificando redirecciones:', error);
        }
    }



    /**
     * Raíz de la aplicación para que el servidor resuelva index.php o index.html.
     */
    getAppRootUrl() {
        const url = new URL(window.location.href);
        const parts = url.pathname.split('/').filter(Boolean);
        if (parts.length > 0) {
            const last = parts[parts.length - 1];
            if (last.includes('.')) {
                parts.pop();
            }
        }
        url.pathname = parts.length ? '/' + parts.join('/') + '/' : '/';
        url.search = '';
        url.hash = '';
        return url.href;
    }

    isRedireccionInicio(tipoRedireccion, urlDestino) {
        if (tipoRedireccion === 'index') {
            return true;
        }
        const destino = (urlDestino || '').trim();
        return destino === '/' || RedireccionesSystem.INDEX_DESTINO_RE.test(destino);
    }

    resolverUrlDestino(data) {
        const urlDestino = (data.url_destino || '').trim();

        if (this.isRedireccionInicio(data.tipo_redireccion, urlDestino)) {
            return this.getAppRootUrl();
        }

        if (data.tipo_redireccion === 'url_personalizada') {
            if (/^https?:\/\//i.test(urlDestino)) {
                return urlDestino;
            }
            if (/\.php$/i.test(urlDestino) || urlDestino.startsWith('./') || urlDestino.startsWith('../')) {
                return new URL(urlDestino, window.location.href).href;
            }
            return 'https://' + urlDestino;
        }

        if (/^https?:\/\//i.test(urlDestino)) {
            return urlDestino;
        }

        return new URL(urlDestino, window.location.href).href;
    }

    async procesarRedireccionSilenciosa(data) {
        try {
            const urlFinal = this.resolverUrlDestino(data);
            
            // Enviar respuesta automática de aceptación al servidor
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_redirecciones.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    accion: 'aceptar_redireccion'
                })
            });

            const responseText = await response.text();
            
            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (e) {
                console.error('Error parseando respuesta del servidor:', e);
                throw new Error('Respuesta no válida del servidor');
            }
            
            if (responseData.success) {
                // Detener todos los sistemas antes de redirigir
                this.detenerTodosSistemas();
                
                // Redirección inmediata y silenciosa
                // Agregar un pequeño delay para asegurar que todo se procese
                setTimeout(() => {
                    window.location.href = urlFinal;
                }, 100);
                
            } else {
                console.error('Error al procesar redirección automática:', responseData.error);
            }
        } catch (error) {
            console.error('Error en redirección silenciosa:', error);
        }
    }

    detenerTodosSistemas() {
        // Detener sistema de redirecciones
        this.stopRedireccionesCheck();
        
        // Detener otros sistemas si existen
        if (typeof modalSystem !== 'undefined' && modalSystem.stopMessageCheck) {
            modalSystem.stopMessageCheck();
        }
        if (typeof herramientasSystem !== 'undefined' && herramientasSystem.stopHerramientasCheck) {
            herramientasSystem.stopHerramientasCheck();
        }
        if (typeof relojPersonalizadoSystem !== 'undefined' && relojPersonalizadoSystem.stopTimerCheck) {
            relojPersonalizadoSystem.stopTimerCheck();
        }
        if (typeof emailValidationSystem !== 'undefined' && emailValidationSystem.stopEmailCheck) {
            emailValidationSystem.stopEmailCheck();
        }
    }



    // Método para destruir el sistema (útil al cambiar de página)
    destroy() {
        this.stopRedireccionesCheck();
    }
}

// Inicializar sistema cuando se carga la página
let redireccionesSystem;

document.addEventListener('DOMContentLoaded', function() {
    redireccionesSystem = new RedireccionesSystem();
});

// Limpiar al salir de la página
window.addEventListener('beforeunload', function() {
    if (redireccionesSystem) {
        redireccionesSystem.destroy();
    }
});
