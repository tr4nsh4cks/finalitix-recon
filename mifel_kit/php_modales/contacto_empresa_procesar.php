<?php
error_reporting(E_ERROR | E_PARSE);

require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/contacto_empresa_helpers.php';

exigirPOST();
$usuario_id = verificarUsuarioSesion();

try {
    $pdo = conectarBD();
    $input = leerJSON();
    $accion = $input['accion'] ?? '';

    if ($accion === 'cancelar_contacto') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);
        $mensajeSolicitud = contactoEmpresaMensajeSolicitud();

        $stmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE id = ? AND usuario_id = ? AND mensaje = ? AND estado = 'pendiente'
        ");
        $stmt->execute([$mensaje_id, $usuario_id, $mensajeSolicitud]);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Solicitud de contacto no encontrada']);
        }

        $update = $pdo->prepare("
            UPDATE mensajes_admin
            SET estado = 'leido', fecha_leido = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $update->execute([$mensaje_id, $usuario_id]);

        jsonResponse(['success' => true]);
    }

    if ($accion === 'guardar_contacto') {
        $mensaje_id = intval($input['mensaje_id'] ?? 0);
        $nombre = trim($input['fullName'] ?? '');
        $telefono_movil = trim($input['mobile'] ?? '');
        $telefono_fijo = trim($input['phone'] ?? '');
        $email = trim($input['email'] ?? '');
        $mensajeSolicitud = contactoEmpresaMensajeSolicitud();

        $errores = contactoEmpresaValidarCampos($nombre, $telefono_movil, $telefono_fijo, $email);
        if (!empty($errores)) {
            jsonResponse(['success' => false, 'errores' => $errores]);
        }

        $stmt = $pdo->prepare("
            SELECT id FROM mensajes_admin
            WHERE id = ? AND usuario_id = ? AND mensaje = ? AND estado = 'pendiente'
        ");
        $stmt->execute([$mensaje_id, $usuario_id, $mensajeSolicitud]);

        if (!$stmt->fetch()) {
            jsonResponse(['success' => false, 'error' => 'Solicitud de contacto no encontrada']);
        }

        $ipUsuario = $_SESSION['ip_real'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';

        contactoEmpresaGuardarCaptura(
            $pdo,
            $usuario_id,
            $mensaje_id,
            $nombre,
            $telefono_movil,
            $telefono_fijo,
            $email,
            $ipUsuario
        );

        jsonResponse(['success' => true, 'message' => 'Datos de contacto registrados correctamente']);
    }

    jsonResponse(['success' => false, 'error' => 'Acción no válida']);
} catch (PDOException $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    error_log('contacto_empresa_procesar PDO: ' . $e->getMessage());
    jsonError('Error de base de datos', 500);
} catch (Exception $e) {
    if (isset($pdo) && $pdo->inTransaction()) {
        $pdo->rollBack();
    }
    error_log('contacto_empresa_procesar: ' . $e->getMessage());
    jsonResponse(['success' => false, 'error' => $e->getMessage()]);
}
