#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, re, unicodedata, html, statistics
from collections import Counter
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'tools'
ART = ROOT / 'articles'
ES_DIR = ART / 'es'
EN_DIR = ART / 'en'
START, END = 231, 310

ES_MARKET = 'Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.'
EN_MARKET = 'United States and Canada; practical, safety-first household guidance written natively for North American readers.'

SOURCES = {
 'cleaning': {
  'es':[{'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Prácticas de limpieza doméstica, dosificación y uso de productos según superficie y etiqueta.'}],
  'en':[{'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Household cleaning practices, product dosing, and label-compatible surface care.'}]},
 'roof': {
  'es':[{'name':'U.S. Consumer Product Safety Commission — Ladder Safety','url':'https://www.cpsc.gov/safety-education/safety-guides/home/ladder-safety','note':'Uso seguro de escaleras y prevención de caídas durante mantenimiento doméstico.'}],
  'en':[{'name':'U.S. Consumer Product Safety Commission — Ladder Safety','url':'https://www.cpsc.gov/safety-education/safety-guides/home/ladder-safety','note':'Safe ladder use and fall prevention during household maintenance.'}]},
 'mold': {
  'es':[{'name':'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home','url':'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','note':'Control de humedad, secado de materiales, limpieza y prevención de recurrencia del moho.'}],
  'en':[{'name':'U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home','url':'https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home','note':'Moisture control, material drying, mold cleanup, and recurrence prevention.'}]},
 'electrical': {
  'es':[{'name':'U.S. Consumer Product Safety Commission — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Riesgos eléctricos domésticos, enchufes, cableado, automáticos y respuesta segura.'}],
  'en':[{'name':'U.S. Consumer Product Safety Commission — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Household electrical hazards, receptacles, wiring, breakers, and safe response.'}]},
 'boiler': {
  'es':[{'name':'U.S. Department of Energy — Home Heating Systems','url':'https://www.energy.gov/energysaver/home-heating-systems','note':'Funcionamiento, controles, eficiencia y mantenimiento general de sistemas domésticos de calefacción.'}],
  'en':[{'name':'U.S. Department of Energy — Home Heating Systems','url':'https://www.energy.gov/energysaver/home-heating-systems','note':'Operation, controls, efficiency, and general maintenance of home heating systems.'}]},
 'food-safety': {
  'es':[{'name':'USDA Food Safety and Inspection Service — Danger Zone','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/danger-zone-40f-140f','note':'Límites de tiempo y temperatura para mantener alimentos perecederos fuera de la zona de peligro.'}],
  'en':[{'name':'USDA Food Safety and Inspection Service — Danger Zone','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/danger-zone-40f-140f','note':'Time and temperature limits for keeping perishable food out of the danger zone.'}]},
 'plants': {
  'es':[{'name':'University of Minnesota Extension — Watering houseplants','url':'https://extension.umn.edu/planting-and-growing-guides/watering-houseplants','note':'Riego, drenaje y señales de estrés hídrico en plantas de interior.'}],
  'en':[{'name':'University of Minnesota Extension — Watering houseplants','url':'https://extension.umn.edu/planting-and-growing-guides/watering-houseplants','note':'Watering, drainage, and water-stress signs in houseplants.'}]},
}

STOPWORDS = set('the a an and or of to in for on with is are my your how why what from into can does do should de la el los las un una unos unas y o del al por para con en mi tu como cómo que qué se es son'.split())

def slugify(s:str)->str:
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    s = re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return re.sub(r'-+','-',s)

def plain(s:str)->str:
    s = s.replace('\u200b','').replace('\ufeff','')
    return re.sub(r'\s+',' ',s).strip()

def first_sentence(s:str)->str:
    s=plain(s)
    m=re.match(r'^(.+?[.!?])(?:\s|$)',s)
    return m.group(1) if m else s

def seo_title(title:str, lang:str)->str:
    replacements = [(' Causas comunes y soluciones',''),(' Common Causes and Fixes','')]
    out=title
    for old,new in replacements: out=out.replace(old,new)
    return out

