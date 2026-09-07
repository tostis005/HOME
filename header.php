<!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
    <link rel="stylesheet" href="/wp-content/themes/home/assets/css/home-v2.css?v=4.1.0">
    <link rel="stylesheet" href="/wp-content/themes/home/assets/css/home-premium.css?v=1.2.0">
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="site-shell home-v2-shell">
<header class="site-header home-v2-header">
    <div class="container header-inner home-v2-header-inner">
        <a class="brand home-v2-brand" href="<?php echo esc_url(home_localized_home_url()); ?>" aria-label="<?php esc_attr_e('HOME homepage', 'home'); ?>">
            <span class="home-v2-brand-icon" aria-hidden="true">
                <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" focusable="false">
                    <path d="M8 30.5 32 10l24 20.5v23A4.5 4.5 0 0 1 51.5 58h-39A4.5 4.5 0 0 1 8 53.5v-23Z" fill="currentColor" opacity=".96"/>
                    <path d="M20 44c8-1 13-6 15-15-9 1-14 6-15 15Zm25 2c-7-1-11-5-13-12 8 1 12 5 13 12Z" fill="#fbf8f1"/>
                    <path d="M27 48c2-9 6-15 13-19" fill="none" stroke="#fbf8f1" stroke-width="2.6" stroke-linecap="round"/>
                </svg>
            </span>
            <span class="home-v2-brand-copy">
                <span class="home-v2-brand-word">HOME</span>
                <span class="home-v2-brand-tagline"><?php esc_html_e('Practical advice for real life', 'home'); ?></span>
            </span>
        </a>

        <nav class="site-nav home-v2-nav" aria-label="<?php esc_attr_e('Primary navigation', 'home'); ?>">
            <?php home_render_primary_menu(); ?>
        </nav>

        <div class="home-v2-header-actions">
            <a class="header-search home-v2-search-button" href="<?php echo esc_url(add_query_arg('s', '', home_localized_home_url())); ?>" aria-label="<?php esc_attr_e('Search HOME', 'home'); ?>">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="2"/><path d="m16 16 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </a>
            <button class="home-language-trigger home-language-trigger--flag-only" type="button" data-home-open="language" aria-controls="home-language-overlay" aria-expanded="false" aria-label="<?php esc_attr_e('Choose language', 'home'); ?>">
                <span class="home-language-flag" aria-hidden="true"><?php echo home_is_english() ? '🇺🇸' : '🇪🇸'; ?></span>
            </button>
            <button class="home-mobile-menu-trigger" type="button" data-home-open="menu" aria-controls="home-mobile-overlay" aria-expanded="false" aria-label="<?php esc_attr_e('Menu', 'home'); ?>"><span></span><span></span></button>
        </div>
    </div>
</header>

<div class="home-fullscreen-overlay home-language-overlay" id="home-language-overlay" data-home-overlay="language" aria-hidden="true">
    <div class="home-overlay-topbar">
        <span class="home-overlay-label"><?php esc_html_e('Language', 'home'); ?></span>
        <button class="home-overlay-close" type="button" data-home-close aria-label="<?php esc_attr_e('Close language selector', 'home'); ?>"><span></span><span></span></button>
    </div>
    <div class="home-language-panel">
        <p class="home-language-kicker">HOME</p>
        <h2><?php esc_html_e('Choose language', 'home'); ?></h2>
        <div class="home-language-options">
            <a class="home-language-option<?php echo home_is_english() ? '' : ' is-current'; ?>" href="<?php echo esc_url(home_language_url('es')); ?>"<?php echo home_is_english() ? '' : ' aria-current="page"'; ?>>
                <span class="home-language-option-flag" aria-hidden="true">🇪🇸</span><span><strong>Español</strong><small>España</small></span><span class="home-language-arrow" aria-hidden="true">→</span>
            </a>
            <a class="home-language-option<?php echo home_is_english() ? ' is-current' : ''; ?>" href="<?php echo esc_url(home_language_url('en')); ?>"<?php echo home_is_english() ? ' aria-current="page"' : ''; ?>>
                <span class="home-language-option-flag" aria-hidden="true">🇺🇸</span><span><strong>English</strong><small>United States</small></span><span class="home-language-arrow" aria-hidden="true">→</span>
            </a>
        </div>
    </div>
</div>

<div class="home-fullscreen-overlay home-mobile-overlay" id="home-mobile-overlay" data-home-overlay="menu" aria-hidden="true">
    <div class="home-overlay-topbar">
        <a class="home-overlay-brand" href="<?php echo esc_url(home_localized_home_url()); ?>">HOME</a>
        <button class="home-overlay-close" type="button" data-home-close aria-label="<?php esc_attr_e('Close menu', 'home'); ?>"><span></span><span></span></button>
    </div>
    <div class="home-mobile-panel">
        <nav class="home-mobile-nav" aria-label="<?php esc_attr_e('Primary navigation', 'home'); ?>"><?php home_render_primary_menu('home-mobile-menu-list'); ?></nav>
        <div class="home-mobile-bottom">
            <button class="home-mobile-language" type="button" data-home-open="language"><span aria-hidden="true"><?php echo home_is_english() ? '🇺🇸' : '🇪🇸'; ?></span><span><?php echo home_is_english() ? 'English' : 'Español'; ?></span><span aria-hidden="true">→</span></button>
            <a class="home-mobile-search" href="<?php echo esc_url(add_query_arg('s', '', home_localized_home_url())); ?>"><?php esc_html_e('Search HOME', 'home'); ?> <span aria-hidden="true">→</span></a>
        </div>
    </div>
</div>

<main id="content">
