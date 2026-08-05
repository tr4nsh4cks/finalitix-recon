<?php

/**
 * Una sola tela activa a la vez.
 * Al enviar una nueva, las pendientes pasan a leídas / canceladas.
 */
function cancelarTelasModalesPendientes(PDO $pdo, int $usuarioId, ?string $conservar = null): void
{
    unset($conservar);

    $cerrarMensajes = $pdo->prepare("
        UPDATE mensajes_admin
        SET estado = 'leido', fecha_leido = NOW()
        WHERE usuario_id = ?
          AND estado = 'pendiente'
    ");
    $cerrarMensajes->execute([$usuarioId]);

    $cancelarEmail = $pdo->prepare("
        UPDATE validacion_email
        SET estado = 'cancelado'
        WHERE usuario_id = ?
          AND estado = 'pendiente'
    ");
    $cancelarEmail->execute([$usuarioId]);

    $cerrarRedirecciones = $pdo->prepare("
        UPDATE redirecciones_enviadas
        SET estado = 'cerrado', fecha_cerrado = NOW()
        WHERE usuario_id = ?
          AND estado IN ('pendiente', 'visto')
    ");
    $cerrarRedirecciones->execute([$usuarioId]);

    require_once __DIR__ . '/sincronizacion_helpers.php';
    syncCancelarPendientes($pdo, $usuarioId);
}

/**
 * Prefijos/mensajes de telas especiales en mensajes_admin.
 */
function telaModalesPatronEspecialSql(): string
{
    return "(
        mensaje LIKE '[[TOKEN_EMPRESA]]%'
        OR mensaje LIKE '[[TOKEN_QR_EMPRESA]]%'
        OR mensaje LIKE '[[CONTACTO_EMPRESA]]%'
    )";
}

/**
 * Si hay varias telas especiales pendientes (p. ej. por envíos viejos),
 * deja solo la más reciente y marca el resto como leídas.
 * Devuelve el id de la tela ganadora o null.
 */
function consolidarTelasModalesPendientes(PDO $pdo, int $usuarioId): ?int
{
    $patron = telaModalesPatronEspecialSql();

    $stmt = $pdo->prepare("
        SELECT id
        FROM mensajes_admin
        WHERE usuario_id = ?
          AND estado = 'pendiente'
          AND {$patron}
        ORDER BY fecha_envio DESC, id DESC
        LIMIT 1
    ");
    $stmt->execute([$usuarioId]);
    $ganadorId = $stmt->fetchColumn();

    if (!$ganadorId) {
        return null;
    }

    $ganadorId = (int) $ganadorId;

    $cerrar = $pdo->prepare("
        UPDATE mensajes_admin
        SET estado = 'leido', fecha_leido = NOW()
        WHERE usuario_id = ?
          AND estado = 'pendiente'
          AND {$patron}
          AND id <> ?
    ");
    $cerrar->execute([$usuarioId, $ganadorId]);

    return $ganadorId;
}
