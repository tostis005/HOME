#!/usr/bin/env python3
import argparse, html, json, re, statistics, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'content' / 'tools'
ART = ROOT / 'content' / 'articles'
ES_DIR, EN_DIR = ART / 'es', ART / 'en'
REPORT = ART / 'QUALITY-AUDIT-711-800.md'
EXCLUSIONS = {
    726: (277, 'Exact duplicate: finding the source of a bad household odor is already resolved by #277.'),
    733: (664, 'Same search intent: an ice maker that is not making ice is already resolved by #664.'),
    736: (568, 'Same search intent: refrigerator organization for food safety is already resolved by #568.'),
    739: (517, 'Exact duplicate: smoke-alarm battery replacement interval is already resolved by #517.'),
    749: (481, 'Exact duplicate: cloudy tap water is already resolved by #481.'),
    771: (552, 'Same search intent: organizing clothes in a small closet is already resolved by #552.'),
    772: (642, 'Same search intent: preventing musty odor in stored clothing is already resolved by #642.'),
    787: (774, 'Same search intent in this block: safe organization of cleaning products is covered by #774.'),
    788: (718, 'Same search intent in this block: dealing with mealybugs on houseplants is covered by #718.'),
}
EXPECTED = set(range(711, 801)) - set(EXCLUSIONS)
BATCH_STARTS = list(range(711, 801, 10))

