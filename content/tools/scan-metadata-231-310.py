#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
errs=[]
for lang in ('es','en'):
  for n in range(231,311):
    ms=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(ms)!=1:
      errs.append(f'{lang} #{n}: file count'); continue
    o=json.loads(ms[0].read_text(encoding='utf-8'))
    alt=o.get('image',{}).get('alt','')
    if not alt: errs.append(f'{lang} #{n}: empty image alt')
    if lang=='es' and alt[:1] in '¿¡': errs.append(f'ES #{n}: image alt starts with inverted punctuation')
    intent=o.get('seo',{}).get('search_intent','')
    if '«¿' in intent or '“why is my garbage disposal not working?' in intent.lower(): errs.append(f'{lang} #{n}: awkward search-intent punctuation')
    if lang=='es' and re.search(r'\bpara cómo\b',intent,re.I): errs.append(f'ES #{n}: para cómo')
    if lang=='en' and re.search(r'\bfor how to\b',intent,re.I): errs.append(f'EN #{n}: for how to')
    if lang=='es' and n==280 and 'son emergencia</h2>' in o['content_html']: errs.append('ES #280: unfinished emergency heading grammar')
if errs:
  print(f'Metadata polish scan FAIL; errors={len(errs)}')
  for e in errs: print('ERROR:',e)
  raise SystemExit(1)
print('Metadata polish scan PASS; errors=0')