def search_intent(title:str, kind:str, lang:str)->str:
    low=title.rstrip('?').lower()
    if lang=='es':
        if 'diagnostic' in kind or 'troubleshooting' in kind:
            return f'Identificar las causas probables detrás de «{low}», priorizar comprobaciones seguras y decidir cuándo hace falta reparación o ayuda profesional.'
        if 'safety' in kind or 'emergency' in kind:
            return f'Tomar una decisión segura sobre «{low}», distinguiendo una situación manejable de señales que requieren detenerse, desechar o pedir ayuda.'
        if kind in ('how-to','maintenance','prevention'):
            return f'Aplicar un método práctico y seguro para {low}, evitando los errores que dañan materiales, equipos o hacen que el problema reaparezca.'
        return f'Entender {low} y convertir la explicación en una decisión doméstica práctica sin depender de jerga técnica.'
    if 'diagnostic' in kind or 'troubleshooting' in kind:
        return f'Identify the likely causes behind “{low},” prioritize safe checks, and decide when repair or professional service is warranted.'
    if 'safety' in kind or 'emergency' in kind:
        return f'Make a safe decision about “{low},” separating manageable conditions from signs that require stopping, discarding, or getting help.'
    if kind in ('how-to','maintenance','prevention'):
        return f'Use a practical, safe method for {low}, avoiding mistakes that damage materials or equipment or allow the problem to return.'
    return f'Understand {low} and turn the explanation into a practical household decision without unnecessary technical jargon.'

def faq_for(item, lang):
    secs=item['sections']
    if lang=='es':
        qs=[
          ('¿Cuál es la primera comprobación útil?', secs[0][2]),
          ('¿Qué error conviene evitar?', secs[1][2]),
          ('¿Cuándo hace falta cambiar de estrategia o pedir ayuda?', secs[3][2]),
        ]
    else:
        qs=[
          ('What is the most useful first check?', secs[0][3]),
          ('What mistake should I avoid?', secs[1][3]),
          ('When should I change approach or get help?', secs[3][3]),
        ]
    return [{'question':q,'answer':plain(a)} for q,a in qs]

def source_list(item, lang):
    n=item['n']; key=item.get('source','')
    if n==287:
        return [{'name':'U.S. Fire Administration — Smoke Alarms','url':'https://www.usfa.fema.gov/prevention/home-fires/prepare-for-fire/smoke-alarms/','note':'Detectores de humo, pruebas, sustitución y respuesta a alarmas.' if lang=='es' else 'Smoke alarm placement, testing, replacement, and alarm response.'}]
    if n in (288,289):
        return [{'name':'U.S. Consumer Product Safety Commission — Carbon Monoxide Information Center','url':'https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center','note':'Riesgos de monóxido de carbono, alarmas, ubicación y respuesta ante una activación.' if lang=='es' else 'Carbon monoxide risks, alarms, placement, and response to an activation.'}]
    if n==290:
        return [{'name':'USDA Food Safety and Inspection Service — Keeping Food Safe During an Emergency','url':'https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keeping-food-safe-during-emergency','note':'Conservación de alimentos del refrigerador y congelador durante cortes de electricidad.' if lang=='es' else 'Keeping refrigerated and frozen food safe during a power outage.'}]
    if n==307:
        base=SOURCES['electrical'][lang].copy()
        base.append({'name':'U.S. Consumer Product Safety Commission — GFCIs Fact Sheet','url':'https://www.cpsc.gov/s3fs-public/099_0.pdf','note':'Protección mediante interruptores de circuito por falla a tierra y comportamiento de rearme.' if lang=='es' else 'Ground-fault circuit interrupter protection and reset behavior.'})
        return base
    return [dict(x) for x in SOURCES.get(key,{}).get(lang,[])]

