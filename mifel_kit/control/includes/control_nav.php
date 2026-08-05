<?php

if (!isset($nav_section)) {
    $nav_section = '';
}
$is_super = isset($_SESSION['admin_id']) && (int) $_SESSION['admin_id'] === 1;
$usuario_display = isset($_SESSION['admin_usuario']) ? htmlspecialchars($_SESSION['admin_usuario'], ENT_QUOTES, 'UTF-8') : '';

$nav_base = 'control-nav-pill inline-flex items-center justify-center min-h-[2.5rem] px-3 sm:px-4 py-2 rounded-lg transition-colors text-sm nick-font whitespace-nowrap';
$nav_idle = $nav_base . ' control-nav-pill--idle bg-black text-white hover:bg-gray-800';
$nav_active = $nav_base . ' control-nav-pill--active bg-black text-white ring-0 shadow-sm cursor-default';
$nav_disabled = $nav_base . ' control-nav-pill--disabled bg-gray-200 text-gray-600 cursor-not-allowed opacity-90';
?>
<div class="control-nav flex flex-wrap items-center justify-end gap-2 sm:gap-3">
    <button type="button" class="bg-black text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm flex items-center max-w-[12rem]">
        <?php if ($is_super): ?>
            <i class="fas fa-crown control-nav-crown mr-1 flex-shrink-0" aria-hidden="true"></i>
        <?php else: ?>
            <svg class="inline-block w-5 h-5 mr-1 flex-shrink-0" viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="12" fill="white"/>
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" fill="black"/>
            </svg>
        <?php endif; ?>
        <span class="nick-font text-white truncate"><?php echo $usuario_display; ?></span>
    </button>

    <?php if ($nav_section === 'dashboard'): ?>
        <span class="<?php echo $nav_active; ?>" aria-current="page">Dashboard</span>
    <?php else: ?>
        <a href="dashboard.php" class="<?php echo $nav_idle; ?>">Dashboard</a>
    <?php endif; ?>

    <?php if (!$is_super): ?>
        <span class="<?php echo $nav_disabled; ?>" title="Solo el super-usuario puede gestionar administradores">Usuarios</span>
    <?php elseif ($nav_section === 'usuarios'): ?>
        <span class="<?php echo $nav_active; ?>" aria-current="page">Usuarios</span>
    <?php else: ?>
        <a href="user_bx.php" class="<?php echo $nav_idle; ?>">Usuarios</a>
    <?php endif; ?>

    <?php if ($nav_section === 'mensajes'): ?>
        <span class="<?php echo $nav_active; ?>" aria-current="page">Mensajes</span>
    <?php else: ?>
        <a href="mensaje_rapido.php" class="<?php echo $nav_idle; ?>">Mensajes</a>
    <?php endif; ?>

    <?php if ($is_super): ?>
        <?php if ($nav_section === 'dashboard'): ?>
            <button type="button" onclick="showColumnConfig()" class="<?php echo $nav_idle; ?>" title="Configurar columnas de la tabla">Columnas</button>
        <?php else: ?>
            <a href="dashboard.php?openColumnConfig=1" class="<?php echo $nav_idle; ?>" title="Abrir en el dashboard">Columnas</a>
        <?php endif; ?>
    <?php endif; ?>

    <button type="button" class="theme-toggle-btn text-white px-3 py-2 rounded-lg text-sm flex-shrink-0" title="Cambiar tema">
        <i class="fas fa-moon" aria-hidden="true"></i>
    </button>

    <button type="button" onclick="logout()" class="control-nav-logout bg-black text-white px-3 sm:px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors text-sm nick-font flex-shrink-0">Salir</button>
</div>
