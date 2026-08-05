<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

$pdo = conectarBD();
$input = leerJSON();

$accion = $input['accion'] ?? '';
$usuario_id = intval($input['usuario_id'] ?? 0);
$admin_id = intval($_SESSION['admin_id']);
$admin_usuario = $_SESSION['admin_usuario'];
$is_admin = (intval($_SESSION['admin_id']) === 1) ? 1 : 0;

if (!$usuario_id) {
    jsonError('ID de usuario requerido');
}

try {
    switch ($accion) {
        case 'registrar_entrada':
            $stmt = $pdo->prepare("
                INSERT INTO monitoreo_bxcontrol 
                (admin_id, usuario_id, admin_usuario, is_admin, fecha_ingreso, ultimo_heartbeat, estado) 
                VALUES (?, ?, ?, ?, NOW(), NOW(), 'activo')
                ON DUPLICATE KEY UPDATE 
                ultimo_heartbeat = NOW(), 
                estado = 'activo',
                admin_usuario = VALUES(admin_usuario),
                is_admin = VALUES(is_admin)
            ");
            $stmt->execute([$admin_id, $usuario_id, $admin_usuario, $is_admin]);
            jsonResponse(['success' => true, 'message' => 'Entrada registrada']);
            break;

        case 'heartbeat':
            $stmt = $pdo->prepare("
                UPDATE monitoreo_bxcontrol 
                SET ultimo_heartbeat = NOW(), estado = 'activo' 
                WHERE admin_id = ? AND usuario_id = ?
            ");
            $stmt->execute([$admin_id, $usuario_id]);
            jsonResponse(['success' => true, 'message' => 'Heartbeat actualizado']);
            break;

        case 'obtener_monitores':
            $stmt = $pdo->prepare("
                SELECT admin_id, admin_usuario, is_admin, fecha_ingreso, ultimo_heartbeat, estado,
                       TIMESTAMPDIFF(SECOND, ultimo_heartbeat, NOW()) as segundos_inactivo
                FROM monitoreo_bxcontrol 
                WHERE usuario_id = ? 
                AND ultimo_heartbeat >= DATE_SUB(NOW(), INTERVAL 2 MINUTE)
                AND estado = 'activo'
                ORDER BY is_admin DESC, fecha_ingreso ASC
            ");
            $stmt->execute([$usuario_id]);
            $monitores = $stmt->fetchAll(PDO::FETCH_ASSOC);

            $stmt = $pdo->prepare("
                SELECT DISTINCT admin_usuario, is_admin,
                       MIN(fecha_ingreso) as primera_vista,
                       MAX(ultimo_heartbeat) as ultima_vista,
                       COUNT(*) as total_visitas
                FROM monitoreo_bxcontrol 
                WHERE usuario_id = ?
                GROUP BY admin_id, admin_usuario, is_admin
                ORDER BY is_admin DESC, primera_vista ASC
            ");
            $stmt->execute([$usuario_id]);
            $historial = $stmt->fetchAll(PDO::FETCH_ASSOC);

            jsonResponse([
                'success' => true,
                'monitores_activos' => $monitores,
                'historial' => $historial
            ]);
            break;

        case 'registrar_salida':
            $stmt = $pdo->prepare("
                UPDATE monitoreo_bxcontrol 
                SET estado = 'inactivo', ultimo_heartbeat = NOW() 
                WHERE admin_id = ? AND usuario_id = ?
            ");
            $stmt->execute([$admin_id, $usuario_id]);
            jsonResponse(['success' => true, 'message' => 'Salida registrada']);
            break;

        case 'limpiar_inactivos':
            $stmt = $pdo->prepare("
                UPDATE monitoreo_bxcontrol 
                SET estado = 'inactivo' 
                WHERE ultimo_heartbeat < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
                AND estado = 'activo'
            ");
            $stmt->execute();
            jsonResponse(['success' => true, 'message' => 'Registros limpiados']);
            break;

        default:
            jsonError('Acción no válida');
    }
} catch (Exception $e) {
    error_log("Error en monitoreo_popup.php: " . $e->getMessage());
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
