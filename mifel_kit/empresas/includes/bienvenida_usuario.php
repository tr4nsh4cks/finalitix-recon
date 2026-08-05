<?php
$usuarioIngresado = htmlspecialchars((string) ($_SESSION['usuario'] ?? ''), ENT_QUOTES, 'UTF-8');
?>
<div class="language-dropdown">
    <span class="language-text">Bienvenido, <?= $usuarioIngresado ?></span>
    <img src="../images/fecha_down_bandera.svg" alt="" class="dropdown-arrow">
</div>
