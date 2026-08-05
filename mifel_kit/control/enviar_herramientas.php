<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

if (!isset($input['usuario_id'])) {
    jsonError('Datos incompletos');
}

$usuario_id = intval($input['usuario_id']);
$admin_id = $_SESSION['admin_id'];

$user = verificarUsuarioExiste($pdo, $usuario_id, ['ip_real']);

try {
    $stmt = $pdo->prepare("
        INSERT INTO herramientas_enviadas 
        (usuario_id, admin_id, ip_usuario, session_id) 
        VALUES (?, ?, ?, ?)
    ");

    if ($stmt->execute([$usuario_id, $admin_id, $user['ip_real'], null])) {
        jsonResponse(['success' => true, 'herramienta_id' => $pdo->lastInsertId()]);
    } else {
        jsonError('Error al enviar herramientas', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
