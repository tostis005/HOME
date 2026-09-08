#!/usr/bin/env python3
from pathlib import Path
import json,re,html

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
OUT=ROOT/'tools'/'FAQ-REVIEW-471-550.md'
DUP={477,480,499}

def sections(data):
    pairs=re.findall(r'<h2>(.*?)</h2><p>(.*?)</p>',data['content_html'])
    return [(html.unescape(re.sub(r'<[^>]+>','',h)).strip(),html.unescape(re.sub(r'<[^>]+>','',p)).strip()) for h,p in pairs]

rows=[]
for n in range(471,551):
    if n in DUP: continue
    cells=[f'#{n}']
    for lang in ('es','en'):
        fs=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(fs)!=1:
            raise SystemExit(f'{lang} #{n}: expected one article')
        d=json.loads(fs[0].read_text(encoding='utf-8'))
        sec=sections(d)
        mapped=[]
        for faq in d['faq']:
            ans=faq['answer'].strip()
            hits=[i+1 for i,(_,p) in enumerate(sec) if p==ans]
            idx=hits[0] if hits else 0
            heading=sec[idx-1][0] if idx else 'NO EXACT SECTION MATCH'
            q=faq['question'].replace('|','\\|')
            h=heading.replace('|','\\|')
            mapped.append(f'Q: {q} → H2 {idx}: {h}')
        cells.append('<br>'.join(mapped))
    rows.append('| '+' | '.join(cells)+' |')

text=['# HOME FAQ alignment review 471–550','','This is a temporary human-review aid. Each FAQ answer must map exactly to the article section shown; the reviewer still checks that the question is semantically answered by that section.','','| Topic | ES mappings | EN mappings |','|---|---|---|']+rows
OUT.write_text('\n'.join(text)+'\n',encoding='utf-8')
print(f'Wrote {OUT} with {len(rows)} topic rows')
