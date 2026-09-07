<?php
if (!defined('ABSPATH')) { exit; }

function home_filter_queries_by_language(WP_Query $query): void {
    if (is_admin() || $query->get('post_type') === 'attachment') { return; }
    $post_type = $query->get('post_type');
    if ($post_type && $post_type !== 'post' && !(is_array($post_type) && in_array('post', $post_type, true))) { return; }

    $existing = $query->get('meta_query');
    $existing = is_array($existing) ? $existing : [];
    $language_clause = home_is_english()
        ? ['key'=>'_home_language','value'=>'en','compare'=>'=']
        : ['relation'=>'OR',['key'=>'_home_language','compare'=>'NOT EXISTS'],['key'=>'_home_language','value'=>'en','compare'=>'!=']];

    $query->set('meta_query', $existing ? ['relation'=>'AND',$existing,$language_clause] : [$language_clause]);
}
add_action('pre_get_posts', 'home_filter_queries_by_language', 20);

function home_localize_post_link(string $permalink, WP_Post $post): string {
    if ($post->post_type === 'post' && get_post_meta($post->ID, '_home_language', true) === 'en') {
        return home_url('/en/' . $post->post_name . '/');
    }
    return $permalink;
}
add_filter('post_link', 'home_localize_post_link', 10, 2);

function home_localize_page_link(string $link, int $post_id): string {
    $page = get_post($post_id);
    if ($page instanceof WP_Post && $page->post_type === 'page' && get_post_meta($post_id, '_home_language', true) === 'en') {
        return home_url('/en/' . trim(get_page_uri($post_id), '/') . '/');
    }
    return $link;
}
add_filter('page_link', 'home_localize_page_link', 10, 2);

add_filter('category_link', static function(string $url, int $term_id): string {
    $term = get_term($term_id, 'category');
    if (!$term instanceof WP_Term) { return $url; }
    $key = home_category_key_from_wp_slug($term->slug);
    return $key ? home_category_url($key) : $url;
}, 10, 2);

add_filter('get_the_archive_title', static function(string $title): string {
    if (!is_category()) { return $title; }
    $term = get_queried_object();
    if (!$term instanceof WP_Term) { return $title; }
    $key = home_category_key_from_wp_slug($term->slug);
    if (!$key) { return $title; }
    $definition = home_category_definitions()[$key];
    return $definition['label_' . home_current_language()];
});

function home_primary_menu_location(): string {
    if (home_is_english()) { return has_nav_menu('primary_en') ? 'primary_en' : ''; }
    if (has_nav_menu('primary_es')) { return 'primary_es'; }
    return has_nav_menu('primary') ? 'primary' : '';
}

function home_fallback_menu(): void {
    echo '<ul>';
    foreach (['cleaning','appliances','plumbing','pests'] as $key) {
        $definition = home_category_definitions()[$key];
        printf('<li><a href="%s">%s</a></li>', esc_url(home_category_url($key)), esc_html($definition['label_' . home_current_language()]));
    }
    echo '</ul>';
}

function home_render_primary_menu(string $menu_class = ''): void {
    $location = home_primary_menu_location();
    if ($location) {
        wp_nav_menu(['theme_location'=>$location,'container'=>false,'menu_class'=>$menu_class,'fallback_cb'=>'home_fallback_menu']);
        return;
    }
    home_fallback_menu();
}

function home_language_url(string $target): string {
    $target = $target === 'en' ? 'en' : 'es';
    if (is_singular(['post','page'])) {
        $id = get_queried_object_id();
        $pair = (int) get_post_meta($id, '_home_translation_' . $target, true);
        if ($pair > 0 && get_post_status($pair) === 'publish') { return get_permalink($pair); }
        $current = get_post_meta($id, '_home_language', true) === 'en' ? 'en' : 'es';
        return $current === $target ? get_permalink($id) : home_localized_home_url($target);
    }
    if (is_category()) {
        $term = get_queried_object();
        if ($term instanceof WP_Term) {
            $key = home_category_key_from_wp_slug($term->slug);
            if ($key) { return home_category_url($key, $target); }
        }
    }
    if (is_search()) { return add_query_arg('s', get_search_query(), home_localized_home_url($target)); }
    return home_localized_home_url($target);
}

add_action('wp_head', static function(): void {
    $es = home_language_url('es');
    $en = home_language_url('en');
    echo '<link rel="alternate" hreflang="es" href="' . esc_url($es) . '">' . "\n";
    echo '<link rel="alternate" hreflang="en" href="' . esc_url($en) . '">' . "\n";
    echo '<link rel="alternate" hreflang="x-default" href="' . esc_url($es) . '">' . "\n";
}, 3);
