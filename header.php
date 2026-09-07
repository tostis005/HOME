<!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
    <link rel="stylesheet" href="/wp-content/themes/home/assets/css/home-v2.css?v=4.0.0">
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div class="site-shell home-v2-shell">
<header class="site-header home-v2-header">
    <div class="container header-inner home-v2-header-inner">
        <a class="brand home-v2-brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="<?php esc_attr_e('HOME homepage', 'home'); ?>">
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
            <?php
            wp_nav_menu([
                'theme_location' => 'primary',
                'container'      => false,
                'fallback_cb'    => 'home_fallback_menu',
            ]);
            ?>
        </nav>

        <div class="home-v2-header-actions">
            <a class="header-search home-v2-search-button" href="<?php echo esc_url(home_url('/?s=')); ?>" aria-label="<?php esc_attr_e('Search HOME', 'home'); ?>">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="6.5" stroke="currentColor" stroke-width="2"/><path d="m16 16 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </a>
            <a class="home-v2-header-cta" href="#home-categories"><?php esc_html_e('Explore HOME', 'home'); ?></a>
        </div>
    </div>
</header>
<main id="content">
