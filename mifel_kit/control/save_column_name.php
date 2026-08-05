<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();
exigirPOST();

$input = leerJSON();
$columna = $input['columna'] ?? '';
$nombrePersonalizado = $input['nombre_personalizado'] ?? null;

if (empty($columna)) {
    jsonError('Columna no especificada');
}

if ($nombrePersonalizado === '') {
    $nombrePersonalizado = null;
}

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        UPDATE configuracion_columnas 
        SET nombre_personalizado = ? 
        WHERE admin_id = ? AND columna = ?
    ");

    $resultado = $stmt->execute([$nombrePersonalizado, $_SESSION['admin_id'], $columna]);

    if ($resultado && $stmt->rowCount() > 0) {
        jsonResponse([
            'success' => true,
            'message' => 'Nombre de columna actualizado correctamente',
            'columna' => $columna,
            'nombre_personalizado' => $nombrePersonalizado
        ]);
    } else {
        jsonError('Columna no encontrada o sin cambios', 404);
    }
} catch (Exception $e) {
    error_log("Error en save_column_name.php: " . $e->getMessage());
    jsonError('Error de base de datos', 500);
}
