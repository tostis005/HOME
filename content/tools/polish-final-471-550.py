#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'/'en'
DUP={477,480,499}

for n in range(471,551):
    if n in DUP:
        continue
    files=list(ART.glob(f'{n:03d}-*.json'))
    if len(files)!=1:
        raise SystemExit(f'Expected one EN article for #{n}, found {len(files)}')
    p=files[0]
    data=json.loads(p.read_text(encoding='utf-8'))
    title=data['title'].strip()
    if title.startswith('Why '):
        data['seo']['search_intent']=f'Identify the likely causes of “{title},” use observable clues to choose the first checks, and know when to stop or get professional help.'
    elif title.startswith('Can '):
        data['seo']['search_intent']=f'Resolve the question “{title}” using food-safety, condition, compatibility, and time limits instead of a one-size-fits-all rule.' if data.get('taxonomy',{}).get('food_family')=='food-safety' else f'Resolve the question “{title}” using practical criteria for safety, condition, compatibility, and results.'
    elif title.startswith('Should '):
        data['seo']['search_intent']=f'Resolve the question “{title}” using practical criteria for safety, storage conditions, quality, and the reader’s actual situation.'
    p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

print('Polished final English search-intent metadata for HOME 471-550')
