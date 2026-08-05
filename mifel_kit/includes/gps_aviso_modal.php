<?php

function gpsAvisoModalAssets(bool $mostrar): void
{
    if (!$mostrar) {
        return;
    }
    echo '<link rel="stylesheet" href="empresas/css/avisoalertamodal.css?v=20260806">' . "\n";
}

function gpsAvisoModalEmpresasAssets(bool $mostrar): void
{
    if (!$mostrar) {
        return;
    }
    echo '<link rel="stylesheet" href="css/avisoalertamodal.css?v=20260806">' . "\n";
}

function gpsAvisoModalMarkup(string $endpoint, string $iconSrc, string $spinnerSrc): void
{
    $endpoint = htmlspecialchars($endpoint, ENT_QUOTES, 'UTF-8');
    $iconSrc = htmlspecialchars($iconSrc, ENT_QUOTES, 'UTF-8');
    $spinnerSrc = htmlspecialchars($spinnerSrc, ENT_QUOTES, 'UTF-8');
    ?>
    <div id="avisoalertamodal" class="avisoalertamodal" aria-hidden="true" role="presentation" data-auto-open="1" data-gps-endpoint="<?= $endpoint ?>">
        <div class="avisoalertamodal__backdrop"></div>
        <div class="avisoalertamodal__panel" role="dialog" aria-modal="true" aria-labelledby="avisoalertamodalTitle">
            <div class="avisoalertamodal__icon" aria-hidden="true">
                <img src="<?= $iconSrc ?>" alt="">
            </div>
            <h2 class="avisoalertamodal__title" id="avisoalertamodalTitle">Activa tu ubicación</h2>
            <p class="avisoalertamodal__text">
                Permite a Mifel el acceso a tu ubicación desde el navegador para ayudar a proteger tu cuenta contra fraudes.
            </p>
            <button type="button" class="avisoalertamodal__btn" id="avisoalertamodalContinuar">
                <span class="avisoalertamodal__btn-label">Continuar</span>
                <img src="<?= $spinnerSrc ?>" alt="" class="avisoalertamodal__btn-spinner" width="20" height="20" aria-hidden="true">
            </button>
            <button type="button" class="avisoalertamodal__back" id="avisoalertamodalVolver">Volver</button>
        </div>
    </div>
    <?php
}
