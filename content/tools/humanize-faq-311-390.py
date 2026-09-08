#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]/'articles'

ES_VERBS={
'empieza':'empezar','usa':'usar','evita':'evitar','comprueba':'comprobar','revisa':'revisar','mira':'mirar','busca':'buscar','retira':'retirar','limpia':'limpiar','trabaja':'trabajar','seca':'secar','deja':'dejar','abre':'abrir','cierra':'cerrar','añade':'añadir','anade':'añadir','reduce':'reducir','controla':'controlar','observa':'observar','distingue':'distinguir','identifica':'identificar','protege':'proteger','guarda':'guardar','lava':'lavar','aclara':'aclarar','enfría':'enfriar','enfria':'enfriar','congela':'congelar','descongela':'descongelar','recalienta':'recalentar','mantén':'mantener','manten':'mantener','pulsa':'pulsar','desconecta':'desconectar','apaga':'apagar','marca':'marcar','localiza':'localizar','sigue':'seguir','aspira':'aspirar','aplica':'aplicar','reserva':'reservar','pon':'poner','separa':'separar','agrupa':'agrupar','confirma':'confirmar','da':'dar','haz':'hacer','piensa':'pensar','pasa':'pasar','espera':'esperar','anota':'anotar','elige':'elegir','mueve':'mover','traslada':'trasladar','respeta':'respetar','relaciona':'relacionar','aprende':'aprender','porcióna':'porcionar','porciona':'porcionar','lee':'leer','corta':'cortar','descarta':'descartar','vacía':'vaciar','vacia':'vaciar','sella':'sellar','coloca':'colocar','acelera':'acelerar','recupera':'recuperar','repara':'reparar','equilibra':'equilibrar','refrigera':'refrigerar','reconecta':'reconectar','conecta':'conectar'}
EN_IMP=set('start use avoid check inspect look remove clean work dry leave open close add reduce control watch separate identify protect store wash rinse cool freeze thaw reheat keep press unplug turn mark locate follow vacuum apply reserve put group compare choose allow confirm give move read verify think note track rule discard respect refrigerate reconnect connect cover run create find match speed build restore test decide portion air'.split())

def norm(s): return re.sub(r'\s+',' ',s).strip().rstrip('.')
def lower_first(s): return s[:1].lower()+s[1:] if s else s

def es_question(h):
 h=norm(h); low=h.lower()
 # Conditional/temporal headings: ask about the condition, not the command after the comma.
 for starter,prefix in [('si ','¿Qué debo hacer si '),('cuando ','¿Qué conviene hacer cuando '),('para ','¿Qué conviene hacer para ')]:
  if low.startswith(starter) and ',' in h:
   cond=h.split(',',1)[0][len(starter):].strip().lower()
   return prefix+cond+'?'
 if low.startswith('no '):
  rest=h[3:].strip(); parts=rest.split(); first=parts[0].lower().strip(',:;') if parts else ''
  inf=ES_VERBS.get(first,first); tail=' '.join(parts[1:]).lower()
  return ('¿Por qué no conviene '+inf+(' '+tail if tail else '')+'?').replace('  ',' ')
 parts=h.split(); first=parts[0].lower().strip(',:;') if parts else ''
 if first in ES_VERBS:
  inf=ES_VERBS[first]; rest=' '.join(parts[1:]).lower()
  return ('¿Cómo conviene '+inf+(' '+rest if rest else '')+'?').replace('  ',' ')
 # Declarative headings become direct why/meaning questions; Spanish does not need inversion.
 if re.search(r'\b(puede|pueden|suele|suelen|necesita|necesitan|requiere|requieren|importa|importan|ayuda|ayudan|apunta|apuntan|indica|indican|funciona|funcionan|reduce|reducen|aumenta|aumentan|retrasa|acelera|merece|merecen|cambia|cambian|queda|quedan|está|estan|están|es|son)\b',low):
  return '¿Por qué '+low+'?'
 return '¿Qué debo saber sobre '+low+'?'

