<?php
/** HOME theme functions. */
if (!defined('ABSPATH')) { exit; }

require_once get_template_directory() . '/inc/bilingual.php';
require_once get_template_directory() . '/inc/translations.php';
require_once get_template_directory() . '/inc/categories.php';
require_once get_template_directory() . '/inc/content-language.php';
require_once get_template_directory() . '/inc/root-url.php';

function home_theme_setup(): void {
    load_theme_textdomain('home', get_template_directory() . '/languages');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', ['height'=>80,'width'=>240,'flex-height'=>true,'flex-width'=>true]);
    add_theme_support('html5', ['search-form','gallery','caption','style','script']);
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');
    register_nav_menus([
        'primary'    => __('Primary navigation', 'home'),
        'primary_es' => __('Primary navigation — Spanish', 'home'),
        'primary_en' => __('Primary navigation — English', 'home'),
        'footer'     => __('Footer navigation', 'home'),
    ]);
}
add_action('after_setup_theme', 'home_theme_setup');

function home_theme_assets(): void {
    $version = wp_get_theme()->get('Version') ?: '1.0.0';
    wp_enqueue_style('home-style', get_stylesheet_uri(), [], $version);
    wp_enqueue_style('home-language-ui', get_template_directory_uri() . '/assets/css/language-ui.css', [], '1.0.0');
    wp_enqueue_script('home-navigation', get_template_directory_uri() . '/assets/js/navigation.js', [], '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'home_theme_assets');

add_filter('excerpt_length', static fn(int $length): int => 24, 999);
add_filter('excerpt_more', static fn(string $more): string => '…');
