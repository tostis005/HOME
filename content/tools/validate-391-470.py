#!/usr/bin/env python3
from pathlib import Path
import json,re,html,math
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'
TOOLS=ROOT/'tools'
REPORT=ART/'QUALITY-AUDIT-391-470.md'
ERR=[]; WARN=[]; BY={}; RECORDS={}

for p in sorted(TOOLS.glob('batch-391-470-*.json')):
    for r in json.loads(p.read_text(encoding='utf-8')):
        if r['n'] in RECORDS: ERR.append(f'duplicate batch topic #{r["n"]}')
        RECORDS[r['n']]=r
if sorted(RECORDS)!=list(range(391,471)):
    ERR.append(f'batch inventory mismatch: found {len(RECORDS)} records')

def text_of(s):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()

def word_count(s):
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",text_of(s)))

def tokens(s):
    stop={'the','a','an','and','or','to','of','in','on','for','with','is','are','my','your','how','why','what','can','you','de','la','el','los','las','y','o','en','un','una','que','por','para','se','mi','como','cómo'}
    return {x for x in re.findall(r'[a-záéíóúñü]+',text_of(s).lower()) if len(x)>2 and x not in stop}

def jac(a,b):
    A=tokens(a); B=tokens(b)
    return (len(A&B)/len(A|B)) if A|B else 0.0

required=['schema_version','id','article_number','translation_group','language','locale','market_context','title','slug','seo','excerpt','taxonomy','content_html','faq','sources','image','status']
ids=[]; slugs=[]
for lang in ('es','en'):
    d=ART/lang
    for n in range(391,471):
        fs=list(d.glob(f'{n:03d}-*.json'))
        if len(fs)!=1:
            ERR.append(f'{lang} #{n}: expected exactly one JSON, found {len(fs)}'); continue
        p=fs[0]
        try: o=json.loads(p.read_text(encoding='utf-8'))
        except Exception as e: ERR.append(f'{lang} #{n}: invalid JSON {e}'); continue
        BY[(lang,n)]=o
        miss=[k for k in required if k not in o]
        if miss: ERR.append(f'{lang} #{n}: missing fields {miss}')
        if o.get('schema_version')!=1 or o.get('article_number')!=n or o.get('language')!=lang or o.get('status')!='publish': ERR.append(f'{lang} #{n}: identity/status mismatch')
        if o.get('locale')!=('es-ES' if lang=='es' else 'en-US'): ERR.append(f'{lang} #{n}: locale mismatch')
        if not o.get('translation_group','').startswith(f'{n}-'): ERR.append(f'{lang} #{n}: malformed translation_group')
        if not o.get('id','').startswith(f'{lang}-{n}-'): ERR.append(f'{lang} #{n}: malformed id')
        ids.append(o.get('id')); slugs.append((lang,o.get('slug')))
        if word_count(o.get('content_html',''))<150: ERR.append(f'{lang} #{n}: article depth below 150 words ({word_count(o.get("content_html",""))})')
        if o.get('content_html','').count('<h2>')!=4: ERR.append(f'{lang} #{n}: expected 4 H2')
        faq=o.get('faq',[])
        if len(faq)!=3: ERR.append(f'{lang} #{n}: expected 3 FAQ')
        rec=RECORDS.get(n,{})
        expected_q=rec.get(f'faq_{lang}',[])
        got_q=[x.get('question','') for x in faq]
        if got_q!=expected_q: ERR.append(f'{lang} #{n}: FAQ questions differ from explicit editorial source')
        if len(set(q.lower() for q in got_q))!=len(got_q): ERR.append(f'{lang} #{n}: duplicate FAQ question')
        for item in faq:
            q=item.get('question',''); a=item.get('answer','')
            if not q.endswith('?') and not q.endswith('？'): ERR.append(f'{lang} #{n}: FAQ not phrased as question: {q}')
            if len(q)<18: WARN.append(f'{lang} #{n}: unusually short FAQ question')
            if a not in o.get('content_html',''): ERR.append(f'{lang} #{n}: FAQ answer not grounded verbatim in article section')
        seo=o.get('seo',{})
        for k in ('title','meta_description','search_intent'):
            if not seo.get(k): ERR.append(f'{lang} #{n}: missing SEO {k}')
        if seo.get('title')!=o.get('title'): ERR.append(f'{lang} #{n}: SEO title differs from article title')
        if len(seo.get('meta_description',''))>190: WARN.append(f'{lang} #{n}: meta description longer than 190 chars')
        if seo.get('title','').endswith('...') or '…' in seo.get('title',''): ERR.append(f'{lang} #{n}: mechanically truncated SEO title')
        intent=seo.get('search_intent','').lower()
        bad_intent=['para cómo','para cada cuánto','prevenir evitar','for how to','to how to','to how often should','for how often should','for where should','prevent prevent']
        if any(x in intent for x in bad_intent): ERR.append(f'{lang} #{n}: artificial search_intent syntax: {seo.get("search_intent")}')
        raw=json.dumps(o,ensure_ascii=False)
        for bad in ('HOME prioriza','HOME recomienda','HOME prioritizes','En este artículo hemos decidido','In this article we decided'):
            if bad.lower() in raw.lower(): ERR.append(f'{lang} #{n}: editorial metadiscourse')
        if lang=='es':
            low=raw.lower()
            for bad in ('\"hvac\"','inverter','topper','pillow-top','peva'):
                if bad in low: ERR.append(f'ES #{n}: avoidable/unexplained terminology {bad}')
            prose=o.get('excerpt','')+' '+o.get('content_html','')
            if re.search(r'\bLED\b',prose) and 'diodos emisores de luz' not in prose.lower(): ERR.append(f'ES #{n}: LED not expanded on first use')
            if re.search(r'\bGFCI\b',prose) and 'falla a tierra' not in prose.lower(): ERR.append(f'ES #{n}: GFCI not explained')
            if ' OFF ' in prose and 'apagado (OFF)' not in prose: ERR.append(f'ES #{n}: untranslated OFF interface label')
            if ' ON ' in prose and 'encendido (ON)' not in prose: ERR.append(f'ES #{n}: untranslated ON interface label')
            for src in o.get('sources',[]):
                u=src.get('url','')
                if any(dom in u for dom in ('epa.gov','cpsc.gov','fsis.usda.gov')) and 'EE. UU.' not in src.get('name',''):
                    ERR.append(f'ES #{n}: U.S. institution lacks country context in source name')
        else:
            prose=o.get('excerpt','')+' '+o.get('content_html','')
            if re.search(r'\bGFCI\b',prose) and 'ground-fault circuit interrupter' not in prose.lower(): ERR.append(f'EN #{n}: GFCI not expanded on first use')
            if re.search(r'\bLED\b',prose) and 'light-emitting diode' not in prose.lower(): ERR.append(f'EN #{n}: LED not expanded on first use')

