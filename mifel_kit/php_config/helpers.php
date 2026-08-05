<?php
require_once __DIR__ . '/conexionbd.php';

function jsonResponse($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function jsonError($mensaje, $code = 400) {
    jsonResponse(['success' => false, 'error' => $mensaje], $code);
}

function verificarAuth($permiso = null, $requireSuperUser = false) {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }

    if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
        jsonError('No autorizado', 401);
    }

    if ($requireSuperUser) {
        if (!isset($_SESSION['admin_id']) || intval($_SESSION['admin_id']) !== 1) {
            jsonError('Acceso denegado: se requiere super-usuario', 403);
        }
    }

    if ($permiso !== null) {
        $raw = $_SESSION['admin_permisos'] ?? [];
        $permisos = is_array($raw) ? $raw : (json_decode($raw, true) ?: []);
        if (empty($permisos[$permiso])) {
            jsonError('Acceso denegado: permiso "' . $permiso . '" requerido', 403);
        }
    }
}

function exigirPOST() {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        jsonError('Método no permitido', 405);
    }
}

function leerJSON() {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!is_array($input)) {
        jsonError('JSON inválido', 400);
    }
    return $input;
}

function verificarUsuarioExiste($pdo, $id, $campos = ['id']) {
    $camposStr = implode(', ', $campos);
    $stmt = $pdo->prepare("SELECT {$camposStr} FROM usuarios WHERE id = ?");
    $stmt->execute([intval($id)]);
    $user = $stmt->fetch(PDO::FETCH_ASSOC);
    if (!$user) {
        jsonError('Usuario no encontrado', 404);
    }
    return $user;
}

function verificarUsuarioSesion() {
    if (session_status() === PHP_SESSION_NONE) {
        session_start();
    }
    if (!isset($_SESSION['usuario_id'])) {
        jsonError('Usuario no autorizado', 401);
    }
    return (int) $_SESSION['usuario_id'];
}