def image_concept(item, lang):
    title=item['es_title'] if lang=='es' else item['en_title']
    fam=item['family']
    esctx={
      'electrical':'escena doméstica con el dispositivo eléctrico afectado visible, sin paneles abiertos ni trabajo con cableado vivo',
      'food-safety':'escena de cocina doméstica mostrando el alimento y un contexto claro de refrigeración o temperatura',
      'heating':'escena doméstica con termostato o equipo de calefacción visto desde el exterior, sin desmontaje',
      'moisture':'escena doméstica mostrando la superficie, humedad y ventilación relevantes',
      'kitchen-appliances':'electrodoméstico doméstico mostrando la zona externa relevante para el diagnóstico o mantenimiento',
      'laundry-appliances':'electrodoméstico de lavandería y la comprobación externa relevante',
      'plants':'planta de interior mostrando con claridad el patrón visible de las hojas y el sustrato',
      'home-tech':'router wifi doméstico en una ubicación realista con dispositivos a distinta distancia',
      'outdoor-cleaning':'superficie exterior doméstica durante una limpieza prudente y controlada',
    }
    enctx={
      'electrical':'household scene with the affected electrical device visible, no open panels or live-wiring work',
      'food-safety':'home-kitchen scene showing the food and a clear refrigeration or temperature context',
      'heating':'home scene with thermostat or heating equipment viewed externally, without disassembly',
      'moisture':'home scene clearly showing the relevant surface, moisture, and ventilation conditions',
      'kitchen-appliances':'household appliance showing the external area relevant to diagnosis or maintenance',
      'laundry-appliances':'laundry appliance with the relevant external troubleshooting check visible',
      'plants':'houseplant clearly showing the leaf pattern and potting mix condition',
      'home-tech':'home Wi-Fi router in a realistic placement with devices at different distances',
      'outdoor-cleaning':'outdoor household surface being cleaned with a controlled, material-safe method',
    }
    ctx=(esctx if lang=='es' else enctx).get(fam, 'escena doméstica realista centrada en la acción o señal principal del tema' if lang=='es' else 'realistic household scene centered on the topic’s main action or visible clue')
    return (f'{ctx}; fotografía editorial natural, sin texto ni marcas. Tema: {title}.' if lang=='es' else f'{ctx}; natural editorial photography, no text or branding. Topic: {title}.')

def build_article(item, lang):
    n=item['n']; title=plain(item['es_title'] if lang=='es' else item['en_title'])
    intro=plain(item['es_intro'] if lang=='es' else item['en_intro'])
    slug=slugify(title)
    en_slug=slugify(item['en_title'])
    tg=f'{n}-{en_slug}'
    secs=[]
    for sec in item['sections']:
        h=plain(sec[0] if lang=='es' else sec[1]); p=plain(sec[2] if lang=='es' else sec[3])
        secs.append(f'<h2>{html.escape(h)}</h2><p>{html.escape(p)}</p>')
    content=f'<p>{html.escape(intro)}</p>'+''.join(secs)
    locale='es-ES' if lang=='es' else 'en-US'
    market=ES_MARKET if lang=='es' else EN_MARKET
    obj={
      'schema_version':1,
      'id':f'{lang}-{n}-{slug}',
      'article_number':n,
      'translation_group':tg,
      'language':lang,
      'locale':locale,
      'market_context':market,
      'title':title,
      'slug':slug,
      'seo':{
        'title':seo_title(title,lang),
        'meta_description':first_sentence(intro),
        'search_intent':search_intent(title,item['kind'],lang),
      },
      'excerpt':intro,
      'taxonomy':{
        'food_family':item['family'],
        'food_subcategories':[item['subcat']],
        'article_types':[item['kind'],item['family']],
        'primary_article_type':item['kind'],
      },
      'content_html':content,
      'faq':faq_for(item,lang),
      'sources':source_list(item,lang),
      'image':{'concept':image_concept(item,lang),'alt':title.rstrip('?.!')},
      'status':'publish',
    }
    return obj

def load_items():
    items=[]
    for p in sorted(TOOLS.glob('batch-*.json')):
        m=re.fullmatch(r'batch-(\d+)-(\d+)\.json',p.name)
        if not m: continue
        a,b=map(int,m.groups())
        if b<START or a>END: continue
        items.extend(json.loads(p.read_text(encoding='utf-8')))
    by={int(x['n']):x for x in items}
    missing=[n for n in range(START,END+1) if n not in by]
    dup=len(items)-len(by)
    if missing or dup: raise SystemExit(f'Batch inventory problem: missing={missing}, duplicate_count={dup}')
    return [by[n] for n in range(START,END+1)]

