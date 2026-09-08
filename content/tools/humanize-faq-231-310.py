#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'

ES_RULES={
 'identifica':('¿Qué debo identificar en','?'), 'restablece':('¿Por qué conviene','?'),
 'comprueba':('¿Qué conviene comprobar sobre','?'), 'revisa':('¿Qué conviene revisar sobre','?'),
 'busca':('¿Qué señales debo buscar sobre','?'), 'usa':('¿Cómo conviene usar','?'),
 'retira':('¿Cómo conviene retirar','?'), 'limpia':('¿Cómo conviene limpiar','?'),
 'mide':('¿Cómo se mide','?'), 'distingue':('¿Cómo distingo','?'),
 'evita':('¿Qué conviene evitar sobre','?'), 'mantén':('¿Cómo mantengo','?'), 'manten':('¿Cómo mantengo','?'),
 'protege':('¿Cómo protejo','?'), 'separa':('¿Cómo separo','?'), 'agrupa':('¿Cómo agrupo','?'),
 'pon':('¿Dónde conviene poner','?'), 'reserva':('¿Qué espacio conviene reservar para','?'),
 'empieza':('¿Por dónde empiezo con','?'), 'observa':('¿Qué debo observar sobre','?'),
 'anota':('¿Qué conviene anotar sobre','?'), 'reduce':('¿Cómo reduzco','?'), 'seca':('¿Cómo seco','?'),
 'corta':('¿Cuándo debo cortar','?'), 'desconecta':('¿Cuándo debo desconectar','?'),
 'localiza':('¿Cómo localizo','?'), 'pretrata':('¿Cómo pretrato','?'), 'lava':('¿Cómo lavo','?'),
 'quita':('¿Cómo quito','?'), 'trata':('¿Cómo trato','?'), 'aspira':('¿Cómo aspiro','?'),
 'abre':('¿Cuándo conviene abrir','?'), 'controla':('¿Cómo controlo','?'),
 'relaciona':('¿Qué pistas debo relacionar sobre','?'), 'cronometra':('¿Por qué conviene cronometrar','?'),
 'conecta':('¿Cómo debo conectar','?'), 'refrigera':('¿Cuándo debo refrigerar','?'),
 'enfría':('¿Cómo enfrío','?'), 'enfria':('¿Cómo enfrío','?'), 'precalienta':('¿Cómo precaliento','?'),
 'añade':('¿Cuándo conviene añadir','?'), 'anade':('¿Cuándo conviene añadir','?'),
 'divide':('¿Cómo divido','?'), 'recalienta':('¿Cómo recaliento','?'), 'libera':('¿Cómo libero','?'),
 'vuelve':('¿Cuándo conviene volver a','?'), 'confirma':('¿Cómo confirmo','?'), 'prueba':('¿Cómo pruebo','?'),
 'corrige':('¿Qué debo corregir sobre','?'), 'deja':('¿Por qué conviene dejar','?'),
 'lee':('¿Qué debo mirar al leer','?'), 'sacude':('¿Qué hago antes de lavar','?'), 'cuelga':('¿Cómo conviene colgar','?'),
 'extiende':('¿Cómo conviene extender','?'), 'trabaja':('¿Cómo conviene trabajar con','?'),
 'gira':('¿Cómo giro','?'), 'guarda':('¿Cómo guardo','?'), 'descarta':('¿Qué debo descartar sobre','?'),
 'cuenta':('¿Cómo cuento','?'), 'ejecuta':('¿Cómo ejecuto','?'), 'aplica':('¿Cómo aplico','?'),
 'coloca':('¿Cómo coloco','?'), 'espera':('¿Cuánto conviene esperar para','?')
}
EN_RULES={
 'check':'What should I check about', 'use':'How should I use', 'remove':'How should I remove',
 'clean':'How should I clean', 'keep':'How should I keep', 'start':'Where should I start with',
 'inspect':'What should I inspect about', 'protect':'How should I protect', 'separate':'How should I separate',
 'group':'How should I group', 'put':'Where should I put', 'reserve':'What space should I reserve for',
 'notice':'What should I notice about', 'measure':'How should I measure', 'avoid':'What should I avoid about',
 'dry':'How should I dry', 'disconnect':'When should I disconnect', 'locate':'How do I locate',
 'wash':'How should I wash', 'treat':'How should I treat', 'vacuum':'How should I vacuum',
 'open':'When should I open', 'control':'How do I control', 'identify':'What should I identify about',
 'match':'What clues should I match about', 'time':'Why should I time', 'plug':'How should I plug in',
 'refrigerate':'When should I refrigerate', 'cool':'How should I cool', 'preheat':'How should I preheat',
 'add':'When should I add', 'divide':'How should I divide', 'reheat':'How should I reheat',
 'reset':'How many times should I reset', 'free':'How do I free', 'confirm':'How do I confirm',
 'test':'How should I test', 'correct':'What should I correct about', 'leave':'Why should I leave',
 'read':'What should I check on', 'shake':'What should I do before washing', 'hang':'How should I hang',
 'spread':'How should I spread', 'work':'How should I work with', 'rotate':'How should I rotate',
 'store':'How should I store', 'discard':'What should I discard about', 'count':'How should I count',
 'look':'What should I look for about', 'hold':'How should I hold', 'trim':'How should I trim',
 'run':'How should I run', 'find':'How do I find', 'give':'How should I give', 'plan':'How should I plan for'
}

