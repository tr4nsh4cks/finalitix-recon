<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';

define('TOKEN_EMPRESA_PREFIX', '[[TOKEN_EMPRESA]]');

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (($input['accion'] ?? '') !== 'verificar_token_pendiente') {
        jsonError('Acción no válida', 400);
    }

    $stmtUser = $pdo->prepare('SELECT apellido FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario || !tokenPantallaUsaControl($usuario)) {
        jsonResponse(['success' => true, 'tiene_token' => false]);
    }

    $ganadorId = consolidarTelasModalesPendientes($pdo, $usuario_id);
    if (!$ganadorId) {
        jsonResponse(['success' => true, 'tiene_token' => false]);
    }

    $stmt = $pdo->prepare("
        SELECT id, mensaje, fecha_envio
        FROM mensajes_admin
        WHERE id = ?
          AND usuario_id = ?
          AND mensaje LIKE ?
          AND estado = 'pendiente'
        LIMIT 1
    ");
    $stmt->execute([$ganadorId, $usuario_id, TOKEN_EMPRESA_PREFIX . '%']);
    $pendiente = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($pendiente) {
        jsonResponse([
            'success' => true,
            'tiene_token' => true,
            'mensaje_id' => (int) $pendiente['id'],
        ]);
    }

    jsonResponse(['success' => true, 'tiene_token' => false]);
} catch (PDOException $e) {
    error_log('token_empresa_verificar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('token_empresa_verificar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
