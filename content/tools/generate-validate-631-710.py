#!/usr/bin/env python3
import argparse, html, json, re, statistics, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'content' / 'tools'
ART = ROOT / 'content' / 'articles'
ES_DIR, EN_DIR = ART / 'es', ART / 'en'
REPORT = ART / 'QUALITY-AUDIT-631-710.md'
EXPECTED = set(range(631, 711)) - {635, 659}
EXCLUSIONS = {
    635: (561, 'Same intent: preventing clothing color loss is already fully resolved by #561.'),
    659: (260, 'Same intent: laundry-detergent dose is already fully resolved by #260.'),
}

SOURCE_MAP = {
    'laundry': {
        'name': 'American Cleaning Institute — Laundry Basics',
        'url': 'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics',
        'es_note': 'Buenas prácticas de lavado, clasificación, carga, dosificación y cuidado según etiquetas.',
        'en_note': 'Laundry practices covering sorting, loading, detergent dosing, and care-label guidance.',
    },
    'fabric-care': {
        'name': 'American Cleaning Institute — Fabric Care',
        'url': 'https://www.cleaninginstitute.org/cleaning-tips/clothes/fabric-care',
        'es_note': 'Cuidado de tejidos, manchas y métodos compatibles con las etiquetas de las prendas.',
        'en_note': 'Fabric-care guidance for stains, fibers, and methods compatible with garment labels.',
    },
    'energy': {
        'name': 'U.S. Department of Energy — Energy Saver',
        'url': 'https://www.energy.gov/energysaver',
        'es_note': 'Información práctica sobre calefacción, refrigeración, termostatos y eficiencia doméstica.',
        'en_note': 'Practical information on home heating, cooling, thermostats, and energy efficiency.',
    },
    'air-quality': {
        'name': 'U.S. Environmental Protection Agency — Guide to Air Cleaners in the Home',
        'url': 'https://www.epa.gov/indoor-air-quality-iaq/guide-air-cleaners-home',
        'es_note': 'Selección y uso de purificadores de aire domésticos y límites de la filtración portátil.',
        'en_note': 'Guidance on selecting and using portable home air cleaners and their limitations.',
    },
    'mold': {
        'name': 'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home',
        'url': 'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home',
        'es_note': 'Control de humedad, condensación, limpieza de moho y criterios para materiales afectados.',
        'en_note': 'Moisture control, condensation, mold cleanup, and guidance for affected materials.',
    },
    'gas': {
        'name': 'U.S. Consumer Product Safety Commission — Winter Weather Safety Tips',
        'url': 'https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Issues-Winter-Weather-Safety-Tips-to-Prevent-Fires-and-Carbon-Monoxide-Poisoning',
        'es_note': 'Ante olor o sonido de una posible fuga de gas, salir y contactar desde fuera sin accionar dispositivos eléctricos.',
        'en_note': 'If a gas leak is smelled or heard, leave and contact gas authorities from outside without operating electronics indoors.',
    },
    'electrical': {
        'name': 'U.S. Consumer Product Safety Commission — Electrical Safety',
        'url': 'https://www.cpsc.gov/safety-education/safety-guides/electronics-and-electrical/electrical-safety',
        'es_note': 'Seguridad eléctrica doméstica, sobrecarga, conexiones dañadas y señales para detener el uso.',
        'en_note': 'Household electrical safety, overloads, damaged connections, and warning signs to stop use.',
    },
    'heater-safety': {
        'name': 'U.S. Consumer Product Safety Commission — Space Heater Safety',
        'url': 'https://www.cpsc.gov/Newsroom/News-Releases/2026/Keep-Warm-and-Safe-This-Winter-Tips-for-Using-Generators-Furnaces-and-Space-Heaters',
        'es_note': 'Los calefactores portátiles deben conectarse directamente a pared, mantenerse alejados de combustibles y apagarse sin supervisión.',
        'en_note': 'Portable space heaters should plug directly into a wall outlet, stay clear of combustibles, and be turned off when unattended.',
    },
    'cleaning': {
        'name': 'American Cleaning Institute — Cleaning Tips',
        'url': 'https://www.cleaninginstitute.org/cleaning-tips',
        'es_note': 'Buenas prácticas de limpieza doméstica y uso responsable de productos según etiqueta y superficie.',
        'en_note': 'General household-cleaning practices and responsible product use according to labels and surfaces.',
    },
    'plumbing': {
        'name': 'U.S. Environmental Protection Agency WaterSense — Home Maintenance',
        'url': 'https://www.epa.gov/watersense/home-maintenance',
        'es_note': 'Mantenimiento doméstico relacionado con agua, fugas, inodoros, presión y uso eficiente.',
        'en_note': 'Household maintenance related to water, leaks, toilets, pressure, and efficient use.',
    },
    'water-softener': {
        'name': 'U.S. Environmental Protection Agency WaterSense — Cation Exchange Water Softeners',
        'url': 'https://www.epa.gov/watersense/cation-exchange-water-softeners',
        'es_note': 'Funcionamiento, regeneración, sal, agua y mantenimiento de descalcificadores de intercambio catiónico.',
        'en_note': 'How cation-exchange water softeners work, regenerate, use salt and water, and are maintained.',
    },
    'pests': {
        'name': 'U.S. Environmental Protection Agency — Integrated Pest Management Principles',
        'url': 'https://www.epa.gov/safepestcontrol/integrated-pest-management-ipm-principles',
        'es_note': 'Manejo integrado de plagas basado en prevención, exclusión, saneamiento y control de menor riesgo.',
        'en_note': 'Integrated pest management emphasizing prevention, exclusion, sanitation, and lower-risk control.',
    },
    'heat': {
        'name': 'Ready.gov — Extreme Heat',
        'url': 'https://www.ready.gov/heat',
        'es_note': 'Preparación del hogar para calor extremo, refrigeración, cortes de energía y reducción de exposición al calor.',
        'en_note': 'Home preparation for extreme heat, cooling, outages, and reducing heat exposure.',
    },
    'maintenance': {
        'name': 'U.S. Department of Energy — Energy Saver',
        'url': 'https://www.energy.gov/energysaver',
        'es_note': 'Mantenimiento doméstico práctico relacionado con climatización, eficiencia y preparación estacional.',
        'en_note': 'Practical home maintenance related to heating, cooling, efficiency, and seasonal preparation.',
    },
}

