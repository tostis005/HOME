#!/usr/bin/env python3
from pathlib import Path
import json,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'articles'; errs=[]; qs={'es':[],'en':[]}; ids=[]; slugs=[]
def words(h): return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",re.sub(r'<[^>]+>',' ',h))
by={}
ES_BAD=re.compile(r'^¿Qué (?:indica|debo saber sobre) (?:confirma|empieza|usa|evita|comprueba|revisa|mira|busca|retira|limpia|trabaja|seca|deja|abre|cierra|añade|reduce|controla|observa|distingue|identifica|protege|guarda|lava|aclara|enfría|congela|descongela|recalienta|mantén|pulsa|desconecta|apaga|marca|localiza|sigue|aspira|aplica|reserva|pon|separa|agrupa)\b',re.I)
EN_BAD=re.compile(r'^What (?:does|should I know about) (?:first confirm|start|use|avoid|check|inspect|look|remove|clean|work|dry|leave|open|close|add|reduce|control|watch|separate|identify|protect|store|wash|rinse|cool|freeze|thaw|reheat|keep|press|unplug|turn|mark|locate|follow|vacuum|apply|reserve|put|group)\b',re.I)
ES_AFTER_COMMA=re.compile(r',\s*(?:busca|revisa|usa|limpia|seca|retira|comprueba|observa|identifica|desconecta|apaga|llama|evita|mantén|abre|cierra)\b',re.I)
EN_AFTER_COMMA=re.compile(r',\s*(?:check|look|use|clean|dry|remove|inspect|identify|disconnect|turn|call|avoid|keep|open|close|diagnose)\b',re.I)
for lang in ('es','en'):
 d=ART/lang
 for n in range(311,391):
  ms=list(d.glob(f'{n:03d}-*.json'))
  if len(ms)!=1: errs.append(f'{lang} #{n}: expected 1 file, found {len(ms)}'); continue
  try: o=json.loads(ms[0].read_text(encoding='utf-8'))
  except Exception as e: errs.append(f'{lang} #{n}: JSON parse {e}'); continue
  by[(lang,n)]=o; ids.append(o.get('id')); slugs.append((lang,o.get('slug')))
  required=['schema_version','id','article_number','translation_group','language','locale','market_context','title','slug','seo','excerpt','taxonomy','content_html','faq','sources','image','status']
  for k in required:
   if k not in o: errs.append(f'{lang} #{n}: missing {k}')
  if o.get('article_number')!=n or o.get('language')!=lang or o.get('status')!='publish': errs.append(f'{lang} #{n}: identity/status mismatch')
  if lang=='es' and o.get('locale')!='es-ES': errs.append(f'ES #{n}: bad locale')
  if lang=='en' and o.get('locale')!='en-US': errs.append(f'EN #{n}: bad locale')
  if len(words(o.get('content_html','')))<145: errs.append(f'{lang} #{n}: too shallow')
  if o.get('content_html','').count('<h2>')!=4: errs.append(f'{lang} #{n}: expected 4 H2')
  if len(o.get('faq',[]))!=3: errs.append(f'{lang} #{n}: expected 3 FAQ')
  for f in o.get('faq',[]):
   q=f.get('question','').strip(); a=f.get('answer','').strip(); qs[lang].append(q)
   if not q.endswith('?'): errs.append(f'{lang} #{n}: FAQ lacks ?')
   if len(words(a))<8: errs.append(f'{lang} #{n}: short FAQ answer')
   if lang=='es' and ES_BAD.search(q): errs.append(f'ES #{n}: mechanical FAQ wording: {q}')
   if lang=='en' and EN_BAD.search(q): errs.append(f'EN #{n}: mechanical FAQ wording: {q}')
   if q.startswith('¿Qué debo hacer si ') and ES_AFTER_COMMA.search(q): errs.append(f'ES #{n}: FAQ copied a command after condition: {q}')
   if q.startswith('What should I do if ') and EN_AFTER_COMMA.search(q): errs.append(f'EN #{n}: FAQ copied a command after condition: {q}')
  seo=o.get('seo',{})
  if not seo.get('title') or not seo.get('meta_description') or not seo.get('search_intent'): errs.append(f'{lang} #{n}: incomplete SEO')
  if '…' in seo.get('title','') or seo.get('title','').endswith('...'): errs.append(f'{lang} #{n}: truncated SEO title')
  raw=json.dumps(o,ensure_ascii=False)
  for bad in ('HOME prioriza','HOME prioritizes','En este artículo hemos decidido'):
   if bad in raw: errs.append(f'{lang} #{n}: editorial metadiscourse')
  if lang=='es':
   if re.search(r'\bHVAC\b',raw): errs.append(f'ES #{n}: HVAC left as Spanish primary term')
   if 'inverter' in raw.lower(): errs.append(f'ES #{n}: avoidable inverter anglicism')
   if 'topper' in raw.lower(): errs.append(f'ES #{n}: avoidable topper anglicism')
for n in range(311,391):
 a=by.get(('es',n)); b=by.get(('en',n))
 if a and b and a.get('translation_group')!=b.get('translation_group'): errs.append(f'#{n}: translation_group mismatch')
if len(by)!=160: errs.append(f'expected 160 files, parsed {len(by)}')
if len(ids)!=len(set(ids)): errs.append('duplicate id')
if len(slugs)!=len(set(slugs)): errs.append('duplicate language slug')
checks={367:[('MERV','Minimum Efficiency Reporting Value')],372:[('LED','diodos emisores de luz')],388:[('GFCI','falla a tierra'),('GFCI','Norteamérica')]}
for n,pairs in checks.items():
 o=by.get(('es',n)); raw=(o.get('excerpt','')+' '+o.get('content_html','')) if o else ''
 for acr,exp in pairs:
  if acr in raw and exp.lower() not in raw.lower(): errs.append(f'ES #{n}: {acr} lacks explanation/context: {exp}')
for lang in ('es','en'):
 dup=[q for q,c in Counter(qs[lang]).items() if c>1]
 if dup: errs.append(f'{lang}: duplicate FAQ questions: {dup[:5]}')
risk={316:['no uses llama','cierra el suministro'],355:['prioriza seguridad'],372:['no retires la placa','electricista'],378:['deja la secadora fuera de servicio'],380:['no pruebes la comida'],388:['no lo puentes','electricista'],389:['deja de usarlo','electricista'],390:['no retires la placa','electricista']}
for n,terms in risk.items():
 o=by.get(('es',n)); raw=(o.get('excerpt','')+' '+o.get('content_html','')).lower() if o else ''
 for t in terms:
  if t not in raw: errs.append(f'ES #{n}: safety concept missing: {t}')
print(f'Final output scan: parsed={len(by)} errors={len(errs)}')
for e in errs: print('ERROR:',e)
if errs: raise SystemExit(1)
print('FINAL OUTPUT PASS 160/160')
