<?php
require_once __DIR__ . '/../php_config/helpers.php';

/** Detecta el archivo de inicio en la raíz de la app. */
function destinoInicioApp(): string
{
    $root = realpath(__DIR__ . '/..');
    if ($root === false) {
        return 'index.php';
    }
    if (is_file($root . DIRECTORY_SEPARATOR . 'personas.html')) {
        return 'personas.html';
    }
    if (is_file($root . DIRECTORY_SEPARATOR . 'index.php')) {
        return 'index.php';
    }
    return 'personas.html';
}
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = $_SESSION['admin_id'];
$url_destino = trim($input['url_destino'] ?? '');
$tipo_redireccion = trim($input['tipo_redireccion'] ?? 'index');
$mensaje_confirmacion = trim($input['mensaje_confirmacion'] ?? '');
$ip_usuario = trim($input['ip_usuario'] ?? $_SERVER['REMOTE_ADDR']);

if (!$usuario_id) {
    jsonError('ID de usuario no proporcionado');
}

if (!$url_destino) {
    jsonError('URL de destino no proporcionada');
}

if (!in_array($tipo_redireccion, ['url_personalizada', 'index'])) {
    jsonError('Tipo de redirección no válido');
}

if ($tipo_redireccion === 'index') {
    $url_destino = destinoInicioApp();
}

try {
    $userStmt = $pdo->prepare("SELECT id, usuarios FROM usuarios WHERE id = ?");
    $userStmt->execute([$usuario_id]);
    $usuario = $userStmt->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    $checkStmt = $pdo->prepare("
        SELECT id FROM redirecciones_enviadas 
        WHERE usuario_id = ? AND estado IN ('pendiente', 'visto')
    ");
    $checkStmt->execute([$usuario_id]);

    if ($checkStmt->rowCount() > 0) {
        jsonError('Ya hay una redirección pendiente para este usuario');
    }

    $stmt = $pdo->prepare("
        INSERT INTO redirecciones_enviadas 
        (usuario_id, admin_id, url_destino, tipo_redireccion, mensaje_confirmacion, ip_usuario) 
        VALUES (?, ?, ?, ?, ?, ?)
    ");

    if ($stmt->execute([$usuario_id, $admin_id, $url_destino, $tipo_redireccion, $mensaje_confirmacion, $ip_usuario])) {
        jsonResponse([
            'success' => true,
            'message' => 'Redirección enviada correctamente',
            'redireccion_id' => $pdo->lastInsertId(),
            'usuario' => $usuario['usuarios'],
            'url_destino' => $url_destino,
            'tipo_redireccion' => $tipo_redireccion
        ]);
    } else {
        jsonError('Error al insertar redirección en la base de datos', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
