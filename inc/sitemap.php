<?php
if (!defined('ABSPATH')) { exit; }

/**
 * DomstIQ language sitemaps.
 *
 * Public endpoints:
 * - /sitemap.xml    -> sitemap index
 * - /sitemap-es.xml -> Spanish posts/pages
 * - /sitemap-en.xml -> English posts/pages
 */

function home_sitemap_xml_escape(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_XML1, 'UTF-8');
}

function home_sitemap_language_meta_query(string $language): array {
    if ($language === 'en') {
        return [
            ['key' => '_home_language', 'value' => 'en', 'compare' => '='],
        ];
    }

    return [
        'relation' => 'OR',
        ['key' => '_home_language', 'compare' => 'NOT EXISTS'],
        ['key' => '_home_language', 'value' => 'en', 'compare' => '!='],
    ];
}

/**
 * Return every indexable published post/page for one language.
 * URLs are keyed so the virtual homepage cannot be duplicated by a WordPress page.
 */
function home_sitemap_urls(string $language): array {
    $language = $language === 'en' ? 'en' : 'es';
    $urls = [];

    $home_url = home_localized_home_url($language);
    $urls[$home_url] = ['loc' => $home_url, 'lastmod' => ''];

    foreach (['page', 'post'] as $post_type) {
        $items = get_posts([
            'post_type'                 => $post_type,
            'post_status'               => 'publish',
            'posts_per_page'            => -1,
            'orderby'                   => 'modified',
            'order'                     => 'DESC',
            'no_found_rows'             => true,
            'suppress_filters'          => false,
            'home_skip_language_filter' => 1,
            'has_password'              => false,
            'meta_query'                => home_sitemap_language_meta_query($language),
        ]);

        foreach ($items as $item) {
            if (!$item instanceof WP_Post) { continue; }

            $loc = get_permalink($item);
            if (!is_string($loc) || $loc === '') { continue; }

            $modified = $item->post_modified_gmt !== '0000-00-00 00:00:00'
                ? $item->post_modified_gmt
                : $item->post_modified;
            $lastmod = $modified ? mysql2date('c', $modified, false) : '';

            $urls[$loc] = [
                'loc'     => $loc,
                'lastmod' => is_string($lastmod) ? $lastmod : '',
            ];
        }
    }

    return array_values($urls);
}

function home_render_sitemap_index(): void {
    $root = home_site_root_url();
    $entries = [
        $root . 'sitemap-es.xml',
        $root . 'sitemap-en.xml',
    ];

    echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
    echo '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
    foreach ($entries as $loc) {
        echo "  <sitemap><loc>" . home_sitemap_xml_escape($loc) . "</loc></sitemap>\n";
    }
    echo "</sitemapindex>\n";
}

function home_render_language_sitemap(string $language): void {
    $urls = home_sitemap_urls($language);

    echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
    echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";
    foreach ($urls as $entry) {
        echo "  <url>\n";
        echo '    <loc>' . home_sitemap_xml_escape((string) $entry['loc']) . "</loc>\n";
        if (!empty($entry['lastmod'])) {
            echo '    <lastmod>' . home_sitemap_xml_escape((string) $entry['lastmod']) . "</lastmod>\n";
        }
        echo "  </url>\n";
    }
    echo "</urlset>\n";
}

function home_maybe_render_sitemap(): void {
    $uri = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '';
    $path = trim((string) wp_parse_url($uri, PHP_URL_PATH), '/');

    if (!in_array($path, ['sitemap.xml', 'sitemap-es.xml', 'sitemap-en.xml'], true)) {
        return;
    }

    status_header(200);
    header('Content-Type: application/xml; charset=UTF-8');
    header('Cache-Control: public, max-age=900');

    if ($path === 'sitemap.xml') {
        home_render_sitemap_index();
    } else {
        home_render_language_sitemap($path === 'sitemap-en.xml' ? 'en' : 'es');
    }

    exit;
}
add_action('template_redirect', 'home_maybe_render_sitemap', -100);

// Avoid publishing a second, overlapping WordPress core sitemap.
add_filter('wp_sitemaps_enabled', '__return_false');

// Advertise the canonical sitemap index to crawlers via /robots.txt.
add_filter('robots_txt', static function(string $output, bool $public): string {
    if (!$public) { return $output; }

    $sitemap = home_site_root_url() . 'sitemap.xml';
    if (stripos($output, 'Sitemap: ' . $sitemap) === false) {
        $output = rtrim($output) . "\nSitemap: " . $sitemap . "\n";
    }

    return $output;
}, 20, 2);
