<?php

define('CONTROL_FOLDER_NAME', 'control');

function getControlPath() {
    return CONTROL_FOLDER_NAME . '/';
}

function getControlPathRelative() {
    return '../' . CONTROL_FOLDER_NAME . '/';
}

function getControlPathJS() {
    return CONTROL_FOLDER_NAME . '/';
}
