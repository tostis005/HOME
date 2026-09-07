<?php
function home_category_pillars(): array { return []; }
function home_category_url(string $slug): string { return home_url('/'); }
function home_category_count(string $slug): int { return 0; }
function home_category_art(string $slug, string $tone = '#dce8df'): string { return ''; }
function home_reading_time(?int $post_id = null): string { return '1 min read'; }
function home_primary_category_name(?int $post_id = null): string { return 'Home guide'; }
function home_fallback_menu(): void { echo '<ul></ul>'; }
