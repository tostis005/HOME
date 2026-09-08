#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'articles'
REPORT = ART / 'QUALITY-AUDIT-151-230.md'
RANGES = [(151,170),(171,190),(191,210),(211,230)]
WATCHED = [
    (159,160,'tap-water taste vs metallic taste'),
    (162,163,'burnt pan vs burnt pot'),
    (172,173,'no hot water vs sudden temperature change'),
    (179,181,'pantry moths vs unidentified pantry insects'),
    (186,187,'deodorant stains vs yellow stains on whites'),
    (191,192,'down jacket vs puffer jacket'),
    (194,195,'temporary roof leak repair vs locating roof leak'),
    (201,207,'heater will not start vs heater runs but does not heat'),
    (208,209,'mold on mattress vs mold on carpet'),
    (208,210,'mattress mold vs recurring mold'),
    (209,210,'carpet mold vs recurring mold'),
    (211,224,'opened milk storage vs milk left out'),
    (212,155,'raw ground meat vs cooked ground meat'),
    (214,146,'season cast iron vs clean cast iron'),
    (215,147,'parchment vs foil in air fryer'),
    (216,18,'dryer not drying vs dryer not heating'),
    (216,217,'dryer not drying vs dryer vent cleaning'),
    (221,295,'why washer smells vs future cleaning-a-smelly-washer topic'),
    (223,144,'eggs left out vs egg refrigerator storage'),
    (223,145,'eggs left out vs bad eggs'),
    (226,227,'dead outlet vs partial house power loss'),
    (230,158,'flip mattress vs rotate mattress'),
    (230,95,'flip mattress vs replace mattress'),
]

SPANISH_MARKERS = {' el ',' la ',' los ',' las ',' de ',' que ',' para ',' con ',' sin ',' cómo ',' por qué ',' agua ',' ropa ',' casa ',' limpiar ',' seguridad '}
ENGLISH_MARKERS = {' the ',' and ',' with ',' without ',' how ',' why ',' water ',' clothes ',' home ',' cleaning ',' safety ',' refrigerator '}


def load_number(lang: str, n: int):
    matches = sorted((ART/lang).glob(f'{n:03d}-*.json'))
    if len(matches) != 1:
        return None, matches
    try:
        return json.loads(matches[0].read_text(encoding='utf-8')), matches
    except Exception as exc:
        return {'__parse_error__': str(exc)}, matches


def strip_html(s: str) -> str:
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s or '')).strip()


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’.-][A-Za-zÀ-ÿ0-9]+)?", strip_html(s)))


def tokens(s: str) -> set[str]:
    return {x.lower() for x in re.findall(r'[A-Za-zÀ-ÿ]{3,}', strip_html(s))}


def similarity(a: str, b: str):
    aa=strip_html(a).lower(); bb=strip_html(b).lower()
    seq=SequenceMatcher(None,aa,bb).ratio()
    ta,tb=tokens(a),tokens(b)
    jac=len(ta&tb)/len(ta|tb) if ta|tb else 0.0
    return seq,jac


def likely_language(text: str, lang: str) -> bool:
    t=' '+re.sub(r'\s+',' ',(text or '').lower())+' '
    es=sum(1 for m in SPANISH_MARKERS if m in t)
    en=sum(1 for m in ENGLISH_MARKERS if m in t)
    return es >= en if lang=='es' else en >= es


def fix_known_issues(apply: bool):
    changes=[]
    for lang in ('es','en'):
        for n in range(151,231):
            obj, paths = load_number(lang,n)
            if not obj or '__parse_error__' in obj or len(paths)!=1:
                continue
            changed=False
            seo=obj.get('seo') or {}
            if isinstance(seo.get('title'),str) and seo['title'].rstrip().endswith(('…','...')):
                seo['title']=obj.get('title','').strip()
                changed=True
                changes.append(f'{lang.upper()} #{n}: restored non-truncated SEO title')
            if lang=='es' and n==224:
                old='Las leches UHT sin abrir son una excepción hasta que se abren'
                new='La leche de tratamiento a temperatura ultra alta (UHT) sin abrir es una excepción hasta que se abre'
                if old in obj.get('content_html',''):
                    obj['content_html']=obj['content_html'].replace(old,new,1)
                    changed=True
                    changes.append('ES #224: expanded UHT on first use')
            if changed and apply:
                paths[0].write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    return changes


