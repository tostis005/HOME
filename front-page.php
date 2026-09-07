<?php
get_header();

$latest_posts = get_posts([
    'post_type'           => 'post',
    'post_status'         => 'publish',
    'numberposts'         => 6,
    'ignore_sticky_posts' => true,
]);
?>

<section class="home-v2-hero home-premium-hero">
    <div class="container home-premium-hero-wrap">
        <div class="home-premium-hero-card">
            <figure class="home-premium-hero-media" aria-hidden="true">
                <img
                    src="<?php echo esc_url(home_hero_image_url()); ?>"
                    alt=""
                    width="1800"
                    height="1200"
                    fetchpriority="high"
                    decoding="async"
                >
            </figure>
            <div class="home-v2-hero-copy home-premium-hero-copy">
                <span class="home-v2-eyebrow"><?php esc_html_e('Practical advice. Real solutions. A brighter home.', 'home'); ?></span>
                <h1><?php esc_html_e('Home advice', 'home'); ?><br><em><?php esc_html_e('for real life.', 'home'); ?></em></h1>
                <p><?php esc_html_e('Simple, trustworthy guidance for cleaning, fixing, maintaining and understanding the place you live — without turning every small problem into a project.', 'home'); ?></p>
                <div class="home-v2-hero-actions">
                    <a class="home-v2-primary-button" href="#home-categories"><?php esc_html_e('Explore all categories', 'home'); ?><span aria-hidden="true">→</span></a>
                    <a class="home-v2-text-button" href="#latest-guides"><?php esc_html_e('See latest guides', 'home'); ?></a>
                </div>
                <div class="home-v2-hero-search"><?php get_search_form(); ?></div>
            </div>
        </div>
    </div>
</section>

<section class="home-v2-values" aria-label="<?php esc_attr_e('What HOME stands for', 'home'); ?>">
    <div class="container home-v2-values-grid">
        <div class="home-v2-value">
            <span class="home-v2-value-icon" aria-hidden="true">⌂</span>
            <div><strong><?php esc_html_e('Trusted advice', 'home'); ?></strong><small><?php esc_html_e('Practical, reliable and easy to follow.', 'home'); ?></small></div>
        </div>
        <div class="home-v2-value">
            <span class="home-v2-value-icon leaf" aria-hidden="true">✦</span>
            <div><strong><?php esc_html_e('A healthier home', 'home'); ?></strong><small><?php esc_html_e('Small changes that make everyday life better.', 'home'); ?></small></div>
        </div>
        <div class="home-v2-value">
            <span class="home-v2-value-icon warm" aria-hidden="true">♡</span>
            <div><strong><?php esc_html_e('Clear next steps', 'home'); ?></strong><small><?php esc_html_e('Know what to try, what to avoid and when to call.', 'home'); ?></small></div>
        </div>
    </div>
</section>

