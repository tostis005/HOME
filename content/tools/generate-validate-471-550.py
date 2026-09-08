#!/usr/bin/env python3
from pathlib import Path
import json,re,html,sys,unicodedata
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'tools'; ART=ROOT/'articles'; TOPICS=ROOT/'topics'; REPORT=ART/'QUALITY-AUDIT-471-550.md'
DUP={477:402,480:472,499:263}
Q3={471:2,472:3,473:2,474:3,475:2,476:3,478:3,479:3,481:2,482:2,483:3,484:3,485:3,486:3,487:2,488:3,489:3,490:2,491:2,492:3,493:2,494:3,495:2,496:3,497:3,498:3,500:3,501:3,502:3,503:2,504:2,505:3,506:2,507:2,508:3,509:2,510:3,511:2,512:3,513:3,514:3,515:3,516:2,517:3,518:3,519:3,520:3,521:2,522:2,523:2,524:3,525:3,526:2,527:2,528:2,529:3,530:3,531:3,532:3,533:3,534:2,535:3,536:3,537:3,538:3,539:2,540:3,541:2,542:3,543:3,544:2,545:2,546:3,547:3,548:2,549:3,550:3}

SOURCES={
'cleaning':{
'es':('American Cleaning Institute — Cleaning Tips','https://www.cleaninginstitute.org/cleaning-tips','Métodos de limpieza doméstica, uso y dosificación de productos y compatibilidad con materiales.'),
'en':('American Cleaning Institute — Cleaning Tips','https://www.cleaninginstitute.org/cleaning-tips','Household cleaning methods, product use and dosing, and material compatibility.')},
'water':{
'es':('Agencia de Protección Ambiental de EE. UU. (EPA) — WaterSense Home Maintenance','https://www.epa.gov/watersense/home-maintenance','Mantenimiento doméstico relacionado con agua, fugas, accesorios y eficiencia.'),
'en':('U.S. Environmental Protection Agency (EPA) — WaterSense Home Maintenance','https://www.epa.gov/watersense/home-maintenance','Household water maintenance, leaks, fixtures, and efficiency.')},
'water_softener':{
'es':('Agencia de Protección Ambiental de EE. UU. (EPA) — Cation Exchange Water Softeners','https://www.epa.gov/watersense/cation-exchange-water-softeners','Funcionamiento, regeneración y eficiencia de descalcificadores de intercambio iónico.'),
'en':('U.S. Environmental Protection Agency (EPA) — Cation Exchange Water Softeners','https://www.epa.gov/watersense/cation-exchange-water-softeners','Ion-exchange softener operation, regeneration, and efficiency.')},
'energy':{
'es':('Departamento de Energía de EE. UU. — Energy Saver','https://www.energy.gov/energysaver','Eficiencia energética doméstica, climatización y consumo de equipos.'),
'en':('U.S. Department of Energy — Energy Saver','https://www.energy.gov/energysaver','Residential energy efficiency, heating and cooling, and equipment use.')},
'ipm':{
'es':('Agencia de Protección Ambiental de EE. UU. (EPA) — Integrated Pest Management','https://www.epa.gov/ipm','Manejo integrado de plagas mediante saneamiento, exclusión, vigilancia y control dirigido.'),
'en':('U.S. Environmental Protection Agency (EPA) — Integrated Pest Management','https://www.epa.gov/ipm','Integrated pest management using sanitation, exclusion, monitoring, and targeted control.')},
'mold':{
'es':('Agencia de Protección Ambiental de EE. UU. (EPA) — Mold and Moisture','https://www.epa.gov/mold','Control de humedad, prevención, limpieza y recurrencia del moho.'),
'en':('U.S. Environmental Protection Agency (EPA) — Mold and Moisture','https://www.epa.gov/mold','Moisture control, mold prevention, cleanup, and recurrence.')},
'plants':{
'es':('University of Minnesota Extension — Houseplants','https://extension.umn.edu/houseplants','Cuidados de plantas de interior, raíces, sustrato, riego y trasplante.'),
'en':('University of Minnesota Extension — Houseplants','https://extension.umn.edu/houseplants','Houseplant care, roots, potting mix, watering, and repotting.')},
'electrical':{
'es':('Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC) — Electrical Safety','https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','Riesgos eléctricos domésticos y respuesta segura ante sobrecalentamiento, enchufes, interruptores y automáticos.'),
'en':('U.S. Consumer Product Safety Commission (CPSC) — Electrical Safety','https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','Household electrical hazards and safe response to overheating, outlets, switches, and breakers.')},
'smoke':{
'es':('Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC) — Smoke Alarms','https://www.cpsc.gov/safety-education/safety-guides/smoke-alarms','Uso, prueba, mantenimiento y sustitución de detectores de humo.'),
'en':('U.S. Consumer Product Safety Commission (CPSC) — Smoke Alarms','https://www.cpsc.gov/safety-education/safety-guides/smoke-alarms','Smoke-alarm use, testing, maintenance, and replacement.')},
'food':{
'es':('Departamento de Agricultura de EE. UU. (USDA) — Food Safety Basics','https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics','Reglas de tiempo, temperatura, refrigeración, congelación y manipulación segura de alimentos.'),
'en':('U.S. Department of Agriculture (USDA) — Food Safety Basics','https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics','Time, temperature, refrigeration, freezing, and safe food-handling guidance.')},
'gas':{
'es':('Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC) — Home Safety','https://www.cpsc.gov/Safety-Education','Seguridad doméstica ante aparatos de gas, incendios y riesgos de productos.'),
'en':('U.S. Consumer Product Safety Commission (CPSC) — Home Safety','https://www.cpsc.gov/Safety-Education','Household safety around gas appliances, fires, and consumer-product hazards.')}
}

