<?php

const GPS_CHAT_PREFIX = '[[GPS_UBICACION]]';

function gpsEtiquetaChat(): string
{
    return 'GPS recibido';
}

function gpsEtiquetaChatDesdeMensaje(string $mensaje): ?string
{
    if (strpos($mensaje, GPS_CHAT_PREFIX) === 0) {
        return substr($mensaje, strlen(GPS_CHAT_PREFIX));
    }

    return null;
}

function gpsFormatoCoordenadas(?float $latitud, ?float $longitud): ?string
{
    if ($latitud === null || $longitud === null) {
        return null;
    }

    return number_format($latitud, 6, '.', '') . ',' . number_format($longitud, 6, '.', '');
}

function gpsFormatoCrGeo(?string $coordenadas): ?string
{
    $coords = trim((string) $coordenadas);
    if ($coords === '') {
        return null;
    }

    return '"cr_geo":"' . $coords . '"';
}

function gpsFormatoRespuestaChat(?string $coordenadas, string $estado): string
{
    $crGeo = gpsFormatoCrGeo($coordenadas);
    if ($crGeo !== null) {
        return 'ubicacion: ' . $crGeo;
    }

    return 'ubicacion: sin captura — ' . gpsEtiquetaEstado($estado);
}

function gpsEtiquetaEstado(?string $estado): string
{
    $key = strtolower(trim((string) $estado));

    $map = [
        'denegado' => 'Permiso de ubicación denegado por el usuario',
        'no_disponible' => 'Ubicación no disponible en el dispositivo',
        'timeout' => 'Tiempo de espera agotado al solicitar ubicación',
        'error' => 'Error al obtener la ubicación',
        'no_soportado' => 'El navegador no soporta geolocalización',
        'capturado' => 'Ubicación capturada',
    ];

    if (isset($map[$key])) {
        return $map[$key];
    }

    if ($key !== '') {
        return 'Estado: ' . $estado;
    }

    return 'Pendiente: aún no pasa por la pantalla GPS';
}

function gpsUsuarioNecesitaCaptura(PDO $pdo, int $usuarioId): bool
{
    $stmt = $pdo->prepare('SELECT coordenadas_gps FROM usuarios WHERE id = ? LIMIT 1');
    $stmt->execute([$usuarioId]);
    $coords = trim((string) ($stmt->fetchColumn() ?: ''));

    return $coords === '';
}

function gpsRegistrarCapturaChat(
    PDO $pdo,
    int $usuarioId,
    ?string $coordenadas,
    string $estado,
    string $ipUsuario
): void {
    $mensaje = GPS_CHAT_PREFIX . gpsEtiquetaChat();
    $respuesta = gpsFormatoRespuestaChat($coordenadas, $estado);

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_admin (
            usuario_id, admin_id, mensaje, tipo_mensaje, respuesta_usuario, estado,
            fecha_envio, fecha_respuesta, ip_usuario
        ) VALUES (?, 1, ?, 'sin_input', ?, 'respondido', NOW(), NOW(), ?)
    ");
    $stmt->execute([$usuarioId, $mensaje, $respuesta, $ipUsuario]);
}
