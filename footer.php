</main>
<footer class="site-footer">
    <div class="container">
        <div class="footer-grid">
            <div>
                <div class="footer-brand">HOME.</div>
                <p class="footer-copy"><?php esc_html_e('Clear, practical guidance for the everyday problems that come with having a home.', 'home'); ?></p>
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
                <p class="footer-title"><?php esc_html_e('More at home', 'home'); ?></p>
                <ul class="footer-links">
                    <?php foreach (array_slice(home_category_pillars(), 4, 4, true) as $slug => $pillar) : ?>
                        <li><a href="<?php echo esc_url(home_category_url($slug)); ?>"><?php echo esc_html($pillar['label']); ?></a></li>
                    <?php endforeach; ?>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <span>&copy; <?php echo esc_html(wp_date('Y')); ?> HOME</span>
            <span><?php esc_html_e('Useful answers. Calm explanations. Better homes.', 'home'); ?></span>
        </div>
    </div>
</footer>
</div>
<?php wp_footer(); ?>
</body>
</html>
