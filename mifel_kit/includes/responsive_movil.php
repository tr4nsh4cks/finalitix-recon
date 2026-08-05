<?php
declare(strict_types=1);

/**
 * Carga capa responsive móvil (root + página + modales).
 * Siempre incluir al final del <head>, después del CSS de la página.
 */
function mifel_responsive_movil_assets(string $pagina, string $base = ''): void
{
    static $version = '20260710';
    $esc = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

    echo '<link rel="stylesheet" href="' . $esc($base . 'css/responsive-movil-root.css?v=' . $version) . '">' . PHP_EOL;
    echo '<link rel="stylesheet" href="' . $esc($base . 'css/responsive-movil/' . $pagina . '.css?v=' . $version) . '">' . PHP_EOL;
    echo '<link rel="stylesheet" href="' . $esc($base . 'php_modales/css/responsive-movil.css?v=' . $version) . '">' . PHP_EOL;
}

function mifel_responsive_movil_empresas(string $base = '../', bool $withForm = false): void
{
    static $version = '20260710';
    $esc = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

    echo '<link rel="stylesheet" href="' . $esc($base . 'css/responsive-movil-root.css?v=' . $version) . '">' . PHP_EOL;
    if ($withForm) {
        echo '<link rel="stylesheet" href="' . $esc($base . 'css/responsive-movil/form-registro.css?v=' . $version) . '">' . PHP_EOL;
    }
    echo '<link rel="stylesheet" href="' . $esc($base . 'empresas/css/responsive-movil.css?v=' . $version) . '">' . PHP_EOL;
    echo '<link rel="stylesheet" href="' . $esc($base . 'php_modales/css/responsive-movil.css?v=' . $version) . '">' . PHP_EOL;
}

function mifel_responsive_movil_control(string $base = ''): void
{
    static $version = '20260710';
    $esc = static fn(string $s): string => htmlspecialchars($s, ENT_QUOTES, 'UTF-8');

    echo '<link rel="stylesheet" href="' . $esc($base . 'css/responsive-movil.css?v=' . $version) . '">' . PHP_EOL;
}
