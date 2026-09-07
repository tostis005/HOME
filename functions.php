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

/**
 * Theme-owned premium image pack helpers.
 * Root-relative URLs are intentional while HOME is served on :8081.
 */
function home_theme_image_exists(string $relative_path): bool {
    $relative_path = ltrim($relative_path, '/');
    return is_file(get_template_directory() . '/' . $relative_path);
}

function home_theme_image_url(string $relative_path): string {
    $relative_path = ltrim($relative_path, '/');
    return '/wp-content/themes/home/' . $relative_path;
}

function home_hero_image_url(): string {
    $premium = 'assets/images/home/hero.jpg';
    if (home_theme_image_exists($premium)) {
        return home_theme_image_url($premium);
    }
    return home_theme_image_url('assets/generated/hero-living-room-v2.jpg') . '?v=6';
}

function home_category_image_url(string $category_key): string {
    $relative = 'assets/images/categories/' . sanitize_file_name($category_key) . '.jpg';
    return home_theme_image_exists($relative) ? home_theme_image_url($relative) : '';
}

function home_post_category_key(?int $post_id = null): string {
    $categories = get_the_category($post_id ?: get_the_ID());
    if (!empty($categories)) {
        $key = home_category_key_from_wp_slug($categories[0]->slug);
        if ($key) {
            return $key;
        }
    }
    return 'cleaning';
}
