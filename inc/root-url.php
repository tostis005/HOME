<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Keep legacy root links/search forms inside /en/ while browsing English pages.
 * Only rewrites the bare site root on the frontend; localized category/post URLs
 * and explicit Spanish targets are left untouched.
 */
function home_localize_root_home_url($url, $path, $orig_scheme = null, $blog_id = null): string {
    if (is_admin() || !did_action('template_redirect') || !home_is_english()) {
        return (string) $url;
    }

    if ($path === '' || $path === '/') {
        return home_localized_home_url('en');
    }

    return (string) $url;
}
add_filter('home_url', 'home_localize_root_home_url', 10, 4);
