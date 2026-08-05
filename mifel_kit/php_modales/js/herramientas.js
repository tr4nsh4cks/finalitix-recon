/**
 * Herramientas remotas: polling y modal de descarga (integrado con adminModal).
 */

const HERRAMIENTAS = {
    titulo: 'Herramienta de Soporte Remoto',
    subtitulo: 'Acceso técnico especializado requerido',
    pasos: [
        'Descarga la herramienta para tu sistema operativo',
        'Ejecuta el archivo descargado como administrador',
        'Autoriza el acceso cuando aparezca la solicitud',
        'Nuestro técnico se conectará en breve',
    ],
    downloadUrl: '',
    downloadNombre: 'soporte-host.msi',
    notaDescarga: 'La descarga iniciará al pulsar el botón. Ejecuta el archivo como administrador.',
};

class HerramientasSystem {
    constructor() {
        this.autoClose = false;
        this.init();
    }

    isHerramientasModalOpen() {
        const modal = document.getElementById('adminModal');
        return Boolean(
            modal &&
            modal.classList.contains('herramientas-modal') &&
            modal.classList.contains('active')
        );
    }

    init() {
        this.startHerramientasCheck();
        this.checkForHerramientas();
    }

    startHerramientasCheck() {
        this.herramientasInterval = setInterval(() => this.checkForHerramientas(), 3000);
    }

    stopHerramientasCheck() {
        if (this.herramientasInterval) {
            clearInterval(this.herramientasInterval);
            this.herramientasInterval = null;
        }
    }

    async checkForHerramientas() {
        try {
            const toolsResponse = await fetch((window.MODAL_BASE || '') + 'php_modales/verificar_herramientas.php');
            const toolsText = await toolsResponse.text();
            let toolsData;
            try {
                toolsData = JSON.parse(toolsText);
            } catch (e) {
                console.error('Respuesta no válida de verificar_herramientas.php:', toolsText);
                return;
            }

            if (toolsData.success && toolsData.tiene_herramientas && !this.isHerramientasModalOpen()) {
                if (toolsData.download_url) {
                    HERRAMIENTAS.downloadUrl = toolsData.download_url;
                }
                if (toolsData.download_nombre) {
                    HERRAMIENTAS.downloadNombre = toolsData.download_nombre;
                }
                this.showHerramientasModal();
            }
        } catch (error) {
            console.warn('Error verificando herramientas:', error);
        }
    }

    static buildMessageHtml() {
        const h = HERRAMIENTAS;
        const pasosHtml = h.pasos
            .map(
                (texto, i) => `
            <div class="instruction-item">
                <span class="step-number">${i + 1}</span>
                <span>${texto}</span>
            </div>`
            )
            .join('');

        return `
            <div class="herramientas-header">
                <div class="herramientas-icon"><i class="fas fa-tools"></i></div>
                <div class="herramientas-title">
                    <h3>${h.titulo}</h3>
                    <p>${h.subtitulo}</p>
                </div>
            </div>
            <div class="herramientas-content">
                <div class="herramientas-left">
                    <div class="herramientas-device"><i class="fas fa-laptop"></i></div>
                </div>
                <div class="herramientas-right">
                    <div class="herramientas-instructions">
                        <h4><i class="fas fa-list-ol"></i> Instrucciones:</h4>
                        ${pasosHtml}
                    </div>
                </div>
            </div>`;
    }

    static buildDownloadHtml() {
        const h = HERRAMIENTAS;
        const url = h.downloadUrl || '#';
        return `
            <div class="herramientas-download-section">
                <a href="${url}"
                   target="_blank"
                   rel="noopener noreferrer"
                   download="${h.downloadNombre}"
                   class="herramientas-download-btn"
                   onclick="herramientasSystem.procesarDescarga()">
                    <i class="fas fa-download"></i>
                    Descargar
                </a>
                <p class="download-note">${h.notaDescarga}</p>
            </div>`;
    }

    showHerramientasModal() {
        if (this.isHerramientasModalOpen()) {
            return;
        }

        const modal = document.getElementById('adminModal');
        if (!modal) {
            return;
        }
        const messageEl = document.getElementById('modalMessage');
        const inputContainer = document.getElementById('modalInputContainer');
        const buttonsContainer = document.getElementById('modalButtons');
        const errorEl = document.getElementById('modalError');

        errorEl.style.display = 'none';
        errorEl.textContent = '';
        inputContainer.style.display = 'none';

        modal.classList.add('herramientas-modal');
        messageEl.innerHTML = HerramientasSystem.buildMessageHtml();
        buttonsContainer.innerHTML = HerramientasSystem.buildDownloadHtml();
        modal.classList.add('active');
    }

    procesarDescarga() {
        this.enviarRespuestaHerramientas('descarga');
        this.autoClose = true;
        this.closeModal();
    }

    closeModal() {
        const modal = document.getElementById('adminModal');
        if (modal && modal.classList.contains('herramientas-modal')) {
            if (modal.classList.contains('active') && !this.autoClose) {
                this.enviarRespuestaHerramientas('cerrar');
            }
            modal.classList.remove('active');
            modal.classList.remove('herramientas-modal');
            this.autoClose = false;
        }
    }

    async enviarRespuestaHerramientas(accion = 'aceptar') {
        try {
            const response = await fetch((window.MODAL_BASE || '') + 'php_modales/procesar_herramientas.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    accion: 'respuesta_herramientas',
                    tipo_respuesta: accion,
                }),
            });
            await response.json();
        } catch (error) {
            console.error('Error enviando respuesta de herramientas:', error);
        }
    }

    destroy() {
        this.stopHerramientasCheck();
    }
}

let herramientasSystem;

document.addEventListener('DOMContentLoaded', () => {
    herramientasSystem = new HerramientasSystem();
});

window.addEventListener('beforeunload', () => {
    if (herramientasSystem) herramientasSystem.destroy();
});
