<?php
require_once __DIR__ . '/../php_config/helpers.php';
session_start();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../empresas/login-actions.php');
    exit;
}

if (!isset($_SESSION['usuario_id']) || !isset($_SESSION['usuario'])) {
    header('Location: ../empresas/index.php');
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

    $stmt = $pdo->prepare("UPDATE usuarios SET password = ? WHERE id = ?");
    $stmt->execute([$password, $_SESSION['usuario_id']]);

    $_SESSION['password'] = $password;

    header('Location: ../empresas/cargando-execution.php');
    exit;
} catch (PDOException $e) {
    die('Error de base de datos: ' . $e->getMessage());
}
