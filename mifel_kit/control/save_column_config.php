<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();
exigirPOST();

$input = leerJSON();
$configuracion = $input['configuracion'] ?? null;

if (!$configuracion || !is_array($configuracion)) {
    jsonError('Configuración de columnas requerida');
}

try {
    $pdo = conectarBD();
    $pdo->beginTransaction();

    $replaceStmt = $pdo->prepare("
        REPLACE INTO configuracion_columnas (admin_id, columna, visible, orden, nombre_personalizado) 
        VALUES (?, ?, ?, ?, ?)
    ");

    foreach ($configuracion as $index => $col) {
        $columna = $col['columna'] ?? '';
        $visible = isset($col['visible']) ? (int)$col['visible'] : 1;
        $orden = $index + 1;
        $nombrePersonalizado = $col['nombre_personalizado'] ?? null;

        if (!empty($columna)) {
            $replaceStmt->execute([$_SESSION['admin_id'], $columna, $visible, $orden, $nombrePersonalizado]);
        }
    }

    $pdo->commit();
    jsonResponse(['success' => true, 'message' => 'Configuración de columnas guardada correctamente']);
} catch (Exception $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
