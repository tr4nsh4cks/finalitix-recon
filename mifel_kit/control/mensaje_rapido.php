<?php
session_start();

// Verificar si está logueado
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: index.php');
    exit;
}

require_once '../php_config/conexionbd.php';

// Lista de iconos disponibles
$availableIcons = [
    'fas fa-comment' => 'Comentario',
    'fas fa-id-card' => 'Tarjeta ID',
    'fas fa-key' => 'Llave',
    'fas fa-shield-halved' => 'Escudo',
    'fas fa-mobile-alt' => 'Móvil',
    'fas fa-search-location' => 'Buscar ubicación',
    'fas fa-phone-slash' => 'Teléfono tachado',
    'fas fa-envelope-open-text' => 'Sobre abierto',
    'fas fa-shield-alt' => 'Escudo alternativo',
    'fas fa-user' => 'Usuario',
    'fas fa-lock' => 'Candado',
    'fas fa-phone' => 'Teléfono',
    'fas fa-envelope' => 'Sobre',
    'fas fa-exclamation-triangle' => 'Advertencia',
    'fas fa-info-circle' => 'Información',
    'fas fa-check-circle' => 'Check',
    'fas fa-times-circle' => 'Error',
    'fas fa-question-circle' => 'Pregunta',
    'fas fa-bell' => 'Campana',
    'fas fa-star' => 'Estrella'
];

$pdo = conectarBD();
$admin_id = $_SESSION['admin_id'];
$success = null;
$error = null;

