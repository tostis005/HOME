<?php
/** Idempotent JSON importer for HOME articles. */
if ( PHP_SAPI !== 'cli' ) { fwrite( STDERR, "CLI only.\n" ); exit( 1 ); }
if ( $argc < 3 ) { fwrite( STDERR, "Usage: php import-articles.php <wp-root> <articles-root> [options]\n" ); exit( 1 ); }
$wp_root = rtrim( $argv[1], '/' );
$articles_root = rtrim( $argv[2], '/' );
$options = array( 'language'=>'all', 'from'=>1, 'to'=>PHP_INT_MAX, 'status'=>'json', 'force'=>'0', 'successful_sha'=>'', 'state'=>'import' );
foreach ( array_slice( $argv, 3 ) as $arg ) {
    if ( 0 !== strpos( $arg, '--' ) || false === strpos( $arg, '=' ) ) { continue; }
    list( $key, $value ) = explode( '=', substr( $arg, 2 ), 2 );
    $key = str_replace( '-', '_', $key );
    if ( array_key_exists( $key, $options ) ) { $options[ $key ] = $value; }
}
$options['from'] = max( 1, (int) $options['from'] );
$options['to'] = max( $options['from'], (int) $options['to'] );
$options['force'] = in_array( strtolower( (string) $options['force'] ), array( '1','true','yes','on' ), true );
if ( ! in_array( $options['language'], array( 'es','en','all' ), true ) ) { throw new RuntimeException( 'Invalid language option.' ); }
if ( ! in_array( $options['status'], array( 'publish','draft','review','json' ), true ) ) { throw new RuntimeException( 'Invalid status option.' ); }
if ( ! in_array( $options['state'], array( 'import','read' ), true ) ) { throw new RuntimeException( 'Invalid state option.' ); }
if ( '' !== $options['successful_sha'] && ! preg_match( '/^[0-9a-f]{40}$/i', (string) $options['successful_sha'] ) ) { throw new RuntimeException( 'Invalid successful SHA.' ); }
$wp_load = $wp_root . '/wp-load.php';
if ( ! is_readable( $wp_load ) ) { fwrite( STDERR, "Cannot read {$wp_load}\n" ); exit( 1 ); }
require_once $wp_load;
if ( 'read' === $options['state'] ) { echo 'IMPORT_STATE_SHA=' . (string) get_option( 'home_last_successful_import_sha', '' ) . "\n"; exit( 0 ); }
if ( ! is_dir( $articles_root ) ) { fwrite( STDERR, "Articles directory not found: {$articles_root}\n" ); exit( 1 ); }

function home_import_required_string( $data, $key, $file ) {
    if ( ! isset( $data[$key] ) || ! is_string( $data[$key] ) || '' === trim( $data[$key] ) ) { throw new RuntimeException( "Missing or invalid {$key} in {$file}" ); }
    return trim( $data[$key] );
}
function home_import_status( $json, $override ) {
    if ( 'json' !== $override ) { return 'review' === $override ? 'draft' : $override; }
    return 'publish' === $json ? 'publish' : 'draft';
}
function home_import_find_existing( $source_id, $slug ) {
    $ids = get_posts( array( 'post_type'=>'post','post_status'=>'any','posts_per_page'=>1,'fields'=>'ids','meta_key'=>'_home_source_id','meta_value'=>$source_id ) );
    if ( ! empty( $ids ) ) { return get_post( (int) $ids[0] ); }
    $post = get_page_by_path( $slug, OBJECT, 'post' );
    return $post instanceof WP_Post ? $post : null;
}
function home_import_sources_html( $sources, $language ) {
    if ( empty( $sources ) || ! is_array( $sources ) ) { return ''; }
    $items = '';
    foreach ( $sources as $source ) {
        if ( empty( $source['name'] ) || empty( $source['url'] ) ) { continue; }
        $items .= '<li><a href="' . esc_url( (string) $source['url'] ) . '" rel="noopener noreferrer">' . esc_html( (string) $source['name'] ) . '</a>' . ( ! empty( $source['note'] ) ? ' — ' . esc_html( (string) $source['note'] ) : '' ) . '</li>';
    }
    return '' === $items ? '' : '<h2>' . ( 'en' === $language ? 'Sources' : 'Fuentes' ) . '</h2><ul class="home-article-sources">' . $items . '</ul>';
}
function home_import_category_definitions() {
    return array( 'cleaning'=>'Cleaning','kitchen'=>'Kitchen','bathroom'=>'Bathroom','laundry'=>'Laundry','appliances'=>'Appliances','plumbing'=>'Plumbing','pests'=>'Pests','heating-cooling'=>'Heating & air' );
}
function home_import_ensure_categories() {
    $ids = array();
    foreach ( home_import_category_definitions() as $slug=>$name ) {
        $term = get_category_by_slug( $slug );
        if ( ! $term instanceof WP_Term ) {
            $created = wp_insert_term( $name, 'category', array( 'slug'=>$slug ) );
            if ( is_wp_error( $created ) ) { throw new RuntimeException( $created->get_error_message() ); }
            $term = get_term( (int) $created['term_id'], 'category' );
        }
        if ( $term instanceof WP_Term ) { $ids[$slug] = (int) $term->term_id; }
    }
    return $ids;
}
/**
 * HOME has eight mutually-exclusive editorial categories. The JSON taxonomy is
 * richer than WordPress categories, but every public article must resolve to
 * exactly one primary HOME category. Secondary concepts remain in _home_taxonomy.
 */
