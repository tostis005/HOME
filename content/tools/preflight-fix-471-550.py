#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'tools'

records={}
paths={}
for p in sorted(TOOLS.glob('batch-*.json')):
    if not any(x in p.name for x in ('471-480','481-490','491-500','501-510','511-520','521-530','531-540','541-550')):
        continue
    data=json.loads(p.read_text(encoding='utf-8'))
    for r in data:
        records[int(r['n'])]=r
        paths[int(r['n'])]=p

def set_intro(n,lang,text):
    records[n][f'intro_{lang}']=text

def replace_en(n,old,new):
    r=records[n]
    r['intro_en']=r['intro_en'].replace(old,new)
    for sec in r['sections']:
        sec[3]=sec[3].replace(old,new)

# Natural, concise meta-description first sentences.
set_intro(484,'es','Un calefactor eléctrico portátil consume mucha potencia mientras la resistencia está encendida. El coste depende de vatios, horas reales de uso y tarifa eléctrica, además de cuánto cicla el termostato.')
set_intro(495,'es','Lavar ropa blanca y de color junta puede funcionar con prendas estables, pero aumenta el riesgo de transferencia de tinte. La decisión depende de la solidez del color, la temperatura y cuánto te importe mantener los blancos brillantes.')
set_intro(516,'es','Un enchufe sin corriente con el automático normal puede depender de un interruptor, una protección diferencial aguas arriba, una conexión floja o un fallo de la toma. Empieza por comprobaciones externas y no retires la placa.')
set_intro(516,'en','A dead outlet with a normal-looking breaker may be controlled by a wall switch, upstream ground-fault protection, a loose connection, or an internal receptacle fault. Start with external checks and do not remove the cover.')
set_intro(534,'es','Hervir agua puede precipitar parte de la dureza temporal, pero no elimina todos los minerales responsables de la cal. Tampoco es una forma práctica de ablandar el agua de toda una vivienda.')
set_intro(550,'es','Las aves pueden anidar en salidas de baño, cocina o secadora, pero cerrar un conducto activo puede atrapar adultos o crías. Primero identifica el conducto y confirma que el nido esté inactivo antes de proteger la salida.')
set_intro(550,'en','Birds can nest in bathroom, kitchen, or dryer exhausts, but closing an active vent can trap adults or young. Identify the vent and confirm the nest is inactive before installing a compatible guard.')

# Replace unexplained HVAC shorthand in article prose.
replace_en(513,'HVAC','heating and cooling system')
replace_en(514,'HVAC','heating and cooling system')

# Ensure LED is explicitly expanded at first prose use.
set_intro(530,'en','LED lights use light-emitting diode (LED) technology and can flicker because of a loose bulb, incompatible dimmer, failing driver, or power variation. Flicker in one lamp is often local; several rooms changing brightness together deserve more attention.')

# Expand energy units in headings/questions before the acronym is reused.
r=records[483]
r['sections'][1][0]='Convierte potencia y horas en kilovatios-hora (kWh)'
r['sections'][1][1]='Convert power and runtime into kilowatt-hours (kWh)'
r=records[484]
r['sections'][1][0]='Calcula kilovatios-hora (kWh) con el tiempo real de calefacción'
r['sections'][1][1]='Calculate kilowatt-hours (kWh) from actual heating time'
r['faq_es'][0]='¿Cuántos kilovatios-hora (kWh) consume un calefactor de 1500 W en cuatro horas?'
r['faq_en'][0]='How many kilowatt-hours (kWh) does a 1,500-watt heater use in four hours?'

# Keep the reviewed cigarette-smoke FAQ wording in the canonical generation input.
r=records[514]
r['faq_es'][0]='¿Qué conviene retirar o lavar primero al quitar olor a tabaco?'
r['faq_en'][0]='What should I remove or wash first when tackling cigarette smoke odor?'

# Write each touched batch once.
for p in sorted(set(paths.values())):
    data=json.loads(p.read_text(encoding='utf-8'))
    for i,r in enumerate(data):
        n=int(r['n'])
        if n in records:
            data[i]=records[n]
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('Applied HOME 471-550 preflight editorial fixes')
