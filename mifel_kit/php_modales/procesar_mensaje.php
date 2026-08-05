<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['accion'])) {
        jsonResponse(['success' => false, 'error' => 'Datos no válidos']);
    }

    $accion = $input['accion'];

    if ($accion === 'marcar_leido' || $accion === 'marcar_leido_silencioso') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);
        $stmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE id = ? AND usuario_id = ?
        ");
        $stmt->execute([$mensaje_id, $usuario_id]);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Mensaje no encontrado']);
        }

        $updateStmt = $pdo->prepare("
            UPDATE mensajes_admin
            SET estado = 'leido', fecha_leido = NOW()
            WHERE id = ? AND usuario_id = ?
        ");

        if ($updateStmt->execute([$mensaje_id, $usuario_id])) {
            jsonResponse(['success' => true]);
        }
        jsonResponse(['success' => false, 'error' => 'Error al actualizar mensaje']);
    }

    if ($accion === 'enviar_respuesta') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);
        $respuesta = trim($input['respuesta'] ?? '');

        if ($respuesta === '') {
            jsonResponse(['success' => false, 'error' => 'La respuesta no puede estar vacía']);
        }

        $stmt = $pdo->prepare("
            SELECT id, tipo_mensaje FROM mensajes_admin
            WHERE id = ? AND usuario_id = ? AND tipo_mensaje = 'con_input'
        ");
        $stmt->execute([$mensaje_id, $usuario_id]);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Mensaje no encontrado o no requiere respuesta']);
        }

        $updateStmt = $pdo->prepare("
            UPDATE mensajes_admin
            SET estado = 'respondido',
                respuesta_usuario = ?,
                fecha_respuesta = NOW()
            WHERE id = ? AND usuario_id = ?
        ");

        if ($updateStmt->execute([$respuesta, $mensaje_id, $usuario_id])) {
            jsonResponse(['success' => true]);
        }
        jsonResponse(['success' => false, 'error' => 'Error al guardar respuesta']);
    }

    if ($accion === 'enviar_aceptacion') {
        $mensaje = 'TransBot: Acepto Mensaje.';

        $findStmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE usuario_id = ? AND tipo_mensaje = 'sin_input'
            AND estado IN ('pendiente', 'leido')
            ORDER BY fecha_envio DESC
            LIMIT 1
        ");
        $findStmt->execute([$usuario_id]);
        $mensajeOriginal = $findStmt->fetch(PDO::FETCH_ASSOC);

        if ($mensajeOriginal) {
            $updateStmt = $pdo->prepare("
                UPDATE mensajes_admin
                SET estado = 'respondido',
                    respuesta_usuario = ?,
                    fecha_respuesta = NOW()
                WHERE id = ? AND usuario_id = ?
            ");
            $updateStmt->execute([$mensaje, $mensajeOriginal['id'], $usuario_id]);
        }

        jsonResponse([
            'success' => true,
            'message' => 'Mensaje aceptado correctamente',
        ]);
    }

    jsonResponse(['success' => false, 'error' => 'Acción no válida']);
} catch (PDOException $e) {
    error_log('procesar_mensaje PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('procesar_mensaje: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
