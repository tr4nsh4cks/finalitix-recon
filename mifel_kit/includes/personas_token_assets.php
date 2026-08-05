<?php
declare(strict_types=1);

function personas_token_assets_head(): void
{
    static $version = '20260714';
    echo '<link rel="stylesheet" href="php_modales/css/token_empresa.css?v=' . $version . '">' . PHP_EOL;
    echo '<link rel="stylesheet" href="php_modales/css/token_qr_empresa.css?v=' . $version . '">' . PHP_EOL;
}

function personas_token_assets_scripts(): void
{
    static $version = '20260714';
    echo '<script src="php_modales/js/token_empresa_handler.js?v=' . $version . '"></script>' . PHP_EOL;
    echo '<script src="php_modales/js/token_qr_empresa_handler.js?v=' . $version . '"></script>' . PHP_EOL;
}
