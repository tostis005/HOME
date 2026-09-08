#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'tools'

FAQ_MAP={
391:[0,1,3],392:[0,2,3],393:[0,1,3],394:[0,1,3],395:[0,1,2],396:[0,1,2],397:[0,1,3],398:[0,1,2],399:[0,1,2],400:[0,1,2],
401:[0,1,3],402:[0,1,3],403:[0,2,3],404:[0,1,3],405:[0,1,3],406:[0,1,3],407:[0,1,3],408:[0,1,3],409:[0,1,2],410:[0,1,2],
411:[0,1,3],412:[0,1,2],413:[0,1,2],414:[0,1,2],415:[0,1,2],416:[0,1,3],417:[0,1,2],418:[0,1,3],419:[0,1,3],420:[0,1,3],
421:[0,1,3],422:[0,1,3],423:[0,1,2],424:[0,1,3],425:[0,1,3],426:[0,1,2],427:[0,1,2],428:[0,1,2],429:[0,1,3],430:[0,1,2],
431:[0,1,2],432:[0,1,3],433:[0,1,2],434:[0,1,3],435:[0,1,2],436:[0,1,3],437:[0,1,2],438:[0,1,2],439:[0,1,2],440:[0,1,3],
441:[0,1,2],442:[0,1,2],443:[0,1,3],444:[0,1,2],445:[0,1,3],446:[0,1,2],447:[0,1,3],448:[0,1,3],449:[0,1,3],450:[0,1,2],
451:[0,1,3],452:[0,1,3],453:[0,1,2],454:[0,1,3],455:[0,2,3],456:[0,1,2],457:[0,1,3],458:[0,2,3],459:[0,1,3],460:[0,1,3],
461:[0,1,3],462:[0,1,3],463:[0,1,2],464:[0,1,2],465:[0,1,2],466:[0,1,2],467:[0,2,3],468:[0,1,3],469:[0,1,3],470:[0,1,2]
}

QUESTION_OVERRIDES={
403:{
'es':['¿Por qué conviene dejar enfriar la placa y retirar la grasa suelta primero?','¿Qué hago si la grasa no sale con la primera aplicación?','¿Puedo encender la placa si aún queda producto de limpieza?'],
'en':['Why should I let the cooktop cool and remove loose grease first?','What should I do if baked-on grease does not come off the first time?','Can I heat the cooktop if cleaner residue remains?']},
418:{
'es':['¿Qué recurso hace que una fila de hormigas siga regresando?','¿Por qué no conviene depender solo de aerosoles sobre la fila de hormigas?','¿Cuándo conviene pasar de limpieza y sellado a un control dirigido?'],
'en':['What resource keeps an ant trail active?','Why should I not rely only on spraying the visible ant trail?','When should I move from sanitation and sealing to targeted control?']},
446:{
'es':['¿Por qué un purificador solo reduce el polvo que pasa por el aparato?','¿Por qué seguiré viendo polvo sobre los muebles?','¿Cómo sé si un purificador tiene capacidad suficiente para la habitación?'],
'en':['Why can an air purifier only reduce dust that passes through the unit?','Why will I still see dust on furniture?','How can I tell whether a purifier is large enough for the room?']}
}

seen=[]
for p in sorted(TOOLS.glob('batch-391-470-*.json')):
    rows=json.loads(p.read_text(encoding='utf-8'))
    changed=False
    for r in rows:
        n=r['n']; seen.append(n)
        expected=FAQ_MAP.get(n)
        if expected is None:
            raise SystemExit(f'No reviewed FAQ map for #{n}')
        if r.get('faq_sections')!=expected:
            r['faq_sections']=expected; changed=True
        if n in QUESTION_OVERRIDES:
            for lang in ('es','en'):
                key=f'faq_{lang}'
                if r.get(key)!=QUESTION_OVERRIDES[n][lang]:
                    r[key]=QUESTION_OVERRIDES[n][lang]; changed=True
    if changed:
        p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if sorted(seen)!=list(range(391,471)):
    raise SystemExit(f'Expected exact 391-470 batch coverage, got {len(seen)} topics')
print('Applied hand-reviewed FAQ section map to all 80 HOME topics')
