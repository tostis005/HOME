<?php
if (!defined('ABSPATH')) { exit; }

/**
 * Imports may legitimately rewrite an existing post from draft to the status
 * stored in JSON. Keep HOME's editorial scope authoritative even when an old
 * food-specific JSON still says publish.
 */
function home_guard_food_only_publication(string $new_status, string $old_status, WP_Post $post): void {
    if ($new_status !== 'publish' || $post->post_type !== 'post') { return; }
    if ((int) get_post_meta($post->ID, '_home_managed_article', true) !== 1) { return; }

    $scope = (string) get_post_meta($post->ID, '_home_editorial_scope', true);
    $number = (int) get_post_meta($post->ID, '_home_article_number', true);
    if ($scope !== 'food-specific' && !in_array($number, home_editorial_food_only_numbers(), true)) { return; }

    remove_action('transition_post_status', 'home_guard_food_only_publication', 20);
    wp_update_post(['ID' => $post->ID, 'post_status' => 'draft']);
    add_action('transition_post_status', 'home_guard_food_only_publication', 20, 3);
}
add_action('transition_post_status', 'home_guard_food_only_publication', 20, 3);
