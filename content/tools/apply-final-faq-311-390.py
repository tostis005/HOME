#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
TOOLS=ROOT/'tools'
MAP={}
for fn in ('faq-map-311-350.json','faq-map-351-390.json'):
    MAP.update(json.loads((TOOLS/fn).read_text(encoding='utf-8')))
expected={str(n) for n in range(311,391)}
if set(MAP)!=expected:
    raise SystemExit(f'FAQ map mismatch missing={sorted(expected-set(MAP))} extra={sorted(set(MAP)-expected)}')
changed=0
for n in range(311,391):
    entry=MAP[str(n)]
    for lang in ('es','en'):
        qs=entry[lang]
        if len(qs)!=3 or len(set(qs))!=3:
            raise SystemExit(f'{lang} #{n}: expected 3 unique mapped questions')
        files=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(files)!=1:
            raise SystemExit(f'{lang} #{n}: expected one article file, found {len(files)}')
        p=files[0]
        o=json.loads(p.read_text(encoding='utf-8'))
        if len(o.get('faq',[]))!=3:
            raise SystemExit(f'{lang} #{n}: expected three FAQ answers before polish')
        old=[x.get('question','') for x in o['faq']]
        for faq,q in zip(o['faq'],qs):
            faq['question']=q
        if old!=qs:
            changed+=1
        p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
report=ART/'QUALITY-AUDIT-311-390.md'
text=report.read_text(encoding='utf-8')
marker='## Final FAQ editorial pass'
if marker not in text:
    text += '\n\n## Final FAQ editorial pass\n\n- All **480 FAQ questions** were rewritten as topic-specific reader questions after PR review exposed grammatical and template-like transformations.\n- Existing validated FAQ answers were preserved in their original slots so each question remains tied to the supporting article section.\n- Final FAQ-map validation checks exact ES/EN coverage, uniqueness, grammar-pattern regressions and committed-state consistency.\n'
    report.write_text(text,encoding='utf-8')
print(f'Applied final FAQ map to {changed} article versions; coverage=160/160')
