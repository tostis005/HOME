</main>
<footer class="site-footer home-v2-footer">
    <div class="container">
        <div class="home-v2-footer-main">
            <div class="home-v2-footer-brand-block">
                <a class="brand home-v2-brand home-v2-footer-brand domstiq-brand" href="<?php echo esc_url(home_url('/')); ?>">
                    <span class="home-v2-brand-copy domstiq-brand-copy">
                        <img class="domstiq-logo-image" src="<?php echo esc_url(home_brand_asset_url('domstiq-logo.png')); ?>" alt="DomstIQ" width="600" height="150" loading="lazy" decoding="async">
                        <span class="home-v2-brand-tagline"><?php esc_html_e('A calmer home starts with a clear answer', 'home'); ?></span>
                    </span>
                </a>
                <p class="footer-copy home-v2-footer-copy"><?php esc_html_e('Clear, practical guidance for the everyday problems that come with having a home.', 'home'); ?></p>
            </div>
            <div>
                <p class="footer-title"><?php esc_html_e('Explore', 'home'); ?></p>
                <ul class="footer-links">
                    <?php foreach (array_slice(home_category_pillars(), 0, 4, true) as $slug => $pillar) : ?>
                        <li><a href="<?php echo esc_url(home_category_url($slug)); ?>"><?php echo esc_html($pillar['label']); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <div>
                <p class="footer-title"><?php esc_html_e('Around the house', 'home'); ?></p>
                <ul class="footer-links">
                    <?php foreach (array_slice(home_category_pillars(), 4, 4, true) as $slug => $pillar) : ?>
                        <li><a href="<?php echo esc_url(home_category_url($slug)); ?>"><?php echo esc_html($pillar['label']); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
        <div class="footer-bottom home-v2-footer-bottom">
            <span>&copy; <?php echo esc_html(wp_date('Y')); ?> DomstIQ</span>
            <span><?php esc_html_e('Useful answers. Calm explanations. Better homes.', 'home'); ?></span>
        </div>
    </div>
</footer>
</div>
<?php wp_footer(); ?>
</body>
</html>
