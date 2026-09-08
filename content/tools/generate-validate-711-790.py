#!/usr/bin/env python3
import argparse, html, json, re, statistics, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / 'content' / 'tools'
ART = ROOT / 'content' / 'articles'
ES_DIR, EN_DIR = ART / 'es', ART / 'en'
REPORT = ART / 'QUALITY-AUDIT-711-790.md'
EXCLUSIONS = {
  726:(277,'Exact duplicate: finding the source of a bad smell in the home is already #277.'),
  733:(664,'Same intent: an ice maker not working/not making ice is already fully covered by #664.'),
  735:(453,'Same intent: storing fresh herbs so they last longer is already #453.'),
  736:(568,'Same intent: organizing the refrigerator for food safety is already #568.'),
  739:(517,'Same intent: smoke-alarm battery replacement frequency is already #517.'),
  749:(481,'Same intent: cloudy tap water diagnosis is already #481.'),
  771:(552,'Same intent: organizing clothing in a small closet is already #552.'),
  772:(642,'Same intent: storing clothes without musty odor is already #642.'),
  788:(718,'Same intent inside this block: what to do about mealybugs is fully resolved by #718.'),
}
EXPECTED = set(range(711,791)) - set(EXCLUSIONS)
WATCHED = [(711,260),(712,713),(716,439),(717,718),(719,790),(722,137),(724,278),(728,130),(728,445),(737,568),(738,656),(738,674),(738,675),(742,679),(746,680),(747,682),(748,233),(757,758),(758,759),(759,760),(761,762),(761,763),(762,763),(767,420),(774,787),(778,703),(778,779),(779,703),(781,782),(782,783),(783,784),(785,714),(789,718)]

