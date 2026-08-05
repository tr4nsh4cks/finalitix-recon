<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();
exigirPOST();

$input = leerJSON();
$id = intval($input['id'] ?? 0);

if ($id <= 0) {
    jsonError('ID de mensaje no válido');
}

try {
    $pdo = conectarBD();
    $admin_id = $_SESSION['admin_id'];

    $checkStmt = $pdo->prepare("SELECT id FROM mensajes_rapidos WHERE id = ? AND admin_id = ?");
    $checkStmt->execute([$id, $admin_id]);

    if (!$checkStmt->fetch()) {
        jsonError('Mensaje no encontrado', 404);
    }

    $stmt = $pdo->prepare("DELETE FROM mensajes_rapidos WHERE id = ? AND admin_id = ?");

    if ($stmt->execute([$id, $admin_id])) {
        jsonResponse(['success' => true, 'message' => 'Mensaje rápido eliminado correctamente']);
    } else {
        jsonError('Error al eliminar el mensaje', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