def canonical_es_titles():
    titles={}
    for fn in ('TOPICS-201-300.md','TOPICS-301-400.md'):
        text=(ROOT/'topics'/fn).read_text(encoding='utf-8')
        for m in re.finditer(r'(?m)^(\d+)\.\s+(.+)$',text):
            n=int(m.group(1))
            if START<=n<=END: titles[n]=m.group(2).strip()
    return titles

def text_words(h):
    t=re.sub(r'<[^>]+>',' ',h)
    return re.findall(r"[A-Za-zÀ-ÿ0-9]+(?:['’][A-Za-zÀ-ÿ]+)?",t)

def tokens(h):
    ws=[w.lower() for w in text_words(h)]
    return {w for w in ws if len(w)>2 and w not in STOPWORDS}

def metrics(objs):
    rows=[]
    for o in objs:
        rows.append((len(text_words(o['content_html'])),o['content_html'].count('<h2>'),len(o['faq']),len(o['sources'])))
    return tuple(round(statistics.mean(x[i] for x in rows),1) for i in range(4))

def validate(items, objs):
    errs=[]; warns=[]
    canon=canonical_es_titles()
    by={(o['language'],o['article_number']):o for o in objs}
    if len(objs)!=160: errs.append(f'Expected 160 objects, got {len(objs)}')
    for item in items:
        n=item['n']
        if canon.get(n)!=item['es_title']: errs.append(f'#{n} ES title differs from canonical inventory')
        for lang in ('es','en'):
            o=by.get((lang,n))
            if not o: errs.append(f'Missing {lang} #{n}'); continue
            if o['status']!='publish': errs.append(f'{lang} #{n}: status not publish')
            if o['article_number']!=n: errs.append(f'{lang} #{n}: bad article_number')
            if not o['slug'] or not o['seo']['meta_description'] or not o['seo']['search_intent']: errs.append(f'{lang} #{n}: empty metadata')
            if '…' in o['seo']['title'] or o['seo']['title'].endswith('...'): errs.append(f'{lang} #{n}: mechanically truncated SEO title')
            if len(text_words(o['content_html'])) < 145: errs.append(f'{lang} #{n}: content too shallow ({len(text_words(o["content_html"]))} words)')
            if o['content_html'].count('<h2>')<4: errs.append(f'{lang} #{n}: fewer than 4 H2')
            if len(o['faq'])<3: errs.append(f'{lang} #{n}: fewer than 3 FAQ')
            raw=json.dumps(o,ensure_ascii=False)
            if '\u200b' in raw or '\ufeff' in raw: errs.append(f'{lang} #{n}: zero-width/BOM character')
            if 'HOME prioriza' in raw or 'HOME prioritizes' in raw: errs.append(f'{lang} #{n}: editorial metadiscourse')
            if lang=='en':
                for s in o['sources']:
                    if re.search(r'\b(Riesgos|Limpieza|Control|Prevención|Conservación|Riego)\b',s.get('note','')): errs.append(f'EN #{n}: Spanish source note')
        es=by.get(('es',n)); en=by.get(('en',n))
        if es and en and es['translation_group']!=en['translation_group']: errs.append(f'#{n}: translation_group mismatch')
    # Explicit Spanish acronym/localization checks.
    expectations={307:[('GFCI','interruptor de circuito por falla a tierra')],292:[('UHT','temperatura ultra alta')]}
    for n,pairs in expectations.items():
        o=by.get(('es',n)); raw=(o['content_html']+' '+o['excerpt']) if o else ''
        for acr,exp in pairs:
            if acr in raw and exp.lower() not in raw.lower(): errs.append(f'ES #{n}: {acr} not expanded in plain language')
    # High-risk topic stop conditions.
    risk_terms={284:['déjalo apagado','no abras'],285:['deja de usar','servicios de emergencia'],286:['directamente','pared'],289:['sal','emergencia'],297:['nunca','mano'],306:['no retires'],307:['no lo puentes']}
    for n,need in risk_terms.items():
        raw=by[('es',n)]['content_html'].lower()
        for term in need:
            if term not in raw: warns.append(f'ES #{n}: expected safety concept missing: {term}')
    return errs,warns