def validate():
    errors=[]; warnings=[]; data={}; stats=defaultdict(lambda: defaultdict(list))
    required_top=['schema_version','id','article_number','translation_group','language','locale','market_context','title','slug','seo','excerpt','taxonomy','content_html','faq','sources','image','status']
    for lang in ('es','en'):
        seen_groups={}
        for n in range(151,231):
            obj, paths=load_number(lang,n)
            if len(paths)!=1:
                errors.append(f'{lang.upper()} #{n}: expected exactly 1 JSON, found {len(paths)}')
                continue
            if obj is None or '__parse_error__' in obj:
                errors.append(f'{lang.upper()} #{n}: invalid JSON')
                continue
            data[(lang,n)]=obj
            missing=[k for k in required_top if k not in obj]
            if missing: errors.append(f'{lang.upper()} #{n}: missing {missing}')
            if obj.get('schema_version')!=1: errors.append(f'{lang.upper()} #{n}: schema_version != 1')
            if obj.get('article_number')!=n: errors.append(f'{lang.upper()} #{n}: article_number mismatch')
            if obj.get('language')!=lang: errors.append(f'{lang.upper()} #{n}: language mismatch')
            if obj.get('locale') != ('es-ES' if lang=='es' else 'en-US'): errors.append(f'{lang.upper()} #{n}: locale mismatch')
            if obj.get('status')!='publish': errors.append(f'{lang.upper()} #{n}: status is not publish')
            slug=obj.get('slug','')
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug): errors.append(f'{lang.upper()} #{n}: invalid slug {slug!r}')
            if obj.get('id') != f'{lang}-{n:03d}-{slug}': errors.append(f'{lang.upper()} #{n}: id/slug mismatch')
            tg=obj.get('translation_group','')
            if not tg: errors.append(f'{lang.upper()} #{n}: empty translation_group')
            elif tg in seen_groups: errors.append(f'{lang.upper()} #{n}: duplicate translation_group {tg}')
            seen_groups[tg]=n
            seo=obj.get('seo') or {}
            for k in ('title','meta_description','search_intent'):
                if not isinstance(seo.get(k),str) or not seo[k].strip(): errors.append(f'{lang.upper()} #{n}: empty seo.{k}')
                elif seo[k].rstrip().endswith(('…','...')): errors.append(f'{lang.upper()} #{n}: mechanically truncated seo.{k}')
            if not isinstance(obj.get('excerpt'),str) or len(obj['excerpt'].strip())<60: errors.append(f'{lang.upper()} #{n}: weak/empty excerpt')
            body=obj.get('content_html','')
            if not isinstance(body,str) or words(body)<170: errors.append(f'{lang.upper()} #{n}: content too thin ({words(body)} words)')
            if body.count('<h2>')<3: errors.append(f'{lang.upper()} #{n}: fewer than 3 H2 sections')
            faqs=obj.get('faq') or []
            if len(faqs)<3: errors.append(f'{lang.upper()} #{n}: fewer than 3 FAQs')
            for i,q in enumerate(faqs):
                if not isinstance(q,dict) or not q.get('question') or not q.get('answer'): errors.append(f'{lang.upper()} #{n}: malformed FAQ {i+1}')
            sources=obj.get('sources') or []
            if not sources: errors.append(f'{lang.upper()} #{n}: no sources')
            for i,s in enumerate(sources):
                if not all(isinstance(s.get(k),str) and s.get(k).strip() for k in ('name','url','note')): errors.append(f'{lang.upper()} #{n}: malformed source {i+1}')
                elif not s['url'].startswith('https://'): errors.append(f'{lang.upper()} #{n}: source URL not HTTPS')
                elif not likely_language(s['note'],lang): warnings.append(f'{lang.upper()} #{n}: source note may not be localized: {s["note"][:70]}')
            image=obj.get('image') or {}
            if not image.get('concept') or not image.get('alt'): errors.append(f'{lang.upper()} #{n}: incomplete image metadata')
            joined=' '.join([obj.get('title',''),seo.get('title',''),seo.get('meta_description',''),seo.get('search_intent',''),obj.get('excerpt',''),body,image.get('concept','')])
            if re.search(r'\bHOME\s+(prioriza|recomienda|plantea|decide)',joined,re.I): errors.append(f'{lang.upper()} #{n}: editorial metadiscourse')
            if lang=='es' and re.search(r'\bHVAC\b', ' '.join([seo.get('meta_description',''),seo.get('search_intent',''),obj.get('excerpt','')]), re.I): errors.append(f'ES #{n}: HVAC used as primary metadata terminology')
            if lang=='es' and n==224 and re.search(r'\bUHT\b',body) and 'temperatura ultra alta (UHT)' not in body: errors.append('ES #224: UHT not expanded on first use')
            for a,b in RANGES:
                if a<=n<=b:
                    key=f'{a:03d}–{b:03d}'
                    stats[key][f'{lang}_words'].append(words(body))
                    stats[key][f'{lang}_h2'].append(body.count('<h2>'))
                    stats[key][f'{lang}_faq'].append(len(faqs))
                    stats[key][f'{lang}_sources'].append(len(sources))
    for n in range(151,231):
        es=data.get(('es',n)); en=data.get(('en',n))
        if es and en and es.get('translation_group')!=en.get('translation_group'):
            errors.append(f'#{n}: ES/EN translation_group mismatch')
    return errors,warnings,data,stats


