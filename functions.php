<?php
/**
 * HOME theme functions.
 */

if (!defined('ABSPATH')) {
    exit;
}

function home_theme_setup(): void {
    load_theme_textdomain('home', get_template_directory() . '/languages');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo', [
        'height'      => 80,
        'width'       => 240,
        'flex-height' => true,
        'flex-width'  => true,
    ]);
    add_theme_support('html5', ['search-form', 'gallery', 'caption', 'style', 'script']);
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');

    register_nav_menus([
        'primary' => __('Primary navigation', 'home'),
        'footer'  => __('Footer navigation', 'home'),
    ]);
}
add_action('after_setup_theme', 'home_theme_setup');

function home_theme_assets(): void {
    $version = wp_get_theme()->get('Version');
    wp_enqueue_style('home-style', get_stylesheet_uri(), [], $version);
}
add_action('wp_enqueue_scripts', 'home_theme_assets');

function home_excerpt_length(int $length): int {
    return 24;
}
add_filter('excerpt_length', 'home_excerpt_length', 999);

function home_excerpt_more(string $more): string {
    return '…';
}
add_filter('excerpt_more', 'home_excerpt_more');

/**
 * Curated editorial pillars used on the homepage.
 * Slugs intentionally mirror the household taxonomy used by the content set.
 */
function home_category_pillars(): array {
    return [
        'cleaning' => [
            'label'       => __('Cleaning', 'home'),
            'description' => __('Surfaces, rooms, stains and the routines that keep a home feeling good.', 'home'),
            'tone'        => '#dce8df',
        ],
        'kitchen' => [
            'label'       => __('Kitchen', 'home'),
            'description' => __('Everyday kitchen care, messes, odors and practical fixes.', 'home'),
            'tone'        => '#eee0c7',
        ],
        'bathroom' => [
            'label'       => __('Bathroom', 'home'),
            'description' => __('Mold, drains, fixtures and the small problems that need fast answers.', 'home'),
            'tone'        => '#d7e7e8',
        ],
        'laundry' => [
            'label'       => __('Laundry', 'home'),
            'description' => __('Clothes, stains, washers, dryers and better laundry habits.', 'home'),
            'tone'        => '#e4dfef',
        ],
        'appliances' => [
            'label'       => __('Appliances', 'home'),
            'description' => __('Troubleshooting and care for the machines you rely on every day.', 'home'),
            'tone'        => '#dfe3dc',
        ],
        'plumbing' => [
            'label'       => __('Plumbing', 'home'),
            'description' => __('Leaks, clogs, drains and water problems—what to try and when to stop.', 'home'),
            'tone'        => '#cfe1e4',
        ],
        'pests' => [
            'label'       => __('Pests', 'home'),
            'description' => __('Ants, roaches, mice, flies and practical prevention around the home.', 'home'),
            'tone'        => '#e9ddca',
        ],
        'heating-cooling' => [
            'label'       => __('Heating & air', 'home'),
            'description' => __('Comfort, airflow, AC and heating basics for a healthier home.', 'home'),
            'tone'        => '#d6e3d6',
        ],
    ];
}

function home_category_url(string $slug): string {
    $term = get_category_by_slug($slug);
    if ($term instanceof WP_Term) {
        $url = get_category_link($term->term_id);
        if (!is_wp_error($url)) {
            return $url;
        }
    }

    return add_query_arg('s', rawurlencode(str_replace('-', ' ', $slug)), home_url('/'));
}

function home_category_count(string $slug): int {
    $term = get_category_by_slug($slug);
    return $term instanceof WP_Term ? (int) $term->count : 0;
}

/**
 * Small, self-contained category illustrations. No remote image dependency.
 */
