#!/usr/bin/env python3
from pathlib import Path
import json, re, unicodedata

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'articles'
BATCHES = sorted((ROOT / 'tools').glob('batch-391-470-*.json'))

SOURCES = {
  'cleaning': {
    'en': {'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Household cleaning methods, product use, dosing, and material compatibility.'},
    'es': {'name':'American Cleaning Institute — Cleaning Tips','url':'https://www.cleaninginstitute.org/cleaning-tips','note':'Métodos de limpieza doméstica, uso y dosificación de productos y compatibilidad con materiales.'}},
  'electrical': {
    'en': {'name':'U.S. Consumer Product Safety Commission — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Household electrical hazards and safe response to overheating, outlets, switches, and breakers.'},
    'es': {'name':'Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC) — Electrical Safety','url':'https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety','note':'Riesgos eléctricos domésticos y respuesta segura ante sobrecalentamiento, enchufes, interruptores y automáticos.'}},
  'food': {
    'en': {'name':'U.S. Department of Agriculture — Food Safety','url':'https://www.fsis.usda.gov/food-safety','note':'Food-safety guidance for refrigeration, leftovers, freezing, and time-temperature control.'},
    'es': {'name':'Departamento de Agricultura de EE. UU. (USDA) — Food Safety','url':'https://www.fsis.usda.gov/food-safety','note':'Orientación de seguridad alimentaria sobre refrigeración, sobras, congelación y control de tiempo y temperatura.'}},
  'mold': {
    'en': {'name':'U.S. Environmental Protection Agency — Mold and Moisture','url':'https://www.epa.gov/mold','note':'Moisture control, mold prevention, cleanup, and recurrence.'},
    'es': {'name':'Agencia de Protección Ambiental de EE. UU. (EPA) — Mold and Moisture','url':'https://www.epa.gov/mold','note':'Control de humedad, prevención, limpieza y recurrencia del moho.'}},
  'pests': {
    'en': {'name':'U.S. Environmental Protection Agency — Integrated Pest Management','url':'https://www.epa.gov/ipm','note':'Integrated pest management using sanitation, exclusion, monitoring, and targeted control.'},
    'es': {'name':'Agencia de Protección Ambiental de EE. UU. (EPA) — Integrated Pest Management','url':'https://www.epa.gov/ipm','note':'Manejo integrado de plagas mediante saneamiento, exclusión, vigilancia y control dirigido.'}},
  'energy': {
    'en': {'name':'ENERGY STAR — Home Energy','url':'https://www.energystar.gov/saveathome','note':'Household energy use, efficiency, heating, cooling, and appliance guidance.'},
    'es': {'name':'ENERGY STAR — Home Energy','url':'https://www.energystar.gov/saveathome','note':'Uso y eficiencia de energía en el hogar, climatización y electrodomésticos.'}},
  'plants': {
    'en': {'name':'University of Minnesota Extension — Houseplants','url':'https://extension.umn.edu/houseplants','note':'Houseplant watering, root health, light, and recovery guidance.'},
    'es': {'name':'University of Minnesota Extension — Houseplants','url':'https://extension.umn.edu/houseplants','note':'Orientación sobre riego, salud de raíces, luz y recuperación de plantas de interior.'}},
}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    s = re.sub(r"[^a-z0-9]+", '-', s).strip('-')
    return s

def strip_title(title, lang, kind):
    t = title.strip('¿? ')
    if lang == 'es' and t.lower().startswith('cómo '): return t[5:]
    if lang == 'en' and t.lower().startswith('how to '): return t[7:]
    return t

