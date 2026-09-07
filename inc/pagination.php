<?php
if (!defined('ABSPATH')) { exit; }

/** Keep archive grids complete: 3 columns × 4 rows on desktop. */
function home_set_listing_page_size(WP_Query $query): void {
    if (is_admin() || !$query->is_main_query()) { return; }
    if ((string) $query->get('home_front') === '1') { return; }

    if ($query->is_category() || $query->is_archive() || $query->is_search() || $query->get('category_name')) {
        $query->set('posts_per_page', 12);
    }
}
add_action('pre_get_posts', 'home_set_listing_page_size', 35);

/** Pretty localized pagination for category archives. */
function home_register_category_pagination_rewrites(): void {
    foreach (home_category_definitions() as $definition) {
        add_rewrite_rule(
            '^categoria/' . preg_quote($definition['slug_es'], '#') . '/page/([0-9]+)/?$',
            'index.php?category_name=' . $definition['wp_slug'] . '&home_lang=es&paged=$matches[1]',
            'top'
        );
        add_rewrite_rule(
            '^en/category/' . preg_quote($definition['slug_en'], '#') . '/page/([0-9]+)/?$',
            'index.php?category_name=' . $definition['wp_slug'] . '&home_lang=en&paged=$matches[1]',
            'top'
        );
    }
}
add_action('init', 'home_register_category_pagination_rewrites', 21);

/** Fallback routing when production rewrite rules have not been refreshed yet. */
function home_route_category_pagination(WP $wp): void {
    $uri = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '/';
    $path = trim((string) wp_parse_url($uri, PHP_URL_PATH), '/');

    foreach (home_category_definitions() as $definition) {
        if (preg_match('#^categoria/' . preg_quote($definition['slug_es'], '#') . '/page/([0-9]+)$#', $path, $matches)) {
            $wp->query_vars = array_merge($wp->query_vars, [
                'category_name' => $definition['wp_slug'],
                'home_lang' => 'es',
                'paged' => max(1, (int) $matches[1]),
            ]);
            unset($wp->query_vars['error'], $wp->query_vars['name'], $wp->query_vars['pagename']);
            return;
        }

        if (preg_match('#^en/category/' . preg_quote($definition['slug_en'], '#') . '/page/([0-9]+)$#', $path, $matches)) {
            $wp->query_vars = array_merge($wp->query_vars, [
                'category_name' => $definition['wp_slug'],
                'home_lang' => 'en',
                'paged' => max(1, (int) $matches[1]),
            ]);
            unset($wp->query_vars['error'], $wp->query_vars['name'], $wp->query_vars['pagename']);
            return;
        }
    }
}
add_action('parse_request', 'home_route_category_pagination', 0);

function home_category_pagination(string $category_key): string {
    global $wp_query;
    if (!$wp_query instanceof WP_Query || $wp_query->max_num_pages <= 1) { return ''; }

    $current = max(1, (int) get_query_var('paged'));
    $base = trailingslashit(home_category_url($category_key)) . 'page/%#%/';

    return (string) paginate_links([
        'base' => $base,
        'format' => '',
        'current' => $current,
        'total' => (int) $wp_query->max_num_pages,
        'mid_size' => 1,
        'end_size' => 1,
        'prev_text' => home_is_english() ? '← Previous' : '← Anterior',
        'next_text' => home_is_english() ? 'Next →' : 'Siguiente →',
        'type' => 'plain',
    ]);
}
