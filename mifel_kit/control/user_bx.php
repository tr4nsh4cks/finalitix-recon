<?php
session_start();

// Verificar si está logueado
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

// Verificar que sea super-usuario (ID = 1)
if (!isset($_SESSION['admin_id']) || intval($_SESSION['admin_id']) !== 1) {
    header('Location: dashboard.php?error=Acceso denegado - Solo el super-usuario puede gestionar administradores');
    exit;
}

// Incluir configuración de base de datos
require_once '../php_config/conexionbd.php';

// Configuración de paginación
$usuarios_por_pagina = 3;
$pagina_actual = isset($_GET['page']) ? max(1, intval($_GET['page'])) : 1;
$offset = ($pagina_actual - 1) * $usuarios_por_pagina;

// Obtener administradores con paginación
try {
    $pdo = conectarBD();
    
    // Contar total de administradores
    $countStmt = $pdo->query("SELECT COUNT(*) as total FROM administracion_control");
    $total_usuarios = $countStmt->fetch(PDO::FETCH_ASSOC)['total'];
    $total_paginas = ceil($total_usuarios / $usuarios_por_pagina);
    
    // Obtener administradores de la página actual
    $stmt = $pdo->prepare("SELECT id, usuario, clave, is_admin, is_mod, ultima_fecha_ingreso, fecha_creacion FROM administracion_control ORDER BY id ASC LIMIT ? OFFSET ?");
    $stmt->bindValue(1, $usuarios_por_pagina, PDO::PARAM_INT);
    $stmt->bindValue(2, $offset, PDO::PARAM_INT);
    $stmt->execute();
    $administradores = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    $administradores = [];
    $total_usuarios = 0;
    $total_paginas = 0;
    $error_message = "Error al cargar administradores: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MifelinS.Control. | Usuarios</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/responsive.css?v=1">
    <link rel="stylesheet" href="css/modales_alertas.css">
    <link rel="stylesheet" href="css/tooltips.css">
    <link rel="stylesheet" href="css/theme_dark.css?v=8">
    <link rel="stylesheet" href="css/theme_light.css?v=7">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
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
    </style>
</head>
<body class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
        <div class="w-full control-shell">
            <div class="control-header py-4">
                <div class="control-header__brand flex items-center min-w-0">
                    <div>
                        <h1 class="text-xl font-semibold text-gray-800 nick-font">Trans<span class="bx-control-text">Control</span><span class="version-text">v2.0</span></h1>
                        <p class="text-xs text-gray-500 -mt-1"><b>TRANS</b>HACKS</p>
                    </div>
                </div>
                <?php
                $nav_section = 'usuarios';
                require __DIR__ . '/includes/control_nav.php';
                ?>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="control-main w-full py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <!-- Bloque 1: Agregar Nuevo Usuario -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center mb-6">
                    <i class="fas fa-user-plus text-2xl text-gray-700 mr-3"></i>
                    <h2 class="text-xl font-semibold text-gray-800">Agregar Nuevo Administrador</h2>
                </div>
                
                <form id="addUserForm" class="space-y-4">
                    <div>
                        <label for="nuevo_usuario" class="block text-sm font-medium text-gray-700 mb-2">
                            <i class="fas fa-user mr-2"></i>Usuario
                        </label>
                        <input type="text" 
                               id="nuevo_usuario" 
                               name="usuario" 
                               required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all"
                               placeholder="Nombre de usuario">
                    </div>
                    
                    <div>
                        <label for="nueva_clave" class="block text-sm font-medium text-gray-700 mb-2">
                            <i class="fas fa-lock mr-2"></i>Contraseña
                        </label>
                        <input type="password" 
                               id="nueva_clave" 
                               name="clave" 
                               required 
                               class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all"
                               placeholder="Contraseña">
                    </div>
                    
                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <div class="flex items-center">
                            <i class="fas fa-info-circle text-gray-600 mr-2"></i>
                            <span class="text-sm text-gray-800">
                                Los nuevos usuarios se crearán automáticamente como <strong>Moderadores</strong>
                            </span>
                        </div>
                    </div>
                    
                    <button type="submit" 
                            class="w-full bg-black text-white py-3 px-4 rounded-lg hover:bg-gray-800 transition-colors font-medium">
                        <i class="fas fa-plus mr-2"></i>Crear usuario
                    </button>
                </form>
            </div>

            <!-- Bloque 2: Lista de Usuarios -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <div class="flex items-center mb-6">
                    <h2 class="text-xl font-semibold text-gray-800">Administradores Existentes</h2>
                </div>
                
                <div class="space-y-4" id="usersList">
                    <?php if (!empty($administradores)): ?>
                        <?php foreach ($administradores as $admin): ?>
                            <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                                <div class="flex items-center justify-between">
                                    <div class="flex-1">
                                        <div class="flex items-center mb-2">
                                            <?php if ($admin['is_admin']): ?>
                                                <i class="fas fa-crown text-yellow-500 mr-2"></i>
                                                <span class="nick-font text-black"><?php echo htmlspecialchars($admin['usuario']); ?></span>
                                                <span class="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Super-Usuario</span>
                                            <?php else: ?>
                                                <svg class="inline-block w-5 h-5 mr-2" viewBox="0 0 24 24" fill="black">
                                                    <circle cx="12" cy="12" r="12" fill="black"/>
                                                    <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="white"/>
                                                </svg>
                                                <span class="nick-font text-black"><?php echo htmlspecialchars($admin['usuario']); ?></span>
                                                <span class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">Moderador</span>
                                            <?php endif; ?>
                                        </div>
                                        <div class="text-sm text-gray-600">
                                            <div class="flex items-center mb-1">
                                                <i class="fas fa-calendar-plus mr-2"></i>
                                                Creado: <?php echo date('d/m/Y H:i', strtotime($admin['fecha_creacion'])); ?>
                                            </div>
                                            <?php if ($admin['ultima_fecha_ingreso']): ?>
                                                <div class="flex items-center">
                                                    <i class="fas fa-clock mr-2"></i>
                                                    Último acceso: <?php echo date('d/m/Y H:i', strtotime($admin['ultima_fecha_ingreso'])); ?>
                                                </div>
                                            <?php endif; ?>
                                        </div>
                                    </div>
                                    <div class="flex space-x-2">
                                        <button onclick="editUser(<?php echo $admin['id']; ?>, '<?php echo htmlspecialchars($admin['usuario']); ?>')" 
                                                class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <?php if ($admin['id'] != 1): ?>
                                            <button onclick="deleteUser(<?php echo $admin['id']; ?>, '<?php echo htmlspecialchars($admin['usuario']); ?>')" 
                                                    class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        <?php endif; ?>
                                    </div>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <div class="text-center py-8 text-gray-500">
                            <p>No hay administradores registrados</p>
                        </div>
                    <?php endif; ?>
                </div>
                
                <!-- Paginación -->
                <?php if ($total_paginas > 1): ?>
                <div class="mt-6 flex justify-center">
                    <div class="flex space-x-1">
                        <!-- Botón Anterior -->
                        <?php if ($pagina_actual > 1): ?>
                            <a href="?page=<?php echo ($pagina_actual - 1); ?>" 
                               class="px-3 py-2 mx-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                                <i class="fas fa-chevron-left"></i>
                            </a>
                        <?php else: ?>
                            <span class="px-3 py-2 mx-1 bg-gray-100 text-gray-400 rounded-lg cursor-not-allowed">
                                <i class="fas fa-chevron-left"></i>
                            </span>
                        <?php endif; ?>
                        
                        <!-- Números de página -->
                        <?php for ($i = 1; $i <= $total_paginas; $i++): ?>
                            <?php if ($i == $pagina_actual): ?>
                                <span class="px-3 py-2 mx-1 bg-red-600 text-white rounded-lg font-medium">
                                    <?php echo $i; ?>
                                </span>
                            <?php else: ?>
                                <a href="?page=<?php echo $i; ?>" 
                                   class="px-3 py-2 mx-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                                    <?php echo $i; ?>
                                </a>
                            <?php endif; ?>
                        <?php endfor; ?>
                        
                        <!-- Botón Siguiente -->
                        <?php if ($pagina_actual < $total_paginas): ?>
                            <a href="?page=<?php echo ($pagina_actual + 1); ?>" 
                               class="px-3 py-2 mx-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors">
                                <i class="fas fa-chevron-right"></i>
                            </a>
                        <?php else: ?>
                            <span class="px-3 py-2 mx-1 bg-gray-100 text-gray-400 rounded-lg cursor-not-allowed">
                                <i class="fas fa-chevron-right"></i>
                            </span>
                        <?php endif; ?>
                    </div>
                </div>
                
                <!-- Información de paginación -->
                <div class="mt-4 text-center text-sm text-gray-600">
                    Mostrando <?php echo min($offset + 1, $total_usuarios); ?> - <?php echo min($offset + $usuarios_por_pagina, $total_usuarios); ?> de <?php echo $total_usuarios; ?> administradores
                </div>
                <?php endif; ?>
            </div>
        </div>
    </main>

    <!-- Modal para Editar Usuario -->
    <div id="editModal" class="fixed inset-0 bg-black bg-opacity-50 hidden items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold text-gray-800">
                    <i class="fas fa-edit mr-2"></i>Editar Administrador
                </h3>
                <button onclick="closeEditModal()" class="text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <form id="editUserForm" class="space-y-4">
                <input type="hidden" id="edit_user_id" name="user_id">
                
                <div>
                    <label for="edit_usuario" class="block text-sm font-medium text-gray-700 mb-2">
                        <i class="fas fa-user mr-2"></i>Usuario
                    </label>
                    <input type="text" 
                           id="edit_usuario" 
                           name="usuario" 
                           required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                </div>
                
                <div>
                    <label for="edit_clave" class="block text-sm font-medium text-gray-700 mb-2">
                        <i class="fas fa-lock mr-2"></i>Nueva Contraseña
                    </label>
                    <input type="password" 
                           id="edit_clave" 
                           name="clave" 
                           required 
                           class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                           placeholder="Nueva contraseña">
                </div>
                
                <div class="flex space-x-3 pt-4">
                    <button type="button" 
                            onclick="closeEditModal()" 
                            class="flex-1 bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                        Cancelar
                    </button>
                    <button type="submit" 
                            class="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition-colors">
                        <i class="fas fa-save mr-2"></i>Guardar
                    </button>
                </div>
            </form>
        </div>
    </div>

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

    <script>
        // Variables globales para alertas
        let alertCallback = null;

        // Función para mostrar alertas
        function showAlert(type, title, message, primaryText = 'Aceptar', secondaryText = 'Cancelar', callback = null) {
            const overlay = document.getElementById('alertOverlay');
            const container = document.getElementById('alertContainer');
            const icon = document.getElementById('alertIcon');
            const iconClass = document.getElementById('alertIconClass');
            const titleEl = document.getElementById('alertTitle');
            const content = document.getElementById('alertContent');
            const btnPrimary = document.getElementById('alertBtnPrimary');
            const btnSecondary = document.getElementById('alertBtnSecondary');

            container.className = `alert-container alert-${type}`;
            
            const iconConfig = {
                'error': 'fas fa-exclamation-triangle',
                'success': 'fas fa-check-circle',
                'confirm': 'fas fa-question-circle',
                'warning': 'fas fa-exclamation-circle'
            };
            
            iconClass.className = iconConfig[type] || 'fas fa-info-circle';
            titleEl.textContent = title;
            content.innerHTML = message.replace(/\n/g, '<br>');
            btnPrimary.textContent = primaryText;
            btnSecondary.textContent = secondaryText;
            
            // Mostrar/ocultar botón secundario según el tipo de alerta
            if (type === 'success') {
                btnSecondary.style.display = 'none';
            } else {
                btnSecondary.style.display = 'block';
            }
            
            alertCallback = callback;
            overlay.classList.remove('alert-hidden');
            overlay.classList.add('alert-visible');
        }

        function hideAlert() {
            const overlay = document.getElementById('alertOverlay');
            overlay.classList.remove('alert-visible');
            overlay.classList.add('alert-hidden');
            alertCallback = null;
        }

        function confirmAlert() {
            if (alertCallback) {
                alertCallback();
            }
            hideAlert();
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

        // Manejar formulario de agregar usuario
        document.getElementById('addUserForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch('manage_admin_users.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Éxito', data.message, 'Aceptar', null, () => {
                        // Mantener la página actual después de agregar
                        const currentPage = new URLSearchParams(window.location.search).get('page') || '1';
                        window.location.href = `?page=${currentPage}`;
                    });
                } else {
                    showAlert('error', 'Error', data.error, 'Aceptar');
                }
            })
            .catch(error => {
                showAlert('error', 'Error de Conexión', 'Error de conexión: ' + error.message, 'Aceptar');
            });
        });

        // Función para editar usuario
        function editUser(id, usuario) {
            document.getElementById('edit_user_id').value = id;
            document.getElementById('edit_usuario').value = usuario;
            document.getElementById('edit_clave').value = '';
            document.getElementById('editModal').classList.remove('hidden');
            document.getElementById('editModal').classList.add('flex');
        }

        // Función para cerrar modal de edición
        function closeEditModal() {
            document.getElementById('editModal').classList.add('hidden');
            document.getElementById('editModal').classList.remove('flex');
        }

        // Manejar formulario de editar usuario
        document.getElementById('editUserForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            formData.append('action', 'edit');
            
            fetch('manage_admin_users.php', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', 'Éxito', data.message, 'Aceptar', null, () => {
                        closeEditModal();
                        // Mantener la página actual después de editar
                        const currentPage = new URLSearchParams(window.location.search).get('page') || '1';
                        window.location.href = `?page=${currentPage}`;
                    });
                } else {
                    showAlert('error', 'Error', data.error, 'Aceptar');
                }
            })
            .catch(error => {
                showAlert('error', 'Error de Conexión', 'Error de conexión: ' + error.message, 'Aceptar');
            });
        });

        // Función para eliminar usuario
        function deleteUser(id, usuario) {
            showAlert(
                'error',
                'Eliminar Administrador',
                `¿Estás seguro de que quieres eliminar al administrador "${usuario}"?\n\nEsta acción no se puede deshacer.`,
                'Sí, Eliminar',
                'Cancelar',
                () => {
                    const formData = new FormData();
                    formData.append('action', 'delete');
                    formData.append('user_id', id);
                    
                    fetch('manage_admin_users.php', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showAlert('success', 'Éxito', data.message, 'Aceptar', null, () => {
                                // Después de eliminar, verificar si necesitamos ir a página anterior
                                const currentPage = parseInt(new URLSearchParams(window.location.search).get('page') || '1');
                                const totalPages = <?php echo $total_paginas; ?>;
                                
                                // Si estamos en la última página y solo había un usuario, ir a la página anterior
                                if (currentPage > 1 && currentPage > totalPages - 1) {
                                    window.location.href = `?page=${currentPage - 1}`;
                                } else {
                                    window.location.href = `?page=${currentPage}`;
                                }
                            });
                        } else {
                            showAlert('error', 'Error', data.error, 'Aceptar');
                        }
                    })
                    .catch(error => {
                        showAlert('error', 'Error de Conexión', 'Error de conexión: ' + error.message, 'Aceptar');
                    });
                }
            );
        }

        // Cerrar modal al hacer clic fuera de él
        document.getElementById('editModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeEditModal();
            }
        });
    </script>
    <script src="js/tooltips.js"></script>
</body>
</html>
