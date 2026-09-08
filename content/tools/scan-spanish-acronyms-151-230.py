#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'/'es'
known={
 'EPA':'Agencia de Protección Ambiental',
 'CDC':'Centros para el Control y la Prevención de Enfermedades',
 'USDA':'Departamento de Agricultura',
 'CPSC':'Comisión de Seguridad de Productos del Consumidor',
 'DOE':'Departamento de Energía',
 'UHT':'temperatura ultra alta (UHT)',
 'GFCI':'interruptor de circuito por falla a tierra',
 'HVAC':'sistema de climatización',
 'MERV':'valor mínimo de eficiencia de reporte',
 'HE':'alta eficiencia',
}
seen={}
errors=[]
for n in range(151,231):
    ms=list(ROOT.glob(f'{n:03d}-*.json'))
    if len(ms)!=1: continue
    o=json.loads(ms[0].read_text(encoding='utf-8'))
    text=' '.join([o.get('title',''),o.get('excerpt',''),o.get('content_html','')]+[q.get('question','')+' '+q.get('answer','') for q in o.get('faq',[])])
    plain=re.sub(r'<[^>]+>',' ',text)
    toks=sorted(set(re.findall(r'(?<![A-Za-zÁÉÍÓÚÑÜ])([A-Z]{2,6})(?![A-Za-zÁÉÍÓÚÑÜ])',plain)))
    if toks: seen[n]=toks
    for ac,exp in known.items():
        if ac not in toks: continue
        if ac=='GFCI':
            ok=(exp.lower() in plain.lower() or 'interruptor diferencial de fuga a tierra' in plain.lower())
        elif ac=='HVAC':
            ok=('sistema de climatización' in plain.lower())
        else:
            ok=exp.lower() in plain.lower()
        if not ok:
            errors.append(f'ES #{n}: {ac} appears without the expected plain-language expansion')
print('Spanish uppercase/acronym inventory:')
for n,toks in seen.items(): print(f'  #{n}: {", ".join(toks)}')
if errors:
    print('Acronym errors:')
    for e in errors: print(' - '+e)
    raise SystemExit(1)
print('Known-acronym expansion audit: PASS')
