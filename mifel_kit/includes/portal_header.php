<?php
require_once __DIR__ . '/portal_config.php';
require_once __DIR__ . '/portal_nav_icons.php';
require_once __DIR__ . '/portal_nav_data.php';
?>
<header role="banner" id="header">
    <div class="msp-pre-header d-none d-lg-flex w-100">
        <div class="container d-flex justify-content-between msp-pre-header__tabs">
            <ul class="nav nav-tabs pt-2 border-0">
                <li class="nav-item"><a class="msp-sub-p msp-fw-regular active" aria-current="page" href="personas.html">Personas</a></li>
                <li class="nav-item"><a class="msp-sub-p msp-fw-regular" href="empresas/index.php">Empresas</a></li>
            </ul>
            <ul class="d-flex align-items-center m-0 msp-pre-header__help-center p-0 msp-sub-p">
                <li><a href="#" class="msp-close-menu"><span class="icon icon-star" aria-hidden="true">
                    <svg role="img" width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px">
                        <path d="M6.84823 20.4772L12 17.2129L17.1518 20.5135L15.7687 14.3838L20.2982 10.2489L14.3511 9.70489L12 3.9379L9.64886 9.66862L3.70184 10.2127L8.23125 14.3475L6.84823 20.4772ZM12 19.1715L6.12214 22.871C5.96078 22.9678 5.80519 23.0101 5.65537 22.998C5.50554 22.9859 5.36147 22.9315 5.22317 22.8348C5.10792 22.738 5.02148 22.6171 4.96385 22.4721C4.90623 22.327 4.90046 22.1577 4.94657 21.9643L6.46789 14.9641L1.31612 10.2127C1.15477 10.0918 1.0568 9.95274 1.02223 9.79557C0.987652 9.6384 0.993414 9.47518 1.03951 9.30592C1.08562 9.16083 1.17205 9.03993 1.29883 8.94321C1.42561 8.84649 1.56968 8.78604 1.73103 8.76186L8.57701 8.14527L11.2739 1.50779C11.3431 1.33852 11.4468 1.21158 11.5851 1.12695C11.7234 1.04231 11.8617 1 12 1C12.1383 1 12.2766 1.04231 12.4149 1.12695C12.5532 1.21158 12.6569 1.33852 12.7261 1.50779L15.423 8.14527L22.269 8.76186C22.4303 8.78604 22.5744 8.84649 22.7012 8.94321C22.8279 9.03993 22.9144 9.16083 22.9605 9.30592C23.0066 9.47518 23.0123 9.6384 22.9778 9.79557C22.9432 9.95274 22.8452 10.0918 22.6839 10.2127L17.5321 14.9641L19.088 21.9643C19.1111 22.1577 19.0938 22.327 19.0361 22.4721C18.9785 22.6171 18.8921 22.738 18.7768 22.8348C18.6385 22.9315 18.4945 22.9859 18.3446 22.998C18.1948 23.0101 18.0392 22.9678 17.8779 22.871L12 19.1715Z" fill="#141414"></path>
                    </svg>
                </span> Promociones</a></li>
                <li><a href="#" class="msp-close-menu"><span class="icon icon-support_agent" aria-hidden="true">
                    <svg role="img" width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px">
                        <path d="M11.3846 20.5V19H18.6923C18.7756 19 18.8477 18.9744 18.9086 18.9231C18.9695 18.8718 19 18.8045 19 18.7211V11.7269C19 9.81537 18.316 8.20608 16.9481 6.89903C15.5801 5.592 13.9307 4.93848 12 4.93848C10.0692 4.93848 8.41985 5.592 7.0519 6.89903C5.68395 8.20608 4.99998 9.81537 4.99998 11.7269V17.6154H4.25C3.77052 17.6154 3.35898 17.4484 3.0154 17.1144C2.6718 16.7804 2.5 16.3737 2.5 15.8942V13.9519C2.5 13.6276 2.59231 13.3304 2.77693 13.0606C2.96154 12.7907 3.20257 12.5737 3.5 12.4096L3.54618 11.1327C3.62821 10.0443 3.91089 9.03593 4.39423 8.10773C4.87756 7.17952 5.49743 6.3715 6.25383 5.68368C7.01024 4.99586 7.88332 4.45997 8.87305 4.07601C9.8628 3.69202 10.9051 3.50003 12 3.50003C13.0948 3.50003 14.1346 3.69202 15.1192 4.07601C16.1038 4.45997 16.9769 4.99331 17.7384 5.67601C18.5 6.35869 19.1198 7.16413 19.598 8.09233C20.0762 9.02053 20.3615 10.0289 20.4538 11.1173L20.5 12.3693C20.791 12.5064 21.0304 12.7026 21.2182 12.9577C21.406 13.2128 21.5 13.4974 21.5 13.8115V16.0442C21.5 16.3583 21.406 16.6429 21.2182 16.8981C21.0304 17.1532 20.791 17.3493 20.5 17.4865V18.7211C20.5 19.2134 20.3233 19.633 19.9701 19.9798C19.6169 20.3266 19.191 20.5 18.6923 20.5H11.3846ZM9.1923 13.7692C8.94743 13.7692 8.73878 13.6862 8.56635 13.5202C8.39392 13.3542 8.3077 13.1487 8.3077 12.9039C8.3077 12.659 8.39392 12.4519 8.56635 12.2827C8.73878 12.1135 8.94743 12.0289 9.1923 12.0289C9.43717 12.0289 9.64582 12.1135 9.81825 12.2827C9.99068 12.4519 10.0769 12.659 10.0769 12.9039C10.0769 13.1487 9.99068 13.3542 9.81825 13.5202C9.64582 13.6862 9.43717 13.7692 9.1923 13.7692ZM14.8077 13.7692C14.5628 13.7692 14.3541 13.6862 14.1817 13.5202C14.0093 13.3542 13.923 13.1487 13.923 12.9039C13.923 12.659 14.0093 12.4519 14.1817 12.2827C14.3541 12.1135 14.5628 12.0289 14.8077 12.0289C15.0525 12.0289 15.2612 12.1135 15.4336 12.2827C15.606 12.4519 15.6923 12.659 15.6923 12.9039C15.6923 13.1487 15.606 13.3542 15.4336 13.5202C15.2612 13.6862 15.0525 13.7692 14.8077 13.7692ZM6.37115 12.2C6.2673 10.5679 6.77499 9.17148 7.89423 8.01058C9.01346 6.8497 10.3987 6.26926 12.05 6.26926C13.4371 6.26926 14.6612 6.69842 15.7221 7.55676C16.783 8.41507 17.4269 9.52628 17.6538 10.8904C16.2333 10.8737 14.9208 10.5006 13.7163 9.77116C12.5118 9.04167 11.5872 8.04168 10.9423 6.77118C10.6885 8.01476 10.1564 9.11411 9.34615 10.0692C8.53588 11.0243 7.54422 11.7346 6.37115 12.2Z" fill="#141414"></path>
                    </svg>
                </span> Centro de ayuda</a></li>
                <li><a href="#" class="msp-close-menu"><span class="icon icon-mobile_friendly" aria-hidden="true">
                    <svg role="img" width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px">
                        <path d="M6.3 22.5C5.8 22.5 5.375 22.325 5.025 21.975C4.675 21.625 4.5 21.2 4.5 20.7V3.3C4.5 2.8 4.675 2.375 5.025 2.025C5.375 1.675 5.8 1.5 6.3 1.5H15.7C16.2 1.5 16.625 1.675 16.975 2.025C17.325 2.375 17.5 2.8 17.5 3.3V6.95H16V5.75H6V18.25H16V17.05H17.5V20.7C17.5 21.2 17.325 21.625 16.975 21.975C16.625 22.325 16.2 22.5 15.7 22.5H6.3ZM6 19.75V20.7C6 20.7667 6.03333 20.8333 6.1 20.9C6.16667 20.9667 6.23333 21 6.3 21H15.7C15.7667 21 15.8333 20.9667 15.9 20.9C15.9667 20.8333 16 20.7667 16 20.7V19.75H6ZM14.95 15.65L11.05 11.75L12.1 10.7L14.95 13.55L20.625 7.875L21.675 8.925L14.95 15.65ZM6 4.25H16V3.3C16 3.23333 15.9667 3.16667 15.9 3.1C15.8333 3.03333 15.7667 3 15.7 3H6.3C6.23333 3 6.16667 3.03333 6.1 3.1C6.03333 3.16667 6 3.23333 6 3.3V4.25ZM6 19.75V21V20.7V19.75Z" fill="#141414"></path>
                    </svg>
                </span> Experiencia digital</a></li>
                <li><a href="#" class="msp-close-menu"><span class="icon icon-menu_book" aria-hidden="true">
                    <svg role="img" width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px">
                        <path d="M 14.175 8.7237 v -1.7213 q 0.8353 -0.3544 1.7086 -0.5316 t 1.8352 -0.1772 q 0.6581 0 1.2909 0.1013 t 1.2403 0.2531 v 1.62 q -0.6075 -0.2278 -1.2277 -0.3417 T 17.7188 7.8125 q -0.9619 0 -1.8478 0.2405 T 14.175 8.7237 Z m 0 5.5688 v -1.7213 q 0.8353 -0.3544 1.7086 -0.5316 t 1.8352 -0.1772 q 0.6581 0 1.2909 0.1013 t 1.2403 0.2531 v 1.62 q -0.6075 -0.2278 -1.2277 -0.3417 T 17.7188 13.3813 q -0.9619 0 -1.8478 0.2278 t -1.6959 0.6834 Z m 0 -2.7844 v -1.7213 q 0.8353 -0.3544 1.7086 -0.5316 t 1.8352 -0.1772 q 0.6581 0 1.2909 0.1013 t 1.2403 0.2531 v 1.62 q -0.6075 -0.2278 -1.2277 -0.3417 T 17.7188 10.5969 q -0.9619 0 -1.8478 0.2405 T 14.175 11.5081 Z M 6.5812 14.9 q 1.1897 0 2.3161 0.2658 T 11.1375 15.9631 v -9.9731 q -1.0378 -0.6075 -2.2022 -0.9113 t -2.3541 -0.3038 q -0.9113 0 -1.8098 0.1772 T 3.0375 5.4837 v 10.0238 q 0.8859 -0.3038 1.7592 -0.4556 t 1.7845 -0.1519 Z m 6.5812 1.0631 q 1.1138 -0.5316 2.2402 -0.7973 T 17.7188 14.9 q 0.9113 0 1.7845 0.1519 t 1.7592 0.4556 v -10.0238 q -0.8353 -0.3544 -1.7339 -0.5316 t -1.8098 -0.1772 q -1.1897 0 -2.3541 0.3038 t -2.2022 0.9113 v 9.9731 Z m -1.0125 2.9869 q -1.215 -0.9619 -2.6325 -1.4934 t -2.9363 -0.5316 q -1.0631 0 -2.0883 0.2784 T 2.5313 17.9881 q -0.5316 0.2784 -1.0252 -0.0253 T 1.0125 17.0769 v -12.2006 q 0 -0.2784 0.1392 -0.5316 T 1.5694 3.965 q 1.1644 -0.6075 2.43 -0.9113 t 2.5819 -0.3038 q 1.4681 0 2.873 0.3797 T 12.15 4.2688 q 1.2909 -0.7594 2.6958 -1.1391 T 17.7188 2.75 q 1.3163 0 2.5819 0.3038 t 2.43 0.9113 q 0.2784 0.1266 0.4177 0.3797 t 0.1392 0.5316 v 12.2006 q 0 0.5822 -0.4936 0.8859 t -1.0252 0.0253 q -0.9366 -0.5062 -1.9617 -0.7847 T 17.7188 16.925 q -1.5188 0 -2.9363 0.5316 t -2.6325 1.4934 Z M 7.0875 10.4956 Z" fill="#141414"></path>
                    </svg>
                </span> Blog</a></li>
                <li><a href="#" class="msp-close-menu"><span class="icon icon-where_to_vote" aria-hidden="true">
                    <svg role="img" width="16px" height="16px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px">
                        <path d="M10.7 12.725L15.3 8.125L14.225 7.05L10.7 10.575L9.3 9.175L8.225 10.25L10.7 12.725ZM11.75 19.55C13.8167 17.7167 15.375 15.9623 16.425 14.287C17.475 12.6123 18 11.1667 18 9.95C18 8.05 17.396 6.5 16.188 5.3C14.9793 4.1 13.5 3.5 11.75 3.5C10 3.5 8.52067 4.1 7.312 5.3C6.104 6.5 5.5 8.05 5.5 9.95C5.5 11.1667 6.025 12.6123 7.075 14.287C8.125 15.9623 9.68333 17.7167 11.75 19.55ZM11.75 21.55C9.15 19.2833 7.20833 17.1833 5.925 15.25C4.64167 13.3167 4 11.55 4 9.95C4 7.53333 4.77933 5.604 6.338 4.162C7.896 2.72067 9.7 2 11.75 2C13.8 2 15.6043 2.72067 17.163 4.162C18.721 5.604 19.5 7.53333 19.5 9.95C19.5 11.55 18.8583 13.3167 17.575 15.25C16.2917 17.1833 14.35 19.2833 11.75 21.55Z" fill="#141414"></path>
                    </svg>
                </span> Sucursales y cajeros</a></li>
            </ul>
        </div>
    </div>
    <nav class="navbar navbar-expand-lg navbar-light msp-header w-100">
        <div class="container">
            <a href="index.php" class="msp-header__logo" aria-label="Ir a página de inicio de Mifel">
                <img src="assets/recursos_site/cnds/logo-mifel.svg" alt="Logo Mifel">
            </a>
            <button class="navbar-toggler shadow-none collapsed msp-navbar-header" type="button" data-bs-toggle="collapse" data-bs-target="#msp-navbar-header" aria-controls="msp-navbar-header" aria-expanded="false" aria-label="Toggle navigation">
                <span class="icon icon-menu" aria-hidden="true">
                    <svg role="img" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:24px;height:24px">
                        <path d="M3 17.25V15.75H20.5V17.25H3ZM3 12.375V10.875H20.5V12.375H3ZM3 7.49999V5.99999H20.5V7.49999H3Z" fill="#141414"></path>
                    </svg>
                </span>
                <span class="icon icon-close" aria-hidden="true">
                    <svg role="img" width="24px" height="24px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:24px;height:24px">
                        <path d="M6.05 18.3L5 17.25L10.6 11.65L5 6.05L6.05 5L11.65 10.6L17.25 5L18.3 6.05L12.7 11.65L18.3 17.25L17.25 18.3L11.65 12.7L6.05 18.3Z" fill="#141414"></path>
                    </svg>
                </span>
            </button>
            <div class="collapse navbar-collapse msp-header__navbar-collapse" id="msp-navbar-header">
                <div class="msp-pre-header__tabs d-lg-none">
                    <div class="container">
                        <ul class="nav nav-tabs pt-2 border-0 justify-content-around">
                            <li class="nav-item"><a class="msp-sub-p msp-fw-regular active" href="personas.html">Personas</a></li>
                            <li class="nav-item"><a class="msp-sub-p msp-fw-regular" href="empresas/index.php">Empresas</a></li>
                        </ul>
                    </div>
                </div>
                <div class="container d-lg-flex align-items-center p-0">
                    <ul class="navbar-nav navbar-nav-scroll msp-header__nav pt-3 pt-lg-0 me-auto ms-0 ms-lg-5">
                        <li class="nav-item msp-nav-item dropdown msp-hide-dropdown">
                            <button class="btn msp-dropdown__expand d-flex d-lg-block justify-content-between color-primary-semilight w-100" type="button" id="msp-dropdown-products" data-bs-toggle="dropdown" aria-expanded="false">Productos para ti <?php $size = 24; portal_nav_icon('chevron_down', $size); ?></button>
                            <ul class="dropdown-menu msp-dropdown__menu msp-sub-p p-0 mt-0 mt-lg-2" aria-labelledby="msp-dropdown-products">
                                <?php foreach ($portalNavProducts as $product): ?>
                                <li><a href="<?= htmlspecialchars($product['href'], ENT_QUOTES, 'UTF-8') ?>" class="dropdown-item color-primary-semilight msp-fw-light" type="button"><?php $size = 24; portal_nav_icon($product['icon'], $size); ?> <?= htmlspecialchars($product['label'], ENT_QUOTES, 'UTF-8') ?></a></li>
                                <?php endforeach; ?>
                            </ul>
                        </li>
                        <div class="d-block d-lg-none">
                            <p class="m-0 p-3 font-weight-regular msp-fw-regular">Productos para ti</p>
                            <div class="d-flex flex-column pb-3">
                                <?php foreach ($portalNavProducts as $product): ?>
                                <a href="<?= htmlspecialchars($product['href'], ENT_QUOTES, 'UTF-8') ?>" class="d-flex btn p-3 text-start msp-header__nav--options msp-sub-p color-primary-semilight msp-close-menu" type="button"><?php $size = 24; portal_nav_icon($product['icon'], $size); ?> <?= htmlspecialchars($product['label'], ENT_QUOTES, 'UTF-8') ?></a>
                                <?php endforeach; ?>
                            </div>
                        </div>
                        <ul class="d-flex d-lg-none flex-column msp-pre-header__help-center msp-sub-p">
                            <?php foreach ($portalNavHelpMobile as $link): ?>
                            <li><a href="<?= htmlspecialchars($link['href'], ENT_QUOTES, 'UTF-8') ?>" class="msp-close-menu"><?php $size = 16; portal_nav_icon($link['icon'], $size); ?> <?= htmlspecialchars($link['label'], ENT_QUOTES, 'UTF-8') ?></a></li>
                            <?php endforeach; ?>
                        </ul>
                    </ul>
                    <div class="d-flex msp-header__options flex-column flex-lg-row justify-content-center ms-lg-auto pb-3 pb-lg-0">
                        <button type="button" class="msp-btn msp-btn--secondary d-block d-md-inline-block text-center me-lg-2 mb-2 mb-lg-0" onclick="showMyModalQr()">Hazte cliente.</button>
                        <div class="dropdown dropup" id="getinto-dropdown">
                            <button class="msp-btn text-center msp-btn--primary dropdown-toggle w-100" type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-expanded="false">
                                <?php include __DIR__ . '/icon_pc_widget_x7.php'; ?>
                                Ingresa a tu banca
                                <?php $size = 24; portal_nav_icon('chevron_down', $size); ?>
                            </button>
                            <ul class="dropdown-menu msp-sub-p p-0 mt-0 mt-lg-2" aria-labelledby="dropdownMenuButton1">
                                <li><a class="dropdown-item color-primary-semilight msp-fw-light msp-close-menu" href="personas.html"> Mifel Personas</a></li>
                                <li><a class="dropdown-item color-primary-semilight msp-fw-light msp-close-menu" href="empresas/index.php"> Mifel Empresas</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </nav>
