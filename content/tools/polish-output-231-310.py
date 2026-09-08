#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'
IMPERATIVE_ES={
 'comprueba':'comprobar','revisa':'revisar','busca':'buscar','usa':'usar','retira':'retirar','limpia':'limpiar','mide':'medir','distingue':'distinguir','evita':'evitar','mantén':'mantener','manten':'mantener','protege':'proteger','separa':'separar','agrupa':'agrupar','pon':'poner','reserva':'reservar','empieza':'empezar','observa':'observar','anota':'anotar','reduce':'reducir','seca':'secar','corta':'cortar','desconecta':'desconectar','localiza':'localizar','saca':'sacar','pretrata':'pretratar','lava':'lavar','quita':'quitar','trata':'tratar','aspira':'aspirar','abre':'abrir','controla':'controlar','identifica':'identificar','relaciona':'relacionar','cronometra':'cronometrar','conecta':'conectar','refrigera':'refrigerar','enfría':'enfriar','enfria':'enfriar','precalienta':'precalentar','añade':'añadir','anade':'añadir','divide':'dividir','recalienta':'recalentar','restablece':'restablecer','libera':'liberar','vuelve':'volver','confirma':'confirmar','prueba':'probar','corrige':'corregir','deja':'dejar','lee':'leer','sacude':'sacudir','cuelga':'colgar','extiende':'extender','trabaja':'trabajar','gira':'girar','guarda':'guardar','descarta':'descartar','cuenta':'contar','mantente':'mantenerse'
}
IMPERATIVE_EN=set('check use remove clean keep start inspect protect separate group put reserve notice measure avoid dry disconnect locate wash treat vacuum open control identify match time plug refrigerate cool preheat add divide reheat reset free confirm test correct leave read shake hang spread work rotate store discard count look hold trim run find give'.split())
OLD_ES={'¿Cuál es la primera comprobación útil?','¿Qué error conviene evitar?','¿Cuándo hace falta cambiar de estrategia o pedir ayuda?'}
OLD_EN={'What is the most useful first check?','What mistake should I avoid?','When should I change approach or get help?'}

def q_es(h):
    h=h.strip(); low=h.lower()
    if low.startswith('si '):
        cond=h.split(',',1)[0].lower()
        return f'¿Qué debo hacer {cond}?'
    if low.startswith('no '):
        words=h.split()
        if len(words)>1:
            v=words[1].lower().strip(',:;')
            inf=IMPERATIVE_ES.get(v)
            if inf:
                rest=' '.join(words[2:]).rstrip('.').lower()
                return f'¿Por qué conviene no {inf}{(" "+rest) if rest else ""}?'
        return f'¿Por qué conviene evitar este error: «{h}»?'
    words=h.split(); first=words[0].lower().strip(',:;') if words else ''
    if first in IMPERATIVE_ES:
        inf=IMPERATIVE_ES[first]; rest=' '.join(words[1:]).rstrip('.').lower()
        return f'¿Qué debo tener en cuenta al {inf}{(" "+rest) if rest else ""}?'
    return f'¿Por qué es importante «{h}» en este caso?'

def q_en(h):
    h=h.strip(); low=h.lower()
    if low.startswith('if '):
        cond=h.split(',',1)[0]
        return f'What should I do {cond.lower()}?'
    if low.startswith('do not '):
        return f'Why should I avoid {h[7:].rstrip(".").lower()}?'
    first=low.split()[0].strip(',:;') if low.split() else ''
    if first in IMPERATIVE_EN:
        return f'Why does it matter to {h.rstrip(".").lower()}?'
    return f'Why does “{h}” matter in this situation?'

for lang in ('es','en'):
    folder=ROOT/lang
    for n in range(231,311):
        ms=list(folder.glob(f'{n:03d}-*.json'))
        if len(ms)!=1: raise SystemExit(f'Expected one {lang} #{n}, found {len(ms)}')
        p=ms[0]; o=json.loads(p.read_text(encoding='utf-8'))
        hs=re.findall(r'<h2>(.*?)</h2>',o['content_html'])
        if len(hs)<4: raise SystemExit(f'{lang} #{n}: insufficient H2')
        picks=[hs[0],hs[1],hs[3]]
        for faq,h in zip(o['faq'],picks):
            faq['question']=q_es(h) if lang=='es' else q_en(h)
        title=o['title'].strip('¿?¡! ')
        first=hs[0]
        if lang=='es':
            o['seo']['search_intent']=o['seo']['search_intent'].replace('«¿','«').replace('«¡','«')
            o['image']['concept']=f'Fotografía editorial realista sobre «{title}», mostrando visualmente «{first}» como detalle principal; contexto doméstico natural, sin texto ni marcas.'
        else:
            o['image']['concept']=f'Realistic editorial photograph about “{title},” visually centered on “{first}” as the main clue or action; natural household setting, no text or branding.'
        p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Polished final FAQ questions, search intent punctuation, and image concepts for 231-310')
