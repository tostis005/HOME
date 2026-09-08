#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
VERBS={'comprueba':'comprobar','revisa':'revisar','busca':'buscar','usa':'usar','retira':'retirar','limpia':'limpiar','mide':'medir','distingue':'distinguir','evita':'evitar','mantén':'mantener','manten':'mantener','protege':'proteger','separa':'separar','agrupa':'agrupar','pon':'poner','reserva':'reservar','empieza':'empezar','observa':'observar','anota':'anotar','reduce':'reducir','seca':'secar','corta':'cortar','desconecta':'desconectar','localiza':'localizar','saca':'sacar','pretrata':'pretratar','lava':'lavar','quita':'quitar','trata':'tratar','aspira':'aspirar','abre':'abrir','controla':'controlar','identifica':'identificar','relaciona':'relacionar','cronometra':'cronometrar','conecta':'conectar','refrigera':'refrigerar','enfría':'enfriar','enfria':'enfriar','precalienta':'precalentar','añade':'añadir','anade':'añadir','divide':'dividir','recalienta':'recalentar','restablece':'restablecer','libera':'liberar','vuelve':'volver','confirma':'confirmar','prueba':'probar','corrige':'corregir','deja':'dejar','lee':'leer','sacude':'sacudir','cuelga':'colgar','extiende':'extender','trabaja':'trabajar','gira':'girar','guarda':'guardar','descarta':'descartar','cuenta':'contar','mantente':'mantenerse','ejecuta':'ejecutar','aplica':'aplicar','coloca':'colocar','retira':'retirar','espera':'esperar','mantiene':'mantener'}
ACRONYMS=['CO','GFCI','UHT','EPA','CDC','USDA','CPSC','MERV','HVAC']

def restore(s,h):
    for a in ACRONYMS:
        if re.search(rf'\b{a}\b',h): s=re.sub(rf'\b{a.lower()}\b',a,s,flags=re.I)
    return s

def inf_phrase(h):
    words=h.split(); first=words[0].lower().strip(',:;')
    inf=VERBS.get(first)
    if not inf: return None
    rest=' '.join(words[1:]).rstrip('.').lower()
    def repl(m):
        c,v=m.group(1),m.group(2); return f'{c} {VERBS.get(v.lower(),v)}'
    rest=re.sub(r'\b(y|o)\s+([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\b',repl,rest)
    return restore((inf+(' '+rest if rest else '')),h)

def q_es(h):
    h=h.strip(); low=h.lower()
    if low.startswith('si '):
        cond=h.split(',',1)[0].lower(); return restore(f'¿Qué debo hacer {cond}?',h)
    if low.startswith('no '):
        sub=h[3:].strip(); phr=inf_phrase(sub)
        if phr: return restore(f'¿Por qué conviene no {phr}?',h)
        return f'¿Por qué conviene evitar «{h}»?'
    phr=inf_phrase(h)
    if phr: return restore(f'¿Qué debo tener en cuenta al {phr}?',h)
    return restore(f'¿Por qué es importante «{h}» en este caso?',h)

def q_en(h):
    h=h.strip(); low=h.lower()
    if low.startswith('if '):
        cond=h.split(',',1)[0].lower(); return restore(f'What should I do {cond}?',h)
    if low.startswith('do not '): return restore(f'Why should I avoid {h[7:].rstrip(".").lower()}?',h)
    first=low.split()[0].strip(',:;') if low.split() else ''
    imperative=set('check use remove clean keep start inspect protect separate group put reserve notice measure avoid dry disconnect locate wash treat vacuum open control identify match time plug refrigerate cool preheat add divide reheat reset free confirm test correct leave read shake hang spread work rotate store discard count look hold trim run find give plan'.split())
    if first in imperative: return restore(f'Why does it matter to {h.rstrip(".").lower()}?',h)
    return restore(f'Why does “{h}” matter in this situation?',h)

for lang in ('es','en'):
  for n in range(231,311):
    ms=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(ms)!=1: raise SystemExit(f'{lang} #{n}: expected one file')
    p=ms[0]; o=json.loads(p.read_text(encoding='utf-8'))
    title=o['title'].strip('¿?¡! ')
    if lang=='es' and title.lower().startswith('cómo '):
        action=title[5:].strip().lower()
        o['seo']['search_intent']=f'Aplicar un método práctico y seguro para {action}, evitando errores que dañan materiales o equipos, generan riesgos o hacen que el problema reaparezca.'
    elif lang=='en' and title.lower().startswith('how to '):
        action=title[7:].strip().lower()
        o['seo']['search_intent']=f'Use a practical, safe method to {action}, avoiding mistakes that damage materials or equipment, create hazards, or allow the problem to return.'
    if lang=='es' and n==310:
        o['content_html']=o['content_html'].replace('<h2>Un topper cambia comodidad, no estructura</h2>','<h2>Un sobrecolchón cambia comodidad, no estructura</h2>').replace('Una capa superior puede reducir sensación de desnivel leve','Un sobrecolchón o capa superior puede reducir la sensación de desnivel leve')
        o['image']['concept']=o['image']['concept'].replace('Un topper cambia comodidad, no estructura','Un sobrecolchón cambia comodidad, no estructura')
    hs=re.findall(r'<h2>(.*?)</h2>',o['content_html'])
    picks=[hs[0],hs[1],hs[3]]
    for f,h in zip(o['faq'],picks): f['question']=q_es(h) if lang=='es' else q_en(h)
    if lang=='es' and n==289:
        o['excerpt']=o['excerpt'].replace('alarma de CO','alarma de monóxido de carbono (CO)',1)
        o['content_html']=o['content_html'].replace('alarma de CO','alarma de monóxido de carbono (CO)',1)
    if lang=='es' and n==307:
        o['seo']['search_intent']=re.sub(r'\bgfci\b','GFCI',o['seo']['search_intent'],flags=re.I)
    p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Applied final natural-language, acronym, and Spanish terminology polish to 231-310')
