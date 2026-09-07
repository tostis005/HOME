<?php get_header(); ?>

<section class="empty-state">
    <div class="container">
        <div class="section-kicker">404</div>
        <h1><?php esc_html_e('This room is empty.', 'home'); ?></h1>
        <p><?php esc_html_e('The page may have moved. Search HOME or head back to the homepage to find the right guide.', 'home'); ?></p>
        <div class="hero-search" style="margin:28px auto 0"><?php get_search_form(); ?></div>
        <p style="margin-top:28px"><a class="text-link" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Back to HOME', 'home'); ?> →</a></p>
    </div>
</section>

<?php get_footer(); ?>
