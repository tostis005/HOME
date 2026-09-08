#!/usr/bin/env python3
import argparse, html, json, re, statistics, unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'content'/'tools'; ART=ROOT/'content'/'articles'; ES=ART/'es'; EN=ART/'en'
BATCH=TOOLS/'batch-791-800.json'; REPORT=ART/'QUALITY-AUDIT-791-800.md'
EXPECTED=set(range(791,801))
SOURCE_MAP={
 'laundry':{'name':'American Cleaning Institute — Laundry Basics','url':'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics','es':'Buenas prácticas de lavado, clasificación, carga, dosificación y cuidado según etiquetas.','en':'Laundry practices covering sorting, loading, detergent dosing, and care-label guidance.'},
 'energy':{'name':'U.S. Department of Energy — Energy Saver','url':'https://www.energy.gov/energysaver','es':'Información práctica sobre calefacción, filtros, climatización y eficiencia doméstica.','en':'Practical information on heating, filters, home comfort systems, and energy efficiency.'},
 'mold':{'name':'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home','url':'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','es':'Control de humedad, condensación, moho y secado de materiales y espacios interiores.','en':'Moisture control, condensation, mold prevention, and drying of indoor spaces and materials.'},
}
WATCHED=[(791,721),(792,710),(793,794),(795,723),(795,724),(796,797),(798,799),(800,728),(800,366),(800,367),(800,368)]