if len(BY)!=160: ERR.append(f'expected 160 parsed versions, got {len(BY)}')
if len(ids)!=len(set(ids)): ERR.append('duplicate article id')
if len(slugs)!=len(set(slugs)): ERR.append('duplicate slug within language')
for n in range(391,471):
    es=BY.get(('es',n)); en=BY.get(('en',n))
    if es and en and es.get('translation_group')!=en.get('translation_group'): ERR.append(f'#{n}: translation_group mismatch')

SAFETY={
393:['no camines','profesional'],
400:['cierra la llave','no aprietes'],
412:['no lo combines','gases peligrosos'],
420:['escalera','profesional'],
427:['nunca uses barbacoas o generadores dentro'],
433:['no los amontones','secadora'],
436:['plomo','humedad'],
438:['electricidad mojada','agua contaminada'],
444:['componentes eléctricos','drenaje'],
451:['una sola vez','si vuelve a saltar'],
452:['riesgo de incendio','huele a quemado'],
459:['nunca metas la mano','corta la alimentación'],
460:['olor eléctrico','no viertas agua'],
461:['no abras la base','olor eléctrico'],
465:['no retires la placa','electricista'],
466:['no retires la placa','electricista']
}
for n,terms in SAFETY.items():
    o=BY.get(('es',n)); raw=(o.get('excerpt','')+' '+o.get('content_html','')).lower() if o else ''
    for term in terms:
        if term not in raw: ERR.append(f'ES #{n}: safety concept missing: {term}')

FOOD={454:['tomate cortado','refriger'],455:['descongela en el refrigerador','no congeles leche que ya'],463:['no congeles huevos enteros','descongela en refrigeración']}
for n,terms in FOOD.items():
    raw=(BY.get(('es',n),{}).get('content_html','')).lower()
    for term in terms:
        if term not in raw: ERR.append(f'ES #{n}: food-safety concept missing: {term}')

