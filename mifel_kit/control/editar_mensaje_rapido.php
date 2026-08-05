<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();
exigirPOST();

$input = leerJSON();
$id = intval($input['id'] ?? 0);
$texto = trim($input['texto'] ?? '');
$icono = trim($input['icono'] ?? 'fas fa-comment');
$orden = isset($input['orden']) ? intval($input['orden']) : null;

if ($id <= 0) {
    jsonError('ID de mensaje no válido');
}

if (empty($texto)) {
    jsonError('El texto del mensaje es requerido');
}

try {
    $pdo = conectarBD();
    $admin_id = $_SESSION['admin_id'];

    $checkStmt = $pdo->prepare("SELECT id FROM mensajes_rapidos WHERE id = ? AND admin_id = ?");
    $checkStmt->execute([$id, $admin_id]);

    if (!$checkStmt->fetch()) {
        jsonError('Mensaje no encontrado', 404);
    }

    $updateFields = ['texto = ?', 'icono = ?'];
    $updateValues = [$texto, $icono];

    if ($orden !== null) {
        $updateFields[] = 'orden = ?';
        $updateValues[] = $orden;
    }

    $updateValues[] = $id;
    $updateValues[] = $admin_id;

    $stmt = $pdo->prepare("UPDATE mensajes_rapidos SET " . implode(', ', $updateFields) . " WHERE id = ? AND admin_id = ?");

    if ($stmt->execute($updateValues)) {
        jsonResponse([
            'success' => true,
            'message' => 'Mensaje rápido actualizado correctamente',
            'mensaje' => ['id' => $id, 'texto' => $texto, 'icono' => $icono, 'orden' => $orden]
        ]);
    } else {
        jsonError('Error al actualizar el mensaje', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
