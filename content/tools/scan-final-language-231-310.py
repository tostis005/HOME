#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
errs=[]
for lang in ('es','en'):
  for n in range(231,311):
    ms=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(ms)!=1:
      errs.append(f'{lang} #{n}: file count {len(ms)}'); continue
    o=json.loads(ms[0].read_text(encoding='utf-8'))
    intent=o['seo'].get('search_intent','')
    if lang=='es' and re.search(r'\bpara cómo\b',intent,re.I): errs.append(f'ES #{n}: unnatural para cómo in search_intent')
    if lang=='en' and re.search(r'\bfor how to\b',intent,re.I): errs.append(f'EN #{n}: unnatural for how to in search_intent')
    for f in o.get('faq',[]):
      q=f.get('question','')
      if lang=='es' and re.search(r'\bal\s+\w+[^?]{0,80}\s+y\s+(deja|revisa|usa|limpia|seca|retira|busca|comprueba|mantén|ejecuta)\b',q,re.I): errs.append(f'ES #{n}: mixed infinitive/imperative FAQ grammar: {q}')
      if re.search(r'\b(co|gfci|uht)\b',q) and any(a in q.upper() for a in ['CO','GFCI','UHT']):
        # Catch lowercase rendering only when the article heading carried the acronym.
        if ' co ' in (' '+q+' ') or ' gfci ' in (' '+q+' ') or ' uht ' in (' '+q+' '): errs.append(f'{lang} #{n}: lowercased acronym in FAQ: {q}')
# Required first-use expansion in Spanish prose/excerpt.
requirements={289:('CO','monóxido de carbono (CO)'),307:('GFCI','interruptor de circuito por falla a tierra (GFCI)'),292:('UHT','temperatura ultra alta (UHT)')}
for n,(acr,exp) in requirements.items():
  o=json.loads(next((ROOT/'es').glob(f'{n:03d}-*.json')).read_text(encoding='utf-8'))
  raw=o['excerpt']+' '+o['content_html']
  if acr in raw and exp.lower() not in raw.lower(): errs.append(f'ES #{n}: {acr} not expanded as {exp}')
if errs:
  print(f'Final language scan FAIL; errors={len(errs)}')
  for e in errs: print('ERROR:',e)
  raise SystemExit(1)
print('Final language scan PASS; errors=0')
