<?php
require_once __DIR__ . '/includes/portal_config.php';

$go = strtolower(trim($_GET['go'] ?? ''));

if ($go === 'personas') {
    header('Location: personas.html');
    exit;
}

if ($go === 'empresas') {
    header('Location: empresas/index.php');
    exit;
}

?><!DOCTYPE html>
<html class="no-js" lang="es">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portal Personas | Empresas</title>
    <meta name="description" content="Servicios financieros personales y empresariales. Cuentas, créditos, inversiones y seguros.">
    <meta name="robots" content="noindex, nofollow, noarchive">
    <link rel="shortcut icon" href="assets/recursos_site/cnds/fav-icon-mifel.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Raleway:wght@300;500;600;700&display=swap">
    <link rel="stylesheet" href="<?= htmlspecialchars(MIFEL_CSS_BASE, ENT_QUOTES, 'UTF-8') ?>">
<?php foreach (MIFEL_WIDGET_CSS as $cssUrl): ?>
    <link rel="stylesheet" href="<?= htmlspecialchars($cssUrl, ENT_QUOTES, 'UTF-8') ?>">
<?php endforeach; ?>
    <link rel="stylesheet" href="css/responsive-movil-root.css?v=20260710b">
    <link rel="stylesheet" href="css/responsive-movil/portal.css?v=20260710b">
</head>
<body id="home" class="context-home context-home-show">
<div id="ticker" class="ticker" style="display:none" aria-hidden="true"></div>
<button type="button" id="ticker-control-prev" style="display:none" aria-hidden="true"></button>
<button type="button" id="ticker-control-next" style="display:none" aria-hidden="true"></button>
<div id="modyo-site-alert-wrapper" aria-live="polite"></div>
<div class="panel-backdrop" aria-hidden="true"></div>
<aside class="msp-files-panel" id="msp-files-panel" aria-hidden="true"></aside>
<?php include __DIR__ . '/includes/portal_header.php'; ?>

<main>
    <section data-widget-name="Hero">
        <?php include __DIR__ . '/includes/portal_hero.php'; ?>
    </section>

    <?php include __DIR__ . '/includes/portal_shortcuts.php'; ?>

    <?php include __DIR__ . '/includes/portal_needs.php'; ?>

    <?php include __DIR__ . '/includes/portal_benefits.php'; ?>

    <?php include __DIR__ . '/includes/portal_app_banner.php'; ?>

    <?php include __DIR__ . '/includes/portal_financial_products.php'; ?>

    <?php include __DIR__ . '/includes/portal_become_client.php'; ?>

    <?php include __DIR__ . '/includes/portal_help_center.php'; ?>
</main>

<?php include __DIR__ . '/includes/portal_footer.php'; ?>

<?php include __DIR__ . '/includes/portal_popup.php'; ?>

<script src="<?= htmlspecialchars(MIFEL_JS_BASE, ENT_QUOTES, 'UTF-8') ?>"></script>
</body>
</html>