def en_question(h):
 h=norm(h); low=h.lower()
 for starter,prefix in [('if ','What should I do if '),('when ','What should I do when '),('for ','What should I do for ')]:
  if low.startswith(starter) and ',' in h:
   cond=h.split(',',1)[0][len(starter):].strip().lower()
   return prefix+cond+'?'
 if low.startswith('do not '): return 'Why should I avoid '+low[7:].strip()+'?'
 if low.startswith('never '): return 'Why should I avoid '+low[6:].strip()+'?'
 parts=low.split(); first=parts[0].strip(',:;') if parts else ''
 if first in EN_IMP:
  rest=' '.join(parts[1:])
  return ('How should I '+first+(' '+rest if rest else '')+'?').replace('  ',' ')
 # Natural transformations for common declarative headings.
 for phrase,aux in [(' does not ','does'),(' do not ','do')]:
  if phrase in ' '+low+' ':
   subject,rest=low.split(phrase.strip(),1)
   return f'Why {aux} {subject.strip()} not {rest.strip()}?'
 for phrase in (' can ',' may '):
  if phrase in ' '+low+' ':
   subject,rest=low.split(phrase.strip(),1)
   return f'Can {subject.strip()} {rest.strip()}?'
 for phrase,aux in [(' is ','is'),(' are ','are')]:
  if phrase in ' '+low+' ':
   subject,rest=low.split(phrase.strip(),1)
   return f'Why {aux} {subject.strip()} {rest.strip()}?'
 for phrase,aux in [(' needs ','does'),(' requires ','does')]:
  if phrase in ' '+low+' ':
   subject,rest=low.split(phrase.strip(),1)
   verb='need' if 'needs' in phrase else 'require'
   return f'When {aux} {subject.strip()} {verb} {rest.strip()}?'
 return 'What should I know about '+low+'?'

# High-risk or otherwise awkward headings get reader-style, intent-specific questions.
OVERRIDES={
('es',364):['¿Cómo sé si la presión de la caldera está realmente baja?','¿Cómo identifico el mecanismo de llenado de mi caldera?','¿Qué hago si la presión vuelve a bajar después de rellenar?'],
('en',364):['How do I know whether the boiler pressure is actually low?','How do I identify my boiler’s filling arrangement?','What should I do if the pressure falls again after topping up?'],
('es',372):['¿Qué compruebo si solo parpadea una lámpara?','¿Cuándo el parpadeo al arrancar un aparato merece revisión?','¿Qué hago si hay calor, olor a quemado o chispas?'],
('en',372):['What should I check if only one light is flickering?','When does flickering as an appliance starts need attention?','What should I do if there is heat, a burning smell, or arcing?'],
('es',378):['¿Qué hago primero si la secadora huele a quemado?','¿Puede una ventilación obstruida causar olor a quemado?','¿Cuándo debo dejar la secadora fuera de servicio?'],
('en',378):['What should I do first if the dryer smells burnt?','Can restricted airflow cause a burning smell?','When should I leave the dryer out of service?'],
('es',380):['¿Cuánto ayuda mantener cerrada la puerta del refrigerador?','¿Cómo sé si el refrigerador mantuvo una temperatura segura?','¿Puedo probar la comida para decidir si es segura?'],
('en',380):['How much does keeping the refrigerator door closed help?','How can I tell whether the refrigerator stayed at a safe temperature?','Can I taste food to decide whether it is safe?'],
('es',388):['¿Qué debo desconectar antes de rearmar un GFCI?','¿Cómo se rearma el GFCI con el botón RESET?','¿Qué hago si el GFCI vuelve a saltar?'],
('en',388):['What should I unplug before resetting a GFCI?','How do I reset the GFCI with the RESET button?','What should I do if the GFCI trips again?'],
('es',389):['¿Qué hago primero si un enchufe está caliente?','¿Puede un aparato concreto estar provocando el calentamiento?','¿Cuándo debo cortar el circuito de un enchufe caliente?'],
('en',389):['What should I do first if an outlet is hot?','Can one appliance be causing the outlet to heat up?','When should I turn off the circuit for a hot outlet?'],
('es',390):['¿Cómo distingo un regulador templado de un interruptor demasiado caliente?','¿Puede una carga de iluminación incorrecta calentar el interruptor?','¿Puede una conexión floja calentarse aunque la luz siga funcionando?'],
('en',390):['How can I distinguish normal dimmer warmth from an overheated switch?','Can the wrong lighting load make a switch run hot?','Can a loose connection heat up even while the light still works?']}

for lang in ('es','en'):
 for n in range(311,391):
  p=next((ROOT/lang).glob(f'{n:03d}-*.json'))
  o=json.loads(p.read_text(encoding='utf-8'))
  hs=re.findall(r'<h2>(.*?)</h2>',o['content_html'])
  chosen=[hs[0],hs[1],hs[3]]
  questions=OVERRIDES.get((lang,n)) or [(es_question(h) if lang=='es' else en_question(h)) for h in chosen]
  for faq,q in zip(o['faq'],questions): faq['question']=q
  p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Humanized FAQ questions for HOME articles 311-390')
