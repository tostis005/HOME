<?php
if (!defined('ABSPATH')) { exit; }

function home_category_definitions(): array {
    return [
        'cleaning'=>['wp_slug'=>'cleaning','slug_es'=>'limpieza','slug_en'=>'cleaning','label_es'=>'Limpieza','label_en'=>'Cleaning','description_es'=>'Superficies, habitaciones, manchas y rutinas para mantener la casa agradable.','description_en'=>'Surfaces, rooms, stains and the routines that keep a home feeling good.','tone'=>'#dce8df'],
        'kitchen'=>['wp_slug'=>'kitchen','slug_es'=>'cocina','slug_en'=>'kitchen','label_es'=>'Cocina','label_en'=>'Kitchen','description_es'=>'Cuidados diarios de la cocina, suciedad, olores y soluciones prácticas.','description_en'=>'Everyday kitchen care, messes, odors and practical fixes.','tone'=>'#eee0c7'],
        'bathroom'=>['wp_slug'=>'bathroom','slug_es'=>'bano','slug_en'=>'bathroom','label_es'=>'Baño','label_en'=>'Bathroom','description_es'=>'Moho, desagües, grifería y pequeños problemas que necesitan respuestas rápidas.','description_en'=>'Mold, drains, fixtures and the small problems that need fast answers.','tone'=>'#d7e7e8'],
        'laundry'=>['wp_slug'=>'laundry','slug_es'=>'lavanderia','slug_en'=>'laundry','label_es'=>'Lavandería','label_en'=>'Laundry','description_es'=>'Ropa, manchas, lavadoras, secadoras y mejores hábitos de lavado.','description_en'=>'Clothes, stains, washers, dryers and better laundry habits.','tone'=>'#e4dfef'],
        'appliances'=>['wp_slug'=>'appliances','slug_es'=>'electrodomesticos','slug_en'=>'appliances','label_es'=>'Electrodomésticos','label_en'=>'Appliances','description_es'=>'Soluciones y cuidados para los electrodomésticos que usas cada día.','description_en'=>'Troubleshooting and care for the machines you rely on every day.','tone'=>'#dfe3dc'],
        'plumbing'=>['wp_slug'=>'plumbing','slug_es'=>'fontaneria','slug_en'=>'plumbing','label_es'=>'Fontanería','label_en'=>'Plumbing','description_es'=>'Fugas, atascos, desagües y problemas de agua: qué probar y cuándo parar.','description_en'=>'Leaks, clogs, drains and water problems—what to try and when to stop.','tone'=>'#cfe1e4'],
        'pests'=>['wp_slug'=>'pests','slug_es'=>'plagas','slug_en'=>'pests','label_es'=>'Plagas','label_en'=>'Pests','description_es'=>'Hormigas, cucarachas, ratones, moscas y prevención práctica en casa.','description_en'=>'Ants, roaches, mice, flies and practical prevention around the home.','tone'=>'#e9ddca'],
        'heating-cooling'=>['wp_slug'=>'heating-cooling','slug_es'=>'climatizacion','slug_en'=>'heating-cooling','label_es'=>'Climatización','label_en'=>'Heating & air','description_es'=>'Confort, ventilación, aire acondicionado y calefacción para una casa más saludable.','description_en'=>'Comfort, airflow, AC and heating basics for a healthier home.','tone'=>'#d6e3d6'],
    ];
}
function home_category_pillars(): array {
    $lang=home_current_language(); $result=[];
    foreach(home_category_definitions() as $key=>$d){ $result[$key]=['label'=>$d['label_'.$lang],'description'=>$d['description_'.$lang],'tone'=>$d['tone']]; }
    return $result;
}
function home_category_key_from_wp_slug(string $slug): ?string {
    foreach(home_category_definitions() as $key=>$d){ if($d['wp_slug']===$slug){ return $key; } } return null;
}
function home_category_url(string $key, ?string $language=null): string {
    $defs=home_category_definitions(); if(!isset($defs[$key])){ $key=home_category_key_from_wp_slug($key) ?: $key; }
    if(!isset($defs[$key])){ return home_localized_home_url($language); }
    $language=$language ?: home_current_language(); $slug=$defs[$key]['slug_'.$language];
    return $language==='en' ? home_url('/en/category/'.$slug.'/') : home_url('/categoria/'.$slug.'/');
}
function home_category_count(string $key): int {
    $defs=home_category_definitions(); $term=get_category_by_slug($defs[$key]['wp_slug'] ?? $key); return $term instanceof WP_Term ? (int)$term->count : 0;
}
function home_category_art(string $slug, string $tone='#dce8df'): string {
    $icons=['cleaning'=>'✦','kitchen'=>'⌂','bathroom'=>'◌','laundry'=>'≈','appliances'=>'▣','plumbing'=>'↧','pests'=>'✣','heating-cooling'=>'☼']; $icon=$icons[$slug] ?? '⌂';
    return '<svg viewBox="0 0 320 220" role="img" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg"><rect width="320" height="220" fill="'.esc_attr($tone).'"/><circle cx="160" cy="110" r="62" fill="#fffaf0" opacity=".92"/><text x="160" y="128" text-anchor="middle" font-size="54" fill="#516b58" font-family="Arial, sans-serif">'.esc_html($icon).'</text></svg>';
}
function home_reading_time(?int $post_id=null): string {
    $post_id=$post_id ?: get_the_ID(); $words=str_word_count(wp_strip_all_tags((string)get_post_field('post_content',$post_id))); $minutes=max(1,(int)ceil($words/220));
    return sprintf(home_is_english() ? '%s min read' : '%s min de lectura', number_format_i18n($minutes));
}
function home_primary_category_name(?int $post_id=null): string {
    $categories=get_the_category($post_id ?: get_the_ID()); if(empty($categories)){ return home_is_english() ? 'Home guide' : 'Guía del hogar'; }
    $key=home_category_key_from_wp_slug($categories[0]->slug); if($key){ $d=home_category_definitions()[$key]; return $d['label_'.home_current_language()]; } return $categories[0]->name;
}
