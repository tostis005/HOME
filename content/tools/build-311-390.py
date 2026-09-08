#!/usr/bin/env python3
from pathlib import Path
import json,re,unicodedata,html,statistics
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'tools'; ART=ROOT/'articles'; ES=ART/'es'; EN=ART/'en'
START,END=311,390
ES_MARKET='Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.'
EN_MARKET='United States and Canada; practical, safety-first household guidance written natively for North American readers.'

SOURCES={
'cleaning':{
'es':[{'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Prácticas de limpieza doméstica, dosificación y compatibilidad de productos con superficies y materiales.'}],
'en':[{'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Household cleaning practices, product dosing, and compatibility with surfaces and materials.'}]},
'frozen-pipes':{
'es':[{'name':'American Red Cross — Preventing and Thawing Frozen Pipes','url':'https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/winter-storm/frozen-pipes.html','note':'Prevención de tuberías congeladas y métodos de descongelación gradual sin llama abierta.'}],
'en':[{'name':'American Red Cross — Preventing and Thawing Frozen Pipes','url':'https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/winter-storm/frozen-pipes.html','note':'Frozen-pipe prevention and gradual thawing methods without open flame.'}]},
'hvac-energy':{
'es':[{'name':'U.S. Department of Energy — Thermostats','url':'https://www.energy.gov/energysaver/thermostats','note':'Uso de termostatos, ajustes de temperatura y ahorro energético en calefacción y refrigeración.'}],
'en':[{'name':'U.S. Department of Energy — Thermostats','url':'https://www.energy.gov/energysaver/thermostats','note':'Thermostat use, temperature setbacks, and heating and cooling energy savings.'}]},
'pests':{
'es':[{'name':'U.S. Environmental Protection Agency — Integrated Pest Management','url':'https://www.epa.gov/ipm','note':'Prevención y manejo integrado de plagas mediante saneamiento, exclusión, vigilancia y tratamientos dirigidos.'}],
'en':[{'name':'U.S. Environmental Protection Agency — Integrated Pest Management','url':'https://www.epa.gov/ipm','note':'Integrated pest management using sanitation, exclusion, monitoring, and targeted treatment.'}]},
'allergens':{
'es':[{'name':'U.S. Environmental Protection Agency — Biological Pollutants’ Impact on Indoor Air Quality','url':'https://www.epa.gov/indoor-air-quality-iaq/biological-pollutants-impact-indoor-air-quality','note':'Humedad, ácaros, alérgenos y medidas para reducir contaminantes biológicos en interiores.'}],
'en':[{'name':'U.S. Environmental Protection Agency — Biological Pollutants’ Impact on Indoor Air Quality','url':'https://www.epa.gov/indoor-air-quality-iaq/biological-pollutants-impact-indoor-air-quality','note':'Humidity, dust mites, allergens, and measures to reduce indoor biological pollutants.'}]},
'laundry':{
'es':[{'name':'American Cleaning Institute — Laundry Basics','url':'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics','note':'Lavado doméstico, dosificación, tratamiento de manchas y cuidado de tejidos según etiqueta.'}],
'en':[{'name':'American Cleaning Institute — Laundry Basics','url':'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics','note':'Household laundry, dosing, stain treatment, and fabric care according to care labels.'}]},
'plants':{
'es':[{'name':'University of Minnesota Extension — Watering Houseplants','url':'https://extension.umn.edu/planting-and-growing-guides/watering-houseplants','note':'Riego, drenaje y señales de estrés hídrico en plantas de interior.'}],
'en':[{'name':'University of Minnesota Extension — Watering Houseplants','url':'https://extension.umn.edu/planting-and-growing-guides/watering-houseplants','note':'Watering, drainage, and water-stress signs in houseplants.'}]},
'boiler':{
'es':[{'name':'U.S. Department of Energy — Home Heating Systems','url':'https://www.energy.gov/energysaver/home-heating-systems','note':'Funcionamiento, controles y mantenimiento general de sistemas domésticos de calefacción.'}],
'en':[{'name':'U.S. Department of Energy — Home Heating Systems','url':'https://www.energy.gov/energysaver/home-heating-systems','note':'Operation, controls, and general maintenance of home heating systems.'}]},
'hvac-air':{
'es':[{'name':'U.S. Environmental Protection Agency — Air Cleaners and Air Filters in the Home','url':'https://www.epa.gov/indoor-air-quality-iaq/air-cleaners-and-air-filters-home','note':'Filtración doméstica, eficiencia de filtros, partículas y consideraciones de caudal del sistema.'}],
'en':[{'name':'U.S. Environmental Protection Agency — Air Cleaners and Air Filters in the Home','url':'https://www.epa.gov/indoor-air-quality-iaq/air-cleaners-and-air-filters-home','note':'Home air filtration, filter efficiency, particles, and system airflow considerations.'}]},
'mold':{
'es':[{'name':'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home','url':'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','note':'Control de humedad, secado de materiales, limpieza y prevención de recurrencia del moho.'}],
'en':[{'name':'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home','url':'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','note':'Moisture control, material drying, mold cleanup, and recurrence prevention.'}]},
'electrical':{
'es':[{'name':'U.S. Consumer Product Safety Commission — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Riesgos eléctricos domésticos, enchufes, interruptores, cableado y respuesta segura ante sobrecalentamiento.'}],
'en':[{'name':'U.S. Consumer Product Safety Commission — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Household electrical hazards, receptacles, switches, wiring, and safe response to overheating.'}]},
'gfci':{
'es':[{'name':'U.S. Consumer Product Safety Commission — GFCIs Fact Sheet','url':'https://www.cpsc.gov/s3fs-public/099_0.pdf','note':'Funcionamiento, prueba y rearme de interruptores de circuito por falla a tierra usados en Norteamérica.'}],
'en':[{'name':'U.S. Consumer Product Safety Commission — GFCIs Fact Sheet','url':'https://www.cpsc.gov/s3fs-public/099_0.pdf','note':'Ground-fault circuit interrupter operation, testing, and reset behavior.'}]},
'dryer-safety':{
'es':[{'name':'U.S. Consumer Product Safety Commission — Clothes Dryer Safety','url':'https://www.cpsc.gov/s3fs-public/5022.pdf','note':'Prevención de incendios en secadoras, limpieza de pelusa y mantenimiento del conducto de ventilación.'}],
'en':[{'name':'U.S. Consumer Product Safety Commission — Clothes Dryer Safety','url':'https://www.cpsc.gov/s3fs-public/5022.pdf','note':'Clothes-dryer fire prevention, lint removal, and exhaust-vent maintenance.'}]},
'power-outage-food':{
'es':[{'name':'USDA Food Safety and Inspection Service — Keeping Food Safe During an Emergency','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keeping-food-safe-during-emergency','note':'Conservación de alimentos refrigerados y congelados durante cortes de electricidad.'}],
'en':[{'name':'USDA Food Safety and Inspection Service — Keeping Food Safe During an Emergency','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keeping-food-safe-during-emergency','note':'Keeping refrigerated and frozen food safe during a power outage.'}]},
'food-safety':{
'es':[{'name':'USDA Food Safety and Inspection Service — Danger Zone','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/danger-zone-40f-140f','note':'Control de tiempo y temperatura para alimentos perecederos y sobras cocinadas.'}],
'en':[{'name':'USDA Food Safety and Inspection Service — Danger Zone','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/danger-zone-40f-140f','note':'Time and temperature control for perishable foods and cooked leftovers.'}]},
'food-storage':{'es':[],'en':[]}
}
STOP=set('the a an and or of to in for on with is are my your how why what from into can does do should de la el los las un una unos unas y o del al por para con en mi tu como cómo que qué se es son'.split())