function home_import_category_slugs( $taxonomy ) {
    $family = isset( $taxonomy['food_family'] ) ? strtolower( trim( (string) $taxonomy['food_family'] ) ) : '';
    $subs = ! empty( $taxonomy['food_subcategories'] ) && is_array( $taxonomy['food_subcategories'] ) ? implode( ' ', $taxonomy['food_subcategories'] ) : '';
    $types = ! empty( $taxonomy['article_types'] ) && is_array( $taxonomy['article_types'] ) ? implode( ' ', $taxonomy['article_types'] ) : '';
    $hay = strtolower( $family . ' ' . $subs . ' ' . $types );

    $direct = array(
        'cleaning'=>'cleaning',
        'kitchen'=>'kitchen',
        'bathroom'=>'bathroom',
        'laundry'=>'laundry',
        'appliances'=>'appliances',
        'plumbing'=>'plumbing',
        'pests'=>'pests',
        'pest-prevention'=>'pests',
        'heating-cooling'=>'heating-cooling',
        'hvac'=>'heating-cooling',
        'laundry-appliances'=>'laundry',
        'laundry-textiles'=>'laundry',
        'food-safety'=>'kitchen',
        'water-quality'=>'plumbing',
    );
    if ( isset( $direct[$family] ) ) { return array( $direct[$family] ); }

    if ( 'bathroom-plumbing' === $family ) {
        foreach ( array('plumb','pipe','leak','clog','drain','faucet','water-pressure','water-heater','hard-water') as $needle ) {
            if ( false !== strpos( $hay, $needle ) ) { return array('plumbing'); }
        }
        return array('bathroom');
    }

    if ( 'kitchen-appliances' === $family ) {
        foreach ( array('dishwasher','refrigerator','fridge','freezer','oven','microwave','air-fryer','coffee-maker','appliance') as $needle ) {
            if ( false !== strpos( $hay, $needle ) ) { return array('appliances'); }
        }
        return array('kitchen');
    }

    $rules = array(
        'pests'=>array('pest','ant','cockroach','roach','mouse','mice','bedbug','bed-bug','termite','flea','spider','silverfish','fly','gnat','mosquito'),
        'heating-cooling'=>array('hvac','air-condition','heating','cooling','furnace','thermostat','ventilation'),
        'laundry'=>array('laundry','washer','washing-machine','dryer','clothing','textile','pillow','bedding','duvet'),
        'plumbing'=>array('plumb','pipe','leak','clog','drain','faucet','water-pressure','water-heater','hard-water','water-quality'),
        'bathroom'=>array('bathroom','toilet','shower','grout','bathtub'),
        'appliances'=>array('appliance','dishwasher','refrigerator','fridge','freezer','oven','microwave','air-fryer','coffee-maker'),
        'kitchen'=>array('kitchen','food-safety','leftover','pasta','meat','chicken','countertop'),
        'cleaning'=>array('clean','mold','mould','carpet','sofa','mattress','window','odor','odour','stain'),
    );
    foreach ( $rules as $slug=>$needles ) {
        foreach ( $needles as $needle ) {
            if ( false !== strpos( $hay, $needle ) ) { return array( $slug ); }
        }
    }
    return array('cleaning');
}
function home_import_apply_taxonomies( $post_id, $taxonomy, $category_ids ) {
    $slugs = home_import_category_slugs( $taxonomy );
    $slug = ! empty( $slugs ) ? (string) $slugs[0] : 'cleaning';
    if ( ! isset( $category_ids[$slug] ) ) { $slug = 'cleaning'; }
    if ( isset( $category_ids[$slug] ) ) {
        wp_set_post_categories( $post_id, array( (int) $category_ids[$slug] ), false );
        update_post_meta( $post_id, '_home_primary_category', $slug );
    }
    update_post_meta( $post_id, '_home_taxonomy', $taxonomy );
    update_post_meta( $post_id, '_home_primary_article_type', isset( $taxonomy['primary_article_type'] ) ? (string) $taxonomy['primary_article_type'] : '' );
}
function home_import_save_seo_meta( $post_id, $seo ) {
    $title = isset( $seo['title'] ) ? (string) $seo['title'] : '';
    $desc = isset( $seo['meta_description'] ) ? (string) $seo['meta_description'] : '';
    $intent = isset( $seo['search_intent'] ) ? (string) $seo['search_intent'] : '';
    update_post_meta( $post_id, '_home_seo_title', $title ); update_post_meta( $post_id, '_home_meta_description', $desc ); update_post_meta( $post_id, '_home_search_intent', $intent );
    if ( defined( 'WPSEO_VERSION' ) ) { update_post_meta( $post_id, '_yoast_wpseo_title', $title ); update_post_meta( $post_id, '_yoast_wpseo_metadesc', $desc ); }
    if ( defined( 'RANK_MATH_VERSION' ) ) { update_post_meta( $post_id, 'rank_math_title', $title ); update_post_meta( $post_id, 'rank_math_description', $desc ); }
}
function home_import_author_id() { $ids = get_users( array('role'=>'administrator','number'=>1,'fields'=>'ID') ); return $ids ? (int) $ids[0] : 1; }
function home_import_apply_language( $post_id, $language, $group ) {
    update_post_meta( $post_id, '_home_language', $language ); update_post_meta( $post_id, '_home_translation_group', $group );
    if ( function_exists( 'pll_set_post_language' ) ) { pll_set_post_language( $post_id, $language ); }
}
function home_import_link_translations( $groups ) {
    if ( ! function_exists( 'pll_save_post_translations' ) ) { return; }
    foreach ( array_unique( $groups ) as $group ) {
        $posts = get_posts( array('post_type'=>'post','post_status'=>'any','posts_per_page'=>-1,'meta_key'=>'_home_translation_group','meta_value'=>$group) );
        $translations = array();
        foreach ( $posts as $post ) { $lang = (string) get_post_meta( $post->ID, '_home_language', true ); if ( in_array( $lang, array('es','en'), true ) ) { $translations[$lang] = (int) $post->ID; } }
        if ( count( $translations ) > 1 ) { pll_save_post_translations( $translations ); }
    }
}