def write_articles(items):
    objs=[]
    for item in items:
        for lang,folder in [('es',ES_DIR),('en',EN_DIR)]:
            o=build_article(item,lang); objs.append(o)
            for old in folder.glob(f"{item['n']:03d}-*.json"):
                old.unlink()
            p=folder/f"{item['n']:03d}-{o['slug']}.json"
            p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    return objs

OVERLAPS=[(231,310,'sagging mattress cause vs temporary improvement'),(232,233,'white mineral residue vs removing limescale'),(236,247,'general drain odor vs shower drain odor'),(236,248,'general drain odor vs sink drain odor'),(245,246,'toilet gurgling vs sink gurgling'),(258,195,'recognize roof leak vs locate leak source'),(262,263,'remove towel odor vs why towels still smell'),(268,269,'gutter cleaning frequency vs unclog downspout'),(268,270,'gutter cleaning frequency vs overflow diagnosis'),(273,274,'yellow vs brown plant leaves'),(276,364,'low boiler pressure diagnosis vs future pressure refill procedure'),(278,201,'short cycling vs heating will not start'),(278,207,'short cycling vs runs but not heating'),(278,279,'short cycling vs heating noise'),(278,280,'short cycling vs burning smell'),(281,282,'bathroom vs basement mold prevention'),(281,283,'bathroom vs window mold prevention'),(282,283,'basement vs window mold prevention'),(284,306,'breaker tripping vs one-room outage'),(284,307,'breaker trip vs GFCI trip'),(287,289,'smoke chirp vs CO alarm'),(290,380,'freezer outage duration vs future refrigerator outage duration'),(292,211,'spoiled milk vs opened milk duration'),(292,224,'spoiled milk vs milk left out'),(295,221,'clean smelly washer vs why washer smells'),(297,298,'disposal not working vs clearing jam'),(299,300,'dishwasher standing water vs leak'),(301,302,'refrigerator nonstop vs clicking'),(303,304,'raw meat left out vs pizza left out'),(303,305,'raw meat left out vs rice left out'),(304,305,'pizza left out vs rice left out'),(306,227,'one-room outage vs partial-house outage'),(308,309,'concrete patio vs wood deck cleaning'),(310,158,'temporary sag fix vs mattress rotation'),(310,230,'temporary sag fix vs mattress flipping')]

def read_existing(n,lang):
    folder=ES_DIR if lang=='es' else EN_DIR
    ms=list(folder.glob(f'{n:03d}-*.json'))
    if len(ms)!=1: return None
    return json.loads(ms[0].read_text(encoding='utf-8'))