# quantify FAQ starter repetition without forcing a single style
for lang in ('es','en'):
    starters=[]
    for n in range(391,471):
        for item in BY.get((lang,n),{}).get('faq',[]):
            q=re.sub(r'^[¿?]+','',item.get('question','')).strip().lower()
            starters.append(' '.join(q.split()[:2]))
    counts=Counter(starters)
    if counts and counts.most_common(1)[0][1]>24:
        ERR.append(f'{lang}: FAQ starter overused: {counts.most_common(1)[0]}')

# overlap diagnostics, including earlier and future canonical intents
PAIRS=[
(391,392,'green algae film vs moss mat on a patio'),(393,194,'roof moss safety vs temporary roof-leak containment'),(395,312,'filter replacement procedure vs replacement interval'),(396,470,'whole-house filter interval vs slow filtered-water flow'),(397,174,'toilet base leak vs overflowing toilet'),(398,415,'general slow sink vs kitchen-specific slow drain'),(402,171,'range-hood filter cleaning vs full hood cleaning'),(402,477,'current filter-cleaning article vs exact future canonical duplicate'),(403,168,'baked-on cooktop grease vs general glass-cooktop cleaning'),(405,166,'pet urine on flooring vs urine odor in mattress'),(406,322,'safe vinegar uses vs surfaces vinegar should not clean'),(407,408,'general fabric chair vs upholstered dining-chair set'),(409,410,'curtains in place vs blackout-curtain material care'),(411,475,'full shower curtain vs future liner-specific cleaning'),(412,330,'baking-soda/vinegar myth vs kitchen-sink unclogging method'),(413,415,'water backup vs slow kitchen drainage'),(414,398,'bathtub backflow vs slow sink diagnosis'),(416,417,'whole-home electricity ranking vs dryer electricity use'),(418,178,'why ants return vs prevention in the kitchen'),(421,251,'mice inside walls vs general signs of mice'),(421,422,'confirm wall activity vs find exterior entry route'),(422,335,'systematic entry search vs common mouse entry points'),(422,423,'find house entry vs prevent garage entry'),(425,469,'squeaky floor vs squeaky bed'),(426,195,'weather/penetration roof-source diagnosis vs earlier leak tracing'),(430,498,'towel softness vs future musty-towel prevention'),(430,499,'towel softness vs future post-wash odor diagnosis'),(431,346,'prevent shrinking vs recover already shrunken clothes'),(432,433,'microfiber care vs chemically contaminated cleaning-rag safety'),(436,491,'repair peeling paint vs future diagnosis of why paint peels'),(436,437,'peeling repair vs paint-bubble diagnosis'),(441,358,'rescue overwatered plant vs identify overwatering'),(441,442,'general overwatering recovery vs root-rot treatment'),(443,360,'weak Wi-Fi coverage vs repeated disconnects'),(443,361,'improve coverage vs router placement'),(444,449,'musty AC source vs musty bedroom source'),(444,450,'musty AC vs basement moisture odor'),(447,362,'one hot room vs one cold room'),(447,448,'diagnose hot room vs balance airflow'),(451,306,'reset one tripped breaker vs one-room outage diagnosis'),(451,307,'breaker reset vs repeatedly tripping GFCI diagnosis'),(451,388,'breaker reset vs GFCI reset'),(452,217,'dryer-vent cleaning interval vs cleaning procedure'),(454,374,'tomato refrigeration decision vs bread storage'),(455,224,'freeze milk vs milk left out'),(456,163,'burnt oil on stainless pan vs burnt pot cleaning'),(458,222,'dishwasher cleaning procedure vs why dishwasher smells'),(459,461,'jammed disposal hum vs air-fryer no-start'),(460,384,'air-fryer smoke vs oven smoke'),(463,223,'freezing eggs vs eggs left unrefrigerated'),(464,374,'freeze bread vs room-temperature bread storage'),(465,390,'buzzing switch vs hot switch'),(466,389,'buzzing outlet vs hot outlet'),(467,468,'general siding cleaning vs vinyl-specific method'),(469,425,'bed squeak vs floor squeak'),(470,312,'slow filtered-water flow vs refrigerator-filter interval')]

def article_text(lang,n):
    o=BY.get((lang,n))
    if o: return o.get('title','')+' '+o.get('content_html','')
    fs=list((ART/lang).glob(f'{n:03d}-*.json'))
    if len(fs)==1:
        try:
            z=json.loads(fs[0].read_text(encoding='utf-8')); return z.get('title','')+' '+z.get('content_html','')
        except: return ''
    return ''

