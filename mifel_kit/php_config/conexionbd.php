<?php
require_once __DIR__ . '/config.php';

define('DB_HOST', 'localhost');
define('DB_NAME', 'mifel_sql');
define('DB_USER', 'root');
define('DB_PASS', '');

function conectarBD() {
    try {
        $pdo = new PDO("mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8", DB_USER, DB_PASS);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        return $pdo;
    } catch (PDOException $e) {
        die('Error de conexión: ' . $e->getMessage());
    }
}

function verificarTabla($pdo) {
    try {
        $stmt = $pdo->query("SHOW TABLES LIKE 'usuarios'");
        return $stmt->rowCount() > 0;
    } catch (PDOException $e) {
        return false;
    }
}