def search_intent(title, lang, kind):
    core = strip_title(title, lang, kind)
    if lang == 'es':
        if kind in ('how-to','maintenance'):
            return f'Aplicar un método práctico y seguro para {core[0].lower()+core[1:]}, con criterios claros para saber qué comprobar, qué evitar y cuándo cambiar de estrategia.'
        if kind in ('diagnostics','safety-diagnostics'):
            return f'Identificar las causas probables de «{core}», usar señales observables para decidir qué comprobar primero y saber cuándo corresponde detenerse o pedir ayuda.'
        if kind in ('decision-guide','safety-guide'):
            return f'Tomar una decisión práctica sobre «{core}» usando criterios de seguridad, compatibilidad y resultado en lugar de una regla genérica.'
        if kind == 'prevention':
            return f'Prevenir {core[0].lower()+core[1:]} actuando sobre las causas más probables y usando medidas domésticas sostenibles antes de recurrir a intervenciones mayores.'
        return f'Resolver «{core}» con una secuencia doméstica clara, segura y orientada a la causa.'
    if kind in ('how-to','maintenance'):
        return f'Use a practical, safe method to {core[0].lower()+core[1:]}, with clear checks, limits, and next steps.'
    if kind in ('diagnostics','safety-diagnostics'):
        return f'Identify the likely causes of “{core},” use observable clues to choose the first checks, and know when to stop or get professional help.'
    if kind in ('decision-guide','safety-guide'):
        return f'Make a practical decision about “{core}” using safety, compatibility, and performance criteria instead of a one-size-fits-all rule.'
    if kind == 'prevention':
        return f'Prevent {core[0].lower()+core[1:]} by addressing the most likely causes and using sustainable household measures before escalating.'
    return f'Resolve “{core}” with a clear, safe, cause-based household approach.'

def first_sentence(text):
    m = re.search(r'^(.+?[.!?])(?:\s|$)', text.strip())
    return m.group(1) if m else text.strip()

def make_one(r, lang):
    title = r[f'{lang}_title']
    en_slug = slugify(r['en_title'])
    slug = slugify(title)
    n = r['n']
    secs = r['sections']
    intro = r[f'{lang}_intro']
    html = '<p>'+intro+'</p>' + ''.join(f"<h2>{s[f'{lang}_h']}</h2><p>{s[f'{lang}_p']}</p>" for s in secs)
    faq_q = r[f'faq_{lang}']
    faq_idx = r.get('faq_sections',[0,1,3])
    faq = [{'question':q,'answer':secs[i][f'{lang}_p']} for q,i in zip(faq_q,faq_idx)]
    srcs = [SOURCES[k][lang] for k in r.get('source_keys',[]) if k in SOURCES]
    locale = 'es-ES' if lang=='es' else 'en-US'
    market = ('Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica.' if lang=='es' else 'United States and Canada; practical, safety-first household guidance written natively for North American readers.')
    return {
      'schema_version':1,
      'id':f'{lang}-{n}-{slug}',
      'article_number':n,
      'translation_group':f'{n}-{en_slug}',
      'language':lang,
      'locale':locale,
      'market_context':market,
      'title':title,
      'slug':slug,
      'seo':{'title':title,'meta_description':first_sentence(intro),'search_intent':search_intent(title,lang,r['kind'])},
      'excerpt':intro,
      'taxonomy':{'food_family':r['family'],'food_subcategories':[r['subcat']],'article_types':[r['kind'],r['family']],'primary_article_type':r['kind']},
      'content_html':html,
      'faq':faq,
      'sources':srcs,
      'image':{
        'concept': (f'Fotografía editorial doméstica realista sobre «{title.strip("¿?")}», mostrando de forma clara {secs[0]["es_h"].lower()} como acción o pista principal; materiales y equipo cotidianos, sin texto ni marcas.' if lang=='es' else f'Realistic household editorial photograph about “{title.strip("?")},” clearly showing {secs[0]["en_h"].lower()} as the main action or clue; ordinary home materials and equipment, no text or branding.'),
        'alt':title.strip('¿?')},
      'status':'publish'}

def main():
    records=[]
    for p in BATCHES:
        records.extend(json.loads(p.read_text(encoding='utf-8')))
    nums=sorted(r['n'] for r in records)
    if nums != list(range(391,471)):
        raise SystemExit(f'Expected exact topics 391-470; got {nums[:3]}...{nums[-3:] if nums else []} count={len(nums)}')
    for r in records:
        if len(r['sections']) != 4 or len(r['faq_es']) != 3 or len(r['faq_en']) != 3:
            raise SystemExit(f"#{r['n']} malformed sections/FAQ")
        for lang in ('es','en'):
            o=make_one(r,lang)
            out=ART/lang/f"{r['n']:03d}-{o['slug']}.json"
            out.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    print(f'Generated {len(records)*2} article JSON files from {len(BATCHES)} batches')

if __name__=='__main__': main()
