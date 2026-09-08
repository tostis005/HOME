#!/usr/bin/env python3
from pathlib import Path
import json,re,html

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
DUP={477:402,480:472,499:263}
expected=[n for n in range(471,551) if n not in DUP]
EXPECTED_FAQ_SECTIONS={
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
EXPECTED_Q1_514={
    'es':'¿Qué conviene retirar o lavar primero al quitar olor a tabaco?',
    'en':'What should I remove or wash first when tackling cigarette smoke odor?',
}
errors=[]

def sections(data):
    pairs=re.findall(r'<h2>(.*?)</h2><p>(.*?)</p>',data.get('content_html',''))
    return [(html.unescape(re.sub(r'<[^>]+>','',h)).strip(),html.unescape(re.sub(r'<[^>]+>','',p)).strip()) for h,p in pairs]

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

        sec=sections(data)
        if len(sec)!=4:
            errors.append(f'{lang} #{n}: expected 4 H2 sections, found {len(sec)}')
        else:
            for i,faq in enumerate(data.get('faq',[])):
                answer=faq.get('answer','').strip()
                exact=[j+1 for j,(_,p) in enumerate(sec) if p==answer]
                if not exact:
                    errors.append(f'{lang} #{n} FAQ {i+1}: answer does not exactly match any article section')
                if n in EXPECTED_FAQ_SECTIONS and exact and exact[0]!=EXPECTED_FAQ_SECTIONS[n][i]:
                    errors.append(f'{lang} #{n} FAQ {i+1}: expected section {EXPECTED_FAQ_SECTIONS[n][i]}, got {exact[0]}')

        if n==514 and data.get('faq',[{}])[0].get('question')!=EXPECTED_Q1_514[lang]:
            errors.append(f'{lang} #514: reviewed FAQ 1 wording regressed')

        if lang=='en':
            intent=data.get('seo',{}).get('search_intent','')
            bad=[r'\bIdentify why (?:is|are|do|does|did|can|should|will|won\'t)\b',r'\bDecide whether (?:can|should|is|are|do|does)\b',r'\bfor how to\b']
            for pat in bad:
                if re.search(pat,intent,re.I): errors.append(f'en #{n}: artificial search_intent: {intent}')
            if n==513 and '<p>heating and cooling system' in data.get('content_html',''):
                errors.append('en #513: paragraph begins with lowercase heating and cooling system')
            if 'HVAC' in data.get('content_html',''):
                errors.append(f'en #{n}: unexplained HVAC remains in article prose')
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
for lang in ('es','en'):
    if not list((ART/lang).glob('472-*.json')):
        errors.append(f'{lang} canonical target #472 missing')

if errors:
    print(f'FINAL HOME 471-550 VALIDATION FAILED: {len(errors)} error(s)')
    for e in errors: print('ERROR:',e)
    raise SystemExit(1)
print('FINAL HOME 471-550 VALIDATION PASS: 154/154 JSON, 462/462 FAQ, reviewed FAQ alignment checks, 3 duplicate exceptions, 0 metadata regressions')
