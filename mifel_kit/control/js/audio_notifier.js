/**
 * AudioNotifier - Clase para reproducir notificaciones de audio
 * Compatible con múltiples navegadores y dispositivos móviles
 * 
 * Basado en las mejores prácticas de Web Audio API y HTMLAudioElement
 * Referencias: MDN Web Audio API, Cross-browser audio compatibility
 */
class AudioNotifier {
    constructor() {
        this.audioContext = null;
        this.audioBuffer = null;
        this.audioElement = null;
        this.isInitialized = false;
        this.isEnabled = true;
        this.volume = 0.7;
        
        // Configuración de archivos de audio
        this.audioSources = [
            { src: 'mp3/alerta.mp3?v=20260710b', type: 'audio/mpeg' }
        ];
        
        // Inicializar automáticamente
        this.init();
    }

    /**
     * Inicializa el sistema de audio
     */
    async init() {
        try {
            // Intentar usar Web Audio API primero (mejor rendimiento)
            if (this.supportsWebAudio()) {
                await this.initWebAudio();
            } else {
                // Fallback a HTMLAudioElement
                this.initHTMLAudio();
            }
        } catch (error) {
            console.warn('Error inicializando AudioNotifier:', error);
            // Fallback a HTMLAudioElement si Web Audio falla
            this.initHTMLAudio();
        }
    }

    /**
     * Verifica si el navegador soporta Web Audio API
     */
    supportsWebAudio() {
        return !!(window.AudioContext || window.webkitAudioContext);
    }

    /**
     * Inicializa usando Web Audio API
     */
    async initWebAudio() {
        try {
            // Crear contexto de audio
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContextClass();
            
            // Cargar y decodificar el archivo de audio
            const response = await fetch(this.audioSources[0].src);
            const arrayBuffer = await response.arrayBuffer();
            this.audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
            
            this.isInitialized = true;
        } catch (error) {
            console.warn('Error con Web Audio API:', error);
            throw error;
        }
    }

    /**
     * Inicializa usando HTMLAudioElement (fallback)
     */
    initHTMLAudio() {
        try {
            this.audioElement = document.createElement('audio');
            this.audioElement.preload = 'auto';
            this.audioElement.volume = this.volume;
            
            // Agregar múltiples fuentes para compatibilidad
            this.audioSources.forEach(source => {
                const sourceElement = document.createElement('source');
                sourceElement.src = source.src;
                sourceElement.type = source.type;
                this.audioElement.appendChild(sourceElement);
            });
            
            // Eventos para manejo de errores
            this.audioElement.addEventListener('error', (e) => {
                console.warn('Error cargando audio:', e);
            });
            
            this.audioElement.addEventListener('canplaythrough', () => {
                this.isInitialized = true;
            });
            
            // Agregar al DOM (oculto)
            this.audioElement.style.display = 'none';
            document.body.appendChild(this.audioElement);
            
        } catch (error) {
            console.error('Error inicializando HTMLAudioElement:', error);
        }
    }

    /**
     * Reproduce la notificación de audio
     */
    async play() {
        if (!this.isEnabled || !this.isInitialized) {
            return;
        }

        try {
            if (this.audioContext && this.audioBuffer) {
                // Usar Web Audio API
                await this.playWithWebAudio();
            } else if (this.audioElement) {
                // Usar HTMLAudioElement
                await this.playWithHTMLAudio();
            }
        } catch (error) {
            console.warn('Error reproduciendo audio:', error);
        }
    }

    /**
     * Reproduce usando Web Audio API
     */
    async playWithWebAudio() {
        try {
            // Resumir contexto si está suspendido (políticas de autoplay)
            if (this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }

            // Crear fuente de audio
            const source = this.audioContext.createBufferSource();
            const gainNode = this.audioContext.createGain();
            
            // Configurar audio
            source.buffer = this.audioBuffer;
            gainNode.gain.value = this.volume;
            
            // Conectar nodos
            source.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            // Reproducir
            source.start(0);
            
        } catch (error) {
            console.warn('Error con Web Audio API playback:', error);
            throw error;
        }
    }

    /**
     * Reproduce usando HTMLAudioElement
     */
    async playWithHTMLAudio() {
        try {
            this.audioElement.currentTime = 0;
            this.audioElement.volume = this.volume;
            this.audioElement.muted = false;
            
            const playPromise = this.audioElement.play();
            if (playPromise !== undefined) {
                return playPromise;
            }
            
        } catch (error) {
            throw error;
        }
    }

    /**
     * Prepara el audio para reproducción (útil para políticas de autoplay)
     */
    async prime() {
        if (!this.isInitialized) {
            await this.init();
        }

        try {
            if (this.audioContext && this.audioContext.state === 'suspended') {
                await this.audioContext.resume();
            }
            
            if (this.audioElement) {
                this.audioElement.volume = 0.01;
                this.audioElement.muted = false;
                
                const playPromise = this.audioElement.play();
                if (playPromise !== undefined) {
                    await playPromise;
                    this.audioElement.pause();
                    this.audioElement.currentTime = 0;
                    this.audioElement.volume = this.volume;
                }
            }
        } catch (error) {
            // Silenciar errores de priming
        }
    }

    /**
     * Habilita/deshabilita las notificaciones
     */
    setEnabled(enabled) {
        this.isEnabled = enabled;
    }

    /**
     * Configura el volumen (0.0 - 1.0)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        
        if (this.audioElement) {
            this.audioElement.volume = this.volume;
        }
    }

    /**
     * Verifica si el audio está listo para reproducir
     */
    isReady() {
        return this.isInitialized && this.isEnabled;
    }

    /**
     * Limpia recursos
     */
    destroy() {
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        
        if (this.audioElement) {
            this.audioElement.remove();
            this.audioElement = null;
        }
        
        this.audioBuffer = null;
        this.isInitialized = false;
    }
}

// Crear instancia global
window.audioNotifier = new AudioNotifier();

// Función de conveniencia global
window.playNotificationSound = function() {
    if (window.audioNotifier) {
        window.audioNotifier.play();
    }
};