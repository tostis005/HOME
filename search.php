<?php get_header(); ?>

<section class="archive-hero">
    <div class="container">
        <div class="section-kicker"><?php esc_html_e('Search HOME', 'home'); ?></div>
        <h1><?php printf(esc_html__('Results for “%s”', 'home'), esc_html(get_search_query())); ?></h1>
        <div class="hero-search" style="margin-top:24px"><?php get_search_form(); ?></div>
    </div>
</section>

<div class="container content-grid">
    <?php if (have_posts()) : ?>
        <?php while (have_posts()) : the_post(); ?>
            <article class="article-card">
                <a href="<?php the_permalink(); ?>">
                    <div class="article-thumb"><?php if (has_post_thumbnail()) : the_post_thumbnail('large'); else : ?><div class="article-placeholder"></div><?php endif; ?></div>
                    <div class="article-body">
                        <div class="article-meta"><span><?php echo esc_html(home_primary_category_name()); ?></span><span>•</span><span><?php echo esc_html(home_reading_time()); ?></span></div>
                        <h3><?php the_title(); ?></h3>
                        <p><?php echo esc_html(get_the_excerpt()); ?></p>
                    </div>
                </a>
            </article>
        <?php endwhile; ?>
        <div class="pagination"><?php the_posts_pagination(['mid_size' => 1]); ?></div>
    <?php else : ?>
        <div class="empty-state" style="grid-column:1/-1">
            <h1><?php esc_html_e('No exact match.', 'home'); ?></h1>
            <p><?php esc_html_e('Try fewer words or search for the symptom rather than the appliance or room.', 'home'); ?></p>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
