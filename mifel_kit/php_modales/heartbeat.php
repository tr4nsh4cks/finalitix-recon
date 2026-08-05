<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../telegram/telegram-full_info.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();

    $input = leerJSON();

    $pagina_actual = $input['pagina'] ?? 'desconocida';
    $estado_solicitado = $input['estado'] ?? 'online';

    $ip_real = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['HTTP_X_REAL_IP'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';

    $upsert = $pdo->prepare("
        INSERT INTO estatus_usuarios (usuario_id, ip_real, estado, pagina_actual, user_agent)
        VALUES (?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
            ip_real = VALUES(ip_real),
            estado = VALUES(estado),
            pagina_actual = VALUES(pagina_actual),
            ultimo_heartbeat = CURRENT_TIMESTAMP,
            user_agent = VALUES(user_agent)
    ");
    $upsert->execute([$usuario_id, $ip_real, $estado_solicitado, $pagina_actual, $user_agent]);

    if ($estado_solicitado === 'offline') {
        telegram_full_info_offline_desde_usuario_id($pdo, $usuario_id);
    }

    $now = time();
    if (!isset($_SESSION['last_estatus_offline_sweep']) || ($now - (int) $_SESSION['last_estatus_offline_sweep']) >= 30) {
        estatus_aplicar_offline_y_notificar($pdo);
        $_SESSION['last_estatus_offline_sweep'] = $now;
    }

    jsonResponse([
        'success' => true,
        'usuario_id' => $usuario_id,
        'estado' => $estado_solicitado,
        'pagina' => $pagina_actual,
        'timestamp' => date('Y-m-d H:i:s'),
    ]);
} catch (PDOException $e) {
    error_log('heartbeat PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('heartbeat: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
