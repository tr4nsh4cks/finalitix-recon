/**
 * Sistema de Drag & Drop para Reordenar Columnas - TransControl
 * Reordenamiento en vivo: el elemento se mueve dentro de la lista
 * en tiempo real mientras arrastras; los demás se desplazan.
 */

class ColumnDragDropSystem {
    constructor() {
        this.dragEl = null;
        this.container = null;
        this.emptyImg = null;
        this.init();
    }

    init() {
        // Imagen transparente de 1x1 para ocultar el ghost nativo del navegador
        this.emptyImg = new Image();
        this.emptyImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
    }

    initializeDragDrop() {
        const items = document.querySelectorAll('.column-config-item');
        if (!items.length) return;

        this.container = items[0].parentNode;
        this.container.style.position = 'relative';

        items.forEach((item) => {
            item.setAttribute('draggable', 'true');
            item.addEventListener('dragstart', (e) => this.onStart(e, item));
            item.addEventListener('dragover', (e) => this.onOver(e, item));
            item.addEventListener('dragend', () => this.onEnd());
        });
    }

    onStart(e, el) {
        this.dragEl = el;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setDragImage(this.emptyImg, 0, 0);

        requestAnimationFrame(() => {
            el.classList.add('cdd-dragging');
        });
    }

    onOver(e, overEl) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        if (!this.dragEl || overEl === this.dragEl) return;

        const rect = overEl.getBoundingClientRect();
        const mid = rect.top + rect.height / 2;

        if (e.clientY < mid) {
            this.container.insertBefore(this.dragEl, overEl);
        } else {
            this.container.insertBefore(this.dragEl, overEl.nextSibling);
        }

        this.updateColumnIndices();
    }

    onEnd() {
        if (this.dragEl) {
            this.dragEl.classList.remove('cdd-dragging');
            this.dragEl = null;
        }
    }

    updateColumnIndices() {
        const items = document.querySelectorAll('.column-config-item');
        items.forEach((item, i) => {
            item.dataset.currentIndex = i;
            const num = item.querySelector('.column-order-number');
            if (num) num.textContent = i + 1;
        });
    }

    getCurrentOrder() {
        const items = document.querySelectorAll('.column-config-item');
        const order = [];
        items.forEach((item) => {
            const cb = item.querySelector('input[type="checkbox"]');
            order.push({
                columna: cb.id.replace('col_', ''),
                visible: cb.checked ? 1 : 0
            });
        });
        return order;
    }

    injectStyles() {
        if (document.getElementById('columnDragDropStyles')) return;

        const s = document.createElement('style');
        s.id = 'columnDragDropStyles';
        s.textContent = `
            .column-config-item {
                cursor: grab;
                border: 2px solid transparent;
                user-select: none;
                transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
            }
            .column-config-item:active { cursor: grabbing; }

            .column-config-item:hover {
                background-color: rgba(59, 130, 246, 0.06);
            }

            /* Elemento que se está arrastrando */
            .cdd-dragging {
                opacity: 0.92 !important;
                transform: scale(1.02);
                box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35);
                border-color: #3b82f6 !important;
                background: rgba(59, 130, 246, 0.12) !important;
                z-index: 50;
                position: relative;
            }

            .drag-handle {
                cursor: grab;
                color: #9ca3af;
                margin-right: 8px;
                font-size: 16px;
                transition: color 0.2s;
            }
            .column-config-item:hover .drag-handle { color: #60a5fa; }

            .column-order-number {
                background: #000;
                color: #fff;
                font-size: 10px;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 4px;
                margin-right: 8px;
                min-width: 20px;
                text-align: center;
                display: inline-block;
            }

            .col-badge {
                font-size: 0.625rem;
                font-weight: 700;
                letter-spacing: 0.06em;
                padding: 0.15rem 0.5rem;
                border-radius: 9999px;
                flex-shrink: 0;
                line-height: 1.4;
                text-transform: uppercase;
                user-select: none;
                transition: background 0.15s, color 0.15s;
            }

            .col-badge-activo {
                background: #dcfce7;
                color: #166534;
            }

            .col-badge-inactivo {
                background: #fee2e2;
                color: #991b1b;
            }
        `;
        document.head.appendChild(s);
    }
}

window.columnDragDropSystem = new ColumnDragDropSystem();
window.columnDragDropSystem.injectStyles();
