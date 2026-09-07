<?php get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article>
        <header class="single-hero">
            <div class="narrow">
                <div class="single-breadcrumb"><a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('HOME', 'home'); ?></a> / <?php echo esc_html(home_primary_category_name()); ?></div>
                <h1 class="single-title"><?php the_title(); ?></h1>
                <?php if (has_excerpt()) : ?><p class="single-deck"><?php echo esc_html(get_the_excerpt()); ?></p><?php endif; ?>
                <div class="single-meta">
                    <span><?php echo esc_html(home_primary_category_name()); ?></span>
                    <span>•</span>
                    <span><?php echo esc_html(home_reading_time()); ?></span>
                    <span>•</span>
                    <time datetime="<?php echo esc_attr(get_the_date('c')); ?>"><?php echo esc_html(get_the_date()); ?></time>
                </div>
            </div>
        </header>

        <?php if (has_post_thumbnail()) : ?>
            <div class="single-featured"><?php the_post_thumbnail('full'); ?></div>
        <?php endif; ?>

        <div class="narrow article-content">
            <?php the_content(); ?>
        </div>
    </article>
<?php endwhile; endif; ?>

<?php get_footer(); ?>
