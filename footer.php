</main>
<footer class="site-footer home-v2-footer">
    <div class="container">
        <div class="home-v2-footer-main">
            <div class="home-v2-footer-brand-block">
                <a class="brand home-v2-brand home-v2-footer-brand" href="<?php echo esc_url(home_url('/')); ?>">
                    <span class="home-v2-brand-icon" aria-hidden="true">
                        <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" focusable="false"><path d="M8 30.5 32 10l24 20.5v23A4.5 4.5 0 0 1 51.5 58h-39A4.5 4.5 0 0 1 8 53.5v-23Z" fill="currentColor"/><path d="M20 44c8-1 13-6 15-15-9 1-14 6-15 15Zm25 2c-7-1-11-5-13-12 8 1 12 5 13 12Z" fill="#fbf8f1"/><path d="M27 48c2-9 6-15 13-19" fill="none" stroke="#fbf8f1" stroke-width="2.6" stroke-linecap="round"/></svg>
                    </span>
                    <span class="home-v2-brand-copy">
                        <span class="home-v2-brand-word">HOME</span>
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
            <span>&copy; <?php echo esc_html(wp_date('Y')); ?> HOME</span>
            <span><?php esc_html_e('Useful answers. Calm explanations. Better homes.', 'home'); ?></span>
        </div>
    </div>
</footer>
</div>
<?php wp_footer(); ?>
</body>
</html>
