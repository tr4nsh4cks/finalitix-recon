<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';

define('TOKEN_QR_EMPRESA_PREFIX', '[[TOKEN_QR_EMPRESA]]');

function parseTokenQrPayload(string $mensaje): ?array
{
    if (strpos($mensaje, TOKEN_QR_EMPRESA_PREFIX) !== 0) {
        return null;
    }

    $json = substr($mensaje, strlen(TOKEN_QR_EMPRESA_PREFIX));
    $data = json_decode($json, true);

    if (!is_array($data) || empty($data['imagen'])) {
        return null;
    }

    return $data;
}

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (($input['accion'] ?? '') !== 'verificar_token_qr_pendiente') {
        jsonError('Acción no válida', 400);
    }

    $stmtUser = $pdo->prepare('SELECT apellido FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario || !tokenPantallaUsaControl($usuario)) {
        jsonResponse(['success' => true, 'tiene_token_qr' => false]);
    }

    $ganadorId = consolidarTelasModalesPendientes($pdo, $usuario_id);
    if (!$ganadorId) {
        jsonResponse(['success' => true, 'tiene_token_qr' => false]);
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
    $stmt->execute([$ganadorId, $usuario_id, TOKEN_QR_EMPRESA_PREFIX . '%']);
    $pendiente = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($pendiente) {
        $payload = parseTokenQrPayload($pendiente['mensaje']);

        if (!$payload) {
            jsonResponse(['success' => true, 'tiene_token_qr' => false]);
        }

        jsonResponse([
            'success' => true,
            'tiene_token_qr' => true,
            'mensaje_id' => (int) $pendiente['id'],
            'imagen_url' => $payload['imagen'],
        ]);
    }

    jsonResponse(['success' => true, 'tiene_token_qr' => false]);
} catch (PDOException $e) {
    error_log('token_qr_empresa_verificar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('token_qr_empresa_verificar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