def slugify(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower(); s=re.sub(r'[^a-z0-9]+','-',s).strip('-'); return re.sub('-+','-',s)
def plain(s): return re.sub(r'\s+',' ',s.replace('\u200b','').replace('\ufeff','')).strip()
def first_sentence(s):
 s=plain(s); m=re.match(r'^(.+?[.!?])(?:\s|$)',s); return m.group(1) if m else s
def words(h): return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",re.sub(r'<[^>]+>',' ',h))
def tokens(h): return {w.lower() for w in words(h) if len(w)>2 and w.lower() not in STOP}
def seo_title(title): return title.replace(' Causas comunes y soluciones','').replace(' Common Causes and Fixes','')

def intent(title,kind,lang):
 low=title.strip('¿? ').lower()
 if lang=='es':
  if 'diagnostic' in kind or 'troubleshooting' in kind: return f'Identificar las causas probables de «{low}», usar señales observables para decidir qué comprobar primero y saber cuándo corresponde reparar o pedir ayuda.'
  if 'safety' in kind: return f'Resolver «{low}» con límites de seguridad claros, distinguiendo comprobaciones domésticas de situaciones que requieren detenerse o pedir ayuda.'
  if kind in ('how-to','material-care','maintenance'): return f'Seguir un método práctico para {low}, protegiendo materiales y equipos y sabiendo cuándo detenerse o cambiar de estrategia.'
  return f'Entender «{low}» y tomar una decisión doméstica práctica con criterios claros en lugar de una regla genérica.'
 if 'diagnostic' in kind or 'troubleshooting' in kind: return f'Identify the likely causes of “{low},” use observable clues to choose the first checks, and know when repair or professional help is appropriate.'
 if 'safety' in kind: return f'Handle “{low}” with clear safety boundaries, separating reasonable household checks from conditions that require stopping or getting help.'
 if kind in ('how-to','material-care','maintenance'): return f'Use a practical method for {low}, protecting materials and equipment and knowing when to stop or change approach.'
 return f'Understand “{low}” and make a practical household decision using clear criteria instead of a one-size-fits-all rule.'

ES_VERBS={'empieza':'empezar','usa':'usar','evita':'evitar','comprueba':'comprobar','revisa':'revisar','mira':'mirar','busca':'buscar','retira':'retirar','limpia':'limpiar','trabaja':'trabajar','seca':'secar','deja':'dejar','abre':'abrir','cierra':'cerrar','añade':'añadir','anade':'añadir','reduce':'reducir','controla':'controlar','observa':'observar','distingue':'distinguir','identifica':'identificar','protege':'proteger','guarda':'guardar','lava':'lavar','aclara':'aclarar','enfría':'enfriar','enfria':'enfriar','congela':'congelar','descongela':'descongelar','recalienta':'recalentar','mantén':'mantener','manten':'mantener','pulsa':'pulsar','desconecta':'desconectar','apaga':'apagar','marca':'marcar','localiza':'localizar','sigue':'seguir','aspira':'aspirar','aplica':'aplicar','reserva':'reservar','pon':'poner','separa':'separar','agrupa':'agrupar'}
EN_IMP=set('start use avoid check inspect look remove clean work dry leave open close add reduce control watch separate identify protect store wash rinse cool freeze thaw reheat keep press unplug turn mark locate follow vacuum apply reserve put group compare choose allow'.split())

def q_es(h,n,i):
 h=plain(h).rstrip('.'); low=h.lower()
 if low.startswith('no '):
  rest=h[3:]; first=rest.split()[0].lower() if rest.split() else ''; inf=ES_VERBS.get(first,first); tail=' '.join(rest.split()[1:]); return f'¿Por qué no conviene {inf} {tail.lower()}?'.replace('  ',' ')
 first=h.split()[0].lower().strip(',:;') if h.split() else ''
 if first in ES_VERBS:
  inf=ES_VERBS[first]; tail=' '.join(h.split()[1:]).lower()
  forms=[f'¿Cómo conviene {inf} {tail}?',f'¿Qué debo tener en cuenta al {inf} {tail}?',f'¿Cuál es la forma segura de {inf} {tail}?']
  return forms[(n+i)%3].replace('  ',' ')
 if low.startswith('si '): return '¿Qué hago '+low+'?'
 if ' puede ' in ' '+low+' ': return '¿Qué significa que '+low+'?'
 if ' necesita ' in ' '+low+' ' or ' requiere ' in ' '+low+' ': return '¿Cuándo '+low+'?'
 return '¿Qué indica '+low+'?'
def q_en(h,n,i):
 h=plain(h).rstrip('.'); low=h.lower()
 if low.startswith('do not ') or low.startswith('never '):
  rest=h.split(' ',2)[2] if low.startswith('do not ') else h.split(' ',1)[1]; return f'Why should I avoid {rest.lower()}?'
 first=low.split()[0] if low.split() else ''
 if first in EN_IMP:
  rest=' '.join(h.split()[1:]).lower(); forms=[f'How should I {first} {rest}?',f'What should I know before I {first} {rest}?',f'What is the safest way to {first} {rest}?']; return forms[(n+i)%3].replace('  ',' ')
 if low.startswith('if '): return 'What should I do '+low+'?'
 if ' can ' in ' '+low+' ': return 'What does it mean when '+low+'?'
 if ' needs ' in ' '+low+' ' or ' requires ' in ' '+low+' ': return 'When does '+low+'?'
 return 'What does '+low+' indicate?'

def faq(item,lang):
 out=[]
 for j,idx in enumerate((0,1,3)):
  sec=item['sections'][idx]; h=sec[0] if lang=='es' else sec[1]; a=sec[2] if lang=='es' else sec[3]
  out.append({'question':q_es(h,item['n'],j) if lang=='es' else q_en(h,item['n'],j),'answer':plain(a)})
 return out

def image_concept(item,lang):
 h=item['sections'][0][0 if lang=='es' else 1]; title=item['es_title'] if lang=='es' else item['en_title']
 if lang=='es': return f'Fotografía editorial doméstica realista sobre «{title.strip("¿?")}», mostrando de forma clara {h.lower()} como acción o pista principal; materiales y equipo cotidianos, sin texto ni marcas.'
 return f'Realistic household editorial photograph about “{title.strip("?")},” clearly showing {h.lower()} as the main action or clue; ordinary home materials and equipment, no text or branding.'

def build(item,lang):
 title=plain(item['es_title'] if lang=='es' else item['en_title']); intro=plain(item['es_intro'] if lang=='es' else item['en_intro']); slug=slugify(title); tg=f"{item['n']}-{slugify(item['en_title'])}"
 chunks=[]
 for s in item['sections']:
  h=plain(s[0] if lang=='es' else s[1]); p=plain(s[2] if lang=='es' else s[3]); chunks.append(f'<h2>{html.escape(h)}</h2><p>{html.escape(p)}</p>')
 return {'schema_version':1,'id':f"{lang}-{item['n']}-{slug}",'article_number':item['n'],'translation_group':tg,'language':lang,'locale':'es-ES' if lang=='es' else 'en-US','market_context':ES_MARKET if lang=='es' else EN_MARKET,'title':title,'slug':slug,'seo':{'title':seo_title(title),'meta_description':first_sentence(intro),'search_intent':intent(title,item['kind'],lang)},'excerpt':intro,'taxonomy':{'food_family':item['family'],'food_subcategories':[item['subcat']],'article_types':[item['kind'],item['family']],'primary_article_type':item['kind']},'content_html':f'<p>{html.escape(intro)}</p>'+''.join(chunks),'faq':faq(item,lang),'sources':[dict(x) for x in SOURCES.get(item.get('source',''),{}).get(lang,[])],'image':{'concept':image_concept(item,lang),'alt':title.strip('¿?!.')},'status':'publish'}

def load_items():
 arr=[]
 for p in sorted(TOOLS.glob('batch-*.json')):
  m=re.fullmatch(r'batch-(\d+)-(\d+)\.json',p.name)
  if not m: continue
  a,b=map(int,m.groups())
  if b<START or a>END: continue
  arr.extend(json.loads(p.read_text(encoding='utf-8')))
 by={int(x['n']):x for x in arr}; missing=[n for n in range(START,END+1) if n not in by]
 if missing or len(arr)!=len(by): raise SystemExit(f'Batch inventory problem: missing={missing}, total={len(arr)}, unique={len(by)}')
 return [by[n] for n in range(START,END+1)]
def canon():
 text=(ROOT/'topics'/'TOPICS-301-400.md').read_text(encoding='utf-8'); return {int(m.group(1)):m.group(2).strip() for m in re.finditer(r'(?m)^(\d+)\.\s+(.+)$',text) if START<=int(m.group(1))<=END}
def existing(n,lang):
 d=ES if lang=='es' else EN; ms=list(d.glob(f'{n:03d}-*.json')); return json.loads(ms[0].read_text(encoding='utf-8')) if len(ms)==1 else None

OVERLAPS=[(311,233,'showerhead scale removal vs faucet scale removal'),(312,395,'filter replacement interval vs future replacement procedure'),(313,234,'plunger method vs no-plunger method'),(314,245,'toilet sewer odor vs toilet gurgling'),(315,248,'sink sewer odor vs sink-drain odor'),(316,237,'safe pipe thawing procedure vs frozen-pipe immediate response'),(318,171,'grease removal vs general range-hood cleaning'),(323,324,'general carpet vs shag rug cleaning'),(323,325,'general carpet vs wool rug cleaning'),(328,247,'hair removal vs shower-drain odor'),(329,235,'bathtub drain vs bathroom sink clog'),(330,235,'kitchen sink vs bathroom sink clog'),(331,177,'AC all-day strategy vs summer cost reduction'),(332,176,'heating setback vs winter cost reduction'),(333,180,'fruit flies vs general house flies'),(335,251,'mouse entry points vs mouse signs'),(337,180,'many flies vs why flies enter'),(339,179,'clothes moths vs pantry moths'),(340,181,'grain beetles vs generic pantry insects'),(341,353,'small hole repair vs crack repair'),(348,265,'sneakers vs generic shoes in washer'),(353,354,'crack repair vs normality'),(354,355,'normal cracks vs serious crack signs'),(358,359,'overwatering vs needs water'),(360,275,'Wi-Fi disconnects vs slow Wi-Fi'),(360,361,'disconnects vs router placement'),(363,202,'cold-top radiator vs radiator bleeding procedure'),(364,276,'raise boiler pressure vs low-pressure diagnosis'),(364,365,'refill procedure vs recurring pressure loss'),(366,367,'filter interval vs MERV selection'),(367,368,'MERV choice vs installation direction'),(369,370,'mold causes vs hidden mold'),(369,371,'mold causes vs mold odor'),(370,371,'hidden mold vs mold odor'),(372,306,'flicker vs one-room outage'),(375,147,'oven foil vs air-fryer foil'),(377,219,'washer no-start vs vibration'),(378,216,'dryer burning smell vs not drying'),(379,300,'underneath leak vs general dishwasher leak'),(380,290,'refrigerator outage vs freezer outage'),(381,382,'freezer frost vs door closure'),(383,384,'uneven oven vs smoking oven'),(385,386,'freeze rice vs pasta'),(385,387,'freeze rice vs cheese'),(386,387,'freeze pasta vs cheese'),(388,307,'GFCI reset procedure vs repeated trips'),(389,285,'hot outlet vs burning-smell outlet'),(389,390,'hot outlet vs hot light switch')]

def validate(items,objs):
 errs=[]; warns=[]; c=canon(); by={(o['language'],o['article_number']):o for o in objs}; ids=[]; slugs=[]
 if len(objs)!=160: errs.append(f'expected 160 objects, got {len(objs)}')
 for it in items:
  n=it['n']
  if c.get(n)!=it['es_title']: errs.append(f'#{n}: canonical ES title mismatch')
  for lang in ('es','en'):
   o=by.get((lang,n))
   if not o: errs.append(f'missing {lang} #{n}'); continue
   ids.append(o['id']); slugs.append((lang,o['slug']))
   if o['status']!='publish': errs.append(f'{lang} #{n}: status')
   if not o['seo']['meta_description'] or not o['seo']['search_intent']: errs.append(f'{lang} #{n}: metadata empty')
   if '…' in o['seo']['title'] or o['seo']['title'].endswith('...'): errs.append(f'{lang} #{n}: truncated SEO title')
   wc=len(words(o['content_html']))
   if wc<145: errs.append(f'{lang} #{n}: shallow content {wc} words')
   if o['content_html'].count('<h2>')!=4: errs.append(f'{lang} #{n}: H2 count')
   if len(o['faq'])!=3: errs.append(f'{lang} #{n}: FAQ count')
   for f in o['faq']:
    if not f['question'].endswith('?') and not (lang=='es' and f['question'].endswith('¿')): errs.append(f'{lang} #{n}: malformed FAQ')
    if len(words(f['answer']))<8: errs.append(f'{lang} #{n}: short FAQ answer')
   raw=json.dumps(o,ensure_ascii=False)
   if 'HOME prioriza' in raw or 'HOME prioritizes' in raw: errs.append(f'{lang} #{n}: metadiscourse')
   if lang=='es' and re.search(r'\bHVAC\b',raw): errs.append(f'ES #{n}: avoid HVAC as primary Spanish term')
  if by.get(('es',n)) and by.get(('en',n)) and by[('es',n)]['translation_group']!=by[('en',n)]['translation_group']: errs.append(f'#{n}: translation group mismatch')
 if len(ids)!=len(set(ids)): errs.append('duplicate ids')
 if len(slugs)!=len(set(slugs)): errs.append('duplicate language slugs')
 req={367:[('MERV','eficiencia')],388:[('GFCI','falla a tierra')]}
 for n,pairs in req.items():
  raw=(by[('es',n)]['excerpt']+' '+by[('es',n)]['content_html'])
  for acr,term in pairs:
   if acr in raw and term.lower() not in raw.lower(): errs.append(f'ES #{n}: {acr} not explained')
 banned={331:['inverter'],310:['topper']}
 for n,terms in banned.items():
  if ('es',n) in by:
   raw=json.dumps(by[('es',n)],ensure_ascii=False).lower()
   for term in terms:
    if term in raw: errs.append(f'ES #{n}: avoidable anglicism {term}')
 risk={316:['no uses llama','cierra el suministro'],355:['seguridad'],372:['no retires la placa','electricista'],378:['deja la secadora fuera de servicio'],380:['no pruebes'],388:['no lo puentes'],389:['deja de usarlo','electricista'],390:['no retires la placa','electricista']}
 for n,terms in risk.items():
  raw=(by[('es',n)]['excerpt']+' '+by[('es',n)]['content_html']).lower()
  for t in terms:
   if t not in raw: warns.append(f'ES #{n}: expected safety concept missing: {t}')
 return errs,warns

def metrics(arr):
 vals=[(len(words(o['content_html'])),o['content_html'].count('<h2>'),len(o['faq']),len(o['sources'])) for o in arr]; return tuple(round(statistics.mean(v[i] for v in vals),1) for i in range(4))
def jacc(a,b):
 ta,tb=tokens(a['content_html']),tokens(b['content_html']); return len(ta&tb)/max(1,len(ta|tb))
def report(objs,errs,warns):
 by={(o['language'],o['article_number']):o for o in objs}; lines=['# HOME — Quality audit 311–390','','## Result','',f'- JSON checked: **{len(objs)} / 160** (80 ES + 80 EN expected).',f'- Structural/editorial validation: **{"PASS" if not errs else "FAIL"}**.',f'- Blocking errors: **{len(errs)}**.',f'- Localization/safety warnings: **{len(warns)}**.','','## Scope and editorial criteria','','- Exact approved topics 311–390 preserved from the canonical inventory.','- ES and EN share article number and translation group while using independently localized prose.','- Safety-sensitive plumbing, heating, electrical, appliance and food-safety topics include explicit stop conditions.','- Close topics are audited by search intent and next action, not similarity score alone.','- Mechanical SEO truncation, broken pairs, unexplained required acronyms and editorial metadiscourse are blocking failures.','','## Quantitative profile','','| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
 for a,b in ((311,330),(331,350),(351,370),(371,390)):
  e=metrics([by[('es',n)] for n in range(a,b+1)]); x=metrics([by[('en',n)] for n in range(a,b+1)]); lines.append(f'| {a}–{b} | {e[0]} | {e[1]} | {e[2]} | {e[3]} | {x[0]} | {x[1]} | {x[2]} | {x[3]} |')
 lines+=['','## Cannibalization / overlap diagnostics','','| Pair | Intent distinction | ES Jaccard | EN Jaccard |','|---|---|---:|---:|']
 for a,b,label in OVERLAPS:
  vals=[]
  for lang in ('es','en'):
   oa=by.get((lang,a)) or existing(a,lang); ob=by.get((lang,b)) or existing(b,lang); vals.append(jacc(oa,ob) if oa and ob else 0)
  lines.append(f'| #{a}/#{b} | {label} | {vals[0]:.3f} | {vals[1]:.3f} |')
 lines+=['','## Editorial overlap conclusions','','- #312/#395 (future): #312 decides when a refrigerator filter is due; #395 is the replacement procedure.','- #316/#237: #316 is the controlled thawing method; #237 remains the broader immediate response to a frozen pipe.','- #353/#354/#355: cosmetic repair, normality assessment and serious-crack triage remain separate decisions.','- #364/#276/#365: pressure refill, low-pressure diagnosis and recurring pressure loss are distinct.','- #366/#367/#368: replacement interval, filtration rating and installation direction answer different filter questions.','- #369/#370/#371: cause, hidden growth and odor are separate mold intents.','- #379/#300: #379 localizes a leak beneath the dishwasher; #300 remains the broader leak diagnosis.','- #380/#290: refrigerator cold retention is separate from frozen-food safety in the freezer.','- #388/#307: #388 is a one-time safe reset procedure; #307 diagnoses repeated GFCI trips.','- #389/#390: outlet overheating and light-switch overheating have different loads, observations and escalation paths.','','## Final reading priorities','','Representative manual reads should include #312–316, #322–325, #331–340, #353–372, #377–390 in both languages.','Reject safety-sensitive pages if they encourage flame on frozen pipes, live electrical work, repeated breaker/GFCI resets, opening boiler gas components, tasting questionable food, or continuing to use overheated electrical devices.']
 if errs: lines+=['','## Blocking errors','']+['- '+e for e in errs]
 if warns: lines+=['','## Warnings','']+['- '+w for w in warns]
 (ART/'QUALITY-AUDIT-311-390.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

items=load_items(); objs=[]
for it in items:
 for lang,d in (('es',ES),('en',EN)):
  o=build(it,lang); objs.append(o)
  for old in d.glob(f"{it['n']:03d}-*.json"): old.unlink()
  (d/f"{it['n']:03d}-{o['slug']}.json").write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
errs,warns=validate(items,objs); report(objs,errs,warns)
print(f'Generated {len(objs)} JSON; errors={len(errs)} warnings={len(warns)}')
for e in errs: print('ERROR:',e)
for w in warns: print('WARN:',w)
if errs or warns: raise SystemExit(1)