<section class="home-v2-category-section" id="home-categories">
    <div class="container home-v2-category-panel home-premium-category-panel">
        <div class="home-v2-section-head">
            <div>
                <span class="home-v2-kicker"><?php esc_html_e('Explore the house', 'home'); ?></span>
                <h2><?php esc_html_e('Practical help for every corner of home.', 'home'); ?></h2>
            </div>
            <p><?php esc_html_e('Choose the area that needs attention. Each category brings together fixes, maintenance, cleaning and prevention.', 'home'); ?></p>
        </div>

        <div class="home-v2-category-grid home-premium-category-grid">
            <?php foreach (home_category_pillars() as $slug => $pillar) : ?>
                <?php $category_image = home_category_image_url($slug); ?>
                <a class="home-v2-category-card home-premium-category-card" href="<?php echo esc_url(home_category_url($slug)); ?>">
                    <div class="home-v2-category-art home-premium-category-art" style="background-color:<?php echo esc_attr($pillar['tone']); ?>">
                        <?php if ($category_image) : ?>
                            <img src="<?php echo esc_url($category_image); ?>" alt="<?php echo esc_attr($pillar['label']); ?>" loading="lazy" decoding="async">
                        <?php else : ?>
                            <?php echo home_category_art($slug, $pillar['tone']); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?>
                        <?php endif; ?>
                    </div>
                    <div class="home-v2-category-card-copy">
                        <div>
                            <h3><?php echo esc_html($pillar['label']); ?></h3>
                            <p><?php echo esc_html($pillar['description']); ?></p>
                        </div>
                        <span class="home-v2-category-arrow" aria-hidden="true">→</span>
                    </div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<section class="home-v2-featured home-premium-featured" id="latest-guides">
    <div class="container">
        <div class="home-v2-section-head compact">
            <div>
                <span class="home-v2-kicker"><?php esc_html_e('Fresh from HOME', 'home'); ?></span>
                <h2><?php esc_html_e('Featured guides & practical fixes.', 'home'); ?></h2>
            </div>
        </div>

        <?php if (!empty($latest_posts)) : ?>
            <div class="home-v2-featured-main home-premium-featured-grid">
                <?php foreach (array_slice($latest_posts, 0, 3) as $post) : setup_postdata($post); ?>
                    <?php $article_image = home_category_image_url(home_post_category_key()); ?>
                    <article class="home-v2-article-card home-premium-article-card">
                        <a href="<?php the_permalink(); ?>">
                            <div class="home-v2-article-media">
                                <?php if (has_post_thumbnail()) : ?>
                                    <?php the_post_thumbnail('large'); ?>
                                <?php elseif ($article_image) : ?>
                                    <img src="<?php echo esc_url($article_image); ?>" alt="" loading="lazy" decoding="async">
                                <?php else : ?>
                                    <div class="home-v2-article-placeholder"><?php echo home_category_art(home_post_category_key(), '#e7e1d5'); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></div>
                                <?php endif; ?>
                            </div>
                            <div class="home-v2-article-copy">
                                <span class="home-v2-article-category"><?php echo esc_html(home_primary_category_name()); ?></span>
                                <h3><?php the_title(); ?></h3>
                                <p><?php echo esc_html(get_the_excerpt()); ?></p>
                                <span class="home-v2-read-more"><?php esc_html_e('Read guide', 'home'); ?> <span aria-hidden="true">→</span></span>
                            </div>
                        </a>
                    </article>
                <?php endforeach; wp_reset_postdata(); ?>
            </div>

            <?php if (count($latest_posts) > 3) : ?>
                <div class="home-premium-more-guides">
                    <div class="home-premium-more-guides-head">
                        <span class="home-v2-kicker"><?php esc_html_e('More from HOME', 'home'); ?></span>
                    </div>
                    <div class="home-premium-more-guides-grid">
                        <?php foreach (array_slice($latest_posts, 3, 3) as $post) : ?>
                            <a href="<?php echo esc_url(get_permalink($post)); ?>">
                                <span><?php echo esc_html(home_primary_category_name($post->ID)); ?></span>
                                <strong><?php echo esc_html(get_the_title($post)); ?></strong>
                                <i aria-hidden="true">→</i>
                            </a>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>
        <?php else : ?>
            <div class="home-v2-empty"><?php esc_html_e('Published WordPress articles will appear here automatically.', 'home'); ?></div>
        <?php endif; ?>
    </div>
</section>

<section class="home-v2-cta home-premium-cta">
    <div class="container">
        <div class="home-v2-cta-box home-premium-cta-box">
            <div>
                <span class="home-v2-kicker"><?php esc_html_e('Make home feel easier', 'home'); ?></span>
                <h2><?php esc_html_e('One clear answer can save a lot of guessing.', 'home'); ?></h2>
                <p><?php esc_html_e('Search the HOME library whenever something leaks, smells, stops working, stains, clogs or simply needs a better routine.', 'home'); ?></p>
            </div>
            <div class="home-v2-cta-search"><?php get_search_form(); ?></div>
        </div>
    </div>
</section>

<?php get_footer(); ?>