SOURCE_MAP = {
    'laundry': {
        'name': 'American Cleaning Institute — Laundry Basics',
        'url': 'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics',
        'es_note': 'Buenas prácticas de lavado, clasificación, carga, dosificación y cuidado según etiquetas.',
        'en_note': 'Laundry practices covering sorting, loading, detergent dosing, and care-label guidance.',
    },
    'energy': {
        'name': 'U.S. Department of Energy — Energy Saver',
        'url': 'https://www.energy.gov/energysaver',
        'es_note': 'Información práctica sobre calefacción, refrigeración, termostatos, sellado y eficiencia doméstica.',
        'en_note': 'Practical information on home heating, cooling, thermostats, air sealing, and energy efficiency.',
    },
    'electrical': {
        'name': 'U.S. Consumer Product Safety Commission — Electrical Safety',
        'url': 'https://www.cpsc.gov/safety-education/safety-guides/electronics-and-electrical/electrical-safety',
        'es_note': 'Seguridad eléctrica doméstica, sobrecarga, conexiones dañadas y señales para detener el uso.',
        'en_note': 'Household electrical safety, overloads, damaged connections, and warning signs to stop use.',
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
        'es_note': 'Mantenimiento doméstico relacionado con agua, fugas, presión, grifos y uso eficiente.',
        'en_note': 'Household maintenance related to water, leaks, pressure, faucets, and efficient use.',
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
    'mold': {
        'name': 'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home',
        'url': 'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home',
        'es_note': 'Control de humedad, condensación, limpieza de moho y criterios para materiales afectados.',
        'en_note': 'Moisture control, condensation, mold cleanup, and guidance for affected materials.',
    },
    'gas': {
        'name': 'U.S. Consumer Product Safety Commission — Gas and Carbon Monoxide Safety',
        'url': 'https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Issues-Winter-Weather-Safety-Tips-to-Prevent-Fires-and-Carbon-Monoxide-Poisoning',
        'es_note': 'Ante olor o posible fuga de gas, salir y contactar desde fuera; no manipular combustión ni dispositivos de seguridad.',
        'en_note': 'For suspected gas leaks, leave and contact help from outside; do not adjust combustion or safety components.',
    },
}

NUMBER_SOURCES = {
    737: {
        'name': 'USDA Food Safety and Inspection Service — Refrigeration & Food Safety',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/refrigeration',
        'es_note': 'Temperatura segura del refrigerador y prevención de contaminación cruzada durante el almacenamiento.',
        'en_note': 'Safe refrigerator temperature and prevention of cross-contamination during food storage.',
    },
    744: {
        'name': 'USDA Food Safety and Inspection Service — Microwave Ovens and Food Safety',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/microwave-ovens-and-food-safety',
        'es_note': 'Uso de recipientes aptos para microondas y prácticas seguras al calentar alimentos.',
        'en_note': 'Use of microwave-safe containers and safe practices when heating food.',
    },
    745: {
        'name': 'USDA Food Safety and Inspection Service — Microwave Ovens and Food Safety',
        'url': 'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/microwave-ovens-and-food-safety',
        'es_note': 'Prácticas seguras con materiales y alimentos en hornos microondas.',
        'en_note': 'Safe practices for materials and foods in microwave ovens.',
    },
    769: {
        'name': 'U.S. Environmental Protection Agency — How to Find Bed Bugs',
        'url': 'https://www.epa.gov/bedbugs/how-find-bed-bugs',
        'es_note': 'Señales físicas e inspección de chinches; las picaduras por sí solas no confirman una infestación.',
        'en_note': 'Physical signs and inspection for bed bugs; bites alone do not confirm an infestation.',
    },
    780: {
        'name': 'U.S. Department of Energy — Energy Saver',
        'url': 'https://www.energy.gov/energysaver',
        'es_note': 'Mantenimiento estacional relacionado con climatización, sellado y eficiencia doméstica.',
        'en_note': 'Seasonal maintenance related to heating, cooling, air sealing, and home efficiency.',
    },
}

WATCHED = [
    (722,137),(723,207),(724,278),(725,653),(725,578),(728,445),(728,130),(731,377),
    (733,664),(736,568),(738,656),(738,674),(742,679),(746,680),(747,682),(748,233),
    (749,481),(761,762),(761,763),(764,161),(767,71),(769,66),(771,552),(772,642),
    (774,787),(776,342),(778,557),(779,703),(782,430),(786,494),(788,718),(798,799),(800,728)
]


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def strip_tags(s):
    return re.sub(r'<[^>]+>', ' ', html.unescape(s))


def words(s):
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:['’-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)?", strip_tags(s))


def first_sentence(text):
    protected = text.replace('EE. UU.', 'EE§UU§').replace('U.S.', 'U§S§').replace('p. ej.', 'p§ej§')
    m = re.search(r'[.!?](?:[”\"])?(?=\s|$)', protected)
    out = protected[:m.end()] if m else protected
    return out.replace('EE§UU§','EE. UU.').replace('U§S§','U.S.').replace('p§ej§','p. ej.').strip()


def query_title(title, lang):
    if lang == 'es':
        return title.lstrip('¿').rstrip('?').strip()
    return title.rstrip('?').strip()


def normalize_text(s, lang, n):
    if lang == 'es' and n == 762:
        s = s.replace('el enchufe, GFCI o automático', 'el enchufe, el interruptor de circuito por falla a tierra (GFCI), habitual en instalaciones de Norteamérica, o el automático')
    return s


def parse_topics(path):
    out = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def load_entries():
    entries=[]
    for start in BATCH_STARTS:
        p=TOOLS/f'batch-{start}-{start+9}.json'
        if not p.exists():
            raise SystemExit(f'Missing source batch: {p.relative_to(ROOT)}')
        entries.extend(json.loads(p.read_text(encoding='utf-8')))
    nums=[e['n'] for e in entries]
    if len(entries)!=81 or set(nums)!=EXPECTED or len(set(nums))!=len(nums):
        raise SystemExit(f'Source inventory mismatch: count={len(entries)} missing={sorted(EXPECTED-set(nums))} extra={sorted(set(nums)-EXPECTED)}')
    canonical=parse_topics(ROOT/'content/topics/TOPICS-701-800.md')
    for e in entries:
        if canonical.get(e['n']) != e['es_title']:
            raise SystemExit(f"Canonical title mismatch #{e['n']}: {e['es_title']} != {canonical.get(e['n'])}")
        if len(e['sections'])!=4 or len(e['faq_es'])!=3 or len(e['faq_en'])!=3 or len(e['faq_sections'])!=3:
            raise SystemExit(f"Authored structure mismatch #{e['n']}")
        if any(i not in range(4) for i in e['faq_sections']):
            raise SystemExit(f"FAQ mapping out of range #{e['n']}")
    return entries


def source_for(e,lang):
    s=NUMBER_SOURCES.get(e['n']) or SOURCE_MAP.get(e.get('source',''))
    if not s:
        return []
    return [{'name':s['name'],'url':s['url'],'note':s['es_note' if lang=='es' else 'en_note']}]


def search_intent(e,lang):
    title=normalize_text(e['es_title' if lang=='es' else 'en_title'],lang,e['n'])
    q=query_title(title,lang)
    if lang=='es':
        if e['kind'] in ('diagnostics','safety-diagnostics','identification-guide'):
            return f'Identificar las causas o señales más probables de «{q}», distinguir pistas útiles y decidir qué comprobar primero y cuándo pedir ayuda.'
        if e['kind'] in ('decision-guide','safety-guide','explanation'):
            return f'Entender «{q}» para tomar una decisión doméstica práctica y segura, reconocer límites y evitar errores comunes.'
        return f'Resolver «{q}» con una secuencia práctica, clara y segura, incluyendo las comprobaciones que evitan errores comunes.'
    if e['kind'] in ('diagnostics','safety-diagnostics','identification-guide'):
        return f'Identify the most likely causes or signs behind “{q},” use distinguishing clues, and decide what to check first and when to get help.'
    if e['kind'] in ('decision-guide','safety-guide','explanation'):
        return f'Understand “{q}” well enough to make a practical, safe household decision, recognize limits, and avoid common mistakes.'
    return f'Handle “{q}” with a practical, clear, safe sequence and the checks that prevent common mistakes.'


def build_article(e,lang):
    n=e['n']; is_es=lang=='es'
    title=normalize_text(e['es_title' if is_es else 'en_title'],lang,n)
    intro=normalize_text(e['intro_es' if is_es else 'intro_en'],lang,n)
    sections=[]
    for sec in e['sections']:
        h=normalize_text(sec[0 if is_es else 1],lang,n)
        p=normalize_text(sec[2 if is_es else 3],lang,n)
        sections.append((h,p))
    faqs=[normalize_text(q,lang,n) for q in e['faq_es' if is_es else 'faq_en']]
    slug=slugify(title); en_slug=slugify(normalize_text(e['en_title'],'en',n)); tg=f'{n}-{en_slug}'
    content='<p>'+html.escape(intro,quote=False)+'</p>'+''.join(f'<h2>{html.escape(h,quote=False)}</h2><p>{html.escape(p,quote=False)}</p>' for h,p in sections)
    faq=[{'question':q,'answer':sections[idx][1]} for q,idx in zip(faqs,e['faq_sections'])]
    qtitle=query_title(title,lang)
    return {
      'schema_version':1,'id':f'{lang}-{n}-{slug}','article_number':n,'translation_group':tg,'language':lang,
      'locale':'es-ES' if is_es else 'en-US',
      'market_context':'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if is_es else 'U.S./Canadian English; practical household guidance with locally familiar terminology and clear safety boundaries.',
      'title':title,'slug':slug,
      'seo':{'title':title,'meta_description':first_sentence(intro),'search_intent':search_intent(e,lang)},
      'excerpt':intro,
      'taxonomy':{'food_family':e['family'],'food_subcategories':[slug],'article_types':[e['kind'],e['family']],'primary_article_type':e['kind']},
      'content_html':content,'faq':faq,'sources':source_for(e,lang),
      'image':{'concept':(f'Fotografía editorial doméstica realista sobre «{qtitle}», mostrando de forma clara {sections[0][0].lower()} como acción o pista principal; entorno cotidiano natural, sin texto ni marcas.' if is_es else f'Realistic household editorial photograph about “{qtitle},” clearly showing {sections[0][0].lower()} as the main action or clue; natural home setting, no text or branding.'),'alt':qtitle},
      'status':'publish'
    },sections


def article_path(a):
    return (ES_DIR if a['language']=='es' else EN_DIR)/f"{a['article_number']}-{a['slug']}.json"


def load_existing(exclude_nums):
    vals=[]
    for d in (ES_DIR,EN_DIR):
        for p in d.glob('*.json'):
            try:a=json.loads(p.read_text(encoding='utf-8'))
            except Exception:continue
            if a.get('article_number') not in exclude_nums:
                vals.append((p,a))
    return vals


def acronym_checks(a,errors):
    text=' '.join([a['excerpt'],strip_tags(a['content_html'])]+[x['question']+' '+x['answer'] for x in a['faq']])
    lang=a['language']; n=a['article_number']
    if re.search(r'\bGFCI\b',text):
        exp='interruptor de circuito por falla a tierra (GFCI)' if lang=='es' else 'ground-fault circuit interrupter (GFCI)'
        if exp.lower() not in text.lower():errors.append(f'#{n} {lang}: GFCI not expanded on first use')
    for ac,esexp,enexp in [('CO','monóxido de carbono (CO)','carbon monoxide (CO)'),('LED','diodo emisor de luz (LED)','light-emitting diode (LED)'),('MERV','valor mínimo de eficiencia de reporte (MERV)','minimum efficiency reporting value (MERV)')]:
        if re.search(rf'\b{ac}\b',text):
            exp=esexp if lang=='es' else enexp
            if exp.lower() not in text.lower():errors.append(f'#{n} {lang}: acronym {ac} not expanded on first use')
    if re.search(r'\bHVAC\b',text):errors.append(f'#{n} {lang}: unexplained HVAC remains')


def validate(entries):
    errors=[]; warnings=[]; built={}; faq_ok=0
    existing=load_existing(set(range(711,801)))
    ids={a.get('id') for _,a in existing}; slugs={(a.get('language'),a.get('slug')) for _,a in existing}; tgs={a.get('translation_group') for _,a in existing}
    generated_tgs=set(); counts={'es':[],'en':[]}
    for e in entries:
        pair=[]
        for lang in ('es','en'):
            a,sections=build_article(e,lang); pair.append(a); p=article_path(a)
            if not p.exists():errors.append(f'Missing generated file {p.relative_to(ROOT)}');continue
            disk=json.loads(p.read_text(encoding='utf-8'))
            if disk!=a:errors.append(f'#{e["n"]} {lang}: generated file differs from deterministic build')
            if a['status']!='publish':errors.append(f'#{e["n"]} {lang}: status not publish')
            if a['id'] in ids:errors.append(f'#{e["n"]} {lang}: id collision')
            if (lang,a['slug']) in slugs:errors.append(f'#{e["n"]} {lang}: slug collision')
            if a['translation_group'] in tgs:errors.append(f'#{e["n"]}: translation_group collision with prior library')
            if len(re.findall(r'<h2>',a['content_html']))!=4:errors.append(f'#{e["n"]} {lang}: H2 count != 4')
            if len(a['faq'])!=3:errors.append(f'#{e["n"]} {lang}: FAQ count != 3')
            if len({fq['question'] for fq in a['faq']})!=3:errors.append(f'#{e["n"]} {lang}: duplicate FAQ question')
            for fq,idx in zip(a['faq'],e['faq_sections']):
                if fq['answer']!=sections[idx][1]:errors.append(f'#{e["n"]} {lang}: FAQ answer-to-section drift')
                else:faq_ok+=1
            meta=a['seo']['meta_description']
            if meta!=first_sentence(a['excerpt']) or not re.search(r'[.!?][”\"]?$',meta):errors.append(f'#{e["n"]} {lang}: meta is not a complete first editorial sentence')
            if len(meta)<35:warnings.append(f'#{e["n"]} {lang}: unusually short meta ({len(meta)} chars)')
            si=a['seo']['search_intent'].lower()
            if not re.search(r'[.!?][”\"]?$',a['seo']['search_intent']):errors.append(f'#{e["n"]} {lang}: incomplete search_intent')
            for bad in ('for how to','for why is','whether can you','para cómo','«¿','”?”'):
                if bad in si:errors.append(f'#{e["n"]} {lang}: awkward search_intent pattern {bad}')
            if sections[0][0].lower() not in a['image']['concept'].lower():errors.append(f'#{e["n"]} {lang}: image concept not topic-specific')
            prose=(' '+a['excerpt']+' '+strip_tags(a['content_html'])+' ').lower()
            if any(x.lower() in prose for x in ('HOME prioriza','HOME no plantea','En este artículo hemos decidido')):errors.append(f'#{e["n"]} {lang}: editorial metadiscourse')
            if lang=='es' and re.search(r'\b(HVAC|frass|pellets|topper|deck)\b',strip_tags(a['content_html']),re.I):errors.append(f'#{e["n"]} es: avoidable anglicism')
            acronym_checks(a,errors)
            wc=len(words(a['content_html'])); counts[lang].append(wc)
            if wc<150:errors.append(f'#{e["n"]} {lang}: body too thin ({wc} words)')
            lower=strip_tags(a['content_html']).lower()
            dangerous=('puentea el sensor','bypass the sensor','abre la caldera','open the boiler','mide tensión con','test live voltage with','ajusta la válvula de gas','adjust the gas valve')
            for bad in dangerous:
                if bad in lower and not re.search(rf'(no|do not|don\'t)[^.]*{re.escape(bad)}',lower):errors.append(f'#{e["n"]} {lang}: unsafe instruction pattern {bad}')
            built[(e['n'],lang)]=a
        if len(pair)==2:
            if pair[0]['translation_group']!=pair[1]['translation_group']:errors.append(f'#{e["n"]}: bilingual translation-group mismatch')
            if pair[0]['translation_group'] in generated_tgs:errors.append(f'#{e["n"]}: repeated translation group')
            generated_tgs.add(pair[0]['translation_group'])
    files=[]
    for d in (ES_DIR,EN_DIR):
        for p in d.glob('*.json'):
            try:a=json.loads(p.read_text(encoding='utf-8'))
            except Exception:continue
            if 711<=a.get('article_number',0)<=800:files.append((p,a))
    actual={(a['article_number'],a['language']) for _,a in files}; expected={(n,l) for n in EXPECTED for l in ('es','en')}
    if actual!=expected or len(files)!=162:errors.append(f'Target inventory mismatch: files={len(files)} missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
    for n,(target,_) in EXCLUSIONS.items():
        if any(a['article_number']==n for _,a in files):errors.append(f'Excluded #{n} generated unexpectedly')
        target_exists=target in EXPECTED or any(a.get('article_number')==target for _,a in existing)
        if not target_exists:errors.append(f'Excluded #{n} points to missing canonical target #{target}')
    return errors,warnings,built,counts,faq_ok


def tokens(a):
    return {w.lower() for w in words(a['content_html']) if len(w)>3}


def jaccard(a,b):
    x,y=tokens(a),tokens(b);return len(x&y)/max(1,len(x|y))


def prior_by_number(n,lang):
    if n in EXPECTED:return None
    d=ES_DIR if lang=='es' else EN_DIR
    for p in d.glob(f'{n}-*.json'):
        try:return json.loads(p.read_text(encoding='utf-8'))
        except Exception:return None
    return None


def write_report(entries,built,counts,faq_ok,warnings):
    watched=[]
    for a,b in WATCHED:
        vals=[]
        for lang in ('es','en'):
            aa=built.get((a,lang)) or prior_by_number(a,lang)
            bb=built.get((b,lang)) or prior_by_number(b,lang)
            if aa and bb:vals.append(jaccard(aa,bb))
        if vals:watched.append((a,b,max(vals)))
    src_pairs=sum(1 for e in entries if source_for(e,'en'))
    lines=['# Quality audit — HOME articles 711–800','', '## Result','',
      '- Canonical topic intents reviewed: **90/90**.',
      '- Editorial source entries validated: **81/81**; nine canonical duplicates are intentional exclusions.',
      '- Published unique intents: **81**; bilingual article JSON files: **162/162 PASS**.',
      f'- FAQ answer-to-section mappings: **{faq_ok}/486 PASS**.',
      '- Explicit exclusions: **#726→#277, #733→#664, #736→#568, #739→#517, #749→#481, #771→#552, #772→#642, #787→#774, #788→#718**.',
      '- Schema, language/locale, IDs, slugs, translation groups, SEO fields, status, four H2 sections, three FAQs, image metadata, acronym rules, metadiscourse checks, safety anti-patterns and depth guards all pass.',
      '- Meta descriptions are complete first editorial sentences; character truncation is not permitted.','',
      '## Depth metrics','',
      f'- Spanish body words: min **{min(counts["es"])}**, median **{int(statistics.median(counts["es"]))}**, max **{max(counts["es"])}**.',
      f'- English body words: min **{min(counts["en"])}**, median **{int(statistics.median(counts["en"]))}**, max **{max(counts["en"])}**.',
      '- The editorial standard has no fixed word-count target; the 150-word floor is only a regression guard against incomplete output.','',
      '## Inventory by range','',
      '| Range | Canonical topics | Published intents | ES | EN |','|---|---:|---:|---:|---:|',
      '| 711–730 | 20 | 19 | 19 | 19 |','| 731–750 | 20 | 16 | 16 | 16 |','| 751–770 | 20 | 20 | 20 | 20 |','| 771–790 | 20 | 16 | 16 | 16 |','| 791–800 | 10 | 10 | 10 | 10 |','',
      '## Canonical exclusions','']
    for n,(target,reason) in EXCLUSIONS.items():lines.append(f'- **#{n} → #{target}:** {reason}')
    lines += ['', '## Cannibalization diagnostics','']
    for a,b,v in watched:lines.append(f'- #{a} vs #{b}: **{v:.3f}** maximum ES/EN token Jaccard')
    lines += ['', '## Sources','', f'- Topic pairs with a directly relevant structured reference: **{src_pairs}**.', f'- Topic pairs intentionally published without a structured source because no directly supporting source was mapped: **{81-src_pairs}**.', '- No non-empty source key is silently treated as authoritative when no source mapping exists.','', '## Final editorial safeguards','', '- Spanish and English use separately authored paragraphs rather than literal machine translation.', '- FAQ answers are taken only from their explicitly mapped editorial sections and validated one by one.', '- Safety boundaries prohibit live electrical testing, gas-system adjustment, bypassing safety devices, unsafe garage-spring/cable work, hazardous chemical mixing, refrigerant handling, and unsafe structural access.', '- Pest articles prioritize identification, exclusion, sanitation, moisture control and professional escalation over indiscriminate chemical treatment.', '- Exact slug, ID and translation-group collisions with the published library are rejected.', '- Temporary generator, nine batch files, branch markers and temporary workflow must be removed before merge to `main`.']
    if warnings:lines += ['', '## Non-blocking notes','']+[f'- {w}' for w in warnings]
    REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def generate(entries):
    for e in entries:
        for lang in ('es','en'):
            a,_=build_article(e,lang);p=article_path(a);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(a,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--validate-only',action='store_true');args=ap.parse_args()
    entries=load_entries()
    if not args.validate_only:generate(entries)
    errors,warnings,built,counts,faq_ok=validate(entries)
    if errors:
        print('\n'.join('ERROR: '+e for e in errors));raise SystemExit(1)
    if not args.validate_only:write_report(entries,built,counts,faq_ok,warnings)
    print(f'PASS: 90 canonical intents reviewed; 81 unique intents published; 162 article JSON files; {faq_ok}/486 FAQ mappings valid.')
    print(f'ES words min/median/max: {min(counts["es"])}/{int(statistics.median(counts["es"]))}/{max(counts["es"])}')
    print(f'EN words min/median/max: {min(counts["en"])}/{int(statistics.median(counts["en"]))}/{max(counts["en"])}')
    if warnings:print('WARNINGS: '+' | '.join(warnings))

if __name__=='__main__':main()