function home_category_art(string $slug, string $tone = '#dce8df'): string {
    $common_open = '<svg viewBox="0 0 320 220" role="img" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="220" fill="' . esc_attr($tone) . '"/>';
    $common_close = '</svg>';

    $art = [
        'cleaning' => '<path d="M70 178h180" stroke="#17231d" stroke-opacity=".18"/><rect x="106" y="63" width="82" height="104" rx="18" fill="#fffaf0"/><path d="M132 63v-18h34v18" fill="none" stroke="#516b58" stroke-width="8" stroke-linecap="round"/><path d="M189 91c23 5 38 23 38 47v29h-39" fill="#bd6e52"/><circle cx="148" cy="109" r="20" fill="#a8c9cc"/><path d="M138 108l8 8 14-18" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
        'kitchen' => '<path d="M52 171h216" stroke="#17231d" stroke-opacity=".18"/><rect x="84" y="82" width="152" height="88" rx="10" fill="#fffaf0"/><rect x="102" y="99" width="47" height="52" rx="4" fill="#879c88"/><rect x="160" y="99" width="58" height="52" rx="4" fill="#e7c875"/><path d="M119 81V50h55v31" fill="none" stroke="#17231d" stroke-width="8"/><path d="M184 64c20 0 34 10 34 23" fill="none" stroke="#bd6e52" stroke-width="7" stroke-linecap="round"/>',
        'bathroom' => '<path d="M58 178h204" stroke="#17231d" stroke-opacity=".18"/><path d="M82 102h156v23c0 26-21 47-47 47h-62c-26 0-47-21-47-47v-23z" fill="#fffaf0"/><path d="M104 102V72c0-16 12-29 28-29 14 0 26 10 28 24" fill="none" stroke="#516b58" stroke-width="8" stroke-linecap="round"/><path d="M157 67h35" stroke="#516b58" stroke-width="8" stroke-linecap="round"/><circle cx="201" cy="61" r="9" fill="#a8c9cc"/><circle cx="220" cy="76" r="6" fill="#a8c9cc"/><circle cx="203" cy="85" r="4" fill="#a8c9cc"/>',
        'laundry' => '<path d="M70 180h180" stroke="#17231d" stroke-opacity=".18"/><rect x="93" y="42" width="134" height="136" rx="14" fill="#fffaf0"/><circle cx="160" cy="119" r="42" fill="#a8c9cc"/><circle cx="160" cy="119" r="30" fill="#dbeaed"/><path d="M138 119c11-18 36-20 49-4-8 20-34 31-49 4z" fill="#879c88"/><circle cx="117" cy="66" r="6" fill="#bd6e52"/><circle cx="137" cy="66" r="6" fill="#e7c875"/>',
        'appliances' => '<path d="M57 179h206" stroke="#17231d" stroke-opacity=".18"/><rect x="104" y="36" width="112" height="142" rx="12" fill="#fffaf0"/><path d="M104 87h112" stroke="#17231d" stroke-opacity=".14"/><rect x="121" y="51" width="8" height="24" rx="4" fill="#516b58"/><rect x="121" y="103" width="8" height="36" rx="4" fill="#516b58"/><path d="M74 94h20v78H74z" fill="#bd6e52"/><path d="M64 93h40" stroke="#17231d" stroke-width="7" stroke-linecap="round"/>',
        'plumbing' => '<path d="M54 178h212" stroke="#17231d" stroke-opacity=".18"/><path d="M87 91h71v25h-35v56H98v-56H87z" fill="#fffaf0"/><path d="M158 75h55v52" fill="none" stroke="#516b58" stroke-width="18" stroke-linejoin="round"/><path d="M213 128c0 0 23 26 23 41a23 23 0 01-46 0c0-15 23-41 23-41z" fill="#a8c9cc"/>',
        'pests' => '<path d="M58 180h204" stroke="#17231d" stroke-opacity=".18"/><ellipse cx="160" cy="125" rx="43" ry="53" fill="#bd6e52"/><circle cx="160" cy="75" r="25" fill="#17231d"/><path d="M116 94L83 70M204 94l33-24M116 126H75M204 126h41M119 151l-35 25M201 151l35 25" stroke="#17231d" stroke-width="7" stroke-linecap="round"/><path d="M160 98v79" stroke="#fffaf0" stroke-width="5" stroke-opacity=".75"/><circle cx="151" cy="70" r="3" fill="#fffaf0"/><circle cx="169" cy="70" r="3" fill="#fffaf0"/>',
        'heating-cooling' => '<path d="M60 179h200" stroke="#17231d" stroke-opacity=".18"/><circle cx="160" cy="110" r="48" fill="#fffaf0"/><circle cx="160" cy="110" r="12" fill="#516b58"/><path d="M160 98c-7-23 5-46 25-50 13 23 1 47-25 50zM172 110c23-7 46 5 50 25-23 13-47 1-50-25zM160 122c7 23-5 46-25 50-13-23-1-47 25-50zM148 110c-23 7-46-5-50-25 23-13 47-1 50 25z" fill="#a8c9cc"/><circle cx="245" cy="55" r="26" fill="#e7c875"/>',
    ];

    $body = $art[$slug] ?? $art['cleaning'];
    return $common_open . $body . $common_close;
}

function home_reading_time(?int $post_id = null): string {
    $post_id = $post_id ?: get_the_ID();
    $words = str_word_count(wp_strip_all_tags((string) get_post_field('post_content', $post_id)));
    $minutes = max(1, (int) ceil($words / 220));
    return sprintf(_n('%s min read', '%s min read', $minutes, 'home'), number_format_i18n($minutes));
}

function home_primary_category_name(?int $post_id = null): string {
    $categories = get_the_category($post_id ?: get_the_ID());
    return !empty($categories) ? $categories[0]->name : __('Home guide', 'home');
}

function home_fallback_menu(): void {
    $items = [
        'cleaning'   => __('Cleaning', 'home'),
        'appliances' => __('Appliances', 'home'),
        'plumbing'   => __('Plumbing', 'home'),
        'pests'      => __('Pests', 'home'),
    ];

    echo '<ul>';
    foreach ($items as $slug => $label) {
        printf('<li><a href="%s">%s</a></li>', esc_url(home_category_url($slug)), esc_html($label));
    }
    echo '</ul>';
}
