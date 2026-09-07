<?php
get_header();

$term = get_queried_object();
$category_key = ($term instanceof WP_Term) ? home_category_key_from_wp_slug($term->slug) : null;
$category_key = $category_key ?: 'cleaning';
$definitions = home_category_definitions();
$definition = $definitions[$category_key] ?? null;
$category_name = $definition ? $definition['label_' . home_current_language()] : single_cat_title('', false);
$category_description = $definition ? $definition['description_' . home_current_language()] : category_description();
$category_image = home_category_image_url($category_key);
?>

<section class="category-premium-hero">
    <?php if ($category_image) : ?>
        <figure class="category-premium-hero-media" aria-hidden="true">
            <img src="<?php echo esc_url($category_image); ?>" alt="" width="1536" height="1024" fetchpriority="high" decoding="async">
        </figure>
    <?php endif; ?>
    <div class="category-premium-hero-overlay" aria-hidden="true"></div>
    <div class="container category-premium-hero-inner">
        <div class="category-premium-hero-copy">
            <span class="home-v2-kicker"><?php esc_html_e('Browse HOME', 'home'); ?></span>
            <h1><?php echo esc_html($category_name); ?></h1>
            <?php if ($category_description) : ?>
                <p><?php echo wp_kses_post(wp_strip_all_tags($category_description)); ?></p>
            <?php endif; ?>
        </div>
    </div>
</section>

<section class="category-premium-listing">
    <div class="container">
        <?php if (have_posts()) : ?>
            <div class="content-grid category-premium-grid">
                <?php while (have_posts()) : the_post(); ?>
                    <article class="article-card category-premium-card">
                        <a href="<?php the_permalink(); ?>">
                            <div class="article-thumb category-premium-card-media">
                                <?php if ($category_image) : ?>
                                    <img src="<?php echo esc_url($category_image); ?>" alt="<?php echo esc_attr($category_name); ?>" loading="lazy" decoding="async">
                                <?php else : ?>
                                    <div class="article-placeholder"></div>
                                <?php endif; ?>
                            </div>
                            <div class="article-body">
                                <div class="article-meta">
                                    <span><?php echo esc_html($category_name); ?></span>
                                    <span>•</span>
                                    <span><?php echo esc_html(home_reading_time()); ?></span>
                                </div>
                                <h3><?php the_title(); ?></h3>
                                <p><?php echo esc_html(get_the_excerpt()); ?></p>
                            </div>
                        </a>
                    </article>
                <?php endwhile; ?>
                <div class="pagination"><?php the_posts_pagination(['mid_size' => 1]); ?></div>
            </div>
        <?php else : ?>
            <div class="empty-state">
                <h1><?php esc_html_e('No guides yet.', 'home'); ?></h1>
                <p><?php esc_html_e('New household guides will appear here as they are published.', 'home'); ?></p>
            </div>
        <?php endif; ?>
    </div>
</section>

<?php get_footer(); ?>