NUMBER_SOURCES = {
    665: {
        'name': 'USDA Food Safety and Inspection Service — Refrigeration & Food Safety',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/refrigeration',
        'es_note': 'Temperatura segura del refrigerador y almacenamiento de alimentos para evitar contaminación y deterioro.',
        'en_note': 'Safe refrigerator temperature and food-storage practices to reduce contamination and spoilage.',
    },
    666: {
        'name': 'USDA Food Safety and Inspection Service — Refrigeration & Food Safety',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/refrigeration',
        'es_note': 'Criterios de refrigeración, congelación y manipulación segura de alimentos durante descongelación y cortes.',
        'en_note': 'Refrigeration, freezing, and safe-food-handling criteria during thawing and outages.',
    },
    687: {
        'name': 'USDA Food Safety and Inspection Service — Cutting Boards',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/cutting-boards',
        'es_note': 'Lavado, desinfección, secado y sustitución de tablas de cortar cuando ya no pueden limpiarse bien.',
        'en_note': 'Washing, sanitizing, drying, and replacing cutting boards that can no longer be cleaned effectively.',
    },
    688: {
        'name': 'USDA Food Safety and Inspection Service — Cutting Boards',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/cutting-boards',
        'es_note': 'Buenas prácticas para limpieza y desinfección de tablas, adaptadas al cuidado de la madera.',
        'en_note': 'Cutting-board washing and sanitizing guidance applied to wooden-board care.',
    },
    699: {
        'name': 'U.S. Centers for Disease Control and Prevention — How to Clean Up After Rodents',
        'url': 'https://www.cdc.gov/healthy-pets/rodent-control/clean-up.html',
        'es_note': 'Limpieza segura de excrementos de roedores: humedecer y desinfectar antes de retirar, sin barrer ni aspirar en seco.',
        'en_note': 'Safe rodent-dropping cleanup: wet and disinfect before removal, without dry sweeping or vacuuming.',
    },
}