OVERRIDES={
 ('es',284):['¿Qué aparatos estaban funcionando cuando saltó el automático?','¿Cuántas veces puedo intentar rearmar el automático?','¿Puedo poner un automático de mayor amperaje si sigue saltando?'],
 ('en',284):['What was running when the breaker tripped?','How many times should I try resetting the breaker?','Can I install a higher-amperage breaker if it keeps tripping?'],
 ('es',289):['¿Qué hago si el detector da una alarma de CO?','¿Puedo silenciar una alarma de CO si nadie tiene síntomas?','¿Qué debe revisarse después de una alarma confirmada?'],
 ('en',289):['What should I do if the carbon monoxide alarm sounds?','Can I silence a CO alarm if nobody has symptoms?','What should be inspected after a confirmed CO alarm?'],
 ('es',290):['¿Cuánto aguanta un congelador sin luz si no abro la puerta?','¿Cómo sé si un alimento congelado todavía es seguro?','¿Puedo probar la comida para decidir si está bien?'],
 ('en',290):['How long will a freezer stay cold if I keep the door closed?','How can I tell whether frozen food is still safe?','Can I taste food to decide whether it is safe?'],
 ('es',295):['¿Qué partes de la lavadora conviene limpiar si huele mal?','¿Debo limpiar también el filtro de la lavadora?','¿Cómo evito que el olor vuelva después de limpiarla?'],
 ('en',295):['Which parts of a smelly washer should I clean?','Should I clean the washer filter too?','How do I keep the odor from returning after cleaning?'],
 ('es',297):['¿Qué significa si el triturador no hace ningún ruido?','¿Qué significa si el triturador zumba pero no gira?','¿Cuándo debo dejar de intentar reiniciarlo?'],
 ('en',297):['What does it mean if the garbage disposal is completely silent?','What does it mean if the disposal hums but does not turn?','When should I stop trying to reset the disposal?'],
 ('es',303):['¿Desde cuándo cuenta el tiempo de la carne fuera del frío?','¿Cuándo se reduce el límite de dos horas a una?','¿Cocinar la carne la hace segura si estuvo fuera demasiado tiempo?'],
 ('en',303):['When does the clock start for raw meat left out?','When does the two-hour limit drop to one hour?','Does cooking make raw meat safe if it sat out too long?'],
 ('es',307):['¿Qué hago primero si el GFCI salta continuamente?','¿Puede un solo aparato hacer saltar el GFCI?','¿Qué significa que el GFCI no se pueda rearmar?'],
 ('en',307):['What should I do first if a GFCI keeps tripping?','Can one appliance make a GFCI trip repeatedly?','What does it mean if the GFCI will not reset?'],
 ('es',310):['¿Puede la base estar causando el hundimiento del colchón?','¿Rotar el colchón puede mejorar el hundimiento temporalmente?','¿Qué debo medir antes de reclamar la garantía?'],
 ('en',310):['Can the foundation be causing the mattress sag?','Can rotating the mattress help temporarily?','What should I measure before making a warranty claim?']
}

