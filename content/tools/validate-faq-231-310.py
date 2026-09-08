#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
errs=[]
blocked_es=('¿Qué debo tener en cuenta al','¿Por qué es importante «','¿Por qué conviene evitar «','¿Cuál es la primera comprobación útil?','¿Qué error conviene evitar?')
blocked_en=('Why does “','What is the most useful first check?','What mistake should I avoid?','When should I change approach or get help?')
questions=[]
for lang in ('es','en'):
  for n in range(231,311):
    ms=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(ms)!=1:
      errs.append(f'{lang} #{n}: file count'); continue
    o=json.loads(ms[0].read_text(encoding='utf-8'))
    faqs=o.get('faq',[])
    if len(faqs)!=3: errs.append(f'{lang} #{n}: FAQ count {len(faqs)}')
    for f in faqs:
      q=f.get('question','').strip(); questions.append((lang,n,q))
      if not q.endswith('?'): errs.append(f'{lang} #{n}: FAQ is not a question: {q}')
      for bad in (blocked_es if lang=='es' else blocked_en):
        if bad in q: errs.append(f'{lang} #{n}: templated FAQ wording: {q}')
      if '«No ' in q or '“Do not ' in q: errs.append(f'{lang} #{n}: quoted heading leaked into FAQ: {q}')
      if lang=='es' and re.search(r'\b(co|gfci|uht)\b',q): errs.append(f'ES #{n}: acronym lowercased in FAQ: {q}')
# Ensure no single exact FAQ prompt is repeated excessively across the block.
from collections import Counter
counts=Counter(q for _,_,q in questions)
for q,c in counts.items():
  if c>2: errs.append(f'FAQ repeated {c} times: {q}')
if errs:
  print(f'FAQ humanization validation FAIL; errors={len(errs)}')
  for e in errs: print('ERROR:',e)
  raise SystemExit(1)
print('FAQ humanization validation PASS; errors=0')
