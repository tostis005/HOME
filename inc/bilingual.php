<?php
if (!defined('ABSPATH')) { exit; }

function home_current_language(): string {
    $uri = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '/';
    $path = (string) wp_parse_url($uri, PHP_URL_PATH);
    return preg_match('#^/en(?:/|$)#i', $path) ? 'en' : 'es';
}

function home_is_english(): bool { return home_current_language() === 'en'; }
function home_site_root_url(): string { return trailingslashit((string) get_option('home')); }
function home_localized_home_url(?string $language = null): string {
    $language = $language ?: home_current_language();
    return $language === 'en' ? home_site_root_url() . 'en/' : home_site_root_url();
}

function home_language_attributes(string $output): string {
    $lang = home_is_english() ? 'en-US' : 'es-ES';
    if (preg_match('/lang=("|\')[^"\']*("|\')/i', $output)) {
        return (string) preg_replace('/lang=("|\')[^"\']*("|\')/i', 'lang="' . esc_attr($lang) . '"', $output, 1);
    }
    return trim($output . ' lang="' . esc_attr($lang) . '"');
}
add_filter('language_attributes', 'home_language_attributes');
add_filter('body_class', static function(array $classes): array {
    $classes[] = 'home-lang-' . home_current_language();
    return $classes;
});

function home_register_language_rewrites(): void {
    add_rewrite_tag('%home_lang%', '(es|en)');
    add_rewrite_tag('%home_front%', '1');
    add_rewrite_tag('%home_slug%', '([^&]+)');

    add_rewrite_rule('^en/?$', 'index.php?home_lang=en&home_front=1', 'top');

    foreach (home_category_definitions() as $definition) {
        add_rewrite_rule(
            '^categoria/' . preg_quote($definition['slug_es'], '#') . '/?$',
            'index.php?category_name=' . $definition['wp_slug'] . '&home_lang=es',
            'top'
        );
        add_rewrite_rule(
            '^en/category/' . preg_quote($definition['slug_en'], '#') . '/?$',
            'index.php?category_name=' . $definition['wp_slug'] . '&home_lang=en',
            'top'
        );
    }

    add_rewrite_rule('^en/([^/]+)/?$', 'index.php?home_slug=$matches[1]&home_lang=en', 'top');
}
add_action('init', 'home_register_language_rewrites', 20);

add_filter('query_vars', static function(array $vars): array {
    $vars[] = 'home_lang';
    $vars[] = 'home_front';
    $vars[] = 'home_slug';
    return $vars;
});

function home_resolve_post_slug_for_language(string $slug, string $language): ?WP_Post {
    $post = get_page_by_path($slug, OBJECT, 'post');
    if (!$post instanceof WP_Post || $post->post_status !== 'publish') { return null; }
    $post_language = get_post_meta($post->ID, '_home_language', true) === 'en' ? 'en' : 'es';
    return $post_language === $language ? $post : null;
}

function home_resolve_english_slug(array $query_vars): array {
    if (empty($query_vars['home_slug'])) { return $query_vars; }
    $slug = trim(sanitize_title((string) $query_vars['home_slug']), '/');
    unset($query_vars['home_slug']);

    $post = home_resolve_post_slug_for_language($slug, 'en');
    if ($post instanceof WP_Post) {
        $query_vars['name'] = $post->post_name;
        $query_vars['post_type'] = 'post';
        return $query_vars;
    }

    $query_vars['name'] = '__home_missing_english_content__';
    $query_vars['post_type'] = 'post';
    return $query_vars;
}
add_filter('request', 'home_resolve_english_slug', 5);

/**
 * Fallback router for production environments where WordPress rewrite_rules
 * were not regenerated correctly. Apache only needs to send the request to
 * index.php; this router then resolves all HOME public URLs deterministically.
 */