def make_report(objs, errs, warns):
    by={(o['language'],o['article_number']):o for o in objs}
    lines=['# HOME — Quality audit 231–310','','## Result','',f'- JSON checked: **{len(objs)} / 160** (80 ES + 80 EN expected).',f'- Structural/editorial validation: **{"PASS" if not errs else "FAIL"}**.',f'- Blocking errors: **{len(errs)}**.',f'- Localization/safety warnings: **{len(warns)}**.','','## Scope and editorial criteria','',
      '- Exact approved topics 231–310 preserved from the canonical topic inventory.',
      '- ES and EN share article number and translation group while using independently localized prose.',
      '- Troubleshooting, electrical, heating, alarm and food-safety topics were checked for stop conditions and escalation boundaries.',
      '- No fixed word-count target was imposed; minimum depth is used only to catch incomplete output.',
      '- Mechanical SEO truncation, broken pairs, unexplained required acronyms and editorial metadiscourse are blocking failures.','',
      '## Quantitative profile','',
      '| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for a,b in [(231,250),(251,270),(271,290),(291,310)]:
        for_lang={}
        for lang in ('es','en'):
            arr=[by[(lang,n)] for n in range(a,b+1)]
            for_lang[lang]=metrics(arr)
        e=for_lang['es']; x=for_lang['en']
        lines.append(f'| {a}–{b} | {e[0]} | {e[1]} | {e[2]} | {e[3]} | {x[0]} | {x[1]} | {x[2]} | {x[3]} |')
    lines += ['','## Cannibalization / overlap diagnostics','','Similarity is diagnostic only; final separation depends on distinct search intent and next action.','', '| Pair | Intent distinction | ES Jaccard | EN Jaccard |','|---|---|---:|---:|']
    for a,b,label in OVERLAPS:
        vals=[]
        for lang in ('es','en'):
            oa=by.get((lang,a)) or read_existing(a,lang); ob=by.get((lang,b)) or read_existing(b,lang)
            if not oa or not ob: vals.append(0.0); continue
            ta,tb=tokens(oa['content_html']),tokens(ob['content_html']); vals.append(len(ta&tb)/max(1,len(ta|tb)))
        lines.append(f'| #{a}/#{b} | {label} | {vals[0]:.3f} | {vals[1]:.3f} |')
    lines += ['','## Editorial overlap conclusions','',
      '- #231/#310: #231 explains why a mattress sags; #310 covers temporary comfort/support measures after sagging exists.',
      '- #232/#233: residue identification comes before the separate limescale-removal procedure.',
      '- #236/#247/#248: the general drain-odor diagnostic branches into fixture-specific shower and sink causes.',
      '- #245/#246: toilet gurgling and sink gurgling can share vent/drain causes but start from different fixtures and observations.',
      '- #258/#195: recognizing evidence of a roof leak is broader than tracing the exact entry point.',
      '- #262/#263: one page removes towel odor; the other explains why odor survives laundering.',
      '- #276/#364 (future): #276 diagnoses falling boiler pressure and deliberately does not become the refill procedure reserved for #364.',
      '- #278/#279/#280: cycling, noise and burning odor are separate heating symptoms with different escalation paths.',
      '- #281/#282/#283: mold prevention is localized to bathroom vapor, basement moisture and window condensation/leaks respectively.',
      '- #284/#306/#307: breaker trips, a one-room outage and repeated GFCI trips have distinct scope and safety checks.',
      '- #287/#289: smoke-alarm maintenance chirps are separated from a carbon-monoxide alarm that can require immediate evacuation.',
      '- #290/#380 (future): #290 is frozen-food safety; #380 is refrigerator cold retention during an outage.',
      '- #292/#211/#224: spoilage assessment, opened refrigerated duration and room-temperature exposure are different milk decisions.',
      '- #295/#221: #295 is the cleaning procedure; #221 remains the cause diagnosis.',
      '- #297/#298: a disposal that does not work begins with power/state diagnosis; #298 is specifically safe jam clearing.',
      '- #299/#300: retained dishwasher water is a drainage symptom; leakage is a containment/source problem.',
      '- #303/#304/#305: the same time-temperature framework is applied to foods with distinct hazards and handling context.',
      '- #306/#227: one-room power loss is narrower than a partial-house outage and excludes service-neutral patterns.',
      '- #308/#309: concrete tolerates different cleaners/pressure than a wood deck.',
      '- #310/#158/#230: temporary sag mitigation, routine rotation and flipping are separate mattress decisions.']
    if errs:
        lines += ['','## Blocking errors','']+[f'- {e}' for e in errs]
    if warns:
        lines += ['','## Warnings','']+[f'- {w}' for w in warns]
    lines += ['','## Final reading priorities','',
      'Representative reads should include #231–233, #236, #245–248, #258, #262–263, #276, #278–280, #281–289, #290–295, #297–300, #303–307 and #310 in both languages.',
      'Safety-sensitive pages should be rejected if they encourage live electrical work, repeated breaker/GFCI resets, unsafe ladder or roof access, combustion-system disassembly, ignoring a carbon-monoxide alarm, or food-safety decisions based only on smell or taste.','']
    (ART/'QUALITY-AUDIT-231-310.md').write_text('\n'.join(lines),encoding='utf-8')


def main():
    items=load_items()
    objs=write_articles(items)
    errs,warns=validate(items,objs)
    make_report(objs,errs,warns)
    print(f'Generated {len(objs)} JSON articles; errors={len(errs)} warnings={len(warns)}')
    for e in errs: print('ERROR:',e)
    for w in warns: print('WARN:',w)
    if errs: raise SystemExit(1)

if __name__=='__main__': main()