def slugify(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower(); return re.sub(r'[^a-z0-9]+','-',s).strip('-')
def strip_tags(s): return re.sub(r'<[^>]+>',' ',html.unescape(s))
def words(s): return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:['’-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)?",strip_tags(s))
def first_sentence(t):
 p=t.replace('EE. UU.','EE§UU§').replace('U.S.','U§S§'); m=re.search(r'[.!?](?:[”\"])?(?=\s|$)',p); out=p[:m.end()] if m else p; return out.replace('EE§UU§','EE. UU.').replace('U§S§','U.S.').strip()
def qtitle(t,lang): return t.lstrip('¿').rstrip('?').strip() if lang=='es' else t.rstrip('?').strip()
def parse_topics():
 out={}
 for line in (ROOT/'content/topics/TOPICS-701-800.md').read_text(encoding='utf-8').splitlines():
  m=re.match(r'^(\d+)\.\s+(.+)$',line.strip())
  if m: out[int(m.group(1))]=m.group(2).strip()
 return out
def load_entries():
 e=json.loads(BATCH.read_text(encoding='utf-8')); nums=[x['n'] for x in e]; canonical=parse_topics()
 if len(e)!=10 or set(nums)!=EXPECTED or len(set(nums))!=10: raise SystemExit(f'Inventory mismatch count={len(e)} nums={nums}')
 for x in e:
  if canonical.get(x['n'])!=x['es_title']: raise SystemExit(f"Canonical title mismatch #{x['n']}")
  if len(x['sections'])!=4 or len(x['faq_es'])!=3 or len(x['faq_en'])!=3 or len(x['faq_sections'])!=3: raise SystemExit(f"Structure mismatch #{x['n']}")
  if any(i not in range(4) for i in x['faq_sections']): raise SystemExit(f"FAQ map out of range #{x['n']}")
 return e
def source_for(e,lang):
 s=SOURCE_MAP.get(e.get('source','')); return [] if not s else [{'name':s['name'],'url':s['url'],'note':s[lang]}]
def intent(e,lang):
 title=e['es_title' if lang=='es' else 'en_title']; q=qtitle(title,lang)
 if lang=='es':
  if e['kind']=='diagnostics': return f'Identificar las causas más probables de «{q}», distinguir señales útiles y decidir qué comprobar primero y cuándo pedir ayuda.'
  if e['kind'] in ('decision-guide','explanation'): return f'Entender «{q}» para tomar una decisión doméstica práctica y segura, reconocer límites y evitar errores comunes.'
  return f'Resolver «{q}» con una secuencia práctica, clara y segura, incluyendo las comprobaciones que evitan errores comunes.'
 if e['kind']=='diagnostics': return f'Identify the most likely causes behind “{q},” use distinguishing clues, and decide what to check first and when to get help.'
 if e['kind'] in ('decision-guide','explanation'): return f'Understand “{q}” well enough to make a practical, safe household decision, recognize limits, and avoid common mistakes.'
 return f'Handle “{q}” with a practical, clear, safe sequence and the checks that prevent common mistakes.'
def build(e,lang):
 es=lang=='es'; n=e['n']; title=e['es_title' if es else 'en_title']; intro=e['intro_es' if es else 'intro_en']; sec=[(s[0 if es else 1],s[2 if es else 3]) for s in e['sections']]; faqs=e['faq_es' if es else 'faq_en']; slug=slugify(title); tg=f"{n}-{slugify(e['en_title'])}"; q=qtitle(title,lang)
 content='<p>'+html.escape(intro,quote=False)+'</p>'+''.join(f'<h2>{html.escape(h,quote=False)}</h2><p>{html.escape(p,quote=False)}</p>' for h,p in sec)
 return {'schema_version':1,'id':f'{lang}-{n}-{slug}','article_number':n,'translation_group':tg,'language':lang,'locale':'es-ES' if es else 'en-US','market_context':'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if es else 'U.S./Canadian English; practical household guidance with locally familiar terminology and clear safety boundaries.','title':title,'slug':slug,'seo':{'title':title,'meta_description':first_sentence(intro),'search_intent':intent(e,lang)},'excerpt':intro,'taxonomy':{'food_family':e['family'],'food_subcategories':[slug],'article_types':[e['kind'],e['family']],'primary_article_type':e['kind']},'content_html':content,'faq':[{'question':fq,'answer':sec[i][1]} for fq,i in zip(faqs,e['faq_sections'])],'sources':source_for(e,lang),'image':{'concept':(f'Fotografía editorial doméstica realista sobre «{q}», mostrando de forma clara {sec[0][0].lower()} como acción o pista principal; entorno cotidiano natural, sin texto ni marcas.' if es else f'Realistic household editorial photograph about “{q},” clearly showing {sec[0][0].lower()} as the main action or clue; natural home setting, no text or branding.'),'alt':q},'status':'publish'},sec
def path_for(a): return (ES if a['language']=='es' else EN)/f"{a['article_number']}-{a['slug']}.json"
def library_excluding_target():
 vals=[]
 for d in (ES,EN):
  for p in d.glob('*.json'):
   try:a=json.loads(p.read_text(encoding='utf-8'))
   except Exception: continue
   if a.get('article_number') not in EXPECTED: vals.append(a)
 return vals
def validate(entries):
 err=[]; warn=[]; built={}; counts={'es':[],'en':[]}; faq_ok=0
 old=library_excluding_target(); ids={a.get('id') for a in old}; slugs={(a.get('language'),a.get('slug')) for a in old}; tgs={a.get('translation_group') for a in old}
 for e in entries:
  pair=[]
  for lang in ('es','en'):
   a,sec=build(e,lang); pair.append(a); p=path_for(a)
   if not p.exists(): err.append(f'Missing {p.relative_to(ROOT)}'); continue
   if json.loads(p.read_text(encoding='utf-8'))!=a: err.append(f'#{e["n"]} {lang}: deterministic build drift')
   if a['id'] in ids: err.append(f'#{e["n"]} {lang}: id collision')
   if (lang,a['slug']) in slugs: err.append(f'#{e["n"]} {lang}: slug collision')
   if a['translation_group'] in tgs: err.append(f'#{e["n"]}: translation-group collision')
   if a['status']!='publish': err.append(f'#{e["n"]} {lang}: status')
   if len(re.findall(r'<h2>',a['content_html']))!=4: err.append(f'#{e["n"]} {lang}: H2 count')
   if len(a['faq'])!=3 or len({x['question'] for x in a['faq']})!=3: err.append(f'#{e["n"]} {lang}: FAQ count/duplicate')
   for fq,i in zip(a['faq'],e['faq_sections']):
    if fq['answer']!=sec[i][1]: err.append(f'#{e["n"]} {lang}: FAQ mapping drift')
    else: faq_ok+=1
   meta=a['seo']['meta_description']
   if meta!=first_sentence(a['excerpt']) or not re.search(r'[.!?][”\"]?$',meta): err.append(f'#{e["n"]} {lang}: incomplete meta')
   if len(meta)<35: warn.append(f'#{e["n"]} {lang}: short meta {len(meta)}')
   si=a['seo']['search_intent'].lower()
   for bad in ('for how to','whether can you','para cómo','«¿'):
    if bad in si: err.append(f'#{e["n"]} {lang}: awkward search intent')
   if sec[0][0].lower() not in a['image']['concept'].lower(): err.append(f'#{e["n"]} {lang}: generic image')
   wc=len(words(a['content_html'])); counts[lang].append(wc)
   if wc<150: err.append(f'#{e["n"]} {lang}: thin body {wc}')
   prose=strip_tags(a['content_html']).lower()
   if e['n']==795:
    for required in (('no retires carcasa','do not remove the casing')[0 if lang=='es' else 1],('no hagas una cadena de reinicios','do not keep resetting')[0 if lang=='es' else 1]):
     if required not in prose: err.append(f'#795 {lang}: boiler safety boundary missing')
   if e['n']==797 and ('salpicaduras' if lang=='es' else 'splashed') not in prose: err.append(f'#797 {lang}: wet-location safety missing')
   built[(e['n'],lang)]=a
  if len(pair)==2 and pair[0]['translation_group']!=pair[1]['translation_group']: err.append(f'#{e["n"]}: pair mismatch')
 files=[]
 for d in (ES,EN):
  for p in d.glob('*.json'):
   try:a=json.loads(p.read_text(encoding='utf-8'))
   except Exception: continue
   if 791<=a.get('article_number',0)<=800: files.append(a)
 actual={(a['article_number'],a['language']) for a in files}; expected={(n,l) for n in EXPECTED for l in ('es','en')}
 if actual!=expected or len(files)!=20: err.append(f'Target inventory files={len(files)} missing={sorted(expected-actual)} extra={sorted(actual-expected)}')
 return err,warn,built,counts,faq_ok
def generate(entries):
 for e in entries:
  for lang in ('es','en'):
   a,_=build(e,lang); p=path_for(a); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(a,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def tokens(a): return {w.lower() for w in words(a['content_html']) if len(w)>3}
def jac(a,b):
 x,y=tokens(a),tokens(b); return len(x&y)/max(1,len(x|y))
def by_num(n,lang,built):
 if (n,lang) in built:return built[(n,lang)]
 d=ES if lang=='es' else EN
 for p in d.glob(f'{n}-*.json'):
  try:return json.loads(p.read_text(encoding='utf-8'))
  except Exception:return None
def report(entries,built,counts,faq_ok,warn):
 sims=[]
 for a,b in WATCHED:
  vals=[]
  for lang in ('es','en'):
   aa=by_num(a,lang,built); bb=by_num(b,lang,built)
   if aa and bb: vals.append(jac(aa,bb))
  if vals:sims.append((a,b,max(vals)))
 src=sum(1 for e in entries if source_for(e,'en'))
 lines=['# Quality audit — HOME articles 791–800','','## Result','', '- Canonical topic intents reviewed: **10/10**.','- Published unique intents: **10**; bilingual article JSON files: **20/20 PASS**.',f'- FAQ answer-to-section mappings: **{faq_ok}/60 PASS**.','- Schema, IDs, slugs, translation groups, locales, SEO fields, four H2 sections, three FAQs, image metadata, status, safety checks and collision checks all pass.','- Meta descriptions are complete first editorial sentences; character truncation is rejected.','', '## Depth metrics','',f'- Spanish body words: min **{min(counts["es"])}**, median **{int(statistics.median(counts["es"]))}**, max **{max(counts["es"])}**.',f'- English body words: min **{min(counts["en"])}**, median **{int(statistics.median(counts["en"]))}**, max **{max(counts["en"])}**.','- The 150-word floor is only an incomplete-output regression guard, not an editorial target.','', '## Cannibalization diagnostics','']
 for a,b,v in sims: lines.append(f'- #{a} vs #{b}: **{v:.3f}** maximum ES/EN token Jaccard.')
 lines += ['','## Sources','',f'- Topic pairs with a directly relevant structured reference: **{src}**.',f'- Topic pairs intentionally without a structured source because no directly supporting source was mapped: **{10-src}**.','', '## Editorial safeguards','', '- #793 and #794 are separated as whole-window closure vs latch engagement.','- #795 permits only manufacturer-approved user reset steps; repeated lockout, gas odor, major leak or overheating require escalation.','- #796 and #797 separate how to operate a dehumidifier from where to place it, with wet-location and drainage limits.','- #798 removes an existing musty closet odor; #799 prevents recurrence.','- #800 diagnoses filter loading without duplicating replacement interval (#366), MERV selection (#367), airflow direction (#368), or air-conditioning filter checks (#728).','- Temporary source batch, generator and workflow must be removed before merge to `main`.']
 if warn: lines += ['','## Non-blocking notes','']+[f'- {x}' for x in warn]
 REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--validate-only',action='store_true'); args=ap.parse_args(); e=load_entries()
 if not args.validate_only: generate(e)
 err,warn,built,counts,faq_ok=validate(e)
 if err:
  print('\n'.join('ERROR: '+x for x in err)); raise SystemExit(1)
 if not args.validate_only: report(e,built,counts,faq_ok,warn)
 print(f'PASS entries=10 articles=20 faq={faq_ok} errors=0 warnings={len(warn)}')
 print(f'ES words {min(counts["es"])}/{int(statistics.median(counts["es"]))}/{max(counts["es"])}')
 print(f'EN words {min(counts["en"])}/{int(statistics.median(counts["en"]))}/{max(counts["en"])}')
 if warn: print('WARNINGS: '+' | '.join(warn))
if __name__=='__main__': main()
