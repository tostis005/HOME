#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'articles'

INTENTS={
('es',396):'Determinar cada cuánto cambiar un filtro de agua de toda la casa usando el intervalo y la capacidad del fabricante, la calidad del agua, el consumo y las señales de restricción.',
('en',396):'Determine how often to replace a whole-house water filter using manufacturer limits, water quality, household use, and signs of flow restriction.',
('es',401):'Prevenir la congelación de tuberías identificando los tramos más expuestos, reduciendo corrientes de aire frío y aplicando medidas adicionales antes de episodios de frío intenso.',
('en',401):'Prevent pipes from freezing by identifying the most exposed runs, reducing cold-air leakage, and taking targeted steps before severe cold weather.',
('es',423):'Evitar que entren ratones en el garaje combinando sellado resistente, ajuste de puertas, almacenamiento cerrado y vigilancia de las primeras señales de actividad.',
('en',423):'Keep mice out of a garage by combining rodent-resistant exclusion, door sealing, closed food storage, and early monitoring for activity.',
('es',431):'Reducir el riesgo de que la ropa encoja ajustando temperatura, agitación, carga y secado a las instrucciones de cada tejido y prenda.',
('en',431):'Prevent clothes from shrinking by matching wash temperature, agitation, load size, and drying method to each garment’s care instructions.',
('es',452):'Determinar cada cuánto revisar y limpiar el conducto de la secadora según su recorrido, el uso real y las señales de restricción que pueden aumentar el riesgo de incendio.',
('en',452):'Determine how often to inspect and clean a dryer vent based on vent design, actual use, and restriction signs that can increase fire risk.'
}

META={
('es',416):'Compara qué aparatos consumen más electricidad en casa según potencia, horas de uso y frecuencia para saber dónde merece la pena ahorrar.',
('en',416):'Compare which household appliances use the most electricity based on wattage, run time, and frequency so you know where savings matter most.',
('es',433):'Lava los trapos de limpieza según el residuo que contienen, separa los contaminados y evita mezclas o secados que puedan crear riesgos.'
}

REPL={
('es',411): [('Tela, vinilo, PEVA y recubrimientos especiales','Tela, vinilo, otros forros plásticos y recubrimientos especiales')],
('en',411): [('Fabric, vinyl, PEVA, and specialty coatings','Fabric, vinyl, other plastic liners, and specialty coatings')],
('es',451): [('mueve la palanca afectada a OFF y después a ON una sola vez','mueve la palanca afectada a apagado (OFF) y después a encendido (ON) una sola vez')],
('en',451): [('check the circuit breaker or GFCI protection','check the circuit breaker or ground-fault circuit interrupter (GFCI) protection')],
('es',460): [('No eches agua','No viertas agua'),('no eches agua','no viertas agua')],
('en',461): [('circuit breaker or GFCI protection','circuit breaker or ground-fault circuit interrupter (GFCI) protection')],
('es',465): [('Bombillas LED no compatibles','Bombillas de diodos emisores de luz (LED) no compatibles')],
('en',465): [('LED lamps that are incompatible','Light-emitting diode (LED) lamps that are incompatible')],
('en',444): [('qualified HVAC maintenance','qualified heating-and-cooling maintenance')]
}

for lang in ('es','en'):
    for n in range(391,471):
        files=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(files)!=1:
            raise SystemExit(f'{lang} #{n}: expected one file, found {len(files)}')
        p=files[0]; o=json.loads(p.read_text(encoding='utf-8'))
        if (lang,n) in INTENTS:
            o['seo']['search_intent']=INTENTS[(lang,n)]
        if (lang,n) in META:
            o['seo']['meta_description']=META[(lang,n)]
        if (lang,n) in REPL:
            for old,new in REPL[(lang,n)]:
                o['content_html']=o['content_html'].replace(old,new)
                o['excerpt']=o['excerpt'].replace(old,new)
                for item in o.get('faq',[]):
                    item['answer']=item['answer'].replace(old,new)
        p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Applied final language and metadata polish to HOME 391-470')
