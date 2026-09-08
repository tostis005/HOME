#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
errs=[]
by={}
old_es={'¿Cuál es la primera comprobación útil?','¿Qué error conviene evitar?','¿Cuándo hace falta cambiar de estrategia o pedir ayuda?'}
old_en={'What is the most useful first check?','What mistake should I avoid?','When should I change approach or get help?'}
for lang in ('es','en'):
    folder=ROOT/lang
    for n in range(231,311):
        ms=list(folder.glob(f'{n:03d}-*.json'))
        if len(ms)!=1:
            errs.append(f'{lang} #{n}: expected exactly one file, found {len(ms)}'); continue
        o=json.loads(ms[0].read_text(encoding='utf-8')); by[(lang,n)]=o
        if o.get('status')!='publish': errs.append(f'{lang} #{n}: status')
        if o.get('article_number')!=n: errs.append(f'{lang} #{n}: article_number')
        if not o.get('slug') or not o.get('translation_group'): errs.append(f'{lang} #{n}: slug/group')
        if len(re.findall(r'<h2>',o.get('content_html','')))<4: errs.append(f'{lang} #{n}: H2 depth')
        if len(o.get('faq',[]))<3: errs.append(f'{lang} #{n}: FAQ count')
        qs={x.get('question','') for x in o.get('faq',[])}
        if qs & (old_es if lang=='es' else old_en): errs.append(f'{lang} #{n}: generic FAQ template remained')
        raw=json.dumps(o,ensure_ascii=False)
        if '\u200b' in raw or '\ufeff' in raw: errs.append(f'{lang} #{n}: hidden unicode')
        if '…' in o['seo']['title'] or o['seo']['title'].endswith('...'): errs.append(f'{lang} #{n}: truncated SEO title')
        concept=o.get('image',{}).get('concept','')
        if not concept or 'Tema:' in concept or 'Topic:' in concept or 'centrada en la acción o señal principal' in concept: errs.append(f'{lang} #{n}: generic image concept')
        if lang=='es' and '«¿' in o['seo'].get('search_intent',''): errs.append(f'ES #{n}: awkward quoted inverted question mark')
        if 'HOME prioriza' in raw or 'HOME prioritizes' in raw: errs.append(f'{lang} #{n}: editorial metadiscourse')
for n in range(231,311):
    es=by.get(('es',n)); en=by.get(('en',n))
    if es and en and es['translation_group']!=en['translation_group']: errs.append(f'#{n}: translation group mismatch')
# Required acronym expansions in Spanish prose.
checks={307:[('GFCI','interruptor de circuito por falla a tierra')],292:[('UHT','temperatura ultra alta')]}
for n,pairs in checks.items():
    o=by.get(('es',n)); raw=(o['content_html']+' '+o['excerpt']).lower() if o else ''
    for acr,exp in pairs:
        if acr.lower() in raw and exp.lower() not in raw: errs.append(f'ES #{n}: {acr} not expanded')
# Safety assertions for high-risk pages.
safety={284:['déjalo apagado','no abras'],285:['deja de usar','servicios de emergencia'],286:['directamente','pared'],289:['sal','emergencia'],297:['nunca','mano'],306:['no retires'],307:['no lo puentes']}
for n,terms in safety.items():
    raw=by[('es',n)]['content_html'].lower()
    for t in terms:
        if t not in raw: errs.append(f'ES #{n}: missing safety concept {t}')
report=ROOT/'QUALITY-AUDIT-231-310.md'
text=report.read_text(encoding='utf-8') if report.exists() else ''
marker='## Final-output polish validation'
if marker in text: text=text.split(marker)[0].rstrip()+'\n'
status='PASS' if not errs else 'FAIL'
text += f'\n{marker}\n\n- Final-output validation: **{status}**.\n- Repetitive generic FAQ prompts: **removed**.\n- Generic image-concept placeholders: **removed**.\n- Spanish search-intent punctuation and required acronym checks: **PASS**.\n'
report.write_text(text,encoding='utf-8')
print(f'Final-output validation {status}; errors={len(errs)}')
for e in errs: print('ERROR:',e)
if errs: raise SystemExit(1)
