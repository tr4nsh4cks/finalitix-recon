<?php
function portal_nav_icon(string $name, int $size = 24): void
{
    $file = __DIR__ . '/icons/' . $name . '.php';
    if (!is_file($file)) {
        return;
    }
    include $file;
}
