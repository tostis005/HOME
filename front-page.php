<?php get_header(); ?>

<section class="hero">
    <div class="container hero-grid">
        <div>
            <span class="eyebrow"><?php esc_html_e('Practical help for real homes', 'home'); ?></span>
            <h1><?php esc_html_e('Know what to do,', 'home'); ?> <em><?php esc_html_e('at home.', 'home'); ?></em></h1>
            <p class="hero-copy"><?php esc_html_e('From a clogged toilet to a noisy appliance, HOME turns everyday household problems into clear next steps you can actually use.', 'home'); ?></p>
            <div class="hero-search">
                <?php get_search_form(); ?>
                <div class="hero-note"><?php esc_html_e('Try “washing machine smells”, “ants in kitchen” or “toilet won’t drain”.', 'home'); ?></div>
            </div>
        </div>
        <div class="hero-house" aria-hidden="true">
            <span class="hero-sun"></span>
            <div class="hero-plant"><span></span><span></span><span></span></div>
            <span class="hero-label"><?php esc_html_e('Made for everyday life', 'home'); ?></span>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-head">
            <div>
                <div class="section-kicker"><?php esc_html_e('Browse by area', 'home'); ?></div>
                <h2 class="section-title"><?php esc_html_e('Everything has a place.', 'home'); ?></h2>
            </div>
            <p class="section-intro"><?php esc_html_e('Start with the part of your home that needs attention. Each section brings together fixes, maintenance and prevention.', 'home'); ?></p>
        </div>

        <div class="category-grid">
            <?php foreach (home_category_pillars() as $slug => $pillar) : ?>
                <a class="category-card" href="<?php echo esc_url(home_category_url($slug)); ?>">
                    <div class="category-visual"><?php echo home_category_art($slug, $pillar['tone']); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></div>
                    <div class="category-copy">
                        <div class="category-name">
                            <span><?php echo esc_html($pillar['label']); ?></span>
                            <span aria-hidden="true">↗</span>
                        </div>
                        <p class="category-description"><?php echo esc_html($pillar['description']); ?></p>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="section">
    <div class="container">
        <div class="section-head">
            <div>
                <div class="section-kicker"><?php esc_html_e('A simpler way to solve things', 'home'); ?></div>
                <h2 class="section-title"><?php esc_html_e('Start with the problem.', 'home'); ?></h2>
            </div>
        </div>
        <div class="problem-strip">
            <a class="problem-card" href="<?php echo esc_url(add_query_arg('s', 'not working', home_url('/'))); ?>">
                <span class="problem-number">01</span>
                <div><h3><?php esc_html_e('Something stopped working', 'home'); ?></h3><p><?php esc_html_e('Troubleshoot symptoms before replacing parts or calling for service.', 'home'); ?></p></div>
            </a>
            <a class="problem-card" href="<?php echo esc_url(add_query_arg('s', 'how to clean', home_url('/'))); ?>">
                <span class="problem-number">02</span>
                <div><h3><?php esc_html_e('Something needs cleaning', 'home'); ?></h3><p><?php esc_html_e('Use the right method for the material, stain and room.', 'home'); ?></p></div>
            </a>
            <a class="problem-card" href="<?php echo esc_url(add_query_arg('s', 'prevent', home_url('/'))); ?>">
                <span class="problem-number">03</span>
                <div><h3><?php esc_html_e('Something keeps coming back', 'home'); ?></h3><p><?php esc_html_e('Find the cause and build a practical prevention routine.', 'home'); ?></p></div>
            </a>
        </div>
    </div>
</section>

<?php
$latest = new WP_Query([
    'post_type'           => 'post',
    'post_status'         => 'publish',
    'posts_per_page'      => 6,
    'ignore_sticky_posts' => true,
]);
?>
<section class="section latest-section">
    <div class="container">
        <div class="section-head">
            <div>
                <div class="section-kicker"><?php esc_html_e('Fresh from HOME', 'home'); ?></div>
                <h2 class="section-title"><?php esc_html_e('Useful answers, recently added.', 'home'); ?></h2>
            </div>
            <p class="section-intro"><?php esc_html_e('Practical guides written to help you understand the issue, act safely and know when professional help makes more sense.', 'home'); ?></p>
        </div>

        <?php if ($latest->have_posts()) : ?>
            <div class="latest-grid">
                <?php while ($latest->have_posts()) : $latest->the_post(); ?>
                    <article class="article-card">
                        <a href="<?php the_permalink(); ?>" aria-label="<?php echo esc_attr(get_the_title()); ?>">
                            <div class="article-thumb">
                                <?php if (has_post_thumbnail()) : the_post_thumbnail('large'); else : ?><div class="article-placeholder"></div><?php endif; ?>
                            </div>
                            <div class="article-body">
                                <div class="article-meta"><span><?php echo esc_html(home_primary_category_name()); ?></span><span>•</span><span><?php echo esc_html(home_reading_time()); ?></span></div>
                                <h3><?php the_title(); ?></h3>
                                <p><?php echo esc_html(get_the_excerpt()); ?></p>
                            </div>
                        </a>
                    </article>
                <?php endwhile; ?>
            </div>
        <?php else : ?>
            <div class="problem-card"><h3><?php esc_html_e('The library is being prepared.', 'home'); ?></h3><p><?php esc_html_e('Your first published WordPress articles will appear here automatically.', 'home'); ?></p></div>
        <?php endif; wp_reset_postdata(); ?>
    </div>
</section>

<section class="home-promise">
    <div class="container">
        <div class="promise-box">
            <div class="promise-stamp"><?php esc_html_e('Useful over complicated', 'home'); ?></div>
            <div class="promise-copy">
                <div class="section-kicker"><?php esc_html_e('The HOME standard', 'home'); ?></div>
                <h2><?php esc_html_e('Advice should make the next step obvious.', 'home'); ?></h2>
                <p><?php esc_html_e('HOME is built around practical household questions: what to do first, what to avoid, what you can fix yourself and when the safer answer is to call a professional.', 'home'); ?></p>
            </div>
        </div>
    </div>
</section>

<?php get_footer(); ?>
