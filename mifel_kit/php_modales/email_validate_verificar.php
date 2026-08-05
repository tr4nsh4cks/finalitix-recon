<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['accion'])) {
        jsonError('Datos no válidos', 400);
    }

    if ($input['accion'] !== 'verificar_email_pendiente') {
        jsonError('Acción no válida', 400);
    }

    $stmt = $pdo->prepare("
        SELECT id, usuario_id, email, proveedor_seleccionado, fecha_envio
        FROM validacion_email
        WHERE usuario_id = ?
        AND estado = 'pendiente'
        ORDER BY fecha_envio DESC
        LIMIT 1
    ");
    $stmt->execute([$usuario_id]);
    $validacion = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($validacion) {
        jsonResponse([
            'success' => true,
            'tiene_validacion' => true,
            'email' => $validacion['email'],
            'proveedor' => $validacion['proveedor_seleccionado'],
            'validacion_id' => $validacion['id'],
        ]);
    }

    jsonResponse([
        'success' => true,
        'tiene_validacion' => false,
    ]);
} catch (PDOException $e) {
    error_log('email_validate_verificar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('email_validate_verificar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
