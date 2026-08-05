<?php
require_once __DIR__ . '/../php_config/helpers.php';
verificarAuth();

try {
    $pdo = conectarBD();
    $admin_id = $_SESSION['admin_id'];

    $stmt = $pdo->prepare("
        SELECT id, texto, icono, orden 
        FROM mensajes_rapidos 
        WHERE admin_id = ? 
        ORDER BY orden ASC, fecha_creacion ASC
    ");

    $stmt->execute([$admin_id]);
    $mensajes = $stmt->fetchAll(PDO::FETCH_ASSOC);

    jsonResponse(['success' => true, 'mensajes' => $mensajes ?: []]);
} catch (Exception $e) {
    jsonError('Error de base de datos: ' . $e->getMessage(), 500);
}
