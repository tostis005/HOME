#!/usr/bin/env python3
from pathlib import Path
import json, re

ROOT=Path(__file__).resolve().parent
EXTRA={
 (242,'es'):' Si quedan vetas después de secar, no añadas más producto: repasa con una mopa apenas húmeda y agua limpia, porque el exceso de limpiador puede dejar una película difícil de retirar.',
 (242,'en'):' If streaks remain after drying, do not add more product. Make a final pass with a barely damp mop and clean water, because excess cleaner can leave a film that attracts more soil.',
 (243,'es'):' En zonas de mucho paso, coloca protectores bajo muebles y limpia arena o gravilla pronto; esas partículas actúan como abrasivo y pueden marcar la capa de uso incluso cuando el producto de limpieza sea correcto.',
 (244,'en'):' For grout lines, use a separate soft brush and a cleaner compatible with both grout and tile. Avoid assuming that a product safe for ceramic tile is automatically suitable for natural stone or specialty grout.',
 (255,'en'):' Sealing gaps before the seasonal influx is more effective than repeatedly vacuuming adults indoors. Check sunny exterior walls, window trim, attic penetrations, and damaged screens while weather is still mild enough for repair.',
 (266,'es'):' Si las cortinas son muy grandes, dividir la carga reduce arrugas y esfuerzo sobre costuras y motor. Comprueba también que el peso mojado no supere lo permitido por la lavadora doméstica.',
 (266,'en'):' For very large curtains, splitting the load reduces wrinkling and stress on seams and the washer. Also consider how heavy the fabric becomes when wet before deciding that a home machine is suitable.',
 (267,'es'):' Si el borde inferior vuelve a ensuciarse enseguida, revisa también ventilación y si la cortina queda pegada a la bañera húmeda; limpiar sin mejorar el secado hace que el problema reaparezca rápido.',
 (267,'en'):' If the lower edge becomes dirty again quickly, also check ventilation and whether the liner stays pressed against a wet tub. Cleaning without improving drying conditions leads to fast recurrence.',
 (268,'en'):' A simple inspection log helps in tree-heavy properties: note when gutters were cleared and what debris was present. That makes the next interval evidence-based instead of relying on an arbitrary twice-a-year rule.',
 (270,'en'):' During a moderate rain, observing the system from the ground can be informative: note whether overflow begins at one outlet, a sagging section, or the entire run. Do not climb a ladder while gutters are wet.',
 (272,'es'):' Deja una pequeña zona para productos abiertos o que deben consumirse pronto. Separarlos del inventario de reserva evita que queden ocultos detrás de envases nuevos y reduce desperdicio.',
 (273,'en'):' If yellowing began soon after repotting, moving the plant, or changing the watering schedule, that timing is valuable evidence. Give corrected conditions time to work before stacking several new treatments at once.',
 (291,'en'):' Do not crowd a deep container with multiple wet layers of berries. A shallow layer or breathable original container usually makes it easier to spot condensation and remove a failing berry before it affects the rest.',
 (293,'en'):' Quality loss becomes more noticeable in lean meats, bread, and exposed surfaces because dry air pulls moisture from unprotected food. Double wrapping or removing excess package air slows that dehydration during longer storage.',
 (296,'es'):' Si el filtro vuelve a llenarse de restos muy rápido, revisa la carga: platos que bloquean brazos rociadores o grandes cantidades de comida sólida pueden aumentar lo que llega al filtro y empeorar el resultado.',
 (296,'en'):' If the filter fills with debris again very quickly, review loading habits. Dishes that block spray arms or large amounts of solid food can increase what reaches the filter and reduce cleaning performance.',
 (303,'es'):' Para transporte, una bolsa térmica con acumuladores de frío ayuda a mantener la carne fuera de la zona de peligro. Al llegar, refrigera o congela de inmediato en vez de dejar la compra mientras haces otras tareas.',
 (305,'en'):' Large pots of rice cool slowly in the center. Divide leftovers into shallow containers rather than placing one deep, tightly packed mass in the refrigerator and assuming the outside temperature represents the whole batch.',
 (308,'es'):' En manchas antiguas de aceite, trabaja por ciclos cortos de absorción, limpiador y aclarado en vez de inundar la zona. El hormigón es poroso y una mancha profunda puede necesitar varias aplicaciones moderadas.',
 (308,'en'):' For old oil stains, work in short cycles of absorption, cleaner, scrubbing, and rinsing rather than flooding the area. Concrete is porous, so a deep stain may need several moderate treatments instead of one aggressive pass.',
 (309,'es'):' Después de limpiar, espera a que la madera alcance un secado adecuado antes de decidir si necesita sellador. Encerrar humedad bajo un acabado puede provocar mala adherencia y deterioro prematuro.',
 (309,'en'):' After cleaning, let the wood dry adequately before deciding whether it needs stain or sealer. Trapping moisture beneath a finish can cause poor adhesion and shorten the life of the coating.',
 (285,'es'):' Deja de usar el enchufe y cualquier aparato conectado hasta que se identifique la causa del sobrecalentamiento; cambiar de clavija o mover la carga a otro punto no convierte ese receptáculo en seguro.'
}

for p in sorted(ROOT.glob('batch-*.json')):
    m=re.fullmatch(r'batch-(\d+)-(\d+)\.json',p.name)
    if not m: continue
    a,b=map(int,m.groups())
    if b<231 or a>310: continue
    data=json.loads(p.read_text(encoding='utf-8'))
    changed=False
    for item in data:
        n=int(item['n'])
        for lang,idx in [('es',2),('en',3)]:
            extra=EXTRA.get((n,lang))
            if not extra: continue
            if extra.strip() not in item['sections'][-1][idx]:
                item['sections'][-1][idx]=item['sections'][-1][idx].rstrip()+extra
                changed=True
    if changed:
        p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
        print('uplifted',p.name)
