#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'articles'; errs=[]; by={}; ids=[]; slugs=[]
def word_count(html):
    text=re.sub(r'<[^>]+>',' ',html)
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",text))
for lang in ('es','en'):
    for n in range(311,391):
        fs=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(fs)!=1:
            errs.append(f'{lang} #{n}: expected one JSON, found {len(fs)}'); continue
        try: o=json.loads(fs[0].read_text(encoding='utf-8'))
        except Exception as e: errs.append(f'{lang} #{n}: invalid JSON {e}'); continue
        by[(lang,n)]=o; ids.append(o.get('id')); slugs.append((lang,o.get('slug')))
        if o.get('article_number')!=n or o.get('language')!=lang or o.get('status')!='publish': errs.append(f'{lang} #{n}: identity/status mismatch')
        if o.get('locale')!=('es-ES' if lang=='es' else 'en-US'): errs.append(f'{lang} #{n}: locale mismatch')
        if word_count(o.get('content_html',''))<145: errs.append(f'{lang} #{n}: content below depth floor')
        if o.get('content_html','').count('<h2>')!=4: errs.append(f'{lang} #{n}: expected 4 H2')
        if len(o.get('faq',[]))!=3: errs.append(f'{lang} #{n}: expected 3 FAQ')
        seo=o.get('seo',{})
        if not all(seo.get(k) for k in ('title','meta_description','search_intent')): errs.append(f'{lang} #{n}: incomplete SEO')
        if '…' in seo.get('title','') or seo.get('title','').endswith('...'): errs.append(f'{lang} #{n}: truncated SEO title')
        raw=json.dumps(o,ensure_ascii=False)
        for bad in ('HOME prioriza','HOME prioritizes','En este artículo hemos decidido'):
            if bad in raw: errs.append(f'{lang} #{n}: editorial metadiscourse')
        if lang=='es':
            if re.search(r'\bHVAC\b',raw): errs.append(f'ES #{n}: HVAC left as primary Spanish wording')
            if 'inverter' in raw.lower(): errs.append(f'ES #{n}: avoidable inverter anglicism')
            if 'topper' in raw.lower(): errs.append(f'ES #{n}: avoidable topper anglicism')
if len(by)!=160: errs.append(f'expected 160 article versions, parsed {len(by)}')
if len(ids)!=len(set(ids)): errs.append('duplicate article id')
if len(slugs)!=len(set(slugs)): errs.append('duplicate slug within language')
for n in range(311,391):
    es=by.get(('es',n)); en=by.get(('en',n))
    if es and en and es.get('translation_group')!=en.get('translation_group'): errs.append(f'#{n}: translation_group mismatch')
checks={367:[('MERV','Minimum Efficiency Reporting Value')],372:[('LED','diodos emisores de luz')],388:[('GFCI','falla a tierra'),('GFCI','Norteamérica')]}
for n,pairs in checks.items():
    o=by.get(('es',n)); raw=(o.get('excerpt','')+' '+o.get('content_html','')) if o else ''
    for acr,exp in pairs:
        if acr in raw and exp.lower() not in raw.lower(): errs.append(f'ES #{n}: {acr} lacks explanation/context {exp}')
risk={316:['no uses llama','cierra el suministro'],355:['prioriza seguridad'],372:['no retires la placa','electricista'],378:['deja la secadora fuera de servicio'],380:['no pruebes la comida'],388:['no lo puentes','electricista'],389:['deja de usarlo','electricista'],390:['no retires la placa','electricista']}
for n,terms in risk.items():
    o=by.get(('es',n)); raw=(o.get('excerpt','')+' '+o.get('content_html','')).lower() if o else ''
    for t in terms:
        if t not in raw: errs.append(f'ES #{n}: safety concept missing: {t}')
print(f'Full final-state audit: articles={len(by)} errors={len(errs)}')
for e in errs: print('ERROR:',e)
if errs: raise SystemExit(1)
print('FINAL STATE PASS 160/160')
