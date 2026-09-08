#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
DUP={477:402,480:472,499:263}
expected=[n for n in range(471,551) if n not in DUP]
errors=[]

for lang in ('es','en'):
    files=[]
    for n in expected:
        matches=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(matches)!=1:
            errors.append(f'{lang} #{n}: expected one JSON, found {len(matches)}')
            continue
        files.append(matches[0])
        data=json.loads(matches[0].read_text(encoding='utf-8'))
        if data.get('status')!='publish': errors.append(f'{lang} #{n}: status not publish')
        if len(data.get('faq',[]))!=3: errors.append(f'{lang} #{n}: FAQ count != 3')
        if len(data.get('seo',{}).get('meta_description',''))>190: errors.append(f'{lang} #{n}: meta description >190 chars')
        if lang=='en':
            intent=data.get('seo',{}).get('search_intent','')
            bad=[r'\bIdentify why (?:is|are|do|does|did|can|should|will|won\'t)\b',r'\bDecide whether (?:can|should|is|are|do|does)\b',r'\bfor how to\b']
            for pat in bad:
                if re.search(pat,intent,re.I): errors.append(f'en #{n}: artificial search_intent: {intent}')
        if lang=='es':
            intent=data.get('seo',{}).get('search_intent','')
            if re.search(r'\bpara cómo\b',intent,re.I): errors.append(f'es #{n}: artificial search_intent: {intent}')
    if len(files)!=77: errors.append(f'{lang}: expected 77 publishable JSONs, found {len(files)}')
    for n in DUP:
        if list((ART/lang).glob(f'{n:03d}-*.json')):
            errors.append(f'{lang} #{n}: canonical duplicate must not emit JSON')

# Verify canonical targets for blocked duplicates still exist.
for lang,target in [('es',402),('en',402),('es',263),('en',263)]:
    if not list((ART/lang).glob(f'{target:03d}-*.json')):
        errors.append(f'{lang} canonical target #{target} missing')
# #472 is generated inside this block.
for lang in ('es','en'):
    if not list((ART/lang).glob('472-*.json')):
        errors.append(f'{lang} canonical target #472 missing')

if errors:
    print(f'FINAL HOME 471-550 VALIDATION FAILED: {len(errors)} error(s)')
    for e in errors: print('ERROR:',e)
    raise SystemExit(1)
print('FINAL HOME 471-550 VALIDATION PASS: 154/154 JSON, 462/462 FAQ, 3 duplicate exceptions, 0 metadata regressions')