ES_VERBS={'abras':'abrir','aumentes':'aumentar','silencies':'silenciar','vuelvas':'volver','uses':'usar','metas':'meter','pruebes':'probar','mezcles':'mezclar','subas':'subir','toques':'tocar','selles':'sellar','pintes':'pintar','ignores':'ignorar','cierres':'cerrar','desmontes':'desmontar','introduzcas':'introducir','fuerces':'forzar','compres':'comprar','añadas':'añadir','anadas':'añadir','dejes':'dejar'}

def lower_first(s):
    return s[:1].lower()+s[1:] if s else s

def es_infinitive_phrase(s):
    words=s.split()
    out=[]
    for w in words:
        key=w.lower().strip(',:;.')
        repl=ES_VERBS.get(key)
        if repl:
            punct=w[len(w.rstrip(',:;.')):] if w.rstrip(',:;.').lower()==key else ''
            out.append(repl+punct)
        else: out.append(w)
    return ' '.join(out)

def q_es(h):
    h=h.strip().rstrip('.')
    low=h.lower()
    if low.startswith('si '): return '¿Qué hago '+low+'?'
    if low.startswith('no '): return '¿Por qué no debo '+lower_first(es_infinitive_phrase(h[3:]))+'?'
    words=h.split(); first=words[0].lower().strip(',:;') if words else ''
    rest=' '.join(words[1:]).strip()
    if first=='restablece': return '¿Por qué conviene restablecer '+lower_first(rest)+'?'
    rule=ES_RULES.get(first)
    if rule:
        prefix,_=rule
        return prefix+' '+lower_first(rest)+'?'
    if ' puede ' in ' '+low+' ': return '¿Puede '+lower_first(h.replace(' puede ',' ',1))+'?'
    if ' no ' in ' '+low+' ': return '¿Por qué '+lower_first(h)+'?'
    if ' requiere ' in ' '+low+' ': return '¿Cuándo '+lower_first(h)+'?'
    if ' ayuda' in low or ' ayudan' in low: return '¿'+h+'?'
    if ' significa ' in ' '+low+' ': return '¿Qué '+lower_first(h)+'?'
    if ' vs ' in low: return '¿Cómo se comparan '+lower_first(h)+'?'
    return '¿Qué indica '+lower_first(h)+'?'

def q_en(h):
    h=h.strip().rstrip('.')
    low=h.lower()
    if low.startswith('if '): return 'What should I do '+low+'?'
    if low.startswith('do not '): return "Why shouldn't I "+lower_first(h[7:])+'?'
    words=h.split(); first=words[0].lower().strip(',:;') if words else ''; rest=' '.join(words[1:]).strip()
    rule=EN_RULES.get(first)
    if rule: return rule+' '+lower_first(rest)+'?'
    if ' can ' in ' '+low+' ': return 'Can '+lower_first(h.replace(' can ',' ',1))+'?'
    if ' needs ' in ' '+low+' ' or ' need ' in ' '+low+' ': return 'When does '+lower_first(h)+'?'
    if ' is ' in ' '+low+' ' or ' are ' in ' '+low+' ': return 'What does it mean when '+lower_first(h)+'?'
    return 'What does '+lower_first(h)+' tell me?'

for lang in ('es','en'):
    folder=ROOT/lang
    for n in range(231,311):
        p=next(folder.glob(f'{n:03d}-*.json'))
        o=json.loads(p.read_text(encoding='utf-8'))
        hs=re.findall(r'<h2>(.*?)</h2>',o['content_html'])
        chosen=[hs[0],hs[1],hs[3]]
        questions=OVERRIDES.get((lang,n)) or [(q_es(h) if lang=='es' else q_en(h)) for h in chosen]
        for faq,q in zip(o['faq'],questions): faq['question']=q
        p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Humanized FAQ questions for articles 231-310')
