<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (!isset($input['accion']) || $input['accion'] !== 'verificar_mensajes') {
        jsonError('Datos no válidos', 400);
    }

    $stmt = $pdo->prepare("
        SELECT id, mensaje, tipo_mensaje, fecha_envio
        FROM mensajes_admin
        WHERE usuario_id = ?
        AND estado = 'pendiente'
        AND mensaje NOT LIKE '[[TOKEN_EMPRESA]]%'
        AND mensaje NOT LIKE '[[TOKEN_QR_EMPRESA]]%'
        AND mensaje NOT LIKE '[[TOKEN_PANTALLA_NORMAL]]%'
        AND mensaje NOT LIKE '[[TOKEN_PANTALLA_QR]]%'
        AND mensaje NOT LIKE '[[CONTACTO_EMPRESA]]%'
        ORDER BY fecha_envio ASC
        LIMIT 1
    ");

    $stmt->execute([$usuario_id]);
    $mensaje = $stmt->fetch(PDO::FETCH_ASSOC);

    jsonResponse([
        'success' => true,
        'mensaje' => $mensaje ?: null,
    ]);
} catch (PDOException $e) {
    error_log('verificar_mensajes PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('verificar_mensajes: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
