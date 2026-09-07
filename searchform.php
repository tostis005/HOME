<?php
/**
 * Search form.
 */
?>
<form role="search" method="get" class="search-form" action="<?php echo esc_url(home_url('/')); ?>">
    <input id="home-search-field" type="search" name="s" value="<?php echo esc_attr(get_search_query()); ?>" placeholder="<?php esc_attr_e('What needs fixing, cleaning or checking?', 'home'); ?>" aria-label="<?php esc_attr_e('Search HOME', 'home'); ?>">
    <button type="submit"><?php esc_html_e('Search', 'home'); ?></button>
</form>
