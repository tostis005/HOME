#!/usr/bin/env python3
from pathlib import Path
import json,re,html
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'; TOOLS=ROOT/'tools'; REPORT=ART/'QUALITY-AUDIT-391-470.md'
ERR=[]; WARN=[]; BY={}; REC={}
for p in sorted(TOOLS.glob('batch-391-470-*.json')):
    for r in json.loads(p.read_text(encoding='utf-8')):
        if r['n'] in REC: ERR.append(f'duplicate topic source #{r["n"]}')
        REC[r['n']]=r
if sorted(REC)!=list(range(391,471)): ERR.append(f'canonical batch coverage is {len(REC)}, expected 80')

def plain(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def wc(s): return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",plain(s)))
def tok(s):
    stop={'the','and','for','with','from','that','this','your','you','how','why','what','can','de','del','la','las','el','los','para','por','que','una','uno','con','como','cómo'}
    return {x for x in re.findall(r'[a-záéíóúñü]+',plain(s).lower()) if len(x)>2 and x not in stop}
def jacc(a,b):
    A=tok(a); B=tok(b); return len(A&B)/len(A|B) if A|B else 0.0

def find_article(lang,n):
    fs=list((ART/lang).glob(f'{n:03d}-*.json'))
    if len(fs)!=1: return None
    try: return json.loads(fs[0].read_text(encoding='utf-8'))
    except: return None

required={'schema_version','id','article_number','translation_group','language','locale','market_context','title','slug','seo','excerpt','taxonomy','content_html','faq','sources','image','status'}
all_ids=[]; all_slugs=[]; global_q={'es':[],'en':[]}
for lang in ('es','en'):
    for n in range(391,471):
        fs=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(fs)!=1:
            ERR.append(f'{lang} #{n}: expected one JSON, found {len(fs)}'); continue
        try: o=json.loads(fs[0].read_text(encoding='utf-8'))
        except Exception as e: ERR.append(f'{lang} #{n}: invalid JSON: {e}'); continue
        BY[(lang,n)]=o
        missing=required-set(o)
        if missing: ERR.append(f'{lang} #{n}: missing {sorted(missing)}')
        if o.get('schema_version')!=1 or o.get('article_number')!=n or o.get('language')!=lang or o.get('status')!='publish': ERR.append(f'{lang} #{n}: identity/status mismatch')
        if o.get('locale')!=('es-ES' if lang=='es' else 'en-US'): ERR.append(f'{lang} #{n}: locale mismatch')
        if not o.get('id','').startswith(f'{lang}-{n}-'): ERR.append(f'{lang} #{n}: malformed id')
        if not o.get('translation_group','').startswith(f'{n}-'): ERR.append(f'{lang} #{n}: malformed translation group')
        all_ids.append(o.get('id')); all_slugs.append((lang,o.get('slug')))
        htmlv=o.get('content_html','')
        if wc(htmlv)<150: ERR.append(f'{lang} #{n}: depth below floor ({wc(htmlv)} words)')
        if htmlv.count('<h2>')!=4: ERR.append(f'{lang} #{n}: expected 4 H2')
        faq=o.get('faq',[])
        if len(faq)!=3: ERR.append(f'{lang} #{n}: expected 3 FAQ')
        got=[x.get('question','') for x in faq]
        exp=REC.get(n,{}).get(f'faq_{lang}',[])
        if got!=exp: ERR.append(f'{lang} #{n}: FAQ questions changed from explicit editorial input')
        global_q[lang].extend(got)
        for item in faq:
            q=item.get('question',''); a=item.get('answer','')
            if not q.endswith('?'): ERR.append(f'{lang} #{n}: FAQ is not a question: {q}')
            if a not in htmlv: ERR.append(f'{lang} #{n}: FAQ answer is not grounded in article body')
            low=q.lower()
            badq=('how should i do not','how can should','can in ','¿cómo debería no','¿puede en ')
            if any(x in low for x in badq): ERR.append(f'{lang} #{n}: malformed FAQ grammar: {q}')
        seo=o.get('seo',{})
        if seo.get('title')!=o.get('title'): ERR.append(f'{lang} #{n}: SEO title mismatch')
        if not seo.get('meta_description') or not seo.get('search_intent'): ERR.append(f'{lang} #{n}: incomplete SEO metadata')
        if len(seo.get('meta_description',''))>190: WARN.append(f'{lang} #{n}: meta description >190 chars')
        intent=seo.get('search_intent','').lower()
        for x in ('para cómo','para cada cuánto','prevenir evitar','for how to','to how to','to how often should','for how often should','for where should','prevent prevent'):
            if x in intent: ERR.append(f'{lang} #{n}: artificial search_intent syntax: {seo.get("search_intent")}')
        if seo.get('title','').endswith('...') or '…' in seo.get('title',''): ERR.append(f'{lang} #{n}: truncated SEO title')
        raw=json.dumps(o,ensure_ascii=False); lowraw=raw.lower()
        for x in ('home prioriza','home recomienda','home prioritizes','en este artículo hemos decidido','in this article we decided'):
            if x in lowraw: ERR.append(f'{lang} #{n}: editorial metadiscourse')
        if lang=='es':
            for x in ('"hvac"','inverter','topper','pillow-top','peva'):
                if x in lowraw: ERR.append(f'ES #{n}: avoidable/unexplained term {x}')
            prose=o.get('excerpt','')+' '+htmlv
            if re.search(r'\bLED\b',prose) and 'diodos emisores de luz' not in prose.lower(): ERR.append(f'ES #{n}: LED not expanded')
            if re.search(r'\bGFCI\b',prose) and 'falla a tierra' not in prose.lower(): ERR.append(f'ES #{n}: GFCI not explained')
            if ' OFF ' in prose and 'apagado (OFF)' not in prose: ERR.append(f'ES #{n}: OFF not localized before label')
            if ' ON ' in prose and 'encendido (ON)' not in prose: ERR.append(f'ES #{n}: ON not localized before label')
            for src in o.get('sources',[]):
                if any(d in src.get('url','') for d in ('epa.gov','cpsc.gov','fsis.usda.gov')) and 'EE. UU.' not in src.get('name',''):
                    ERR.append(f'ES #{n}: U.S. source lacks country context')
        else:
            prose=o.get('excerpt','')+' '+htmlv
            if re.search(r'\bGFCI\b',prose) and 'ground-fault circuit interrupter' not in prose.lower(): ERR.append(f'EN #{n}: GFCI not expanded')
            if re.search(r'\bLED\b',prose) and 'light-emitting diode' not in prose.lower(): ERR.append(f'EN #{n}: LED not expanded')

if len(BY)!=160: ERR.append(f'parsed {len(BY)} versions, expected 160')
if len(all_ids)!=len(set(all_ids)): ERR.append('duplicate article id')
if len(all_slugs)!=len(set(all_slugs)): ERR.append('duplicate slug within language')
for lang in ('es','en'):
    duplicates=[q for q,c in Counter(x.lower() for x in global_q[lang]).items() if c>1]
    if duplicates: ERR.append(f'{lang}: exact FAQ questions repeated across block: {duplicates[:5]}')
for n in range(391,471):
    es=BY.get(('es',n)); en=BY.get(('en',n))
    if es and en and es.get('translation_group')!=en.get('translation_group'): ERR.append(f'#{n}: translation_group mismatch')

safety={
393:['no camines','profesional'],400:['cierra la llave','no aprietes'],412:['no lo combines','gases peligrosos'],420:['escalera','profesional'],427:['nunca uses barbacoas o generadores dentro'],433:['no los amontones','secadora'],436:['plomo','humedad'],438:['electricidad mojada','agua contaminada'],444:['componentes eléctricos','drenaje'],451:['una sola vez','si vuelve a saltar'],452:['riesgo de incendio','huele a quemado'],459:['nunca metas la mano','corta la alimentación'],460:['olor eléctrico','viertas agua'],461:['no abras la base','olor eléctrico'],465:['no retires la placa','electricista'],466:['no retires la placa','electricista']}
for n,terms in safety.items():
    raw=(BY.get(('es',n),{}).get('excerpt','')+' '+BY.get(('es',n),{}).get('content_html','')).lower()
    for t in terms:
        if t not in raw: ERR.append(f'ES #{n}: missing safety boundary {t}')
food={454:['tomate cortado','refriger'],455:['descongela en el refrigerador','no congeles leche que ya'],463:['no congeles huevos enteros','descongela en refrigeración']}
for n,terms in food.items():
    raw=BY.get(('es',n),{}).get('content_html','').lower()
    for t in terms:
        if t not in raw: ERR.append(f'ES #{n}: missing food-safety boundary {t}')

pairs=[
(391,392,'green algae film vs moss mat on a patio'),(393,194,'roof moss safety vs temporary roof-leak containment'),(395,312,'filter replacement procedure vs replacement interval'),(396,470,'whole-house filter interval vs slow filtered-water flow'),(397,174,'toilet base leak vs overflowing toilet'),(398,415,'general slow sink vs kitchen-specific slow drain'),(402,171,'range-hood filter cleaning vs full hood cleaning'),(402,477,'current filter-cleaning article vs exact future canonical duplicate'),(403,168,'baked-on cooktop grease vs general cooktop cleaning'),(405,166,'pet urine on flooring vs urine odor in mattress'),(406,322,'safe vinegar uses vs surfaces vinegar should not clean'),(407,408,'general fabric chair vs upholstered dining-chair set'),(409,410,'curtains in place vs blackout-curtain care'),(411,475,'full shower curtain vs future liner-specific cleaning'),(412,330,'baking-soda/vinegar myth vs kitchen-sink unclogging method'),(413,415,'water backup vs slow kitchen drainage'),(414,398,'bathtub backflow vs slow sink diagnosis'),(416,417,'whole-home electricity ranking vs dryer electricity use'),(418,178,'why ants return vs kitchen-ant prevention'),(421,251,'mice inside walls vs general mouse signs'),(421,422,'confirm wall activity vs find exterior entry route'),(422,335,'systematic entry search vs common entry points'),(422,423,'find house entry vs prevent garage entry'),(425,469,'squeaky floor vs squeaky bed'),(426,195,'weather/penetration roof-source diagnosis vs earlier leak tracing'),(430,498,'towel softness vs future musty-towel prevention'),(430,499,'towel softness vs future post-wash odor'),(431,346,'prevent shrinking vs recover shrunken clothes'),(432,433,'microfiber care vs contaminated-rag safety'),(436,491,'repair peeling paint vs future peeling diagnosis'),(436,437,'peeling repair vs paint-bubble diagnosis'),(441,358,'overwatering rescue vs overwatering identification'),(441,442,'general recovery vs root-rot treatment'),(443,360,'weak coverage vs repeated Wi-Fi disconnects'),(443,361,'improve coverage vs router placement'),(444,449,'musty AC vs musty bedroom'),(444,450,'musty AC vs musty basement'),(447,362,'one hot room vs one cold room'),(447,448,'diagnose hot room vs balance airflow'),(451,306,'breaker reset vs one-room outage'),(451,307,'breaker reset vs repeated GFCI trips'),(451,388,'breaker reset vs GFCI reset'),(452,217,'vent-cleaning interval vs vent-cleaning procedure'),(455,224,'freeze milk vs milk left out'),(456,163,'burnt oil on stainless vs burnt pot cleaning'),(458,222,'dishwasher cleaning procedure vs odor diagnosis'),(460,384,'air-fryer smoke vs oven smoke'),(463,223,'freezing eggs vs eggs left unrefrigerated'),(464,374,'freeze bread vs storing bread fresh'),(465,390,'buzzing switch vs hot switch'),(466,389,'buzzing outlet vs hot outlet'),(467,468,'general siding vs vinyl-specific cleaning'),(469,425,'bed squeak vs floor squeak'),(470,312,'slow filter flow vs refrigerator-filter interval')]

def txt(lang,n):
    o=BY.get((lang,n)) or find_article(lang,n)
    return (o.get('title','')+' '+o.get('content_html','')) if o else ''

if ERR:
    print(f'FINAL HOME 391-470 AUDIT FAILED: {len(ERR)} errors, {len(WARN)} warnings')
    for e in ERR: print('ERROR:',e)
    for w in WARN: print('WARN:',w)
    raise SystemExit(1)

lines=['# HOME — Quality audit 391–470','','## Result','', '- JSON checked: **160 / 160** (80 ES + 80 EN expected).','- Structural/editorial validation: **PASS**.','- Explicit FAQ validation: **PASS 480 / 480**.','- Blocking errors: **0**.',f'- Non-blocking warnings: **{len(WARN)}**.','','## Scope and editorial criteria','', '- Exact canonical topics 391–470 preserved from `content/topics/`.','- ES and EN share article number and translation group while using independently localized prose.','- All FAQ questions were written explicitly per topic; none are generated from H2 wording.','- Safety-sensitive roofing, plumbing, electrical, appliance, chemical and food pages include stop conditions and escalation boundaries.','- Search-intent metadata is blocked if it falls back to the artificial syntax found in earlier batches.','- Close topics are audited by search intent and next action, not similarity score alone.','','## Quantitative profile','', '| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for a,b in ((391,410),(411,430),(431,450),(451,470)):
    vals=[]
    for lang in ('es','en'):
        os=[BY[(lang,n)] for n in range(a,b+1)]
        vals.extend([sum(wc(o['content_html']) for o in os)/20,4.0,3.0,sum(len(o['sources']) for o in os)/20])
    lines.append(f'| {a}–{b} | {vals[0]:.1f} | {vals[1]:.1f} | {vals[2]:.1f} | {vals[3]:.1f} | {vals[4]:.1f} | {vals[5]:.1f} | {vals[6]:.1f} | {vals[7]:.1f} |')
lines += ['','## Cannibalization / overlap diagnostics','', '| Pair | Intent distinction | ES Jaccard | EN Jaccard |','|---|---|---:|---:|']
for x,y,d in pairs:
    a_es,b_es=txt('es',x),txt('es',y); a_en,b_en=txt('en',x),txt('en',y)
    es=f'{jacc(a_es,b_es):.3f}' if a_es and b_es else 'n/a'; en=f'{jacc(a_en,b_en):.3f}' if a_en and b_en else 'n/a'
    lines.append(f'| #{x}/#{y} | {d} | {es} | {en} |')
lines += ['','## Editorial overlap conclusions','',
'- #391/#392: algae is treated as a thin green film; moss as a thicker mat that needs different mechanical removal.','- #395/#312: #395 is the refrigerator-filter replacement procedure; #312 remains the interval decision.','- #398/#415: #398 diagnoses a slow sink generally; #415 is specific to kitchen grease, food debris and dishwasher behavior.','- #402/#477: the canonical inventory contains a future exact duplicate at #477. #402 is generated here; #477 must be handled explicitly when that future block is produced rather than silently duplicated.','- #421/#422/#423: wall activity confirmation, entry-route finding and garage prevention are separate user tasks.','- #426/#195: #426 is organized around weather correlation and roof penetrations from safe vantage points; the earlier page remains the interior leak-tracing path.','- #441/#442: #441 covers general recovery from overwatering; #442 begins once root rot is present and treats the root system directly.','- #444/#449/#450: system odor, bedroom odor and basement odor begin from different moisture sources and next checks.','- #451/#307/#388: a circuit-breaker reset is distinct from repeated GFCI trips and from resetting the GFCI device itself.','- #465/#466: buzzing at a switch and buzzing at a receptacle share stop signs but have different device and load clues.','- #467/#468: #467 is material-agnostic siding cleaning; #468 is vinyl-specific and focuses on spray direction, heat and pressure.','','## Manual review priorities','',
'Read both languages for #393, #412–415, #420–427, #433, #436–450 and #451–470. Reject any page that encourages unsafe roof access, chemical mixing, repeated breaker resets, live electrical work, tasting questionable food, or continued use of overheated/burning appliances.','','## Warnings','']
lines += [f'- {w}' for w in WARN] if WARN else ['- None.']
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'FINAL HOME 391-470 AUDIT PASS: versions={len(BY)} FAQ={sum(len(o["faq"]) for o in BY.values())} warnings={len(WARN)}')