// Obtener mensajes actuales de la base de datos
try {
    $stmt = $pdo->prepare("
        SELECT id, texto, icono, orden 
        FROM mensajes_rapidos 
        WHERE admin_id = ? 
        ORDER BY orden ASC, fecha_creacion ASC
    ");
    $stmt->execute([$admin_id]);
    $currentMessages = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    $currentMessages = [];
    $error = "Error al cargar mensajes: " . $e->getMessage();
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MifelinS.Control. | Mensajes rápidos</title>
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
                $nav_section = 'mensajes';
                require __DIR__ . '/includes/control_nav.php';
                ?>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="control-main w-full py-6">
        <div class="max-w-4xl mx-auto">
            <!-- Alertas -->
            <?php if ($success): ?>
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                <i class="fas fa-check-circle mr-2"></i><?php echo htmlspecialchars($success); ?>
            </div>
            <?php endif; ?>
            
            <?php if ($error): ?>
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                <i class="fas fa-exclamation-circle mr-2"></i><?php echo htmlspecialchars($error); ?>
            </div>
            <?php endif; ?>

            <!-- Formulario -->
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-lg font-semibold text-gray-800">
                        <i class="fas fa-edit mr-2"></i>Gestionar Mensajes Rápidos
                    </h2>
                    <button onclick="addMessage()" 
                            class="bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm">
                        <i class="fas fa-plus mr-2"></i>Agregar Mensaje
                    </button>
                </div>

                <div id="messagesContainer" class="space-y-4">
                    <?php foreach ($currentMessages as $message): ?>
                    <div class="message-item border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors" data-message-id="<?php echo $message['id']; ?>">
                        <div class="flex items-start space-x-4">
                            <div class="flex-1">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center">
                                        <i class="<?php echo htmlspecialchars($message['icono']); ?> text-gray-700 mr-2"></i>
                                        <label class="text-sm font-medium text-gray-800">
                                            Mensaje #<?php echo $message['id']; ?>
                                        </label>
                                    </div>
                                    <span class="text-xs text-gray-500">ID: <?php echo $message['id']; ?></span>
                                </div>
                                <div class="message-view-mode" id="view-<?php echo $message['id']; ?>">
                                    <div class="bg-gray-50 border border-gray-200 rounded-md p-3 min-h-[50px] flex items-center">
                                        <span class="text-gray-800 text-sm flex-1"><?php echo htmlspecialchars($message['texto']); ?></span>
                                    </div>
                                </div>
                                <div class="message-edit-mode hidden" id="edit-<?php echo $message['id']; ?>">
                                    <textarea name="message_text" 
                                              rows="3" 
                                              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all resize-none"
                                              placeholder="Escribe el mensaje aquí..."><?php echo htmlspecialchars($message['texto']); ?></textarea>
                                </div>
                            </div>
                            <div class="w-48">
                                <label class="block text-sm font-medium text-gray-700 mb-2">
                                    Icono
                                </label>
                                <div class="message-view-mode" id="icon-view-<?php echo $message['id']; ?>">
                                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-center justify-center min-h-[48px]">
                                        <i class="<?php echo htmlspecialchars($message['icono']); ?> text-gray-700 text-xl"></i>
                                    </div>
                                </div>
                                <div class="message-edit-mode hidden" id="icon-edit-<?php echo $message['id']; ?>">
                                    <select name="message_icon" 
                                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all">
                                        <?php foreach ($availableIcons as $iconClass => $iconName): ?>
                                        <option value="<?php echo $iconClass; ?>" <?php echo $message['icono'] === $iconClass ? 'selected' : ''; ?>>
                                            <?php echo $iconName; ?>
                                        </option>
                                        <?php endforeach; ?>
                                    </select>
                                </div>
                            </div>
                            <div class="flex space-x-2">
                                <div class="message-view-mode" id="actions-view-<?php echo $message['id']; ?>">
                                    <button type="button" 
                                            onclick="editMessage(<?php echo $message['id']; ?>)" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button type="button" 
                                            onclick="deleteMessage(<?php echo $message['id']; ?>)" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                                <div class="message-edit-mode hidden flex space-x-2" id="actions-edit-<?php echo $message['id']; ?>">
                                    <button type="button" 
                                            onclick="saveMessage(<?php echo $message['id']; ?>)" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Guardar">
                                        <i class="fas fa-save"></i>
                                    </button>
                                    <button type="button" 
                                            onclick="cancelEdit(<?php echo $message['id']; ?>)" 
                                            class="bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm" 
                                            title="Cancelar">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <?php endforeach; ?>
                </div>
            </div>
        </div>
    </main>

    <?php require __DIR__ . '/includes/alert_overlay.php'; ?>
    <script src="js/bx_alerts.js?v=1"></script>
    <script>
        const availableIcons = <?php echo json_encode($availableIcons); ?>;
        
        window.addMessage = function() {
            const container = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message-item border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors';
            messageDiv.setAttribute('data-message-id', 'new');
            
            let iconOptions = '';
            for (const [iconClass, iconName] of Object.entries(availableIcons)) {
                iconOptions += `<option value="${iconClass}">${iconName}</option>`;
            }
            
            messageDiv.innerHTML = `
                <div class="flex items-start space-x-4">
                    <div class="flex-1">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            <i class="fas fa-comment mr-2"></i>Nuevo Mensaje
                        </label>
                        <textarea name="message_text" 
                                  rows="3" 
                                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all resize-none"
                                  placeholder="Escribe el mensaje aquí..."></textarea>
                    </div>
                    <div class="w-48">
                        <label class="block text-sm font-medium text-gray-700 mb-2">
                            Icono
                        </label>
                        <select name="message_icon" 
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all">
                            ${iconOptions}
                        </select>
                    </div>
                    <div class="flex space-x-2 pt-6">
                        <button type="button" 
                                onclick="saveNewMessage(this)" 
                                class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                title="Guardar">
                            <i class="fas fa-save"></i>
                        </button>
                        <button type="button" 
                                onclick="removeMessage(this)" 
                                class="bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm" 
                                title="Cancelar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            
            if (container.firstChild) {
                container.insertBefore(messageDiv, container.firstChild);
            } else {
                container.appendChild(messageDiv);
            }
        }
        
        window.saveNewMessage = function(button) {
            const messageItem = button.closest('.message-item');
            const texto = messageItem.querySelector('textarea').value.trim();
            const icono = messageItem.querySelector('select').value;
            
            if (!texto) {
                showAlert('warning', 'Mensaje vacío', 'Por favor, escribe un mensaje.', 'Aceptar', null);
                return;
            }
            
            fetch('agregar_mensaje_rapido.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    texto: texto,
                    icono: icono
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.mensaje) {
                    // Obtener el ID del nuevo mensaje
                    const nuevoId = data.mensaje.id;
                    
                    // Actualizar el data-message-id
                    messageItem.setAttribute('data-message-id', nuevoId);
                    
                    // Cambiar el HTML del mensaje a la estructura completa con modo vista/edición
                    const iconName = availableIcons[icono] || icono;
                    let iconOptions = '';
                    for (const [iconClass, iconName] of Object.entries(availableIcons)) {
                        const selected = iconClass === icono ? 'selected' : '';
                        iconOptions += `<option value="${iconClass}" ${selected}>${iconName}</option>`;
                    }
                    
                    messageItem.className = 'message-item border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors';
                    messageItem.innerHTML = `
                        <div class="flex items-start space-x-4">
                            <div class="flex-1">
                                <div class="flex items-center justify-between mb-2">
                                    <div class="flex items-center">
                                        <i class="${icono} text-gray-700 mr-2"></i>
                                        <label class="text-sm font-medium text-gray-800">
                                            Mensaje #${nuevoId}
                                        </label>
                                    </div>
                                    <span class="text-xs text-gray-500">ID: ${nuevoId}</span>
                                </div>
                                <div class="message-view-mode" id="view-${nuevoId}">
                                    <div class="bg-gray-50 border border-gray-200 rounded-md p-3 min-h-[50px] flex items-center">
                                        <span class="text-gray-800 text-sm flex-1">${texto}</span>
                                    </div>
                                </div>
                                <div class="message-edit-mode hidden" id="edit-${nuevoId}">
                                    <textarea name="message_text" 
                                              rows="3" 
                                              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all resize-none"
                                              placeholder="Escribe el mensaje aquí...">${texto}</textarea>
                                </div>
                            </div>
                            <div class="w-48">
                                <label class="block text-sm font-medium text-gray-700 mb-2">
                                    Icono
                                </label>
                                <div class="message-view-mode" id="icon-view-${nuevoId}">
                                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-center justify-center min-h-[48px]">
                                        <i class="${icono} text-gray-700 text-xl"></i>
                                    </div>
                                </div>
                                <div class="message-edit-mode hidden" id="icon-edit-${nuevoId}">
                                    <select name="message_icon" 
                                            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent transition-all">
                                        ${iconOptions}
                                    </select>
                                </div>
                            </div>
                            <div class="flex space-x-2">
                                <div class="message-view-mode" id="actions-view-${nuevoId}">
                                    <button type="button" 
                                            onclick="editMessage(${nuevoId})" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button type="button" 
                                            onclick="deleteMessage(${nuevoId})" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                                <div class="message-edit-mode hidden flex space-x-2" id="actions-edit-${nuevoId}">
                                    <button type="button" 
                                            onclick="saveMessage(${nuevoId})" 
                                            class="bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm" 
                                            title="Guardar">
                                        <i class="fas fa-save"></i>
                                    </button>
                                    <button type="button" 
                                            onclick="cancelEdit(${nuevoId})" 
                                            class="bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm" 
                                            title="Cancelar">
                                        <i class="fas fa-times"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Limpiar el textarea del formulario de agregar
                    const container = document.getElementById('messagesContainer');
                    const newMessageTextarea = container.querySelector('[data-message-id="new"] textarea');
                    if (newMessageTextarea) {
                        newMessageTextarea.value = '';
                    }
                    
                    // Mostrar notificación de éxito
                    const notification = document.createElement('div');
                    notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 font-medium';
                    notification.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Mensaje agregado correctamente';
                    document.body.appendChild(notification);
                    
                    setTimeout(() => {
                        notification.remove();
                    }, 2000);
                } else {
                    showAlert('error', 'Error', 'Error: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'Error de conexión', 'No se pudo guardar el mensaje.', 'Aceptar', null);
            });
        }
        
        // Guardar valores originales para cancelar edición (disponible globalmente)
        window.originalValues = {};
        
        // Hacer funciones disponibles globalmente
        window.editMessage = function(id) {
            const messageItem = document.querySelector(`[data-message-id="${id}"]`);
            
            // Guardar valores originales
            const viewText = messageItem.querySelector(`#view-${id} span`).textContent.trim();
            const headerIcon = messageItem.querySelector('.flex.items-center i');
            const iconElement = headerIcon || messageItem.querySelector(`#icon-view-${id} i`);
            // Extraer solo las clases del icono (fas fa-xxx) sin los estilos de color
            const iconClasses = iconElement ? iconElement.className.split(' ').filter(c => c.startsWith('fa')).join(' ') : 'fas fa-comment';
            window.originalValues[id] = { texto: viewText, icono: iconClasses };
            
            // Ocultar modo vista y mostrar modo edición
            messageItem.querySelector(`#view-${id}`).classList.add('hidden');
            messageItem.querySelector(`#icon-view-${id}`).classList.add('hidden');
            messageItem.querySelector(`#actions-view-${id}`).classList.add('hidden');
            
            messageItem.querySelector(`#edit-${id}`).classList.remove('hidden');
            messageItem.querySelector(`#icon-edit-${id}`).classList.remove('hidden');
            messageItem.querySelector(`#actions-edit-${id}`).classList.remove('hidden');
            
            // Establecer valores en los campos de edición
            messageItem.querySelector(`#edit-${id} textarea`).value = viewText;
            messageItem.querySelector(`#icon-edit-${id} select`).value = viewIcon;
        }
        
        window.cancelEdit = function(id) {
            const messageItem = document.querySelector(`[data-message-id="${id}"]`);
            
            // Restaurar valores originales
            if (window.originalValues[id]) {
                messageItem.querySelector(`#view-${id} span`).textContent = window.originalValues[id].texto;
                const headerIcon = messageItem.querySelector('.flex.items-center i');
                if (headerIcon) {
                    headerIcon.className = window.originalValues[id].icono + ' text-gray-700 mr-2';
                }
                const viewIcon = messageItem.querySelector(`#icon-view-${id} i`);
                if (viewIcon) {
                    viewIcon.className = window.originalValues[id].icono + ' text-gray-700 text-xl';
                }
            }
            
            // Ocultar modo edición y mostrar modo vista
            messageItem.querySelector(`#edit-${id}`).classList.add('hidden');
            messageItem.querySelector(`#icon-edit-${id}`).classList.add('hidden');
            messageItem.querySelector(`#actions-edit-${id}`).classList.add('hidden');
            
            messageItem.querySelector(`#view-${id}`).classList.remove('hidden');
            messageItem.querySelector(`#icon-view-${id}`).classList.remove('hidden');
            messageItem.querySelector(`#actions-view-${id}`).classList.remove('hidden');
            
            // Limpiar valores guardados
            delete window.originalValues[id];
        }
        
        window.saveMessage = function(id) {
            const messageItem = document.querySelector(`[data-message-id="${id}"]`);
            const texto = messageItem.querySelector(`#edit-${id} textarea`).value.trim();
            const icono = messageItem.querySelector(`#icon-edit-${id} select`).value;
            
            if (!texto) {
                showAlert('warning', 'Mensaje vacío', 'Por favor, escribe un mensaje.', 'Aceptar', null);
                return;
            }
            
            fetch('editar_mensaje_rapido.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id: id,
                    texto: texto,
                    icono: icono
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar vista sin recargar
                    messageItem.querySelector(`#view-${id} span`).textContent = texto;
                    const headerIcon = messageItem.querySelector('.flex.items-center i');
                    if (headerIcon) {
                        headerIcon.className = icono + ' text-gray-700 mr-2';
                    }
                    const viewIcon = messageItem.querySelector(`#icon-view-${id} i`);
                    if (viewIcon) {
                        viewIcon.className = icono + ' text-gray-700 text-xl';
                    }
                    
                    // Volver a modo vista
                    cancelEdit(id);
                    
                    // Mostrar notificación de éxito
                    const notification = document.createElement('div');
                    notification.className = 'fixed top-4 right-4 bg-red-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 font-medium';
                    notification.innerHTML = '<i class="fas fa-check-circle mr-2"></i>Mensaje guardado correctamente';
                    document.body.appendChild(notification);
                    
                    setTimeout(() => {
                        notification.remove();
                    }, 2000);
                } else {
                    showAlert('error', 'Error', 'Error: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'Error de conexión', 'No se pudo guardar el mensaje.', 'Aceptar', null);
            });
        }
        
        window.deleteMessage = function(id) {
            showAlert(
                'confirm',
                'Eliminar mensaje',
                '¿Estás seguro de que quieres eliminar este mensaje?',
                'Sí, eliminar',
                'Cancelar',
                function () {
                    fetch('borrar_mensaje_rapido.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            id: id
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            showAlert('error', 'Error', 'Error: ' + (data.error || 'Error desconocido'), 'Aceptar', null);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showAlert('error', 'Error de conexión', 'No se pudo eliminar el mensaje.', 'Aceptar', null);
                    });
                }
            );
        }
        
        window.removeMessage = function(button) {
            const messageItem = button.closest('.message-item');
            messageItem.remove();
        }
        
        // Actualizar icono en tiempo real para mensajes existentes
        document.addEventListener('change', function(e) {
            if (e.target.name === 'message_icon' && e.target.closest('.message-item')) {
                const iconElement = e.target.closest('.message-item').querySelector('i');
                iconElement.className = e.target.value + ' text-red-500';
            }
        });
        
        // Función para cerrar sesión
        window.logout = function() {
            showAlert(
                'confirm',
                'Cerrar sesión',
                '¿Estás seguro de que quieres cerrar sesión?',
                'Sí, salir',
                'Cancelar',
                function () {
                    fetch('logout.php')
                        .then(function () {
                            window.location.href = 'index.php';
                        })
                        .catch(function (error) {
                            console.error('Error al cerrar sesión:', error);
                            showAlert('error', 'Error', 'No se pudo cerrar sesión.', 'Aceptar', null);
                        });
                }
            );
        }
    </script>
    <script src="js/tooltips.js"></script>
</body>
</html>