</header>
<style>
    #getinto-dropdown {
        position: relative;
    }

    #getinto-dropdown .msp-btn--primary.dropdown-toggle {
        padding: 11px 24px;
    }

    #getinto-dropdown .msp-btn--primary.dropdown-toggle.show {
        color: #002856;
    }

    #getinto-dropdown .msp-btn--primary.dropdown-toggle::after {
        content: "";
        display: inline-block;
        width: 0;
        height: 0;
        margin-left: 0.255em;
        vertical-align: 0.255em;
        border-top: 0.3em solid #002856;
        border-right: 0.3em solid transparent;
        border-left: 0.3em solid transparent;
        border-bottom: 0;
    }

    #getinto-dropdown .msp-btn--primary.dropdown-toggle.show .icon-chevron_down {
        transform: matrix(-1, 0, 0, -1, 0, 0);
    }

    #getinto-dropdown .icon-mifel_pc,
    #getinto-dropdown .msp-btn--primary.dropdown-toggle.show .icon-mifel_pc {
        transform: none !important;
    }

    #getinto-dropdown .icon-mifel_pc svg {
        transform: none !important;
    }

    #getinto-dropdown .dropdown-menu {
        width: 100%;
        min-width: 100%;
        border: 0;
        border-radius: 8px;
        box-shadow: rgba(55, 71, 79, 0.15) 0 6px 12px 0;
        overflow: hidden;
    }

    #getinto-dropdown .dropdown-menu .dropdown-item {
        padding: 16px 24px;
        color: #00438f;
    }

    #getinto-dropdown .dropdown-menu li:first-child {
        border-bottom: 1px solid #b0c5dc;
    }
</style>
