<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';
verificarAuth();

$usuario_id = intval($_GET['usuario_id'] ?? 0);
if (!$usuario_id) {
    jsonError('ID de usuario requerido');
}

try {
    $pdo = conectarBD();
    $row = syncObtenerActiva($pdo, $usuario_id);

    if (!$row) {
        // última completada reciente para feedback
        $stmt = $pdo->prepare("
            SELECT * FROM sincronizacion_dispositivo
            WHERE usuario_id = ?
            ORDER BY fecha_envio DESC, id DESC
            LIMIT 1
        ");
        $stmt->execute([$usuario_id]);
        $ultima = $stmt->fetch(PDO::FETCH_ASSOC);

        $sync = null;
        if ($ultima) {
            $sync = syncPayloadCliente($ultima);
            $sync['codigo_actual'] = $ultima['codigo_actual'] ?? null;
        }

        jsonResponse([
            'success' => true,
            'activa' => false,
            'sync' => $sync,
        ]);
    }

    $payload = syncPayloadCliente($row);
    $payload['codigo_actual'] = $row['codigo_actual'] ?? null;
    $payload['ultimo_codigo'] = $payload['ultimo_codigo'] ?? null;

    jsonResponse([
        'success' => true,
        'activa' => true,
        'sync' => $payload,
    ]);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