function home_route_localized_request(WP $wp): void {
    $uri = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '/';
    $path = trim((string) wp_parse_url($uri, PHP_URL_PATH), '/');

    if ($path === 'en') {
        $wp->query_vars = array_merge($wp->query_vars, ['home_lang'=>'en','home_front'=>'1']);
        unset($wp->query_vars['error'], $wp->query_vars['name'], $wp->query_vars['pagename']);
        return;
    }

    foreach (home_category_definitions() as $definition) {
        if ($path === 'categoria/' . $definition['slug_es']) {
            $wp->query_vars = array_merge($wp->query_vars, ['category_name'=>$definition['wp_slug'],'home_lang'=>'es']);
            unset($wp->query_vars['error'], $wp->query_vars['name'], $wp->query_vars['pagename']);
            return;
        }
        if ($path === 'en/category/' . $definition['slug_en']) {
            $wp->query_vars = array_merge($wp->query_vars, ['category_name'=>$definition['wp_slug'],'home_lang'=>'en']);
            unset($wp->query_vars['error'], $wp->query_vars['name'], $wp->query_vars['pagename']);
            return;
        }
    }

    if (preg_match('#^en/([^/]+)$#', $path, $matches)) {
        $slug = sanitize_title($matches[1]);
        $post = home_resolve_post_slug_for_language($slug, 'en');
        if ($post instanceof WP_Post) {
            $wp->query_vars = array_merge($wp->query_vars, ['name'=>$post->post_name,'post_type'=>'post','home_lang'=>'en']);
            unset($wp->query_vars['error'], $wp->query_vars['pagename']);
        }
        return;
    }

    if ($path !== '' && strpos($path, '/') === false) {
        $slug = sanitize_title($path);
        $post = home_resolve_post_slug_for_language($slug, 'es');
        if ($post instanceof WP_Post) {
            $wp->query_vars = array_merge($wp->query_vars, ['name'=>$post->post_name,'post_type'=>'post','home_lang'=>'es']);
            unset($wp->query_vars['error'], $wp->query_vars['pagename']);
        }
    }
}
add_action('parse_request', 'home_route_localized_request', 1);

function home_ensure_bilingual_permalinks(): void {
    $desired = '/%postname%/';
    $version = 'home-bilingual-2026-09-07-v10';
    $structure_changed = (string) get_option('permalink_structure') !== $desired;

    if ($structure_changed) {
        update_option('permalink_structure', $desired);
        global $wp_rewrite;
        if ($wp_rewrite instanceof WP_Rewrite) {
            $wp_rewrite->permalink_structure = $desired;
        }
    }

    if ($structure_changed || get_option('home_rewrite_version') !== $version) {
        flush_rewrite_rules(false);
        update_option('home_rewrite_version', $version, false);
    }
}
add_action('init', 'home_ensure_bilingual_permalinks', 99);

add_filter('redirect_canonical', static function($redirect_url, $requested_url) {
    $path = (string) wp_parse_url((string) $requested_url, PHP_URL_PATH);
    if ((string) get_query_var('home_front') === '1' || get_query_var('home_lang') || preg_match('#^/en(?:/|$)|^/categoria/#', $path)) {
        return false;
    }
    return $redirect_url;
}, 10, 2);

add_filter('template_include', static function(string $template): string {
    if ((string) get_query_var('home_front') === '1') {
        global $wp_query;
        if ($wp_query instanceof WP_Query) {
            $wp_query->is_404 = false;
            $wp_query->is_home = false;
            $wp_query->is_page = true;
        }
        status_header(200);
        $front = get_theme_file_path('front-page.php');
        if (is_readable($front)) { return $front; }
    }
    return $template;
}, 99);

add_action('template_redirect', static function(): void {
    if ((string) get_query_var('home_front') === '1') {
        global $wp_query;
        if ($wp_query instanceof WP_Query) { $wp_query->is_404 = false; }
        status_header(200);
    }
}, 0);

add_action('pre_get_posts', static function(WP_Query $query): void {
    if ((string) $query->get('home_front') === '1') {
        $query->is_home = false;
        $query->is_page = true;
        $query->is_404 = false;
    }
}, 1);
