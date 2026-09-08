#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
DUP={477,480,499}

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
        if lang=='en':
            if title.startswith('Why '):
                question=(title.split('?',1)[0]+'?') if '?' in title else title
                data['seo']['search_intent']=f'Identify the likely causes behind “{question}” using observable clues to choose the first checks and know when to stop or get professional help.'
            elif title.startswith('Can '):
                data['seo']['search_intent']=f'Resolve the question “{title}” using food-safety, condition, compatibility, and time limits instead of a one-size-fits-all rule.' if data.get('taxonomy',{}).get('food_family')=='food-safety' else f'Resolve the question “{title}” using practical criteria for safety, condition, compatibility, and results.'
            elif title.startswith('Should '):
                data['seo']['search_intent']=f'Resolve the question “{title}” using practical criteria for safety, storage conditions, quality, and the reader’s actual situation.'
            if n in (520,521,522):
                data['image']['alt']=title.replace('? Common Causes and Fixes',': common causes and fixes')
        else:
            if n in (520,521,522):
                question=title.split('?',1)[0].lstrip('¿').strip()
                data['seo']['search_intent']=f'Identificar las causas probables de «{question}», usar señales observables para decidir qué comprobar primero y saber cuándo corresponde detenerse o pedir ayuda.'
                data['image']['alt']=title.lstrip('¿').replace('? Causas comunes y soluciones',': causas comunes y soluciones')
        p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

print('Polished final HOME 471-550 metadata and diagnostic-title punctuation')