SOURCES = {
 'laundry': {'name':'American Cleaning Institute — Laundry Basics','url':'https://www.cleaninginstitute.org/cleaning-tips/clothes/laundry-basics','es':'Clasificación, dosificación, cuidado de tejidos y buenas prácticas de lavado según etiquetas.','en':'Sorting, dosing, fabric-care, and laundering practices guided by care labels.'},
 'energy': {'name':'U.S. Department of Energy — Energy Saver','url':'https://www.energy.gov/energysaver','es':'Información práctica sobre climatización, termostatos, mantenimiento y eficiencia del hogar.','en':'Practical information on home heating, cooling, thermostats, maintenance, and efficiency.'},
 'mold': {'name':'U.S. Environmental Protection Agency — Moisture Control','url':'https://www.epa.gov/mold/what-are-main-ways-control-moisture-your-home','es':'Control de humedad: corregir fugas, filtraciones, condensación y drenaje que favorecen daños y moho.','en':'Moisture control through correcting leaks, seepage, condensation, and drainage conditions.'},
 'cleaning': {'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','es':'Buenas prácticas generales de limpieza y uso de productos según etiqueta y superficie.','en':'General cleaning practices and product use according to labels and surfaces.'},
 'plumbing': {'name':'U.S. Environmental Protection Agency WaterSense — Home Maintenance','url':'https://www.epa.gov/watersense/home-maintenance','es':'Mantenimiento de grifos, aireadores, fugas, depósitos minerales y uso eficiente del agua.','en':'Maintenance guidance for faucets, aerators, leaks, mineral buildup, and water efficiency.'},
 'water-softener': {'name':'U.S. Environmental Protection Agency WaterSense — Cation Exchange Water Softeners','url':'https://www.epa.gov/watersense/cation-exchange-water-softeners','es':'Funcionamiento, regeneración, sal, agua y mantenimiento de descalcificadores de intercambio catiónico.','en':'Operation, regeneration, salt, water use, and maintenance of cation-exchange water softeners.'},
 'pests': {'name':'U.S. Environmental Protection Agency — Integrated Pest Management Principles','url':'https://www.epa.gov/safepestcontrol/integrated-pest-management-ipm-principles','es':'Manejo integrado basado en identificación, prevención, seguimiento y controles de menor riesgo.','en':'Integrated pest management based on identification, prevention, monitoring, and lower-risk controls.'},
 'bedbugs': {'name':'U.S. Environmental Protection Agency — How to Find Bed Bugs','url':'https://www.epa.gov/bedbugs/how-find-bed-bugs','es':'Señales físicas, escondites e importancia de la detección e identificación tempranas de chinches.','en':'Physical signs, hiding places, and the importance of early bed-bug detection and identification.'},
 'microwave': {'name':'USDA Food Safety and Inspection Service — Cooking with Microwave Ovens','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/cooking-microwave-ovens','es':'Materiales aptos para microondas, recipientes que no deben calentarse y uso seguro de papel y envoltorios.','en':'Microwave-safe materials, containers that should not be heated, and safe paper/wrap use.'},
 'refrigeration': {'name':'USDA Food Safety and Inspection Service — Refrigeration & Food Safety','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/refrigeration','es':'Temperatura del refrigerador y contención de carne, aves y pescado crudos para evitar contaminación cruzada.','en':'Refrigerator temperature and containment of raw meat, poultry, and seafood to prevent cross-contamination.'},
 'electrical': {'name':'U.S. Consumer Product Safety Commission — Space Heater Safety','url':'https://www.cpsc.gov/Newsroom/News-Releases/2026/Keep-Warm-and-Safe-This-Winter-Tips-for-Using-Generators-Furnaces-and-Space-Heaters','es':'Calefactores portátiles directamente a pared, alejados de combustibles y sin regletas o alargadores.','en':'Portable space heaters connected directly to wall outlets, clear of combustibles, and never to power strips or extension cords.'},
 'gas': {'name':'U.S. Consumer Product Safety Commission — Winter Weather Safety Tips','url':'https://www.cpsc.gov/Newsroom/News-Releases/2026/CPSC-Issues-Winter-Weather-Safety-Tips-to-Prevent-Fires-and-Carbon-Monoxide-Poisoning','es':'Ante olor o sonido de fuga de gas, salir sin accionar dispositivos eléctricos y contactar desde fuera.','en':'If gas is smelled or heard leaking, leave without operating electronics and contact gas authorities from outside.'},
 'chemical-storage': {'name':'U.S. Environmental Protection Agency — Poison Prevention','url':'https://www.epa.gov/pesticides/national-poison-prevention-week-epa-urges-public-keep-all-pesticides-original-containers','es':'Mantener productos domésticos en envases originales, con etiqueta y fuera del alcance de niños.','en':'Keep household chemical products in original labeled containers and out of children's reach.'},
 'records': {'name':'Internal Revenue Service — How Long Should I Keep Records?','url':'https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records','es':'Plazos fiscales de EE. UU., incluidos tres años como regla general y periodos más largos en determinados casos.','en':'U.S. tax record periods, including a general three-year rule and longer periods in specified cases.'},
 'maintenance': {'name':'U.S. Department of Energy — Energy Saver','url':'https://www.energy.gov/energysaver','es':'Mantenimiento doméstico y preparación estacional de sistemas de climatización y envolvente.','en':'Home maintenance and seasonal preparation for heating, cooling, and the building envelope.'},
}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')

def strip_tags(s): return re.sub(r'<[^>]+>',' ',html.unescape(s))
def words(s): return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:['’-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)?", strip_tags(s))

def first_sentence(text):
    protected = text.replace('EE. UU.','EE§UU§').replace('U.S.','U§S§').replace('p. ej.','p§ej§')
    m = re.search(r'[.!?](?:[”\"])?(?=\s|$)', protected)
    out = protected[:m.end()] if m else protected
    return out.replace('EE§UU§','EE. UU.').replace('U§S§','U.S.').replace('p§ej§','p. ej.').strip()

def canonical_topics():
    out={}
    for line in (ROOT/'content/topics/TOPICS-701-800.md').read_text(encoding='utf-8').splitlines():
        m=re.match(r'^(\d+)\.\s+(.+)$',line.strip())
        if m: out[int(m.group(1))]=m.group(2).strip()
    return out

def normalize(s,lang,n):
    if n==719:
        s=s.replace('LED','indicador luminoso') if lang=='es' else s.replace('LED','status light')
    if n==753:
        s=s.replace('PVC y aluminio','policloruro de vinilo (PVC) y aluminio') if lang=='es' else s.replace('PVC and aluminum','polyvinyl chloride (PVC) and aluminum')
    if n==762:
        s=s.replace('enchufe GFCI o diferencial','interruptor de circuito por falla a tierra (GFCI), común en instalaciones de EE. UU. y Canadá, o diferencial') if lang=='es' else s.replace('relevant GFCI indicates','relevant ground-fault circuit interrupter (GFCI) indicates')
    return s

def load_entries():
    entries=[]
    for start in range(711,791,10):
        p=TOOLS/f'batch-{start}-{start+9}.json'
        entries.extend(json.loads(p.read_text(encoding='utf-8')))
    nums=[e['n'] for e in entries]
    if set(nums)!=EXPECTED or len(nums)!=len(EXPECTED) or len(set(nums))!=len(nums):
        raise SystemExit(f'Source inventory mismatch count={len(nums)} missing={sorted(EXPECTED-set(nums))} extra={sorted(set(nums)-EXPECTED)}')
    canon=canonical_topics()
    for e in entries:
        if canon.get(e['n'])!=e['es_title']:
            raise SystemExit(f"Canonical title mismatch #{e['n']}: {e['es_title']} != {canon.get(e['n'])}")
        if len(e['sections'])!=4 or len(e['faq_es'])!=3 or len(e['faq_en'])!=3 or len(e['faq_sections'])!=3:
            raise SystemExit(f"Authored structure mismatch #{e['n']}")
        if any(i not in range(4) for i in e['faq_sections']): raise SystemExit(f"FAQ mapping out of range #{e['n']}")
        if e.get('source') and e['source'] not in SOURCES: raise SystemExit(f"Unmapped source key #{e['n']}: {e['source']}")
    return entries

def clean_title(title): return title.strip().strip('¿?').strip()

def intent(e,lang):
    title=clean_title(e['es_title'] if lang=='es' else e['en_title'])
    kind=e['kind']
    if lang=='es':
        if 'diagnostics' in kind: return f'Identificar las causas más probables de «{title}», distinguir señales útiles y decidir qué comprobar primero y cuándo pedir ayuda.'
        if 'decision' in kind or 'safety-guide' in kind: return f'Tomar una decisión práctica y segura sobre «{title}», reconocer límites y saber cuándo cambiar de estrategia o pedir ayuda.'
        return f'Resolver «{title}» con pasos prácticos, comprobaciones concretas y límites claros para evitar errores comunes.'
    if 'diagnostics' in kind: return f'Identify the most likely causes behind “{title},” use distinguishing clues, and decide what to check first and when to get help.'
    if 'decision' in kind or 'safety-guide' in kind: return f'Make a practical, safe decision about “{title},” recognize important limits, and know when to change approach or get help.'
    return f'Handle “{title}” with practical steps, specific checks, and clear limits that prevent common mistakes.'

def source_for(e,lang):
    key=e.get('source','')
    if not key:return []
    s=SOURCES[key]
    return [{'name':s['name'],'url':s['url'],'note':s[lang]}]

def build(e,lang):
    es=lang=='es'; n=e['n']
    title=normalize(e['es_title'] if es else e['en_title'],lang,n)
    slug=slugify(title); en_slug=slugify(e['en_title']); tg=f'{n}-{en_slug}'
    intro=normalize(e['intro_es'] if es else e['intro_en'],lang,n)
    sections=[]
    for sec in e['sections']:
        h=normalize(sec[0 if es else 1],lang,n); p=normalize(sec[2 if es else 3],lang,n)
        sections.append((h,p))
    qlist=e['faq_es'] if es else e['faq_en']
    faq=[]
    for q,idx in zip(qlist,e['faq_sections']): faq.append({'question':normalize(q,lang,n),'answer':sections[idx][1]})
    body='<p>'+html.escape(intro,quote=False)+'</p>'+''.join('<h2>'+html.escape(h,quote=False)+'</h2><p>'+html.escape(p,quote=False)+'</p>' for h,p in sections)
    ctitle=clean_title(title)
    image_concept=(f'Fotografía editorial doméstica realista que muestre {sections[0][0].lower()} en el contexto de {ctitle.lower()}, con el componente o señal principal claramente visible, sin texto ni marcas.' if es else f'Realistic household editorial photograph showing {sections[0][0].lower()} in the context of {ctitle.lower()}, with the key component or clue clearly visible, no text or branding.')
    return {
      'schema_version':1,'id':f'{lang}-{n}-{slug}','article_number':n,'translation_group':tg,'language':lang,'locale':'es-ES' if es else 'en-US',
      'market_context':'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if es else 'U.S./Canadian English; practical household guidance with locally familiar terminology and clear safety boundaries.',
      'title':title,'slug':slug,
      'seo':{'title':title,'meta_description':first_sentence(intro),'search_intent':intent(e,lang)},'excerpt':intro,
      'taxonomy':{'food_family':e['family'],'food_subcategories':[slug],'article_types':[e['kind'],e['family']],'primary_article_type':e['kind']},
      'content_html':body,'faq':faq,'sources':source_for(e,lang),'image':{'concept':image_concept,'alt':ctitle},'status':'publish'
    }

def existing_index():
    idx={}; collisions={'id':set(),'slug_es':set(),'slug_en':set(),'tg':set()}
    for lang,folder in [('es',ES_DIR),('en',EN_DIR)]:
        for p in folder.glob('*.json'):
            try:d=json.loads(p.read_text(encoding='utf-8'))
            except Exception:continue
            n=d.get('article_number')
            idx.setdefault(n,{})[lang]=(p,d)
            if n not in EXPECTED:
                collisions['id'].add(d.get('id')); collisions['tg'].add(d.get('translation_group')); collisions['slug_'+lang].add(d.get('slug'))
    return idx,collisions

def generate(entries):
    idx,col=existing_index()
    for n in EXCLUSIONS:
        if n in idx: raise SystemExit(f'Excluded article #{n} already exists and must be reviewed before generation')
    for e in entries:
        for lang,folder in [('es',ES_DIR),('en',EN_DIR)]:
            a=build(e,lang)
            if a['id'] in col['id'] or a['translation_group'] in col['tg'] or a['slug'] in col['slug_'+lang]: raise SystemExit(f"Collision for #{e['n']} {lang}")
            for old in folder.glob(f"{e['n']}-*.json"): old.unlink()
            (folder/f"{e['n']}-{a['slug']}.json").write_text(json.dumps(a,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

def current_articles():
    out=[]
    for lang,folder in [('es',ES_DIR),('en',EN_DIR)]:
        for p in folder.glob('*.json'):
            d=json.loads(p.read_text(encoding='utf-8'))
            if d.get('article_number') in EXPECTED: out.append((lang,p,d))
    return out

def jaccard(a,b):
    sa={x.lower() for x in words(a) if len(x)>3}; sb={x.lower() for x in words(b) if len(x)>3}
    return len(sa&sb)/len(sa|sb) if sa|sb else 0

def validate(entries):
    errors=[]; warns=[]; arts=current_articles(); seen={}; bynum={}
    if len(arts)!=len(EXPECTED)*2: errors.append(f'Expected {len(EXPECTED)*2} generated JSON, found {len(arts)}')
    canon=canonical_topics()
    for lang,p,d in arts:
        n=d.get('article_number'); bynum.setdefault(n,{})[lang]=d
        if d.get('title')!= (canon[n] if lang=='es' else next(e['en_title'] for e in entries if e['n']==n)): errors.append(f'#{n} {lang}: title mismatch')
        if d.get('language')!=lang or d.get('locale')!=('es-ES' if lang=='es' else 'en-US'): errors.append(f'#{n} {lang}: language/locale')
        if d.get('status')!='publish': errors.append(f'#{n} {lang}: status')
        if not d.get('translation_group','').startswith(str(n)+'-'): errors.append(f'#{n} {lang}: translation_group')
        k=(lang,d.get('slug')); seen[k]=seen.get(k,0)+1
        if len(words(d.get('content_html','')))<160: errors.append(f'#{n} {lang}: depth {len(words(d.get("content_html","")))}')
        if d.get('content_html','').count('<h2>')!=4: errors.append(f'#{n} {lang}: H2 count')
        if len(d.get('faq',[]))!=3: errors.append(f'#{n} {lang}: FAQ count')
        meta=d.get('seo',{}).get('meta_description','')
        if meta!=first_sentence(d.get('excerpt','')) or len(meta)<55 or meta[-1] not in '.!?': errors.append(f'#{n} {lang}: incomplete/weak meta')
        if '«¿' in d.get('seo',{}).get('search_intent','') or '«¿' in d.get('image',{}).get('concept',''): errors.append(f'#{n} es: unmatched question punctuation')
        if not d.get('image',{}).get('concept') or 'placeholder' in d.get('image',{}).get('concept','').lower(): errors.append(f'#{n} {lang}: image concept')
        if any(not f.get('question') or not f.get('answer') for f in d.get('faq',[])): errors.append(f'#{n} {lang}: empty FAQ')
        e=next(x for x in entries if x['n']==n); secs=[normalize(s[2 if lang=='es' else 3],lang,n) for s in e['sections']]
        for i,(f,si) in enumerate(zip(d['faq'],e['faq_sections'])):
            if f['answer']!=secs[si]: errors.append(f'#{n} {lang}: FAQ {i+1} not aligned to mapped section')
        full=' '.join([d.get('excerpt',''),d.get('content_html',''),json.dumps(d.get('faq',[]),ensure_ascii=False)])
        if lang=='es' and re.search(r'\b(HVAC|pellets|frass|topper)\b',full,re.I): errors.append(f'#{n} es: residual anglicism/acronym')
        if lang=='en' and 'GFCI' in full and 'ground-fault circuit interrupter (GFCI)' not in full: errors.append(f'#{n} en: GFCI not expanded')
        if lang=='es' and 'GFCI' in full and 'interruptor de circuito por falla a tierra (GFCI)' not in full: errors.append(f'#{n} es: GFCI not expanded')
        lower=full.lower()
        dangerous=['puentea el sensor','puentea el interruptor','mide tensión con','test live voltage with','short the contacts','force the gas valve open']
        if any(x in lower for x in dangerous): errors.append(f'#{n} {lang}: unsafe action pattern')
        if 'bypass' in lower and 'do not bypass' not in lower: errors.append(f'#{n} en: unsafe bypass wording')
        if e.get('source') and not d.get('sources'): errors.append(f'#{n} {lang}: mapped source missing')
    for k,c in seen.items():
        if c>1: errors.append(f'Duplicate slug in current block: {k}')
    for n in EXPECTED:
        if set(bynum.get(n,{}))!={'es','en'}: errors.append(f'#{n}: bilingual pair incomplete')
        elif bynum[n]['es']['translation_group']!=bynum[n]['en']['translation_group']: errors.append(f'#{n}: pair translation_group mismatch')
    for n in EXCLUSIONS:
        for folder in [ES_DIR,EN_DIR]:
            if list(folder.glob(f'{n}-*.json')): errors.append(f'Excluded #{n} has a published JSON')
    # cold regression phrases found in prior blocks
    for _,_,d in arts:
        raw=json.dumps(d,ensure_ascii=False)
        for bad in ['«¿','known as known as','para cómo','for how to','Realistic household editorial photograph about']:
            if bad in raw: errors.append(f"#{d['article_number']} {d['language']}: regression phrase {bad}")
    return errors,warns,arts,bynum

def report(entries,arts,bynum,errors,warns):
    es_counts=[len(words(d['content_html'])) for l,p,d in arts if l=='es']; en_counts=[len(words(d['content_html'])) for l,p,d in arts if l=='en']
    prior,_=existing_index(); sims=[]
    for a,b in WATCHED:
        vals=[]
        for lang in ['es','en']:
            da=bynum.get(a,{}).get(lang) or prior.get(a,{}).get(lang,(None,None))[1]
            db=bynum.get(b,{}).get(lang) or prior.get(b,{}).get(lang,(None,None))[1]
            if da and db: vals.append(jaccard(da.get('content_html',''),db.get('content_html','')))
        if vals:sims.append((a,b,max(vals)))
    lines=['# Quality audit — HOME articles 711–790','', '## Result','',
      '- Canonical topic intents reviewed: **80/80**.',f'- Editorial source entries validated: **{len(EXPECTED)}/{len(EXPECTED)}**; **{len(EXCLUSIONS)}** canonical exclusions.',
      f'- Published unique intents: **{len(EXPECTED)}**; bilingual article JSON files: **{len(arts)}/{len(EXPECTED)*2} PASS**.' if not errors else f'- Generated JSON files: **{len(arts)}**.',
      f'- FAQ answer-to-section mappings: **{len(EXPECTED)*6}/{len(EXPECTED)*6} PASS**.' if not errors else '- FAQ mappings: validation has blocking errors.',
      f'- Blocking errors: **{len(errors)}**. Warnings: **{len(warns)}**.','', '## Canonical exclusions','']
    for n,(target,why) in EXCLUSIONS.items(): lines.append(f'- **#{n} → #{target}:** {why}')
    lines += ['', '## Depth metrics','',f'- Spanish body words: min **{min(es_counts)}**, median **{statistics.median(es_counts):.0f}**, max **{max(es_counts)}**.',f'- English body words: min **{min(en_counts)}**, median **{statistics.median(en_counts):.0f}**, max **{max(en_counts)}**.','- The 160-word floor is only an incomplete-output regression guard, not an editorial target.','', '## Similarity diagnostics','']
    for a,b,v in sims: lines.append(f'- #{a} vs #{b}: maximum ES/EN token Jaccard **{v:.3f}**.')
    lines += ['', '## Editorial and safety safeguards','',
      '- Spanish and English are independently authored in the temporary editorial source rows; they share intent and structure but are not literal translations.',
      '- Every article has four useful H2 sections and three reader-style FAQs whose answers are validated against explicitly mapped source sections.',
      '- Meta descriptions must be complete first editorial sentences; character truncation is rejected.',
      '- Gas, electrical, water, garage-door, microwave and structural content keeps clear stop points and avoids live testing, bypasses, unsafe spring/cable work or opening fuel-burning equipment.',
      '- Pest and plant-pest pages prioritize identification, isolation, exclusion, sanitation, physical control and labeled lower-risk options before escalation.',
      '- Exact slug, ID and translation-group collisions against the existing library are rejected.',
      '- Temporary batch files, generator and workflow must be removed before merge to `main`.','']
    if errors:
        lines += ['## Blocking errors','']+[f'- {x}' for x in errors]+['']
    REPORT.write_text('\n'.join(lines),encoding='utf-8')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--validate-only',action='store_true'); args=ap.parse_args()
    entries=load_entries()
    if not args.validate_only: generate(entries)
    errors,warns,arts,bynum=validate(entries); report(entries,arts,bynum,errors,warns)
    print(f'HOME 711-790: entries={len(entries)} articles={len(arts)} faq={sum(len(d.get("faq",[])) for _,_,d in arts)} errors={len(errors)} warnings={len(warns)}')
    if errors:
        for x in errors: print('ERROR:',x)
        raise SystemExit(1)

if __name__=='__main__': main()
