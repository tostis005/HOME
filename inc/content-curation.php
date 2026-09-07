<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Editorial curation for HOME.
 *
 * HOME uses one primary category per article. The first 70 bilingual articles
 * are explicitly mapped after editorial review so legacy FOOD taxonomy values
 * cannot leak articles into unrelated sections. Pure food-storage/food-safety
 * content is kept in WordPress as draft for possible reuse elsewhere, but is
 * intentionally excluded from the HOME publication.
 */
function home_editorial_category_map(): array {
    return [
        'plumbing' => [1,22,23,36,49,58,61,62,63,64],
        'laundry' => [2,17,18,21,31,41,42,50,52],
        'kitchen' => [3,4,8,15,30],
        'appliances' => [9,19,32,33,51,53,54,57,59,60],
        'heating-cooling' => [10,45,46,65],
        'cleaning' => [7,11,12,26,27,47,48,68],
        'bathroom' => [16,20,28,29],
        'pests' => [5,6,13,14,24,25,38,39,66,67,69,70],
    ];
}

function home_editorial_food_only_numbers(): array {
    return [34,35,37,40,43,44,55,56];
}

function home_editorial_category_for_number(int $number): ?string {
    foreach (home_editorial_category_map() as $category => $numbers) {
        if (in_array($number, $numbers, true)) { return $category; }
    }
    if (in_array($number, home_editorial_food_only_numbers(), true)) { return 'kitchen'; }
    return null;
}

function home_editorial_is_food_only(array $taxonomy, int $article_number = 0): bool {
    if ($article_number > 0 && in_array($article_number, home_editorial_food_only_numbers(), true)) {
        return true;
    }

    $family = strtolower((string) ($taxonomy['food_family'] ?? ''));
    $primary = strtolower((string) ($taxonomy['primary_article_type'] ?? ''));
    $types = array_map('strtolower', array_map('strval', is_array($taxonomy['article_types'] ?? null) ? $taxonomy['article_types'] : []));

    if (in_array($family, ['food-storage','food-safety','food-preparation','recipes','ingredients'], true)) { return true; }
    if ($primary === 'food-safety' && !in_array($family, ['kitchen-appliances','appliances'], true)) { return true; }
    return in_array('food-safety', $types, true) && str_starts_with($family, 'food-');
}

function home_editorial_fallback_category(int $post_id, array $taxonomy): string {
    $family = strtolower((string) ($taxonomy['food_family'] ?? ''));
    $subs = strtolower(implode(' ', array_map('strval', is_array($taxonomy['food_subcategories'] ?? null) ? $taxonomy['food_subcategories'] : [])));
    $types = strtolower(implode(' ', array_map('strval', is_array($taxonomy['article_types'] ?? null) ? $taxonomy['article_types'] : [])));
    $title = strtolower((string) get_the_title($post_id));
    $haystack = $family . ' ' . $subs . ' ' . $types . ' ' . $title;

    $family_map = [
        'bathroom-plumbing' => 'plumbing',
        'laundry-appliances' => 'laundry',
        'laundry-textiles' => 'laundry',
        'pest-prevention' => 'pests',
        'water-quality' => 'plumbing',
        'plumbing' => 'plumbing',
        'hvac' => 'heating-cooling',
        'heating-cooling' => 'heating-cooling',
        'home-energy' => 'heating-cooling',
        'bathroom-cleaning' => 'bathroom',
        'mold-moisture' => 'cleaning',
    ];
    if (isset($family_map[$family])) { return $family_map[$family]; }

    if (preg_match('/\b(washer|washing machine|dryer|laundry|lavadora|secadora|ropa|edred[oó]n|almohada)\b/u', $haystack)) { return 'laundry'; }
    if (preg_match('/\b(ant|cockroach|mouse|mice|termite|bed ?bug|flea|spider|silverfish|fruit fl|drain fl|pest|hormiga|cucaracha|rat[oó]n|termita|chinche|pulga|ara[nñ]a|pececillo|mosca|mosquito|jej[eé]n)\b/u', $haystack)) { return 'pests'; }
    if (preg_match('/\b(air condition|hvac|furnace|thermostat|heating|cooling|aire acondicionado|calefacci[oó]n|climatizaci[oó]n)\b/u', $haystack)) { return 'heating-cooling'; }
    if (preg_match('/\b(drain|plumb|water pressure|water heater|hard water|faucet|clog|desag[uü]e|fontaner|presi[oó]n de agua|agua caliente|grifo|atasc)\b/u', $haystack)) { return 'plumbing'; }
    if (preg_match('/\b(bathroom|toilet cleaning|shower glass|grout|ba[nñ]o|limpiar inodoro|cristal.*ducha|juntas.*azulej)\b/u', $haystack)) { return 'bathroom'; }

    $kitchen_machine = preg_match('/\b(dishwasher|oven|microwave|air fryer|coffee maker|lavavajillas|horno|microondas|freidora|cafetera)\b/u', $haystack);
    $cleaning_intent = preg_match('/\b(clean|cleaning|limpiar|limpieza)\b/u', $haystack);
    if ($kitchen_machine && $cleaning_intent) { return 'kitchen'; }
    if (preg_match('/\b(refrigerator|freezer|dishwasher|oven|microwave|air fryer|coffee maker|appliance|refrigerador|congelador|lavavajillas|horno|microondas|freidora|cafetera|electrodom[eé]stico)\b/u', $haystack)) { return 'appliances'; }
    if (preg_match('/\b(kitchen|cocina)\b/u', $haystack)) { return 'kitchen'; }
    if (preg_match('/\b(clean|mold|mould|carpet|sofa|mattress|window|odor|odour|limpiar|moho|alfombra|sof[aá]|colch[oó]n|ventana|olor)\b/u', $haystack)) { return 'cleaning'; }

    return 'cleaning';
}

