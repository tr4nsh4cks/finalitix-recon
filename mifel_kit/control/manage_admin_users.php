<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth(null, true);
exigirPOST();

$pdo = conectarBD();

try {
    $action = $_POST['action'] ?? 'add';

    switch ($action) {
        case 'add':
            $usuario = trim($_POST['usuario'] ?? '');
            $clave = trim($_POST['clave'] ?? '');

            if (empty($usuario) || empty($clave)) {
                jsonError('Usuario y contraseña son requeridos');
            }

            if (strlen($clave) < 4) {
                jsonError('La contraseña debe tener al menos 4 caracteres');
            }

            $checkStmt = $pdo->prepare("SELECT id FROM administracion_control WHERE usuario = ?");
            $checkStmt->execute([$usuario]);

            if ($checkStmt->fetch()) {
                jsonError('El usuario ya existe');
            }

            $permisos = json_encode([
                'ver_registros' => true,
                'editar_registros' => true,
                'eliminar_registros' => true
            ]);

            $insertStmt = $pdo->prepare("
                INSERT INTO administracion_control (usuario, clave, permisos, is_admin, is_mod, fecha_creacion) 
                VALUES (?, ?, ?, 0, 1, NOW())
            ");
            $insertStmt->execute([$usuario, $clave, $permisos]);

            jsonResponse(['success' => true, 'message' => "Moderador '{$usuario}' creado exitosamente"]);
            break;

        case 'edit':
            $user_id = intval($_POST['user_id'] ?? 0);
            $usuario = trim($_POST['usuario'] ?? '');
            $clave = trim($_POST['clave'] ?? '');

            if (!$user_id || empty($usuario) || empty($clave)) {
                jsonError('Todos los campos son requeridos');
            }

            if (strlen($clave) < 4) {
                jsonError('La contraseña debe tener al menos 4 caracteres');
            }

            $checkStmt = $pdo->prepare("SELECT id, usuario FROM administracion_control WHERE id = ?");
            $checkStmt->execute([$user_id]);
            $existingUser = $checkStmt->fetch(PDO::FETCH_ASSOC);

            if (!$existingUser) {
                jsonError('Usuario no encontrado', 404);
            }

            if ($existingUser['usuario'] !== $usuario) {
                $checkDuplicateStmt = $pdo->prepare("SELECT id FROM administracion_control WHERE usuario = ? AND id != ?");
                $checkDuplicateStmt->execute([$usuario, $user_id]);

                if ($checkDuplicateStmt->fetch()) {
                    jsonError('El nombre de usuario ya está en uso');
                }
            }

            $updateStmt = $pdo->prepare("UPDATE administracion_control SET usuario = ?, clave = ? WHERE id = ?");
            $updateStmt->execute([$usuario, $clave, $user_id]);

            if ($user_id == $_SESSION['admin_id']) {
                $_SESSION['admin_usuario'] = $usuario;
            }

            jsonResponse(['success' => true, 'message' => "Usuario '{$usuario}' actualizado exitosamente"]);
            break;

        case 'delete':
            $user_id = intval($_POST['user_id'] ?? 0);

            if (!$user_id) {
                jsonError('ID de usuario requerido');
            }

            if ($user_id === 1) {
                jsonError('No se puede eliminar al super-usuario');
            }

            if ($user_id == $_SESSION['admin_id']) {
                jsonError('No puedes eliminarte a ti mismo');
            }

            $checkStmt = $pdo->prepare("SELECT usuario FROM administracion_control WHERE id = ?");
            $checkStmt->execute([$user_id]);
            $user = $checkStmt->fetch(PDO::FETCH_ASSOC);

            if (!$user) {
                jsonError('Usuario no encontrado', 404);
            }

            $deleteStmt = $pdo->prepare("DELETE FROM administracion_control WHERE id = ?");
            $deleteStmt->execute([$user_id]);

            jsonResponse(['success' => true, 'message' => "Usuario '{$user['usuario']}' eliminado exitosamente"]);
            break;

        default:
            jsonError('Acción no válida');
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
