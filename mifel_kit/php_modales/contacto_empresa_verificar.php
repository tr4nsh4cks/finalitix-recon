<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/contacto_empresa_helpers.php';
require_once __DIR__ . '/../php_config/tela_modales_helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();

    if (($input['accion'] ?? '') !== 'verificar_contacto_pendiente') {
        jsonError('Acción no válida', 400);
    }

    $stmtUser = $pdo->prepare('SELECT apellido FROM usuarios WHERE id = ?');
    $stmtUser->execute([$usuario_id]);
    $usuario = $stmtUser->fetch(PDO::FETCH_ASSOC);

    if (!$usuario || strcasecmp(trim($usuario['apellido'] ?? ''), 'Empresa') !== 0) {
        jsonResponse(['success' => true, 'tiene_contacto' => false]);
    }

    $ganadorId = consolidarTelasModalesPendientes($pdo, $usuario_id);
    if (!$ganadorId) {
        jsonResponse(['success' => true, 'tiene_contacto' => false]);
    }

    $mensajeSolicitud = contactoEmpresaMensajeSolicitud();
    $stmt = $pdo->prepare("
        SELECT id, mensaje, fecha_envio
        FROM mensajes_admin
        WHERE id = ?
          AND usuario_id = ?
          AND mensaje = ?
          AND estado = 'pendiente'
        LIMIT 1
    ");
    $stmt->execute([$ganadorId, $usuario_id, $mensajeSolicitud]);
    $pendiente = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($pendiente) {
        jsonResponse([
            'success' => true,
            'tiene_contacto' => true,
            'mensaje_id' => (int) $pendiente['id'],
        ]);
    }

    jsonResponse(['success' => true, 'tiene_contacto' => false]);
} catch (PDOException $e) {
    error_log('contacto_empresa_verificar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('contacto_empresa_verificar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