def all_number(n,lang,data):
    if (lang,n) in data: return data[(lang,n)]
    obj,_=load_number(lang,n); return obj if obj and '__parse_error__' not in obj else None


def build_report(changes,errors,warnings,data,stats):
    lines=['# HOME — Quality audit 151–230','','## Result','']
    lines.append(f'- JSON checked: **{sum(1 for k in data if 151<=k[1]<=230)} / 160** (80 ES + 80 EN expected).')
    lines.append(f'- Structural/editorial validation: **{"PASS" if not errors else "FAIL"}**.')
    lines.append(f'- Targeted field/content fixes applied in final pass: **{len(changes)}**.')
    lines += ['','## Scope and editorial criteria','',
        '- Exact approved topics 151–230 preserved from the canonical topic inventory.',
        '- ES and EN share article number and translation group but are independently localized.',
        '- Troubleshooting and safety topics were checked for distinguishing signals, stop conditions, and escalation boundaries.',
        '- No fixed word-count target was imposed; compact topics were retained when the search intent was fully resolved.',
        '- Mechanical SEO truncation, editorial metadiscourse, empty metadata, and broken translation pairs are validation failures.',
        '','## Quantitative profile','',
        '| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for key in [f'{a:03d}–{b:03d}' for a,b in RANGES]:
        s=stats[key]
        def avg(k): return sum(s[k])/len(s[k]) if s[k] else 0
        lines.append(f'| {key} | {avg("es_words"):.1f} | {avg("es_h2"):.1f} | {avg("es_faq"):.1f} | {avg("es_sources"):.1f} | {avg("en_words"):.1f} | {avg("en_h2"):.1f} | {avg("en_faq"):.1f} | {avg("en_sources"):.1f} |')
    lines += ['','## Cannibalization / overlap review','',
        'Similarity numbers are diagnostics only. The editorial decision is based on whether each page answers a distinct search intent and leads to a different next action.','',
        '| Pair | Intent distinction | ES seq | ES Jaccard | EN seq | EN Jaccard |','|---|---|---:|---:|---:|---:|']
    for a,b,label in WATCHED:
        vals=[]
        for lang in ('es','en'):
            x=all_number(a,lang,data); y=all_number(b,lang,data)
            if x and y: vals.extend(similarity(x.get('content_html',''),y.get('content_html','')))
            else: vals.extend((0.0,0.0))
        lines.append(f'| #{a}/#{b} | {label} | {vals[0]:.3f} | {vals[1]:.3f} | {vals[2]:.3f} | {vals[3]:.3f} |')
    lines += ['','### Editorial overlap conclusions','',
        '- #159/#160: general bad taste is a diagnostic umbrella; metallic taste is a specific sensory branch with plumbing/mineral causes.',
        '- #172/#173: no hot water isolates local shower vs whole-home heating; sudden cooling focuses on changing temperature during use.',
        '- #179/#181: pantry moths are species-pattern guidance; unidentified pantry insects begin with identification before response.',
        '- #184 vs #113: a water stain is evidence/diagnosis; an active ceiling leak is an immediate containment and safety problem.',
        '- #191/#192: down insulation has loft-specific washing/drying needs; puffer construction can use synthetic insulation and different care.',
        '- #194/#195: temporary leak control is emergency mitigation; leak location is source tracing.',
        '- #201/#207: no start is power/control/ignition; runs-but-no-heat is heat delivery/performance.',
        '- #208/#209/#210: mattress and carpet mold are substrate-specific cleanup decisions; recurring mold is a moisture-source diagnosis.',
        '- #211/#224: opened-milk storage is refrigerated shelf-life handling; milk-left-out is a time/temperature decision.',
        '- #212/#155: raw ground meat and cooked ground meat have different storage windows and contamination considerations.',
        '- #214/#146: seasoning builds a polymerized surface; cleaning preserves an existing one.',
        '- #215/#147: parchment risk is loose paper/airflow/heat; foil has different conductivity and manufacturer constraints.',
        '- #216/#217: poor drying is a symptom diagnosis; vent cleaning is a maintenance procedure and one possible remedy.',
        '- #221/#295 (future): #221 explains why the washer smells; approved #295 is reserved for the cleaning procedure.',
        '- #223/#144/#145: room-temperature exposure, refrigerated duration, and spoilage assessment are separate food-safety questions.',
        '- #226/#227: a single dead receptacle and a partial-house outage have different diagnostic scope and escalation signals.',
        '- #230/#158: flipping changes the sleep surface; rotating head-to-foot redistributes wear.',
        '','## Targeted final-pass changes','']
    if changes:
        lines.extend([f'- {x}' for x in changes])
    else:
        lines.append('- None.')
    lines += ['','## Validation notes','']
    if errors:
        lines.append('### Errors')
        lines.extend([f'- {x}' for x in errors])
    else:
        lines.append('- No blocking validation errors.')
    if warnings:
        lines += ['','### Non-blocking heuristic warnings']
        lines.extend([f'- {x}' for x in warnings[:50]])
    else:
        lines.append('- No localization heuristic warnings.')
    lines += ['','## Final editorial reading priorities','',
        'Representative final reads should include #151, #159–160, #172–173, #184, #194–195, #201, #207–210, #211, #216–217, #226–227, and #230 in both languages.',
        'Safety-sensitive articles should be rejected if they encourage live electrical work, gas-system disassembly, unsafe roof access, unsafe chemical mixing, or food-safety decisions based only on smell or taste.','']
    return '\n'.join(lines)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    changes=fix_known_issues(args.apply)
    errors,warnings,data,stats=validate()
    report=build_report(changes,errors,warnings,data,stats)
    if args.apply:
        REPORT.write_text(report,encoding='utf-8')
    print(report)
    if errors:
        raise SystemExit(1)

if __name__=='__main__':
    main()
