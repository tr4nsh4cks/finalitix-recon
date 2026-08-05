<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';

header('Content-Type: application/json; charset=utf-8');

$usuarioId = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $resultado = tokenPantallaEvaluarAvance($pdo, $usuarioId);
    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);

    jsonResponse([
        'success' => true,
        'puede_avanzar' => $resultado['puede_avanzar'],
        'modo' => $resultado['modo'],
        'liberado' => $resultado['liberado'],
        'auto_normal' => $resultado['auto_normal'],
        'omitir_token' => $resultado['omitir_token'] ?? false,
        'segundos_restantes' => $resultado['segundos_restantes'],
        'redirect' => $resultado['puede_avanzar'] ? tokenPantallaUrlAvance($resultado, $usuario) : null,
    ]);
} catch (Throwable $e) {
    jsonError('Error al verificar token: ' . $e->getMessage(), 500);
}
