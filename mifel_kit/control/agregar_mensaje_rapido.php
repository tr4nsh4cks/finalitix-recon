<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();
exigirPOST();

$input = leerJSON();
$texto = trim($input['texto'] ?? '');
$icono = trim($input['icono'] ?? 'fas fa-comment');

if (empty($texto)) {
    jsonError('El texto del mensaje es requerido');
}

try {
    $pdo = conectarBD();
    $admin_id = $_SESSION['admin_id'];

    $ordenStmt = $pdo->prepare("
        SELECT COALESCE(MAX(orden), 0) + 1 as siguiente_orden 
        FROM mensajes_rapidos WHERE admin_id = ?
    ");
    $ordenStmt->execute([$admin_id]);
    $orden = $ordenStmt->fetch(PDO::FETCH_ASSOC)['siguiente_orden'];

    $stmt = $pdo->prepare("
        INSERT INTO mensajes_rapidos (admin_id, texto, icono, orden) 
        VALUES (?, ?, ?, ?)
    ");

    if ($stmt->execute([$admin_id, $texto, $icono, $orden])) {
        jsonResponse([
            'success' => true,
            'message' => 'Mensaje rápido agregado correctamente',
            'mensaje' => [
                'id' => $pdo->lastInsertId(),
                'texto' => $texto,
                'icono' => $icono,
                'orden' => $orden
            ]
        ]);
    } else {
        jsonError('Error al agregar el mensaje', 500);
    }
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
