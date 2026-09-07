<?php get_header(); ?>

<?php if (have_posts()) : while (have_posts()) : the_post(); ?>
    <article>
        <header class="single-hero">
            <div class="narrow">
                <div class="single-breadcrumb"><a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('HOME', 'home'); ?></a></div>
                <h1 class="single-title"><?php the_title(); ?></h1>
            </div>
        </header>
        <div class="narrow article-content">
            <?php the_content(); ?>
        </div>
    </article>
<?php endwhile; endif; ?>

<?php get_footer(); ?>
