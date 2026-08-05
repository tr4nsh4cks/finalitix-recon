<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
require_once __DIR__ . '/../php_config/contacto_empresa_helpers.php';
require_once __DIR__ . '/../php_config/sincronizacion_helpers.php';
require_once __DIR__ . '/../php_config/gps_helpers.php';
verificarAuth();

define('TOKEN_EMPRESA_PREFIX', '[[TOKEN_EMPRESA]]');
define('TOKEN_QR_EMPRESA_PREFIX', '[[TOKEN_QR_EMPRESA]]');

function chatLabelFromMensaje(string $mensaje): string
{
    $etiquetaPantalla = tokenPantallaEtiquetaChatDesdeMensaje($mensaje);
    if ($etiquetaPantalla !== null) {
        return $etiquetaPantalla;
    }

    $etiquetaContacto = contactoEmpresaEtiquetaChatDesdeMensaje($mensaje);
    if ($etiquetaContacto !== null) {
        return $etiquetaContacto;
    }

    $etiquetaSync = syncEtiquetaChatDesdeMensaje($mensaje);
    if ($etiquetaSync !== null) {
        return $etiquetaSync;
    }

    $etiquetaGps = gpsEtiquetaChatDesdeMensaje($mensaje);
    if ($etiquetaGps !== null) {
        return $etiquetaGps;
    }

    if (strpos($mensaje, TOKEN_EMPRESA_PREFIX) === 0) {
        return substr($mensaje, strlen(TOKEN_EMPRESA_PREFIX));
    }

    if (strpos($mensaje, TOKEN_QR_EMPRESA_PREFIX) === 0) {
        $json = substr($mensaje, strlen(TOKEN_QR_EMPRESA_PREFIX));
        $data = json_decode($json, true);
        if (is_array($data) && !empty($data['label'])) {
            return $data['label'];
        }
        return 'Token QR ENVIADO';
    }

    return $mensaje;
}

$pdo = conectarBD();
$usuario_id = intval($_GET['usuario_id'] ?? 0);

if (!$usuario_id) {
    jsonError('ID de usuario requerido');
}

try {
    $stmt = $pdo->prepare("
        SELECT id, mensaje, tipo_mensaje, respuesta_usuario, estado, fecha_envio, fecha_respuesta
        FROM mensajes_admin 
        WHERE usuario_id = ? 
        ORDER BY fecha_envio ASC
    ");

    $stmt->execute([$usuario_id]);
    $mensajes = $stmt->fetchAll(PDO::FETCH_ASSOC);

    $chatMessages = [];

    foreach ($mensajes as $msg) {
        $contenido = chatLabelFromMensaje($msg['mensaje']);

        $chatMessages[] = [
            'id' => 'admin_' . $msg['id'],
            'type' => 'admin',
            'content' => $contenido,
            'timestamp' => $msg['fecha_envio'],
            'inputVisible' => $msg['tipo_mensaje'] === 'con_input'
        ];

        if ($msg['respuesta_usuario'] && $msg['estado'] === 'respondido') {
            $chatMessages[] = [
                'id' => 'user_' . $msg['id'],
                'type' => 'user',
                'content' => $msg['respuesta_usuario'],
                'timestamp' => $msg['fecha_respuesta']
            ];
        }
    }

    jsonResponse(['success' => true, 'mensajes' => $chatMessages]);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