$category_ids = home_import_ensure_categories();
$languages = 'all' === $options['language'] ? array('es','en') : array($options['language']);
$files = array();
foreach ( $languages as $language ) { $dir = $articles_root . '/' . $language; if ( is_dir( $dir ) ) { foreach ( glob( $dir . '/*.json' ) ?: array() as $file ) { $files[] = $file; } } }
sort( $files, SORT_NATURAL );
$created=0; $updated=0; $skipped=0; $failed=0; $groups=array(); $author=home_import_author_id();
foreach ( $files as $file ) {
    try {
        $raw = file_get_contents( $file ); if ( false === $raw ) { throw new RuntimeException( 'Could not read JSON.' ); }
        $data = json_decode( $raw, true, 512, JSON_THROW_ON_ERROR ); if ( ! is_array( $data ) ) { throw new RuntimeException( 'JSON root must be an object.' ); }
        $number = isset( $data['article_number'] ) ? (int) $data['article_number'] : 0; if ( $number < $options['from'] || $number > $options['to'] ) { continue; }
        $source_id = home_import_required_string( $data, 'id', $file ); $group = home_import_required_string( $data, 'translation_group', $file );
        $language = home_import_required_string( $data, 'language', $file ); $title = home_import_required_string( $data, 'title', $file ); $slug = home_import_required_string( $data, 'slug', $file );
        $excerpt = home_import_required_string( $data, 'excerpt', $file ); $content_html = home_import_required_string( $data, 'content_html', $file );
        if ( ! in_array( $language, array('es','en'), true ) ) { throw new RuntimeException( 'Invalid language in JSON.' ); }
        $seo = ! empty( $data['seo'] ) && is_array( $data['seo'] ) ? $data['seo'] : array(); $taxonomy = ! empty( $data['taxonomy'] ) && is_array( $data['taxonomy'] ) ? $data['taxonomy'] : array();
        $faq = ! empty( $data['faq'] ) && is_array( $data['faq'] ) ? $data['faq'] : array(); $sources = ! empty( $data['sources'] ) && is_array( $data['sources'] ) ? $data['sources'] : array();
        $image = ! empty( $data['image'] ) && is_array( $data['image'] ) ? $data['image'] : array(); $json_status = isset( $data['status'] ) ? (string) $data['status'] : 'draft';
        $hash = hash( 'sha256', $raw ); $existing = home_import_find_existing( $source_id, $slug );
        if ( $existing instanceof WP_Post && ! $options['force'] && hash_equals( $hash, (string) get_post_meta( $existing->ID, '_home_source_hash', true ) ) ) { $groups[]=$group; ++$skipped; echo "SKIP {$language} #{$number} {$slug}\n"; continue; }
        $postarr = array('post_type'=>'post','post_title'=>$title,'post_name'=>$slug,'post_excerpt'=>$excerpt,'post_content'=>$content_html . home_import_sources_html( $sources, $language ),'post_status'=>home_import_status( $json_status, $options['status'] ),'post_author'=>$author);
        if ( $existing instanceof WP_Post ) { $postarr['ID']=(int)$existing->ID; $result=wp_update_post( wp_slash( $postarr ), true ); ++$updated; $verb='UPDATE'; }
        else { $result=wp_insert_post( wp_slash( $postarr ), true ); ++$created; $verb='CREATE'; }
        if ( is_wp_error( $result ) ) { throw new RuntimeException( $result->get_error_message() ); }
        $post_id=(int)$result;
        update_post_meta( $post_id, '_home_source_id', $source_id ); update_post_meta( $post_id, '_home_source_hash', $hash ); update_post_meta( $post_id, '_home_article_number', $number );
        update_post_meta( $post_id, '_home_locale', isset($data['locale'])?(string)$data['locale']:'' ); update_post_meta( $post_id, '_home_market_context', isset($data['market_context'])?(string)$data['market_context']:'' );
        update_post_meta( $post_id, '_home_faq', $faq ); update_post_meta( $post_id, '_home_sources', $sources ); update_post_meta( $post_id, '_home_image_concept', isset($image['concept'])?(string)$image['concept']:'' );
        update_post_meta( $post_id, '_home_image_alt', isset($image['alt'])?(string)$image['alt']:'' ); update_post_meta( $post_id, '_home_managed_article', 1 );
        home_import_apply_taxonomies( $post_id, $taxonomy, $category_ids ); home_import_apply_language( $post_id, $language, $group ); home_import_save_seo_meta( $post_id, $seo );
        $groups[]=$group; echo "{$verb} {$language} #{$number} post_id={$post_id} {$slug}\n";
    } catch ( Throwable $e ) { ++$failed; fwrite( STDERR, 'FAIL ' . basename( $file ) . ': ' . $e->getMessage() . "\n" ); }
}
home_import_link_translations( $groups );
if ( 0 === $failed && '' !== $options['successful_sha'] ) { update_option( 'home_last_successful_import_sha', strtolower( (string) $options['successful_sha'] ), false ); }
echo "SUMMARY created={$created} updated={$updated} skipped={$skipped} failed={$failed}\n";
exit( 0 === $failed ? 0 : 1 );