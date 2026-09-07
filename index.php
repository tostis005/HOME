<?php get_header(); ?>

<section class="archive-hero">
    <div class="container">
        <div class="section-kicker"><?php esc_html_e('HOME library', 'home'); ?></div>
        <h1><?php esc_html_e('Practical home guides', 'home'); ?></h1>
        <p class="archive-description"><?php esc_html_e('Clear answers for cleaning, repairs, appliances, pests and the everyday maintenance that keeps a home working.', 'home'); ?></p>
    </div>
</section>

<div class="container content-grid">
    <?php if (have_posts()) : ?>
        <?php while (have_posts()) : the_post(); ?>
            <?php $article_image = home_category_image_url(home_post_category_key()); ?>
            <article class="article-card">
                <a href="<?php the_permalink(); ?>">
                    <div class="article-thumb">
                        <?php if ($article_image) : ?>
                            <img src="<?php echo esc_url($article_image); ?>" alt="<?php echo esc_attr(home_primary_category_name()); ?>" loading="lazy" decoding="async">
                        <?php else : ?>
                            <div class="article-placeholder"></div>
                        <?php endif; ?>
                    </div>
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
            <h1><?php esc_html_e('Nothing here yet.', 'home'); ?></h1>
            <p><?php esc_html_e('Try a search or browse one of the household categories from the homepage.', 'home'); ?></p>
            <a class="text-link" href="<?php echo esc_url(home_localized_home_url()); ?>"><?php esc_html_e('Back to HOME', 'home'); ?> →</a>
        </div>
    <?php endif; ?>
</div>

<?php get_footer(); ?>