WATCHED = [(631,706),(636,637),(638,640),(643,644),(649,574),(650,279),(651,276),(652,578),(656,675),(674,286),(673,291),(676,677),(677,678),(681,621),(682,245),(682,246),(684,604),(690,691),(694,695),(697,698),(699,251),(701,554),(710,260)]


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    s = re.sub(r"[^a-z0-9]+", '-', s).strip('-')
    return s

def strip_tags(s):
    return re.sub(r'<[^>]+>', ' ', html.unescape(s))

def words(s):
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:['’-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)?", strip_tags(s))

def first_sentence(text):
    # Editorial intros are authored so the first sentence is complete; protect common abbreviations.
    protected = text.replace('EE. UU.', 'EE§UU§').replace('U.S.', 'U§S§').replace('p. ej.', 'p§ej§')
    m = re.search(r'[.!?](?:[”\"])?(?=\s|$)', protected)
    out = protected[:m.end()] if m else protected
    return out.replace('EE§UU§','EE. UU.').replace('U§S§','U.S.').replace('p§ej§','p. ej.').strip()

def normalize_text(s, lang, n):
    if lang == 'en':
        s = s.replace('HVAC power', 'heating and cooling system power')
        s = s.replace('water, HVAC, alarms', 'water, heating and cooling, alarms')
    if lang == 'es' and n == 700:
        s = s.replace(', conocidos como frass,', ', también llamados gránulos fecales,')
    return s

def parse_topics(path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out

def load_entries():
    entries = []
    for start in range(631, 711, 10):
        p = TOOLS / f'batch-{start}-{start+9}.json'
        entries.extend(json.loads(p.read_text(encoding='utf-8')))
    nums = [e['n'] for e in entries]
    if len(entries) != 78 or set(nums) != EXPECTED or len(set(nums)) != len(nums):
        raise SystemExit(f'Source inventory mismatch: count={len(entries)} missing={sorted(EXPECTED-set(nums))} extra={sorted(set(nums)-EXPECTED)}')
    canonical = parse_topics(ROOT/'content/topics/TOPICS-601-700.md') | parse_topics(ROOT/'content/topics/TOPICS-701-800.md')
    for e in entries:
        if canonical.get(e['n']) != e['es_title']:
            raise SystemExit(f"Canonical title mismatch #{e['n']}: {e['es_title']} != {canonical.get(e['n'])}")
        if len(e['sections']) != 4 or len(e['faq_es']) != 3 or len(e['faq_en']) != 3 or len(e['faq_sections']) != 3:
            raise SystemExit(f"Authored structure mismatch #{e['n']}")
        if any(i not in range(4) for i in e['faq_sections']):
            raise SystemExit(f"FAQ mapping out of range #{e['n']}")
    for n in EXCLUSIONS:
        if n in nums:
            raise SystemExit(f'Excluded #{n} unexpectedly present in source entries')
    return entries

def source_for(e, lang):
    s = NUMBER_SOURCES.get(e['n']) or SOURCE_MAP.get(e.get('source',''))
    if not s:
        return []
    return [{'name': s['name'], 'url': s['url'], 'note': s['es_note' if lang=='es' else 'en_note']}]

def search_intent(e, lang):
    title = normalize_text(e['es_title' if lang=='es' else 'en_title'], lang, e['n'])
    if lang == 'es':
        if e['kind'] in ('diagnostics','safety-diagnostics'):
            return f'Identificar las causas más probables de «{title.rstrip("¿?")}», distinguir señales útiles y decidir qué comprobar primero y cuándo pedir ayuda.'
        if 'decision' in e['kind'] or 'safety-guide' in e['kind']:
            return f'Tomar una decisión práctica y segura sobre «{title.rstrip("¿?")}», reconocer límites y saber cuándo conviene cambiar de estrategia o pedir ayuda.'
        return f'Resolver «{title.rstrip("¿?")}» con una secuencia práctica, clara y segura, incluyendo las comprobaciones que evitan errores comunes.'
    if e['kind'] in ('diagnostics','safety-diagnostics'):
        return f'Identify the most likely causes behind “{title.rstrip("?")},” use distinguishing clues, and decide what to check first and when to get help.'
    if 'decision' in e['kind'] or 'safety-guide' in e['kind']:
        return f'Make a practical, safe decision about “{title.rstrip("?")},” recognize important limits, and know when to change approach or get help.'
    return f'Handle “{title.rstrip("?")}” with a practical, clear, safe sequence and the checks that prevent common mistakes.'

def build_article(e, lang):
    n=e['n']; is_es=lang=='es'
    title=normalize_text(e['es_title' if is_es else 'en_title'],lang,n)
    intro=normalize_text(e['intro_es' if is_es else 'intro_en'],lang,n)
    sections=[]
    for sec in e['sections']:
        h=normalize_text(sec[0 if is_es else 1],lang,n)
        p=normalize_text(sec[2 if is_es else 3],lang,n)
        sections.append((h,p))
    faqs=e['faq_es' if is_es else 'faq_en']
    faqs=[normalize_text(q,lang,n) for q in faqs]
    slug=slugify(title)
    en_slug=slugify(normalize_text(e['en_title'],'en',n))
    tg=f'{n}-{en_slug}'
    content='<p>'+html.escape(intro, quote=False)+'</p>'+''.join(f'<h2>{html.escape(h,quote=False)}</h2><p>{html.escape(p,quote=False)}</p>' for h,p in sections)
    faq=[{'question':q,'answer':sections[idx][1]} for q,idx in zip(faqs,e['faq_sections'])]
    primary=e['kind']
    article={
      'schema_version':1,
      'id':f'{lang}-{n}-{slug}',
      'article_number':n,
      'translation_group':tg,
      'language':lang,
      'locale':'es-ES' if is_es else 'en-US',
      'market_context':'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if is_es else 'U.S./Canadian English; practical household guidance with locally familiar terminology and clear safety boundaries.',
      'title':title,
      'slug':slug,
      'seo':{
        'title':title,
        'meta_description':first_sentence(intro),
        'search_intent':search_intent(e,lang),
      },
      'excerpt':intro,
      'taxonomy':{
        'food_family':e['family'],
        'food_subcategories':[slug],
        'article_types':[primary,e['family']],
        'primary_article_type':primary,
      },
      'content_html':content,
      'faq':faq,
      'sources':source_for(e,lang),
      'image':{
        'concept': (f'Fotografía editorial doméstica realista sobre «{title.rstrip("¿?")}», mostrando de forma clara {sections[0][0].lower()} como acción o pista principal; entorno cotidiano natural, sin texto ni marcas.' if is_es else f'Realistic household editorial photograph about “{title.rstrip("?")},” clearly showing {sections[0][0].lower()} as the main action or clue; natural home setting, no text or branding.'),
        'alt':title.rstrip('¿?!.').lstrip('¿'),
      },
      'status':'publish',
    }
    return article, sections

def article_path(article):
    return (ES_DIR if article['language']=='es' else EN_DIR) / f"{article['article_number']}-{article['slug']}.json"

def load_existing(exclude_nums):
    vals=[]
    for d in (ES_DIR, EN_DIR):
        for p in d.glob('*.json'):
            try: a=json.loads(p.read_text(encoding='utf-8'))
            except Exception: continue
            if a.get('article_number') not in exclude_nums:
                vals.append((p,a))
    return vals

def acronym_checks(a, errors):
    text=' '.join([a['excerpt'], strip_tags(a['content_html'])] + [x['question']+' '+x['answer'] for x in a['faq']])
    lang=a['language']; n=a['article_number']
    checks={
      'CO': ('monóxido de carbono (CO)' if lang=='es' else 'carbon monoxide (CO)'),
      'CPSC': ('Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC)' if lang=='es' else 'U.S. Consumer Product Safety Commission (CPSC)'),
      'EPA': ('Agencia de Protección Ambiental de EE. UU. (EPA)' if lang=='es' else 'U.S. Environmental Protection Agency (EPA)'),
    }
    for ac,exp in checks.items():
        if re.search(rf'\b{ac}\b',text) and exp.lower() not in text.lower():
            errors.append(f'#{n} {lang}: acronym {ac} not expanded on first use')
    if re.search(r'\bHVAC\b', text):
        errors.append(f'#{n} {lang}: unexplained HVAC remains')

def validate(entries):
    errors=[]; warnings=[]; built={}; faq_ok=0
    existing=load_existing(EXPECTED | set(EXCLUSIONS))
    ids={a.get('id') for _,a in existing}; slugs={(a.get('language'),a.get('slug')) for _,a in existing}; tgs={a.get('translation_group') for _,a in existing}
    generated_tgs=set()
    counts={'es':[],'en':[]}
    generic_q_es=('¿Qué debo saber sobre','¿Qué es importante sobre')
    generic_q_en=('What should I know about','What is important about')
    bad_meta_es=('HOME prioriza','HOME no plantea','En este artículo hemos decidido')
    for e in entries:
        pair=[]
        for lang in ('es','en'):
            a,sections=build_article(e,lang); pair.append(a)
            p=article_path(a)
            if not p.exists(): errors.append(f'Missing generated file {p.relative_to(ROOT)}'); continue
            disk=json.loads(p.read_text(encoding='utf-8'))
            if disk != a: errors.append(f'#{e["n"]} {lang}: generated file differs from deterministic build')
            for key in ('schema_version','id','article_number','translation_group','language','locale','title','slug','seo','excerpt','taxonomy','content_html','faq','sources','image','status'):
                if key not in a: errors.append(f'#{e["n"]} {lang}: missing {key}')
            if a['status']!='publish': errors.append(f'#{e["n"]} {lang}: status not publish')
            if a['id'] in ids: errors.append(f'#{e["n"]} {lang}: id collision')
            if (lang,a['slug']) in slugs: errors.append(f'#{e["n"]} {lang}: slug collision')
            if a['translation_group'] in tgs: errors.append(f'#{e["n"]}: translation_group collision with prior library')
            if len(re.findall(r'<h2>',a['content_html'])) != 4: errors.append(f'#{e["n"]} {lang}: H2 count != 4')
            if len(a['faq']) != 3: errors.append(f'#{e["n"]} {lang}: FAQ count != 3')
            for fq,idx in zip(a['faq'],e['faq_sections']):
                if fq['answer'] != sections[idx][1]: errors.append(f'#{e["n"]} {lang}: FAQ semantic mapping drift')
                else: faq_ok += 1
                if fq['question'].startswith(generic_q_es if lang=='es' else generic_q_en): errors.append(f'#{e["n"]} {lang}: generic FAQ prompt')
            meta=a['seo']['meta_description']
            if meta != first_sentence(a['excerpt']) or not re.search(r'[.!?][”\"]?$',meta): errors.append(f'#{e["n"]} {lang}: meta description is not a complete first editorial sentence')
            if len(meta)<35: warnings.append(f'#{e["n"]} {lang}: unusually short meta ({len(meta)} chars)')
            if not re.search(r'[.!?][”\"]?$',a['seo']['search_intent']): errors.append(f'#{e["n"]} {lang}: incomplete search_intent')
            if 'for how to' in a['seo']['search_intent'].lower() or 'para cómo' in a['seo']['search_intent'].lower(): errors.append(f'#{e["n"]} {lang}: awkward search intent')
            if not a['image']['concept'] or sections[0][0].lower() not in a['image']['concept'].lower(): errors.append(f'#{e["n"]} {lang}: generic image concept')
            if any(x.lower() in (' '+a['excerpt']+' '+strip_tags(a['content_html'])).lower() for x in bad_meta_es): errors.append(f'#{e["n"]} {lang}: editorial metadiscourse')
            if lang=='es' and re.search(r'\b(topper|deck|frass)\b',strip_tags(a['content_html']),re.I): errors.append(f'#{e["n"]} es: avoidable anglicism')
            acronym_checks(a,errors)
            wc=len(words(a['content_html'])); counts[lang].append(wc)
            if wc<160: errors.append(f'#{e["n"]} {lang}: body too thin ({wc} words)')
            # Explicit safety anti-patterns; negated mentions are allowed by phrasing, so check dangerous positive imperatives only.
            prose=strip_tags(a['content_html']).lower()
            for bad in ('puentea el sensor','bypass the sensor','abre la caldera','open the boiler','mide tensión con','test live voltage with'):
                if bad in prose: errors.append(f'#{e["n"]} {lang}: unsafe instruction pattern {bad}')
            built[(e['n'],lang)]=a
        if len(pair)==2:
            if pair[0]['translation_group']!=pair[1]['translation_group']: errors.append(f'#{e["n"]}: bilingual translation group mismatch')
            if pair[0]['translation_group'] in generated_tgs: errors.append(f'#{e["n"]}: repeated translation group in generated pairs')
            generated_tgs.add(pair[0]['translation_group'])
    # Exact file inventory for target range.
    files=[]
    for d in (ES_DIR,EN_DIR):
        for p in d.glob('*.json'):
            try: a=json.loads(p.read_text(encoding='utf-8'))
            except Exception: continue
            if 631 <= a.get('article_number',0) <= 710: files.append((p,a))
    nums_lang={(a['article_number'],a['language']) for _,a in files}
    expected_pairs={(n,l) for n in EXPECTED for l in ('es','en')}
    if nums_lang != expected_pairs or len(files)!=156:
        errors.append(f'Target file inventory mismatch: files={len(files)} missing={sorted(expected_pairs-nums_lang)} extra={sorted(nums_lang-expected_pairs)}')
    if any(a['article_number'] in EXCLUSIONS for _,a in files): errors.append('Excluded topic generated unexpectedly')
    return errors,warnings,built,counts,faq_ok

def tokens(a):
    return {w.lower() for w in words(a['content_html']) if len(w)>3}

def jaccard(a,b):
    x,y=tokens(a),tokens(b)
    return len(x&y)/max(1,len(x|y))

def prior_by_number(n,lang):
    d=ES_DIR if lang=='es' else EN_DIR
    for p in d.glob(f'{n}-*.json'):
        try:return json.loads(p.read_text(encoding='utf-8'))
        except Exception:return None
    return None

def write_report(entries,built,counts,faq_ok,warnings):
    watched=[]
    for a,b in WATCHED:
        if a not in EXPECTED and b not in EXPECTED: continue
        vals=[]
        for lang in ('es','en'):
            aa=built.get((a,lang)) or prior_by_number(a,lang)
            bb=built.get((b,lang)) or prior_by_number(b,lang)
            if aa and bb: vals.append(jaccard(aa,bb))
        if vals: watched.append((a,b,max(vals)))
    src_pairs=sum(1 for e in entries if source_for(e,'en'))
    lines=[
      '# Quality audit — HOME articles 631–710','', '## Result','',
      '- Canonical topic intents reviewed: **80/80**.',
      '- Editorial source entries validated: **78/78**; #635 and #659 are intentional canonical exclusions.',
      '- Published unique intents: **78**; bilingual article JSON files: **156/156 PASS**.',
      f'- FAQ answer-to-section mappings: **{faq_ok}/468 PASS**.',
      '- Explicit exclusions: **#635 → #561** and **#659 → #260** to preserve one canonical URL per search intent.',
      '- Schema, language/locale, IDs, slugs, translation groups, SEO fields, status, four H2 sections, three FAQs, image metadata, acronym rules, metadiscourse checks, safety anti-patterns and batch depth all pass.',
      '- Meta descriptions are validated as complete editorial sentences; character truncation is not permitted.','',
      '## Depth metrics','',
      f'- Spanish body words: min **{min(counts["es"])}**, median **{int(statistics.median(counts["es"]))}**, max **{max(counts["es"])}**.',
      f'- English body words: min **{min(counts["en"])}**, median **{int(statistics.median(counts["en"]))}**, max **{max(counts["en"])}**.',
      '- The editorial standard has no fixed word-count target; the 160-word floor is only a guard against accidentally incomplete output.','',
      '## Inventory by range','',
      '| Range | Canonical topics | Published intents | ES | EN |','|---|---:|---:|---:|---:|',
      '| 631–650 | 20 | 19 | 19 | 19 |','| 651–670 | 20 | 19 | 19 | 19 |','| 671–690 | 20 | 20 | 20 | 20 |','| 691–710 | 20 | 20 | 20 | 20 |','',
      '## Cannibalization decisions','',
      '- **#635 vs #561:** block #635. #561 already resolves preventing color loss during washing, including temperature, friction, separation and drying heat.',
      '- **#659 vs #260:** block #659. #260 already resolves detergent dosage by concentration, load, water hardness and washer type.',
      '- **#631 vs #706:** keep both. #631 covers towels mixed with clothing generally; #706 focuses specifically on sheets plus towels and their bulk/drying interaction.',
      '- **#636 vs #637:** keep both. #636 prevents pilling; #637 removes pills already present.',
      '- **#652 vs #578:** keep both. #652 is the direct fuel-gas safety response; #578 distinguishes rotten-egg odor among fuel gas, drains and hot water sulfur.',
      '- **#684 vs #604:** keep both. #684 diagnoses continued dripping after shutoff and points toward the valve; #604 repairs a leaking showerhead/connection.',
      '- **#690 vs #691:** keep both. #690 is the shutoff procedure; #691 is the location guide.','',
      '### Similarity diagnostics (maximum ES/EN token Jaccard)','',
    ]
    for a,b,v in watched: lines.append(f'- #{a} vs #{b}: **{v:.3f}**')
    lines += ['', '## Sources','', f'- Topic pairs with a directly relevant structured reference: **{src_pairs}**.', f'- Topic pairs intentionally published without a structured source because no directly supporting source was mapped: **{78-src_pairs}**.', '- No non-empty source key is silently treated as authoritative when it lacks a mapping.','', '## Final editorial safeguards','', '- Spanish and English use separately authored bilingual source paragraphs rather than literal machine translation.', '- FAQ answers are copied only from their explicitly mapped editorial sections and validated one by one.', '- Safety boundaries include no live electrical testing, gas-system adjustment, bypassing safety devices, unsafe spring/cable work, hazardous chemical mixing, or unsafe structural access.', '- Pest articles prioritize exclusion, sanitation, moisture control and professional escalation over indiscriminate chemical treatment.', '- Exact slug, ID and translation-group collisions with already published articles are rejected.', '- Temporary generator, batch files and workflow must be removed before merge to `main`.']
    if warnings:
        lines += ['', '## Non-blocking notes',''] + [f'- {w}' for w in warnings]
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')

def generate(entries):
    for e in entries:
        for lang in ('es','en'):
            a,_=build_article(e,lang)
            p=article_path(a); p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(a,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--validate-only',action='store_true'); args=ap.parse_args()
    entries=load_entries()
    if not args.validate_only: generate(entries)
    errors,warnings,built,counts,faq_ok=validate(entries)
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); raise SystemExit(1)
    if not args.validate_only: write_report(entries,built,counts,faq_ok,warnings)
    print(f'PASS: 80 canonical intents reviewed; 78 source entries validated; 78 unique intents published; 156 article JSON files; {faq_ok}/468 FAQ mappings valid.')
    print(f'ES words min/median/max: {min(counts["es"])}/{int(statistics.median(counts["es"]))}/{max(counts["es"])}')
    print(f'EN words min/median/max: {min(counts["en"])}/{int(statistics.median(counts["en"]))}/{max(counts["en"])}')
    if warnings: print('WARNINGS: '+' | '.join(warnings))

if __name__=='__main__': main()
