<?php
/** DomstIQ theme functions. */
if (!defined('ABSPATH')) { exit; }

require_once get_template_directory() . '/inc/bilingual.php';
require_once get_template_directory() . '/inc/translations.php';
require_once get_template_directory() . '/inc/categories.php';
require_once get_template_directory() . '/inc/content-language.php';
require_once get_template_directory() . '/inc/root-url.php';
require_once get_template_directory() . '/inc/content-curation.php';
require_once get_template_directory() . '/inc/publication-guard.php';
require_once get_template_directory() . '/inc/pagination.php';

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
 * Public-facing DomstIQ identity. Technical `home_*` identifiers are intentionally
 * preserved so the existing theme, content importers and bilingual routing remain stable.
 */
function home_brand_name(): string {
    return 'DomstIQ';
}

function home_brand_asset_url(string $filename): string {
    return get_template_directory_uri() . '/assets/branding/' . ltrim($filename, '/');
}

function home_brand_legacy_name(string $translation, string $text, string $domain): string {
    if ($domain !== 'home') {
        return $translation;
    }

    return str_replace('HOME', home_brand_name(), $translation);
}
add_filter('gettext', 'home_brand_legacy_name', 20, 3);

function home_brand_bloginfo(string $output, string $show): string {
    if ($show === 'name' && !is_admin()) {
        return home_brand_name();
    }

    return $output;
}
add_filter('bloginfo', 'home_brand_bloginfo', 10, 2);

function home_brand_document_title(array $title): array {
    if (isset($title['site'])) {
        $title['site'] = home_brand_name();
    }

    return $title;
}
add_filter('document_title_parts', 'home_brand_document_title');

function home_brand_head_assets(): void {
    $favicon = home_brand_asset_url('favicon.png');
    echo '<link rel="icon" href="' . esc_url($favicon) . '" type="image/png" sizes="128x128">' . "\n";
    echo '<meta name="theme-color" content="#496048">' . "\n";
}
add_action('wp_head', 'home_brand_head_assets', 100);

/**
 * Theme-owned premium image pack helpers.
 * Root-relative URLs are intentional while DomstIQ is served on :8081.
 */
function home_theme_image_exists(string $relative_path): bool {
    $relative_path = ltrim($relative_path, '/');
    return is_file(get_template_directory() . '/' . $relative_path);
}

function home_theme_image_url(string $relative_path): string {
    $relative_path = ltrim($relative_path, '/');
    $absolute_path = get_template_directory() . '/' . $relative_path;
    $url = '/wp-content/themes/home/' . $relative_path;

    if (is_file($absolute_path)) {
        $version = (string) filemtime($absolute_path);
        if ($version !== '') {
            $url .= '?v=' . rawurlencode($version);
        }
    }

    return $url;
}

function home_hero_image_url(): string {
    $premium = 'assets/images/home/hero.jpg';
    if (home_theme_image_exists($premium)) {
        return home_theme_image_url($premium);
    }
    return home_theme_image_url('assets/generated/hero-living-room-v2.jpg');
}

function home_category_image_url(string $category_key): string {
    $relative = 'assets/images/categories/' . sanitize_file_name($category_key) . '.jpg';
    return home_theme_image_exists($relative) ? home_theme_image_url($relative) : '';
}

function home_post_category_key(?int $post_id = null): string {
    $post_id = $post_id ?: get_the_ID();
    $curated = sanitize_key((string) get_post_meta($post_id, '_home_primary_category', true));
    if ($curated && isset(home_category_definitions()[$curated])) {
        return $curated;
    }

    $categories = get_the_category($post_id);
    if (!empty($categories)) {
        $key = home_category_key_from_wp_slug($categories[0]->slug);
        if ($key) {
            return $key;
        }
    }
    return 'cleaning';
}
