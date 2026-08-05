<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['herramienta_id'])) {
        jsonResponse(['success' => false, 'error' => 'ID de herramienta no proporcionado']);
    }

    $stmt = $pdo->prepare("
        UPDATE herramientas_enviadas
        SET estado = 'cerrado',
            fecha_cerrado = CURRENT_TIMESTAMP
        WHERE id = ?
        AND usuario_id = ?
    ");

    $stmt->execute([$input['herramienta_id'], $usuario_id]);

    jsonResponse([
        'success' => true,
        'message' => 'Herramienta cerrada correctamente',
    ]);
} catch (PDOException $e) {
    error_log('cerrar_herramientas PDO: ' . $e->getMessage());
    jsonError('Error al cerrar herramienta', 500);
}
