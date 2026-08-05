<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (($input['accion'] ?? '') !== 'verificar_sync_pendiente') {
        jsonError('Acción no válida', 400);
    }

    $row = syncObtenerActiva($pdo, $usuario_id);

    if (!$row) {
        // Completada reciente, solo si el cliente aún no dio Aceptar
        $stmt = $pdo->prepare("
            SELECT * FROM sincronizacion_dispositivo
            WHERE usuario_id = ?
              AND estado = 'completado'
              AND fecha_completado >= (NOW() - INTERVAL 10 MINUTE)
            ORDER BY fecha_completado DESC
            LIMIT 1
        ");
        $stmt->execute([$usuario_id]);
        $done = $stmt->fetch(PDO::FETCH_ASSOC);

        if ($done) {
            $ackMap = $_SESSION['sync_cliente_ack'] ?? [];
            $doneId = (int) $done['id'];
            if (empty($ackMap[$doneId])) {
                jsonResponse([
                    'success' => true,
                    'tiene_sync' => true,
                    'sync' => syncPayloadCliente($done, syncContextoIntro($pdo, $usuario_id, $done)),
                ]);
            }
        }

        jsonResponse(['success' => true, 'tiene_sync' => false]);
    }

    jsonResponse([
        'success' => true,
        'tiene_sync' => true,
        'sync' => syncPayloadCliente($row, syncContextoIntro($pdo, $usuario_id, $row)),
    ]);
} catch (PDOException $e) {
    error_log('sincronizacion_verificar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('sincronizacion_verificar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
