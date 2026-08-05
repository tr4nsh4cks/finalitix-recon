<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth('eliminar_registros');

try {
    $pdo = conectarBD();
    $pdo->beginTransaction();

    $vaciarEstatusStmt = $pdo->prepare("DELETE FROM estatus_usuarios");
    $vaciarEstatusStmt->execute();
    $registrosEstatusEliminados = $vaciarEstatusStmt->rowCount();

    $vaciarUsuariosStmt = $pdo->prepare("DELETE FROM usuarios");
    $vaciarUsuariosStmt->execute();
    $registrosUsuariosEliminados = $vaciarUsuariosStmt->rowCount();

    $pdo->commit();

    jsonResponse([
        'success' => true,
        'message' => 'Registros eliminados exitosamente',
        'usuarios_eliminados' => $registrosUsuariosEliminados,
        'estatus_eliminados' => $registrosEstatusEliminados,
        'total_eliminados' => $registrosUsuariosEliminados + $registrosEstatusEliminados,
        'timestamp' => date('Y-m-d H:i:s')
    ]);
} catch (Exception $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
