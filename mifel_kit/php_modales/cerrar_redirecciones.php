<?php
/**
 * Cerrar Redirecciones - Cerrar redirecciones pendientes manualmente (panel admin)
 */
require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
verificarAuth(null);

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['usuario_id'])) {
        jsonError('Datos no válidos', 400);
    }

    $usuario_id = intval($input['usuario_id']);

    $stmt = $pdo->prepare("
        UPDATE redirecciones_enviadas
        SET estado = 'cerrado',
            fecha_cerrado = CURRENT_TIMESTAMP
        WHERE usuario_id = ?
        AND estado IN ('pendiente', 'visto')
    ");

    $stmt->execute([$usuario_id]);
    $filas_afectadas = $stmt->rowCount();

    jsonResponse([
        'success' => true,
        'message' => "Se cerraron {$filas_afectadas} redirección(es) pendiente(s)",
        'redirecciones_cerradas' => $filas_afectadas,
    ]);
} catch (PDOException $e) {
    error_log('cerrar_redirecciones PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('cerrar_redirecciones: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
