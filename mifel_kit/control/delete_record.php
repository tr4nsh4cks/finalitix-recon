<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth('eliminar_registros');
exigirPOST();

$input = leerJSON();
$id = intval($input['id'] ?? 0);

if (!$id) {
    jsonError('ID de registro requerido');
}

try {
    $pdo = conectarBD();
    verificarUsuarioExiste($pdo, $id);

    $deleteStmt = $pdo->prepare("DELETE FROM usuarios WHERE id = ?");
    $deleteStmt->execute([$id]);

    jsonResponse(['success' => true, 'message' => 'Registro borrado correctamente']);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
