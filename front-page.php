<?php
get_header();

$latest_posts = get_posts([
    'post_type'           => 'post',
    'post_status'         => 'publish',
    'numberposts'         => 6,
    'ignore_sticky_posts' => true,
]);

$month = (int) wp_date('n');
if (in_array($month, [12, 1, 2], true)) {
    $season_label = __('Winter at home', 'home');
    $season_items = [
        ['heating', __('Keep heating working efficiently', 'home')],
        ['condensation mold', __('Stay ahead of condensation and mold', 'home')],
        ['frozen pipes', __('Protect plumbing in cold weather', 'home')],
    ];
} elseif (in_array($month, [3, 4, 5], true)) {
    $season_label = __('Spring reset', 'home');
    $season_items = [
        ['spring cleaning', __('Build a room-by-room cleaning reset', 'home')],
        ['pests prevent', __('Close the door on seasonal pests', 'home')],
        ['air conditioner maintenance', __('Get cooling ready before hot days', 'home')],
    ];
} elseif (in_array($month, [6, 7, 8], true)) {
    $season_label = __('Summer at home', 'home');
    $season_items = [
        ['air conditioner cooling', __('Keep rooms cooler and airflow moving', 'home')],
        ['fruit flies ants', __('Handle warm-weather kitchen pests', 'home')],
        ['refrigerator temperature', __('Help the fridge through hotter days', 'home')],
    ];
} else {
    $season_label = __('Fall home reset', 'home');
    $season_items = [
        ['heating maintenance', __('Check heating before colder weather', 'home')],
        ['dryer vent', __('Clean lint and dryer vent buildup', 'home')],
        ['mice prevent', __('Seal common pest entry points', 'home')],
    ];
}
?>

<section class="home-v2-hero">
    <div class="container home-v2-hero-grid">
        <div class="home-v2-hero-copy">
            <span class="home-v2-eyebrow"><?php esc_html_e('Practical advice. Real solutions. A brighter home.', 'home'); ?></span>
            <h1><?php esc_html_e('Home advice', 'home'); ?><br><em><?php esc_html_e('for real life.', 'home'); ?></em></h1>
            <p><?php esc_html_e('Simple, trustworthy guidance for cleaning, fixing, maintaining and understanding the place you live — without turning every small problem into a project.', 'home'); ?></p>
            <div class="home-v2-hero-actions">
                <a class="home-v2-primary-button" href="#home-categories"><?php esc_html_e('Explore all categories', 'home'); ?><span aria-hidden="true">→</span></a>
                <a class="home-v2-text-button" href="#latest-guides"><?php esc_html_e('See latest guides', 'home'); ?></a>
            </div>
            <div class="home-v2-hero-search">
                <?php get_search_form(); ?>
            </div>
        </div>

        <div class="home-v2-room" aria-hidden="true">
            <div class="home-v2-window"><span></span></div>
            <div class="home-v2-room-plant"><i></i><i></i><i></i><i></i><i></i><b></b></div>
            <div class="home-v2-sofa">
                <span class="home-v2-cushion one"></span>
                <span class="home-v2-cushion two"></span>
                <span class="home-v2-throw"></span>
            </div>
            <div class="home-v2-table">
                <span class="home-v2-books"></span>
                <span class="home-v2-mug"></span>
                <span class="home-v2-vase"><i></i><i></i><i></i></span>
            </div>
            <span class="home-v2-hand-note"><?php esc_html_e('Good homes, happier days.', 'home'); ?></span>
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
    <div class="container home-v2-category-panel">
        <div class="home-v2-section-head">
            <div>
                <span class="home-v2-kicker"><?php esc_html_e('Explore the house', 'home'); ?></span>
                <h2><?php esc_html_e('Practical help for every corner of home.', 'home'); ?></h2>
            </div>
            <p><?php esc_html_e('Choose the area that needs attention. Each category brings together fixes, maintenance, cleaning and prevention.', 'home'); ?></p>
        </div>

        <div class="home-v2-category-grid">
            <?php foreach (home_category_pillars() as $slug => $pillar) : ?>
                <a class="home-v2-category-card" href="<?php echo esc_url(home_category_url($slug)); ?>">
                    <div class="home-v2-category-art"><?php echo home_category_art($slug, $pillar['tone']); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></div>
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

<section class="home-v2-featured" id="latest-guides">
    <div class="container">
        <div class="home-v2-section-head compact">
            <div>
                <span class="home-v2-kicker"><?php esc_html_e('Fresh from HOME', 'home'); ?></span>
                <h2><?php esc_html_e('Featured guides & timely fixes.', 'home'); ?></h2>
            </div>
        </div>

        <div class="home-v2-featured-layout">
            <div class="home-v2-featured-main">
                <?php if (!empty($latest_posts)) : ?>
                    <?php foreach (array_slice($latest_posts, 0, 3) as $post) : setup_postdata($post); ?>
                        <article class="home-v2-article-card">
                            <a href="<?php the_permalink(); ?>">
                                <div class="home-v2-article-media">
                                    <?php if (has_post_thumbnail()) : ?>
                                        <?php the_post_thumbnail('large'); ?>
                                    <?php else : ?>
                                        <div class="home-v2-article-placeholder"><?php echo home_category_art(sanitize_title(home_primary_category_name()), '#e7e1d5'); // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped ?></div>
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
                <?php else : ?>
                    <div class="home-v2-empty"><?php esc_html_e('Published WordPress articles will appear here automatically.', 'home'); ?></div>
                <?php endif; ?>
            </div>

            <aside class="home-v2-seasonal">
                <span class="home-v2-kicker"><?php echo esc_html($season_label); ?></span>
                <h3><?php esc_html_e('A few useful things to check now.', 'home'); ?></h3>
                <div class="home-v2-seasonal-list">
                    <?php foreach ($season_items as $index => $item) : ?>
                        <a href="<?php echo esc_url(add_query_arg('s', $item[0], home_url('/'))); ?>">
                            <span class="home-v2-seasonal-number">0<?php echo esc_html((string) ($index + 1)); ?></span>
                            <strong><?php echo esc_html($item[1]); ?></strong>
                            <span aria-hidden="true">→</span>
                        </a>
                    <?php endforeach; ?>
                </div>
                <?php if (count($latest_posts) > 3) : ?>
                    <div class="home-v2-more-guides">
                        <span><?php esc_html_e('Also new', 'home'); ?></span>
                        <?php foreach (array_slice($latest_posts, 3, 3) as $post) : ?>
                            <a href="<?php echo esc_url(get_permalink($post)); ?>"><?php echo esc_html(get_the_title($post)); ?></a>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </aside>
        </div>
    </div>
</section>

<section class="home-v2-cta">
    <div class="container">
        <div class="home-v2-cta-box">
            <div class="home-v2-cta-leaves" aria-hidden="true"><i></i><i></i><i></i></div>
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
