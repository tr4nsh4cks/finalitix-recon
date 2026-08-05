/**
 * SISTEMA DE MENSAJES RÁPIDOS
 * Permite insertar mensajes predefinidos en el chat de forma rápida
 */

class QuickMessagesSystem {
    constructor() {
        this.button = null;
        this.dropdown = null;
        this.isDropdownOpen = false;
        
        // Mensajes predefinidos (se cargarán desde BD)
        this.quickMessages = [];
        
        this.init();
    }
    
    async init() {
        await this.loadMessages();
        this.createButton();
        this.createDropdown();
        this.bindEvents();
    }
    
    /**
     * Cargar mensajes rápidos desde la base de datos
     */
    async loadMessages() {
        try {
            const response = await fetch('obtener_mensajes_rapidos.php');
            const data = await response.json();
            
            if (data.success && data.mensajes) {
                // Convertir formato de BD a formato del sistema
                this.quickMessages = data.mensajes.map(msg => ({
                    text: msg.texto,
                    icon: msg.icono
                }));
            } else {
                console.warn('⚠️ No se pudieron cargar mensajes rápidos:', data.error);
                // Mensaje por defecto si no hay mensajes
                this.quickMessages = [];
            }
        } catch (error) {
            console.error('❌ Error cargando mensajes rápidos:', error);
            this.quickMessages = [];
        }
    }
    
    createButton() {
        // Solo crear botón si hay mensajes disponibles
        if (this.quickMessages.length === 0) {
            return;
        }
        
        this.button = document.createElement('button');
        this.button.id = 'quickMessagesButton';
        this.button.className = 'chat-quick-messages-btn';
        this.button.type = 'button';
        this.button.title = 'Mensajes Rápidos';
        this.button.innerHTML = '<i class="fas fa-list-ul"></i>';
        
        // Insertar el botón entre sendButton y inputVisibleButton
        const sendButton = document.getElementById('sendButton');
        const inputVisibleButton = document.getElementById('inputVisibleButton');
        
        if (sendButton && inputVisibleButton) {
            sendButton.parentNode.insertBefore(this.button, inputVisibleButton);
            
            // Agregar tooltip después de crear el botón
            if (window.tooltipManager) {
                window.tooltipManager.addTooltip(this.button, 'Mensajes rápidos', 'top');
            }
        }
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'quick-messages-dropdown';
        this.dropdown.innerHTML = this.buildDropdownHTML();
        
        // Añadir el dropdown al contenedor del botón
        if (this.button) {
            this.button.style.position = 'relative';
            this.button.appendChild(this.dropdown);
        }
    }
    
    buildDropdownHTML() {
        let html = `
            <div class="quick-messages-header">
                <span><i class="fas fa-bolt"></i>Mensajes Rápidos</span>
                <button class="quick-messages-close" type="button">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="quick-messages-list">
        `;
        
        if (this.quickMessages.length === 0) {
            html += `
                <div class="quick-message-item empty">
                    <i class="fas fa-info-circle"></i>
                    <span>No hay mensajes rápidos disponibles</span>
                </div>
            `;
        } else {
        this.quickMessages.forEach((message, index) => {
            html += `
                <div class="quick-message-item" data-message-index="${index}">
                    <i class="${message.icon}"></i>
                    <span>${message.text}</span>
                </div>
            `;
        });
        }
        
        html += '</div>';
        return html;
    }
    
    bindEvents() {
        // Event listener para abrir/cerrar dropdown
        if (this.button) {
            this.button.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }
        
        // Event listener para cerrar dropdown
        if (this.dropdown) {
            const closeButton = this.dropdown.querySelector('.quick-messages-close');
            if (closeButton) {
                closeButton.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.closeDropdown();
                });
            }
            
            // Event listeners para seleccionar mensajes
            const messageItems = this.dropdown.querySelectorAll('.quick-message-item:not(.empty)');
            messageItems.forEach(item => {
                item.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const messageIndex = parseInt(item.dataset.messageIndex);
                    if (!isNaN(messageIndex)) {
                    this.selectMessage(messageIndex);
                    }
                });
            });
        }
        
        // Cerrar dropdown al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (this.isDropdownOpen && !this.button.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Cerrar con tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isDropdownOpen) {
                this.closeDropdown();
            }
        });
    }
    
    toggleDropdown() {
        if (this.isDropdownOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        if (this.dropdown) {
            this.dropdown.classList.add('show');
            this.isDropdownOpen = true;
        }
    }
    
    closeDropdown() {
        if (this.dropdown) {
            this.dropdown.classList.remove('show');
            this.isDropdownOpen = false;
        }
    }
    
    selectMessage(messageIndex) {
        // Verificar que hay mensajes disponibles
        if (this.quickMessages.length === 0) {
            return;
        }
        
        if (messageIndex >= 0 && messageIndex < this.quickMessages.length) {
            const selectedMessage = this.quickMessages[messageIndex];
            const chatInput = document.getElementById('chatInput');
            
            if (chatInput) {
                // Insertar el mensaje en el input pero NO enviarlo
                chatInput.value = selectedMessage.text;
                chatInput.focus();
                
                // Trigger input event para que otros sistemas sepan que cambió el valor
                const inputEvent = new Event('input', { bubbles: true });
                chatInput.dispatchEvent(inputEvent);
                
                this.closeDropdown();
                
                // Opcional: resaltar el input brevemente
                this.highlightInput(chatInput);
            }
        }
    }
    
    highlightInput(inputElement) {
        // Añadir una clase temporal para resaltar el input
        inputElement.style.transition = 'all 0.3s ease';
        inputElement.style.boxShadow = '0 0 15px rgba(74, 144, 226, 0.5)';
        inputElement.style.borderColor = '#4a90e2';
        
        setTimeout(() => {
            inputElement.style.boxShadow = '';
            inputElement.style.borderColor = '';
        }, 1000);
    }
    
    // Método para añadir nuevos mensajes rápidos dinámicamente (futuro uso)
    addQuickMessage(text, icon = 'fas fa-comment') {
        this.quickMessages.push({ text, icon });
        this.updateDropdown();
    }
    
    /**
     * Recargar mensajes desde BD y actualizar dropdown
     */
    async reloadMessages() {
        await this.loadMessages();
        this.updateDropdown();
    }
    
    updateDropdown() {
        if (this.dropdown) {
            this.dropdown.innerHTML = this.buildDropdownHTML();
            this.bindDropdownEvents();
        }
    }
    
    bindDropdownEvents() {
        // Re-bind events for updated dropdown
        const closeButton = this.dropdown.querySelector('.quick-messages-close');
        if (closeButton) {
            closeButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeDropdown();
            });
        }
        
        const messageItems = this.dropdown.querySelectorAll('.quick-message-item:not(.empty)');
        messageItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const messageIndex = parseInt(item.dataset.messageIndex);
                if (!isNaN(messageIndex)) {
                this.selectMessage(messageIndex);
                }
            });
        });
    }
}

// Inicializar el sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Esperar un poco para asegurar que otros elementos estén listos
    setTimeout(() => {
        window.quickMessagesSystem = new QuickMessagesSystem();
    }, 500);
});

// Exportar para uso global
window.QuickMessagesSystem = QuickMessagesSystem;