#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]/'articles'

ADDITIONS={
 ('en',224): ('<h2>For picnics, commutes, and grocery trips, use temperature rather than the clock alone</h2><p>An insulated cooler with enough ice or cold packs can keep milk at refrigerator temperature while it is away from the kitchen. Milk that has stayed at 40°F (4°C) or below is not equivalent to a carton sitting warm on a table. If you cannot verify that it stayed cold, count the time as unrefrigerated.</p>', '<p>A refrigerated carton forgotten on the counter overnight should be discarded.</p>'),
 ('es',225): ('<h2>En una comida larga, sirve porciones pequeñas</h2><p>Si vas a tener pollo disponible durante bastante tiempo, conserva el resto frío o mantenlo realmente caliente y repón cantidades pequeñas. Sacar toda la bandeja desde el principio hace más difícil controlar cuánto tiempo lleva cada porción en una temperatura insegura.</p>', '<p>Si no sabes si fueron dos horas o toda la tarde, trata el tiempo como desconocido y elige la opción segura.</p>'),
 ('en',225): ('<h2>For a long meal, put out smaller portions</h2><p>If chicken will be served over an extended period, keep the reserve properly chilled or held safely hot and replenish smaller amounts. Setting out the entire tray at the beginning makes it difficult to know how long each portion has spent at an unsafe temperature.</p>', '<p>If you cannot tell whether it was out for two hours or most of the afternoon, treat the time as unknown and choose the safer option.</p>'),
 ('en',228): ('<h2>Confirm what actually leaked before choosing a cleaner</h2><p>A dark automotive spot may be engine oil, but coolant, brake fluid, transmission fluid, and other products have different cleanup and disposal concerns. If the spill is still active, fix or contain the vehicle leak first; repeatedly cleaning the slab will not solve the source.</p>', '<p>For fuel, solvent, or a large spill, safe containment and disposal matter more than cosmetic stain removal.</p>'),
}

for (lang,n),(paragraph,anchor) in ADDITIONS.items():
    matches=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(matches)!=1:
        raise SystemExit(f'Expected one {lang} #{n}, found {len(matches)}')
    p=matches[0]
    obj=json.loads(p.read_text(encoding='utf-8'))
    body=obj['content_html']
    if paragraph not in body:
        if anchor not in body:
            raise SystemExit(f'Anchor missing for {lang} #{n}')
        body=body.replace(anchor,paragraph+anchor,1)
        obj['content_html']=body
        p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        print(f'Expanded {lang.upper()} #{n}')
