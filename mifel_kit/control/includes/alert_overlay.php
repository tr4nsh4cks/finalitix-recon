<?php

?>
<div id="alertOverlay" class="alert-overlay alert-hidden" role="dialog" aria-modal="true" aria-labelledby="alertTitle">
    <div id="alertContainer" class="alert-container">
        <div class="alert-header">
            <div id="alertIcon" class="alert-icon">
                <i id="alertIconClass" aria-hidden="true"></i>
            </div>
            <h3 id="alertTitle" class="alert-title">Título</h3>
        </div>
        <div id="alertContent" class="alert-content">Contenido del mensaje</div>
        <div class="alert-buttons">
            <button type="button" id="alertBtnSecondary" class="alert-btn alert-btn-secondary" onclick="hideAlert()">Cancelar</button>
            <button type="button" id="alertBtnPrimary" class="alert-btn alert-btn-primary" onclick="confirmAlert()">Aceptar</button>
        </div>
    </div>
</div>
