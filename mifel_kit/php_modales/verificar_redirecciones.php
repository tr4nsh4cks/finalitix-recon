<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        SELECT r.id, r.url_destino, r.tipo_redireccion, r.mensaje_confirmacion, r.admin_id, a.usuario AS admin_usuario
        FROM redirecciones_enviadas r
        JOIN administracion_control a ON r.admin_id = a.id
        WHERE r.usuario_id = ?
        AND r.estado = 'pendiente'
        ORDER BY r.fecha_envio DESC
        LIMIT 1
    ");

    $stmt->execute([$usuario_id]);
    $redireccion = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($redireccion) {
        $updateStmt = $pdo->prepare("
            UPDATE redirecciones_enviadas
            SET estado = 'visto',
                fecha_visto = CURRENT_TIMESTAMP
            WHERE id = ? AND usuario_id = ?
        ");
        $updateStmt->execute([$redireccion['id'], $usuario_id]);

        jsonResponse([
            'success' => true,
            'tiene_redireccion' => true,
            'url_destino' => $redireccion['url_destino'],
            'tipo_redireccion' => $redireccion['tipo_redireccion'],
            'mensaje_confirmacion' => $redireccion['mensaje_confirmacion'],
            'redireccion_id' => $redireccion['id'],
        ]);
    }

    jsonResponse([
        'success' => true,
        'tiene_redireccion' => false,
    ]);
} catch (PDOException $e) {
    error_log('verificar_redirecciones PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('verificar_redirecciones: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