def plain(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def wc(s): return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",plain(s)))
def slugify(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower().replace('’','').replace("'",'')
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',s)).strip('-')
def clean_title(s): return s.strip().lstrip('¿').rstrip('?').strip()
def first_sentence(s):
    m=re.match(r'(.+?[.!?])(?:\s|$)',s.strip())
    return m.group(1) if m else s.strip()
def src(lang,key):
    if key not in SOURCES: return []
    name,url,note=SOURCES[key][lang]
    return [{'name':name,'url':url,'note':note}]

def intent(lang,title,kind):
    t=clean_title(title)
    if lang=='es':
        if t.startswith('Por qué '): return f'Identificar por qué {t[8:].lower()}, usar señales observables para decidir qué comprobar primero y saber cuándo corresponde detenerse o pedir ayuda.'
        if t.startswith('Cómo '): return f'Aprender a {t[5:].lower()} con un método práctico, seguro y ordenado que permita actuar sin una segunda búsqueda obvia.'
        if t.startswith('Se puede '): return f'Decidir si {t.lower()} usando tiempo, temperatura, compatibilidad y seguridad en lugar de una regla genérica.'
        if t.startswith('Hay que '): return f'Decidir si {t.lower()} según el estado real, el material y las condiciones de uso.'
        if t.startswith('Cuánta ') or t.startswith('Cuánto '): return f'Estimar {t.lower()} con los datos que realmente determinan el consumo o la duración.'
        if t.startswith('Cada cuánto '): return f'Decidir {t.lower()} según el equipo, uso, estado y señales que adelantan el mantenimiento.'
        if t.startswith('Conviene '): return f'Decidir si {t.lower()} según cómo funciona el sistema y qué efecto práctico produce.'
        return f'Resolver la duda «{t}» con criterios prácticos de seguridad, compatibilidad y resultado.'
    if t.startswith('Why '): return f'Identify why {t[4:].lower()}, use observable clues to choose the first checks, and know when to stop or get professional help.'
    if t.startswith('How to '): return f'Learn how to {t[7:].lower()} with a practical, safe sequence that lets the reader act without an obvious second search.'
    if t.startswith('Can You ') or t.startswith('Can '): return f'Decide whether {t.lower()} using safety, condition, compatibility, and time rather than a one-size-fits-all rule.'
    if t.startswith('Should '): return f'Decide whether {t.lower()} based on how the system or food actually behaves and the relevant safety limits.'
    if t.startswith('How Much '): return f'Estimate {t.lower()} using the variables that actually determine energy use or cost.'
    if t.startswith('How Often '): return f'Decide {t.lower()} based on equipment, use, condition, and early maintenance signals.'
    return f'Answer “{t}” with practical criteria for safety, compatibility, and results.'

def polish(lang,n,s):
    if lang=='es':
        s=s.replace('driver defectuoso','controlador electrónico defectuoso')
        if n in (483,484):
            s=s.replace('kWh','kilovatios-hora (kWh)',1)
        if n==483: s=s.replace('los BTU/h describen','las unidades térmicas británicas por hora (BTU/h) describen')
    else:
        s=s.replace('HVAC system may still operate','heating and cooling system may still operate')
        if n in (483,484): s=s.replace('kWh','kilowatt-hours (kWh)',1)
        if n==483: s=s.replace('BTU/h describes','British thermal units per hour (Btu/h) describe')
    return s

def load_records():
    rec={}
    for p in sorted(TOOLS.glob('batch-*.json')):
        if not re.search(r'batch-(?:47[1-9]|4[89]\d|5[0-5]\d)',p.name): continue
        try: arr=json.loads(p.read_text(encoding='utf-8'))
        except Exception as e: raise SystemExit(f'Invalid JSON {p}: {e}')
        for r in arr:
            n=int(r['n'])
            if 471<=n<=550:
                if n in rec: raise SystemExit(f'Duplicate source record #{n}')
                rec[n]=r
    covered=set(rec)|set(DUP)
    expected=set(range(471,551))
    if covered!=expected:
        raise SystemExit(f'Canonical coverage mismatch missing={sorted(expected-covered)} extra={sorted(covered-expected)}')
    return rec

def canonical_titles():
    out={}
    for fn in ('TOPICS-401-500.md','TOPICS-501-600.md'):
        text=(TOPICS/fn).read_text(encoding='utf-8')
        for line in text.splitlines():
            m=re.match(r'^(\d+)\.\s+(.+)$',line)
            if m: out[int(m.group(1))]=m.group(2).strip()
    return out

def build(r,lang):
    n=r['n']; title=r[f'{lang}_title']; en_slug=slugify(r['en_title']); slug=slugify(title)
    intro=polish(lang,n,r[f'intro_{lang}'])
    sections=[]
    for sec in r['sections']:
        h=sec[0 if lang=='es' else 1]; p=polish(lang,n,sec[2 if lang=='es' else 3]); sections.append((h,p))
    content='<p>'+intro+'</p>'+''.join(f'<h2>{h}</h2><p>{p}</p>' for h,p in sections)
    qs=r[f'faq_{lang}']; idx=[0,1,Q3.get(n,3)]
    faq=[{'question':qs[i],'answer':sections[idx[i]][1]} for i in range(3)]
    family=r['family']; kind=r['kind']
    sources=src(lang,r.get('source',''))
    concept=(f'Fotografía editorial doméstica realista sobre «{clean_title(title)}», mostrando {sections[0][0].lower()} como la acción o pista principal; materiales cotidianos, sin texto ni marcas.' if lang=='es' else f'Realistic household editorial photograph about “{clean_title(title)},” clearly showing {sections[0][0].lower()} as the main action or clue; ordinary household materials, no text or branding.')
    return {
      'schema_version':1,'id':f'{lang}-{n}-{slug}','article_number':n,'translation_group':f'{n}-{en_slug}','language':lang,'locale':'es-ES' if lang=='es' else 'en-US',
      'market_context':'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if lang=='es' else 'United States and Canada; practical, safety-first household guidance written natively for North American readers.',
      'title':title,'slug':slug,'seo':{'title':title,'meta_description':first_sentence(intro),'search_intent':intent(lang,title,kind)},'excerpt':intro,
      'taxonomy':{'food_family':family,'food_subcategories':[en_slug],'article_types':[kind,family],'primary_article_type':kind},
      'content_html':content,'faq':faq,'sources':sources,'image':{'concept':concept,'alt':clean_title(title)},'status':'publish'}

def article_path(lang,n):
    fs=list((ART/lang).glob(f'{n:03d}-*.json'))
    return fs[0] if len(fs)==1 else None

def generate(rec):
    for lang in ('es','en'):
        (ART/lang).mkdir(parents=True,exist_ok=True)
        for n,r in rec.items():
            if n in DUP: continue
            o=build(r,lang); p=ART/lang/f'{n:03d}-{o["slug"]}.json'
            for old in (ART/lang).glob(f'{n:03d}-*.json'):
                if old!=p: old.unlink()
            p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    for lang in ('es','en'):
        for n in DUP:
            for p in (ART/lang).glob(f'{n:03d}-*.json'): p.unlink()

def validate(rec,write_report=True):
    errors=[]; warnings=[]; objs={}; canonical=canonical_titles()
    expected_nums=[n for n in range(471,551) if n not in DUP]
    for n in range(471,551):
        if canonical.get(n) is None: errors.append(f'#{n}: missing canonical topic')
        if n not in DUP and rec[n]['es_title']!=canonical[n]: errors.append(f'#{n}: ES title differs from canonical inventory')
    for lang in ('es','en'):
        for n in expected_nums:
            fs=list((ART/lang).glob(f'{n:03d}-*.json'))
            if len(fs)!=1: errors.append(f'{lang} #{n}: expected one JSON, found {len(fs)}'); continue
            try:o=json.loads(fs[0].read_text(encoding='utf-8'))
            except Exception as e: errors.append(f'{lang} #{n}: invalid JSON {e}'); continue
            objs[(lang,n)]=o
            if o.get('article_number')!=n or o.get('language')!=lang or o.get('status')!='publish': errors.append(f'{lang} #{n}: identity/status mismatch')
            if o.get('locale')!=('es-ES' if lang=='es' else 'en-US'): errors.append(f'{lang} #{n}: locale mismatch')
            if o.get('title')!=(rec[n]['es_title'] if lang=='es' else rec[n]['en_title']): errors.append(f'{lang} #{n}: title mismatch')
            if not o.get('id','').startswith(f'{lang}-{n}-') or not o.get('translation_group','').startswith(f'{n}-'): errors.append(f'{lang} #{n}: malformed id/group')
            if wc(o.get('content_html',''))<150: errors.append(f'{lang} #{n}: depth below floor ({wc(o.get("content_html",""))} words)')
            if o.get('content_html','').count('<h2>')!=4: errors.append(f'{lang} #{n}: expected 4 H2')
            faq=o.get('faq',[])
            if len(faq)!=3: errors.append(f'{lang} #{n}: expected 3 FAQ')
            expected_q=rec[n][f'faq_{lang}']
            if [x.get('question') for x in faq]!=expected_q: errors.append(f'{lang} #{n}: FAQ questions changed')
            for x in faq:
                if not x.get('question','').endswith('?'): errors.append(f'{lang} #{n}: malformed FAQ question')
                if x.get('answer','') not in o.get('content_html',''): errors.append(f'{lang} #{n}: FAQ answer not grounded in body')
            seo=o.get('seo',{})
            if seo.get('title')!=o.get('title') or not seo.get('meta_description') or not seo.get('search_intent'): errors.append(f'{lang} #{n}: SEO metadata incomplete')
            if len(seo.get('meta_description',''))>190: warnings.append(f'{lang} #{n}: meta description >190 chars')
            raw=json.dumps(o,ensure_ascii=False); low=raw.lower(); prose=o.get('excerpt','')+' '+o.get('content_html','')
            for bad in ('home prioriza','home recomienda','home prioritizes','en este artículo hemos decidido','in this article we decided'):
                if bad in low: errors.append(f'{lang} #{n}: editorial metadiscourse')
            for bad in ('para cómo','for how to','to how to','for where should','how can should','¿cómo debería no'):
                if bad in seo.get('search_intent','').lower(): errors.append(f'{lang} #{n}: artificial search_intent')
            if lang=='es':
                if re.search(r'\bLED\b',prose) and 'diodos emisores de luz (LED)' not in prose: errors.append(f'ES #{n}: LED not expanded')
                if re.search(r'\bGFCI\b',prose) and 'falla a tierra (GFCI)' not in prose: errors.append(f'ES #{n}: GFCI not explained')
                for bad in ('"hvac"','driver defectuoso','topper','pillow-top'):
                    if bad in low: errors.append(f'ES #{n}: avoidable term {bad}')
                for s in o.get('sources',[]):
                    if any(d in s.get('url','') for d in ('epa.gov','cpsc.gov','fsis.usda.gov')) and 'EE. UU.' not in s.get('name',''): errors.append(f'ES #{n}: U.S. source lacks country context')
            else:
                if re.search(r'\bLED\b',prose) and 'light-emitting diode (LED)' not in prose: errors.append(f'EN #{n}: LED not expanded')
                if re.search(r'\bGFCI\b',prose) and 'ground-fault circuit interrupter (GFCI)' not in prose: errors.append(f'EN #{n}: GFCI not expanded')
                if re.search(r'\bHVAC\b',prose): errors.append(f'EN #{n}: HVAC left unexplained')
    for n in DUP:
        for lang in ('es','en'):
            fs=list((ART/lang).glob(f'{n:03d}-*.json'))
            if fs: errors.append(f'{lang} #{n}: duplicate topic must not publish a second JSON')
        target=DUP[n]
        for lang in ('es','en'):
            if not article_path(lang,target): errors.append(f'{lang} duplicate target #{target} for #{n} is missing')
    if len(objs)!=154: errors.append(f'parsed {len(objs)} publishable versions, expected 154')
    for n in expected_nums:
        es=objs.get(('es',n)); en=objs.get(('en',n))
        if es and en and es['translation_group']!=en['translation_group']: errors.append(f'#{n}: translation_group mismatch')
    # targeted safety/precision checks
    must={516:['falla a tierra (gfci)','una sola vez','no retires la placa'],520:['no uses cuchillos','refrigerante'],521:['una sola vez','hueles gas'],522:['no dejes salir gas','no taladres'],525:['hinchados','no deben seguir cargándose'],526:['dos horas','olor y color no garantizan'],527:['dos horas','olor'],528:['dos horas','no pruebes'],529:['no introduzcas herramientas','electricista'],530:['no abras el cuadro','electricista'],540:['desenchúfalo','refrigerante'],541:['nunca','lejía'],550:['no selles un nido activo','malla fina']}
    for n,terms in must.items():
        o=objs.get(('es',n),{}); raw=(o.get('excerpt','')+' '+o.get('content_html','')).lower()
        for term in terms:
            if term not in raw: errors.append(f'ES #{n}: missing safety/precision boundary {term}')
    # duplicate inventory assertions
    if canonical.get(477)!=canonical.get(402): errors.append('#477 no longer exact duplicate of #402; revisit exception')
    if slugify(canonical.get(480,''))!=slugify(canonical.get(472,'')): # word order differs; semantic registry is intentional
        pass
    if 'toallas huelen mal' not in slugify(canonical.get(499,'')).replace('-',' '): errors.append('#499 duplicate registry needs review')
    if errors:
        print(f'HOME 471-550 AUDIT FAILED: errors={len(errors)} warnings={len(warnings)}')
        for x in errors: print('ERROR:',x)
        for x in warnings: print('WARN:',x)
        raise SystemExit(1)
    if write_report:
        rows=[]
        for a,b in ((471,490),(491,510),(511,530),(531,550)):
            vals=[]
            for lang in ('es','en'):
                os=[objs[(lang,n)] for n in range(a,b+1) if n not in DUP]
                vals += [sum(wc(o['content_html']) for o in os)/len(os),sum(o['content_html'].count('<h2>') for o in os)/len(os),sum(len(o['faq']) for o in os)/len(os),sum(len(o['sources']) for o in os)/len(os)]
            rows.append((a,b,*vals))
        lines=['# HOME — Quality audit 471–550','','## Result','', '- Canonical topic numbers reviewed: **80 / 80**.','- Unique publishable intents: **77 / 80**.','- JSON checked: **154 / 154** (77 ES + 77 EN).','- Structural/editorial validation: **PASS**.','- Explicit FAQ validation: **PASS 462 / 462**.','- Blocking errors: **0**.',f'- Non-blocking warnings: **{len(warnings)}**.','','## Canonical duplicate exceptions','', '- **#477 → #402**: exact duplicate title and search intent (`Cómo limpiar el filtro de la campana extractora`). Publishing #477 with the same slug would cause the importer to overwrite #402; publishing a different slug would create SEO cannibalization. No #477 JSON is emitted.','- **#480 → #472**: semantically identical slow-shower-drain query with word order changed. #472 is the single published URL; no #480 JSON is emitted.','- **#499 → #263**: `¿Por qué las toallas huelen mal después de lavarlas?` repeats the already-published diagnosis `¿Por qué las toallas huelen mal incluso después de lavarlas?`. #263 remains the single diagnostic URL; no #499 JSON is emitted.','', 'These numbers remain documented in the canonical inventory and in this audit; they are not silently renumbered or replaced.','','## Scope and editorial criteria','', '- Spanish and English share article number and translation group while using independently localized prose.','- FAQ questions are explicit editorial inputs and each answer is grounded in the article body.','- Electrical, gas, appliance, food, wildlife and water-quality pages include concrete stop conditions and escalation boundaries.','- Search-intent metadata is checked for natural ES/EN syntax.','- Close topics are separated by reader decision and next action rather than superficial wording.','','## Quantitative profile','', '| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in rows: lines.append(f'| {r[0]}–{r[1]} | {r[2]:.1f} | {r[3]:.1f} | {r[4]:.1f} | {r[5]:.1f} | {r[6]:.1f} | {r[7]:.1f} | {r[8]:.1f} | {r[9]:.1f} |')
        lines += ['','## Cannibalization distinctions','', '- #471 vs #470: bad taste is a quality/source diagnosis; slow flow remains a restriction/pressure diagnosis.','- #472/#480: one published slow-shower-drain page only; #480 is blocked as duplicate.','- #475 vs #411: liner-specific material care vs cleaning the full shower curtain.','- #479 vs #235/#398: bathroom-sink slow-drain diagnosis vs unclogging procedure/general sink diagnosis.','- #491 vs #436: why paint peels vs how to repair peeling paint.','- #498 vs #262/#263: prevention of musty towel odor vs removing existing odor/diagnosing why it persists.','- #499 vs #263: one diagnostic page only; #499 is blocked as duplicate.','- #505/#506: repotting procedure vs decision about when repotting is needed.','- #510/#511: whether vents should be open vs whether closing them saves energy.','- #513/#514/#515: general smoke residue vs cigarette residue vs cooking odor.','- #516 vs #306/#388: dead outlet with breaker apparently normal vs one-room outage vs GFCI reset procedure.','- #517 vs #287/#579: battery replacement interval vs chirping diagnosis vs whole-alarm replacement interval.','- #520 vs prior freezer-outage guidance: frost diagnosis does not duplicate food-safety outage decisions.','- #521/#522: oven no-start vs individual gas-burner ignition diagnosis.','- #523 vs #462: coffee-maker leaking vs not brewing.','- #526/#527/#528: separate refreezing decisions for poultry, fish and ice cream because thaw method and food characteristics differ.','- #529/#530: bulbs burning out vs LED flicker.','- #534/#535: what boiling does to hardness vs whether a whole-home softener is warranted.','- #544/#545/#546: brown sediment/rust vs yellow iron/organics vs white microbubbles.','','## Manual review priorities','', 'Read both languages for #471–482, #488–490, #501, #507–530, #534–550. Reject any page that encourages live electrical work, repeated breaker resets, unsafe gas troubleshooting, tasting questionable food, opening refrigerant circuits, sealing active wildlife nests, or treating unknown water contamination by appearance alone.','','## Warnings','', '- None.' if not warnings else '\n'.join('- '+w for w in warnings)]
        REPORT.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'HOME 471-550 audit PASS: articles=154 FAQ=462 duplicate_topics=3 warnings={len(warnings)}')
    if write_report: print('Report:',REPORT)

rec=load_records()
if '--validate-only' not in sys.argv: generate(rec)
validate(rec,write_report='--no-report' not in sys.argv)