function home_apply_editorial_curation(int $post_id, ?array $taxonomy = null): void {
    if (get_post_type($post_id) !== 'post') { return; }
    if ((int) get_post_meta($post_id, '_home_managed_article', true) !== 1) { return; }

    $taxonomy = is_array($taxonomy) ? $taxonomy : get_post_meta($post_id, '_home_taxonomy', true);
    $taxonomy = is_array($taxonomy) ? $taxonomy : [];
    $number = (int) get_post_meta($post_id, '_home_article_number', true);

    $category_key = home_editorial_category_for_number($number) ?: home_editorial_fallback_category($post_id, $taxonomy);
    $definitions = home_category_definitions();
    if (!isset($definitions[$category_key])) { $category_key = 'cleaning'; }

    $term = get_category_by_slug($definitions[$category_key]['wp_slug']);
    if ($term instanceof WP_Term) {
        wp_set_post_categories($post_id, [(int) $term->term_id], false);
        update_post_meta($post_id, '_home_primary_category', $category_key);
    }

    $food_only = home_editorial_is_food_only($taxonomy, $number);
    update_post_meta($post_id, '_home_editorial_scope', $food_only ? 'food-specific' : 'home');
    if ($food_only && get_post_status($post_id) !== 'draft') {
        wp_update_post(['ID' => $post_id, 'post_status' => 'draft']);
    }
}

function home_curate_existing_managed_articles(): void {
    $version = 'home-curation-2026-09-07-v3';
    if (get_option('home_content_curation_version') === $version) { return; }

    $ids = get_posts([
        'post_type' => 'post',
        'post_status' => 'any',
        'posts_per_page' => -1,
        'fields' => 'ids',
        'suppress_filters' => true,
        'meta_key' => '_home_managed_article',
        'meta_value' => 1,
    ]);
    foreach ($ids as $post_id) { home_apply_editorial_curation((int) $post_id); }
    update_option('home_content_curation_version', $version, false);
}
add_action('init', 'home_curate_existing_managed_articles', 40);

function home_recategorize_after_taxonomy_meta($meta_id, $post_id, $meta_key, $meta_value): void {
    if ($meta_key !== '_home_taxonomy' || !is_array($meta_value)) { return; }
    home_apply_editorial_curation((int) $post_id, $meta_value);
}
add_action('added_post_meta', 'home_recategorize_after_taxonomy_meta', 20, 4);
add_action('updated_post_meta', 'home_recategorize_after_taxonomy_meta', 20, 4);
