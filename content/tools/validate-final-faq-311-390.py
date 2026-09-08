#!/usr/bin/env python3
from pathlib import Path
import json,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'; TOOLS=ROOT/'tools'; errs=[]; all_q={'es':[],'en':[]}
MAP={}
for fn in ('faq-map-311-350.json','faq-map-351-390.json'):
    MAP.update(json.loads((TOOLS/fn).read_text(encoding='utf-8')))
if set(MAP)!={str(n) for n in range(311,391)}:
    errs.append('FAQ map does not cover exactly 311-390')
BAD=[
    re.compile(r'^Why should I avoid (?:rely|flush|assume|mix|push|overload|line|wait|machine-dry)\b',re.I),
    re.compile(r'^What should I know about\b',re.I),
    re.compile(r'^Can in\b',re.I),
    re.compile(r'^Why is (?:see|know|reassemble|sand)\b',re.I),
    re.compile(r'^¿Qué debo saber sobre\b',re.I),
    re.compile(r'^¿Cómo conviene (?:empezar|usar|comprobar|revisar|limpiar|abrir|cerrar|mirar|buscar|retirar|secar)\b',re.I),
]
for n in range(311,391):
    entry=MAP.get(str(n),{})
    for lang in ('es','en'):
        files=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(files)!=1:
            errs.append(f'{lang} #{n}: expected one article, found {len(files)}'); continue
        o=json.loads(files[0].read_text(encoding='utf-8'))
        actual=[x.get('question','').strip() for x in o.get('faq',[])]
        expected=entry.get(lang,[])
        if actual!=expected:
            errs.append(f'{lang} #{n}: FAQ questions do not match approved editorial map')
        if len(actual)!=3 or len(set(actual))!=3:
            errs.append(f'{lang} #{n}: FAQ questions must be three unique entries')
        for i,f in enumerate(o.get('faq',[]),1):
            q=f.get('question','').strip(); a=f.get('answer','').strip()
            all_q[lang].append(q)
            if not q.endswith('?'): errs.append(f'{lang} #{n} FAQ{i}: question lacks ?')
            if len(re.findall(r'\w+',a,re.UNICODE))<8: errs.append(f'{lang} #{n} FAQ{i}: answer too short')
            for pat in BAD:
                if pat.search(q): errs.append(f'{lang} #{n} FAQ{i}: blocked mechanical grammar: {q}')
for lang in ('es','en'):
    counts=Counter(all_q[lang])
    dup=[q for q,c in counts.items() if c>1]
    if dup: errs.append(f'{lang}: duplicate FAQ questions: {dup[:8]}')
    starters=Counter(' '.join(q.lstrip('¿').split()[:3]).lower() for q in all_q[lang])
    if starters and starters.most_common(1)[0][1] > 45:
        errs.append(f'{lang}: one FAQ starter is overused: {starters.most_common(1)[0]}')
report=(ART/'QUALITY-AUDIT-311-390.md').read_text(encoding='utf-8')
if 'All **480 FAQ questions** were rewritten' not in report:
    errs.append('audit report lacks final FAQ editorial-pass record')
print(f'Final FAQ audit: questions={sum(len(v) for v in all_q.values())} errors={len(errs)}')
for e in errs: print('ERROR:',e)
if errs: raise SystemExit(1)
print('FINAL FAQ PASS 480/480')
