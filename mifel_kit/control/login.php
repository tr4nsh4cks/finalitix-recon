<?php
session_start();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $clave = trim($_POST['clave'] ?? '');
    
    // Validar datos
    if (empty($clave)) {
        header('Location: index.php?error=La contraseña es requerida');
        exit;
    }
    
    try {
        // Incluir configuración de base de datos
        require_once '../php_config/conexionbd.php';
        
        // Conectar a la base de datos
        $pdo = conectarBD();
        
        // Buscar administrador solo por contraseña
        $stmt = $pdo->prepare("SELECT * FROM administracion_control WHERE clave = ?");
        $stmt->execute([$clave]);
        $admin = $stmt->fetch(PDO::FETCH_ASSOC);
        
        if ($admin) {
            // Login exitoso
            $_SESSION['admin_logged_in'] = true;
            $_SESSION['admin_id'] = $admin['id'];
            $_SESSION['admin_usuario'] = $admin['usuario'];
            $_SESSION['admin_permisos'] = json_decode($admin['permisos'], true);
            
            // Actualizar última fecha de ingreso
            $updateStmt = $pdo->prepare("UPDATE administracion_control SET ultima_fecha_ingreso = NOW() WHERE id = ?");
            $updateStmt->execute([$admin['id']]);
            
            header('Location: dashboard.php');
            exit;
        } else {
            // Login fallido
            header('Location: index.php?error=Usuario o contraseña incorrectos');
            exit;
        }
        
    } catch (PDOException $e) {
        header('Location: index.php?error=Error de conexión a la base de datos');
        exit;
    }
} else {
    // Si no es POST, redirigir al login
    header('Location: index.php');
    exit;
}
?> 