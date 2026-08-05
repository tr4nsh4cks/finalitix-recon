<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$proveedor = $input['proveedor'] ?? 'otro';
$ip_usuario = $input['ip_usuario'] ?? 'unknown';

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

$proveedores_validos = ['gmail', 'outlook', 'yahoo', 'otro'];
if (!in_array($proveedor, $proveedores_validos)) {
    $proveedor = 'otro';
}

try {
    $stmtUser = $pdo->prepare("SELECT email FROM usuarios WHERE id = ?");
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario || empty($usuario['email'])) {
        jsonError('El usuario no tiene email registrado');
    }

    cancelarTelasModalesPendientes($pdo, $usuario_id);

    $stmt = $pdo->prepare("
        INSERT INTO validacion_email 
        (usuario_id, email, proveedor_seleccionado, ip_usuario, estado, fecha_envio) 
        VALUES (?, ?, ?, ?, 'pendiente', NOW())
    ");

    if ($stmt->execute([$usuario_id, $usuario['email'], $proveedor, $ip_usuario])) {
        jsonResponse([
            'success' => true,
            'message' => 'Validación de email enviada correctamente',
            'email' => $usuario['email'],
            'proveedor' => $proveedor
        ]);
    } else {
        jsonError('Error al crear la validación', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
