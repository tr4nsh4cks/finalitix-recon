<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';

verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$usuario_id = intval($input['usuario_id'] ?? 0);
$modo = strtolower(trim($input['modo'] ?? ''));
$imagen_url = trim($input['imagen_url'] ?? '');

if (!$usuario_id) {
    jsonError('ID de usuario no válido');
}

if (!in_array($modo, ['normal', 'qr'], true)) {
    jsonError('Modo de token no válido');
}

if ($modo === 'qr' && ($imagen_url === '' || !validarUrlImagenTokenQr($imagen_url))) {
    jsonError('Ingresa una URL válida de imagen (.png, .jpg, .jpeg, .webp o .gif)');
}

try {
    $usuario = tokenPantallaObtenerUsuario($pdo, $usuario_id);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    if (!tokenPantallaUsaControl($usuario)) {
        jsonError('El control de token solo aplica para usuarios Personas o Empresas');
    }

    if (($usuario['token_pantalla_estado'] ?? '') === 'liberado') {
        jsonError('El token ya fue enviado para este usuario');
    }

    if ($modo === 'qr') {
        $stmt = $pdo->prepare("
            UPDATE usuarios
            SET token_pantalla_estado = 'liberado',
                token_pantalla_modo = 'qr',
                token_qr_imagen_url = ?
            WHERE id = ?
        ");
        $stmt->execute([$imagen_url, $usuario_id]);
    } else {
        $stmt = $pdo->prepare("
            UPDATE usuarios
            SET token_pantalla_estado = 'liberado',
                token_pantalla_modo = 'normal',
                token_qr_imagen_url = NULL
            WHERE id = ?
        ");
        $stmt->execute([$usuario_id]);
    }

    jsonResponse([
        'success' => true,
        'message' => $modo === 'qr' ? 'Token QR enviado' : 'Token normal enviado',
        'modo' => $modo,
    ]);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