if ERR:
    print(f'HOME 391-470 audit FAILED: {len(ERR)} errors, {len(WARN)} warnings')
    for e in ERR: print('ERROR:',e)
    for w in WARN: print('WARN:',w)
    raise SystemExit(1)

# Build report only after all blocking checks pass.
lines=['# HOME — Quality audit 391–470','','## Result','', '- JSON checked: **160 / 160** (80 ES + 80 EN expected).','- Structural/editorial validation: **PASS**.','- Explicit FAQ validation: **PASS 480 / 480**.','- Blocking errors: **0**.',f'- Non-blocking warnings: **{len(WARN)}**.','','## Scope and editorial criteria','', '- Canonical topics 391–470 preserved exactly from `content/topics/`.','- Spanish and English share article number and translation group while using independently written prose.','- FAQ questions are explicit editorial inputs, never transformed automatically from H2 headings.','- Safety-sensitive roof, plumbing, electrical, appliance, chemical and food topics include stop conditions and professional boundaries.','- Search-intent metadata is checked for natural ES/EN syntax and prior template regressions.','- Close topics are reviewed by reader decision and next action, not word similarity alone.','','## Quantitative profile','', '| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
for a,b in ((391,410),(411,430),(431,450),(451,470)):
    vals=[]
    for lang in ('es','en'):
        os=[BY[(lang,n)] for n in range(a,b+1)]
        vals += [sum(word_count(o['content_html']) for o in os)/len(os), sum(o['content_html'].count('<h2>') for o in os)/len(os), sum(len(o['faq']) for o in os)/len(os), sum(len(o['sources']) for o in os)/len(os)]
    lines.append(f'| {a}–{b} | {vals[0]:.1f} | {vals[1]:.1f} | {vals[2]:.1f} | {vals[3]:.1f} | {vals[4]:.1f} | {vals[5]:.1f} | {vals[6]:.1f} | {vals[7]:.1f} |')
lines += ['','## Cannibalization / overlap diagnostics','', '| Pair | Intent distinction | ES Jaccard | EN Jaccard |','|---|---|---:|---:|']
for x,y,desc in PAIRS:
    row=[]
    for lang in ('es','en'):
        A=article_text(lang,x); B=article_text(lang,y)
        row.append(f'{jac(A,B):.3f}' if A and B else 'n/a')
    lines.append(f'| #{x}/#{y} | {desc} | {row[0]} | {row[1]} |')
lines += ['','## Editorial overlap conclusions','',
'- #391/#392: algae is a thin green film; moss is a thicker rooted mat requiring different mechanical removal.','- #395/#312: #395 is the refrigerator-filter replacement procedure; #312 remains the replacement-interval decision.','- #398/#415: #398 diagnoses any slow sink; #415 focuses on grease, food debris and dishwasher behavior in the kitchen branch.','- #402/#477: the canonical inventory contains a future exact duplicate at #477. #402 is published in this block; #477 must be handled explicitly when that future block is generated rather than silently duplicated.','- #421/#422/#423: wall activity confirmation, entry-route finding and garage prevention remain separate user decisions.','- #426/#195: #426 emphasizes weather correlation and roof penetrations from safe vantage points; the earlier article remains the interior leak-tracing path.','- #441/#442: #441 covers general recovery from overwatering; #442 starts when root rot is already present and requires root-level treatment.','- #444/#449/#450: system odor, bedroom odor and basement odor each begin from a different moisture source and next diagnostic step.','- #451/#307/#388: a tripped breaker reset is distinct from repeated GFCI trips and from resetting the GFCI device itself.','- #465/#466: buzzing at a light switch and buzzing at a receptacle share electrical stop signs but have different load clues and device behavior.','- #467/#468: #467 is material-agnostic siding cleaning; #468 is specifically about vinyl direction, heat and pressure limits.','','## Manual review priorities','',
'Read both languages for #393, #412–415, #420–427, #433, #436–450 and #451–470. Reject any page that encourages unsafe roof access, chemical mixing, repeated breaker resets, live electrical work, tasting questionable food, or continued use of overheated/burning appliances.','','## Warnings','']
if WARN:
    lines += [f'- {w}' for w in WARN]
else:
    lines.append('- None.')
REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'HOME 391-470 audit PASS: articles={len(BY)} FAQ={sum(len(o["faq"]) for o in BY.values())} warnings={len(WARN)}')
print(f'Report: {REPORT}')
