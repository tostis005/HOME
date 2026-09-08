#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'

def load(lang,n):
    fs=list((ART/lang).glob(f'{n:03d}-*.json'))
    if len(fs)!=1: raise SystemExit(f'{lang} #{n}: expected one JSON, got {len(fs)}')
    p=fs[0]; return p,json.loads(p.read_text(encoding='utf-8'))

def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

p,o=load('en',461)
old='check the circuit breaker or GFCI protection'
new='check the circuit breaker or ground-fault circuit interrupter (GFCI) protection'
o['content_html']=o['content_html'].replace(old,new)
for x in o['faq']: x['answer']=x['answer'].replace(old,new)
save(p,o)

META={
('es',416):'Los mayores consumos eléctricos suelen venir de climatización, agua caliente y aparatos de alta potencia o muchas horas de uso.',
('en',416):'The largest household electricity loads are usually heating, cooling, water heating, and equipment that runs at high power or for many hours.',
('es',433):'Antes de lavar trapos de limpieza, hay que saber qué sustancias contienen y separar los que llevan aceites, disolventes o químicos incompatibles.'
}
for key,value in META.items():
    p,o=load(*key); o['seo']['meta_description']=value; save(p,o)
print('Applied final targeted polish for HOME 391-470')
