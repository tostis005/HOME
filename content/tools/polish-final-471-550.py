#!/usr/bin/env python3
from pathlib import Path
import json,re,html

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
DUP={477,480,499}
FAQ_SECTION_MAP={
    484:[2,3,4],
    489:[1,3,4],
    498:[1,3,4],
    500:[1,3,4],
    512:[2,3,4],
    514:[1,2,4],
    515:[1,3,4],
    520:[1,3,4],
    531:[1,3,4],
    542:[1,3,4],
}
FAQ_Q1_514={
    'es':'¿Qué conviene retirar o lavar primero al quitar olor a tabaco?',
    'en':'What should I remove or wash first when tackling cigarette smoke odor?',
}

def get_sections(content_html):
    pairs=re.findall(r'<h2>(.*?)</h2><p>(.*?)</p>',content_html)
    return [(html.unescape(re.sub(r'<[^>]+>','',h)).strip(), html.unescape(re.sub(r'<[^>]+>','',p)).strip()) for h,p in pairs]

for lang in ('es','en'):
    for n in range(471,551):
        if n in DUP:
            continue
        files=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(files)!=1:
            raise SystemExit(f'Expected one {lang.upper()} article for #{n}, found {len(files)}')
        p=files[0]
        data=json.loads(p.read_text(encoding='utf-8'))
        title=data['title'].strip()

        # Natural search-intent metadata.
        if lang=='en':
            if title.startswith('Why '):
                question=(title.split('?',1)[0]+'?') if '?' in title else title
                data['seo']['search_intent']=f'Identify the likely causes behind “{question}” using observable clues to choose the first checks and know when to stop or get professional help.'
            elif title.startswith('Can '):
                data['seo']['search_intent']=f'Resolve the question “{title}” using food-safety, condition, compatibility, and time limits instead of a one-size-fits-all rule.' if data.get('taxonomy',{}).get('food_family')=='food-safety' else f'Resolve the question “{title}” using practical criteria for safety, condition, compatibility, and results.'
            elif title.startswith('Should '):
                data['seo']['search_intent']=f'Resolve the question “{title}” using practical criteria for safety, storage conditions, quality, and the reader’s actual situation.'
        elif n in (520,521,522):
            question=title.split('?',1)[0].lstrip('¿').strip()
            data['seo']['search_intent']=f'Identificar las causas probables de «{question}», usar señales observables para decidir qué comprobar primero y saber cuándo corresponde detenerse o pedir ayuda.'

        # Keep canonical titles while removing awkward punctuation from accessibility/image metadata.
        if n in (520,521,522):
            if lang=='en':
                clean_alt=title.replace('? Common Causes and Fixes',': common causes and fixes')
                data['image']['alt']=clean_alt
                data['image']['concept']=data['image']['concept'].replace('? Common Causes and Fixes',': common causes and fixes')
            else:
                clean_alt=title.lstrip('¿').replace('? Causas comunes y soluciones',': causas comunes y soluciones')
                data['image']['alt']=clean_alt
                data['image']['concept']=data['image']['concept'].replace('? Causas comunes y soluciones',': causas comunes y soluciones')

        # Final prose cleanup after expanding HVAC shorthand in preflight.
        if lang=='en' and n==513:
            data['content_html']=data['content_html'].replace(
                '<p>heating and cooling system and air-purifier filters can collect smoke particles and later contribute odor or restrict airflow.',
                '<p>Heating and cooling system filters and air-purifier filters can collect smoke particles and later contribute odor or restrict airflow.'
            )
        if lang=='en' and n==514:
            data['content_html']=data['content_html'].replace(
                '<p>Replace heating and cooling system and air-purifier filters and clean accessible grilles.',
                '<p>Replace filters in the heating and cooling system and in air purifiers, and clean accessible grilles.'
            )

        # Human-reviewed FAQ wording/alignment corrections.
        if n==514:
            data['faq'][0]['question']=FAQ_Q1_514[lang]
        if n in FAQ_SECTION_MAP:
            sections=get_sections(data['content_html'])
            if len(sections)!=4:
                raise SystemExit(f'{lang} #{n}: expected 4 sections, found {len(sections)}')
            for i,section_no in enumerate(FAQ_SECTION_MAP[n]):
                data['faq'][i]['answer']=sections[section_no-1][1]

        p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

print('Polished final HOME 471-550 metadata, prose, and human-reviewed FAQ alignment')
