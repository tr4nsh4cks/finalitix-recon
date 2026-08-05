<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

$data = leerJSON();

if (!isset($data['usuario_id']) || !isset($data['comentario'])) {
    jsonError('Faltan datos requeridos');
}

$usuario_id = intval($data['usuario_id']);
$comentario = trim($data['comentario']);

if ($usuario_id <= 0) {
    jsonError('ID de usuario inválido');
}

if (strlen($comentario) > 1000) {
    jsonError('El comentario no puede exceder los 1000 caracteres');
}

try {
    $pdo = conectarBD();

    $stmt = $pdo->prepare("UPDATE usuarios SET comentarios = ? WHERE id = ?");
    $stmt->execute([$comentario, $usuario_id]);

    if ($stmt->rowCount() > 0) {
        jsonResponse(['success' => true, 'message' => 'Comentario actualizado correctamente']);
    }

    $chk = $pdo->prepare("SELECT id FROM usuarios WHERE id = ? LIMIT 1");
    $chk->execute([$usuario_id]);
    if ($chk->fetch()) {
        jsonResponse([
            'success' => true,
            'unchanged' => true,
            'message' => 'Sin cambios en el comentario',
        ]);
    }

    jsonError('Usuario no encontrado', 404);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
