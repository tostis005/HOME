<?php get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <?php
    $category_key = home_post_category_key();
    $category_name = home_primary_category_name();
    $category_url = home_category_url($category_key);
    $category_image = home_category_image_url($category_key);
    $more_category_label = home_is_english()
        ? sprintf('More %s guides', $category_name)
        : sprintf('Más guías sobre %s', $category_name);
    ?>

    <article class="single-premium-article">
        <header class="single-premium-hero">
            <div class="container">
                <div class="single-premium-hero-card">
                    <div class="single-premium-hero-copy">
                        <div class="single-breadcrumb">
                            <a href="<?php echo esc_url(home_localized_home_url()); ?>"><?php esc_html_e('HOME', 'home'); ?></a>
                            <span aria-hidden="true">/</span>
                            <a href="<?php echo esc_url($category_url); ?>"><?php echo esc_html($category_name); ?></a>
                        </div>

                        <a class="single-premium-category" href="<?php echo esc_url($category_url); ?>"><?php echo esc_html($category_name); ?></a>
                        <h1 class="single-title"><?php the_title(); ?></h1>
                        <?php if (has_excerpt()) : ?>
                            <p class="single-deck"><?php echo esc_html(get_the_excerpt()); ?></p>
                        <?php endif; ?>
                        <div class="single-meta single-premium-meta">
                            <span><?php echo esc_html(home_reading_time()); ?></span>
                        </div>
                    </div>

                    <?php if ($category_image) : ?>
                        <figure class="single-premium-hero-media">
                            <img src="<?php echo esc_url($category_image); ?>" alt="<?php echo esc_attr($category_name); ?>" width="1536" height="1024" fetchpriority="high" decoding="async">
                        </figure>
                    <?php endif; ?>
                </div>
            </div>
        </header>

        <div class="container single-premium-reading-layout">
            <div class="narrow article-content single-premium-content">
                <?php the_content(); ?>
            </div>

            <aside class="single-premium-aside">
                <div class="single-premium-aside-card">
                    <span class="home-v2-kicker"><?php echo esc_html($category_name); ?></span>
                    <strong><?php echo esc_html($more_category_label); ?></strong>
                    <a href="<?php echo esc_url($category_url); ?>"><?php esc_html_e('Explore', 'home'); ?> <span aria-hidden="true">→</span></a>
                </div>
                <div class="single-premium-aside-search">
                    <span class="home-v2-kicker"><?php esc_html_e('Search HOME', 'home'); ?></span>
                    <?php get_search_form(); ?>
                </div>
            </aside>
        </div>
    </article>
<?php endwhile; endif; ?>

<?php get_footer(); ?>
