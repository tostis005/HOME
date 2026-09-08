#!/usr/bin/env python3
from pathlib import Path
import json
T=Path(__file__).resolve().parents[1]/'tools'

def load(n):
 for q in T.glob('batch-*.json'):
  data=json.loads(q.read_text(encoding='utf-8'))
  for item in data:
   if item['n']==n:
    return q,data,item
 raise SystemExit(f'missing item {n}')

def save(q,data):
 q.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

q,d,x=load(331); x['sections'][2][2]=x['sections'][2][2].replace('Equipos inverter o de velocidad variable','Los equipos de velocidad variable'); save(q,d)
q,d,x=load(367); x['es_intro']='MERV es una escala de eficiencia de filtración cuyo nombre viene del inglés Minimum Efficiency Reporting Value. Una cifra más alta retiene partículas más pequeñas, pero también puede aumentar la resistencia al aire si el sistema no está diseñado para ese filtro.'; save(q,d)
q,d,x=load(372); x['sections'][0][2]=x['sections'][0][2].replace('En LED, un regulador incompatible','En bombillas LED (diodos emisores de luz), un regulador incompatible'); save(q,d)
q,d,x=load(385); x['es_intro']=x['es_intro'].replace('porque Bacillus cereus','porque la bacteria Bacillus cereus'); save(q,d)
q,d,x=load(388); x['es_intro']='Un enchufe con protección diferencial de tipo GFCI (interruptor de circuito por falla a tierra, habitual en Norteamérica) se rearma con su botón RESET cuando la condición que provocó el disparo ya no está presente. Si no se rearma o vuelve a saltar, no lo puentes ni insistas repetidamente.'; save(q,d)
print('Applied Spanish terminology preflight for 311-390')
