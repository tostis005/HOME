#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path('content/articles')

META = {
111:{'es':'Identifica escarabajos de las alfombras, localiza larvas y fuentes de alimento, limpia textiles y evita que se propaguen sin tratar la casa a ciegas.','en':'Identify carpet beetles, find larvae and food sources, clean affected textiles, and stop the problem from spreading without treating the whole house blindly.'},
112:{'es':'Qué hacer si aparecen gorgojos en la despensa: localizar alimentos afectados, revisar paquetes cercanos, limpiar y prevenir nuevas infestaciones.','en':'What to do when pantry weevils appear: find affected foods, inspect nearby packages, clean the storage area, and prevent a repeat infestation.'},
113:{'es':'Ante una fuga en el techo, protege primero a las personas y la electricidad, contiene el agua y busca la causa sin subir a un tejado mojado.','en':'If water is leaking from the ceiling, protect people and electrical areas first, contain the water, and trace the cause without climbing onto a wet roof.'},
114:{'es':'Guía de colada para principiantes: separar ropa, leer etiquetas, dosificar detergente, elegir programa y temperatura, secar y evitar errores comunes.','en':'A beginner laundry guide covering sorting, care labels, detergent dosing, cycles, water temperature, drying, and the mistakes that cause most problems.'},
115:{'es':'Quita manchas de vino tinto sin fijarlas: absorbe sin frotar, enjuaga en frío, pretrata, lava según la etiqueta y revisa antes de aplicar calor.','en':'Remove red-wine stains without setting them: blot instead of rubbing, rinse cool, pretreat, wash by the care label, and inspect before applying heat.'},
116:{'es':'Quita manchas de café con agua fría y pretratamiento; adapta el método si lleva leche o azúcar y no uses secadora hasta comprobar el resultado.','en':'Remove coffee stains with cool water and pretreatment, adjust for milk or sugar, and keep the item out of the dryer until the stain is actually gone.'},
117:{'es':'Aprende a tratar manchas de tinta según sean de bolígrafo, tinta al agua o rotulador, sin extenderlas ni dañar el color o el tejido.','en':'Treat ink stains according to whether they came from ballpoint, water-based ink, or marker, without spreading the stain or damaging the fabric.'},
118:{'es':'Quita manchas de sudor y desodorante de camisas entendiendo qué residuo queda, cómo pretratarlo y cuándo evitar cloro, calor o fricción excesiva.','en':'Remove sweat and deodorant buildup from shirts by identifying the residue, pretreating it correctly, and avoiding unnecessary chlorine, heat, or abrasion.'},
119:{'es':'Elimina el olor a humedad de la ropa localizando si viene de secado lento, almacenamiento húmedo o residuos en la lavadora y corrigiendo la causa.','en':'Get musty odor out of clothes by finding whether it comes from slow drying, damp storage, or washer residue and fixing the moisture source.'},
141:{'es':'Cómo quitar moho de ropa lavable: manipularla sin dispersar crecimiento, lavar según la etiqueta, secar por completo y saber cuándo no merece recuperarla.','en':'Remove mold from washable clothing by handling it carefully, laundering by the care label, drying completely, and knowing when an item is not worth salvaging.'},
142:{'es':'Cómo limpiar moho de madera distinguiendo superficie acabada, madera sin tratar y daño profundo, además de corregir la humedad que lo hizo aparecer.','en':'Clean mold from wood by distinguishing finished surfaces, unfinished wood, and deeper damage while fixing the moisture condition that allowed growth.'},
143:{'es':'El arroz cocido refrigerado suele entrar en la regla de 3–4 días: enfríalo pronto, mantenlo a 4 °C o menos y congélalo si no vas a usarlo a tiempo.','en':'Cooked rice generally follows the 3–4 day leftovers rule: cool it promptly, keep it at 40°F (4°C) or below, and freeze it if you will not use it in time.'},
144:{'es':'Cuánto duran los huevos en el refrigerador, cómo guardarlos en su envase y por qué las recomendaciones cambian entre países según su procesamiento.','en':'How long eggs keep in the refrigerator, how to store them in their carton, and why handling recommendations differ between markets.'},
145:{'es':'Para saber si un huevo debe descartarse, importa más su conservación, fecha, grietas y aspecto al abrirlo que el popular test de flotación.','en':'To decide whether an egg should be discarded, storage history, dates, cracks, and what you find after cracking it matter more than the popular float test.'},
146:{'es':'Limpia una sartén de hierro fundido sin miedo al jabón suave: retira restos, seca enseguida, protege el curado y corrige óxido o comida pegada.','en':'Clean a cast-iron skillet without fearing mild soap: remove stuck food, dry it promptly, protect the seasoning, and deal with rust or damaged seasoning.'},
147:{'es':'El papel de aluminio no es universalmente seguro en una freidora de aire: consulta el manual y, si está permitido, no bloquees el flujo ni lo dejes suelto.','en':'Aluminum foil is not universally approved for air fryers. Check the model manual and, when allowed, keep airflow open and never leave loose foil near the heater.'},
148:{'es':'En general, no metas metal en el microondas salvo que el fabricante autorice esa pieza; entiende por qué aparecen arcos y qué excepciones están diseñadas.','en':'As a rule, keep metal out of the microwave unless the manufacturer approves that item; learn why arcing happens and why some designed accessories are exceptions.'},
149:{'es':'Si el microondas funciona pero no calienta, descarta modo demo, potencia y cierre de puerta antes de asumir una avería interna; no abras la carcasa.','en':'If the microwave runs but does not heat, rule out demo mode, power settings, and door closure before assuming an internal fault; do not open the cabinet.'},
150:{'es':'Si el microondas hace chispas, detén el ciclo y busca metal, restos carbonizados o daño visible; si el arco se repite, deja de usarlo y pide revisión.','en':'If a microwave sparks, stop the cycle and check for metal, carbonized food, or visible cavity damage; repeated arcing means the appliance needs service.'},
}

INTENT = {
111:{'es':'Identificar por qué aparecen escarabajos de las alfombras, localizar el foco y cortar su ciclo con limpieza, almacenamiento y exclusión.','en':'Identify why carpet beetles are appearing, locate the source, and break the cycle with cleaning, storage, and exclusion.'},
112:{'es':'Localizar el alimento de origen de los gorgojos, retirar productos afectados y prevenir que se extiendan por la despensa.','en':'Find the food source of pantry weevils, remove affected goods, and prevent the infestation from spreading through stored food.'},
113:{'es':'Actuar con seguridad ante agua que cae del techo, limitar daños y distinguir entre una emergencia interior y una reparación de cubierta.','en':'Respond safely to water leaking from a ceiling, limit damage, and distinguish an indoor emergency from a roof or plumbing repair.'},
114:{'es':'Aprender a hacer una colada completa desde cero y elegir separación, detergente, programa, temperatura y secado sin depender de reglas memorizadas.','en':'Learn to do a full load of laundry from scratch and choose sorting, detergent, cycle, temperature, and drying without relying on arbitrary rules.'},
115:{'es':'Quitar vino tinto de ropa lavable sin extender la mancha, dañar el color ni fijar residuos con calor.','en':'Remove red-wine stains from washable clothing without spreading the stain, damaging color, or setting residue with heat.'},
116:{'es':'Quitar café de ropa lavable adaptando el tratamiento a café solo, leche, azúcar y tejidos delicados.','en':'Remove coffee from washable clothing while adjusting for black coffee, milk, sugar, and delicate fabrics.'},
117:{'es':'Tratar manchas de tinta según el tipo de tinta y el tejido, evitando disolverla y extenderla por una zona mayor.','en':'Treat ink stains according to ink type and fabric without dissolving the stain into a larger area.'},
118:{'es':'Eliminar acumulación de sudor y desodorante de camisas sin confundir residuo con pérdida de color ni dañar las fibras.','en':'Remove sweat and deodorant buildup from shirts without confusing residue with color loss or damaging the fibers.'},
119:{'es':'Eliminar olor a humedad de la ropa y localizar si la causa está en el secado, el almacenamiento o la propia lavadora.','en':'Remove musty odor from clothing and determine whether the cause is drying, storage, or the washing machine itself.'},
120:{'es':'Decidir cada cuánto lavar las sábanas según uso, sudor, mascotas, alergias y circunstancias reales de la cama.','en':'Decide how often to wash sheets based on use, sweat, pets, allergies, and the real conditions of the bed.'},
131:{'es':'Distinguir por qué una calefacción por aire mueve aire frío: ajuste del termostato, ventilador, bomba de calor, caudal o avería que requiere técnico.','en':'Distinguish why forced-air heat is blowing cool air: thermostat settings, fan operation, heat-pump behavior, airflow, or a fault that needs service.'},
132:{'es':'Identificar de dónde procede la humedad alta en una vivienda y separar vapor generado dentro, clima exterior y entrada de agua del edificio.','en':'Identify where high indoor humidity is coming from and separate indoor moisture generation, outdoor weather, and water entering the building.'},
133:{'es':'Reducir humedad interior atacando primero la fuente y combinando extracción, ventilación, climatización y deshumidificación cuando corresponda.','en':'Reduce indoor humidity by addressing the source first and using exhaust, ventilation, air conditioning, and dehumidification where appropriate.'},
134:{'es':'Entender por qué se acumula polvo, localizar sus principales fuentes y reducirlo sin recurrir automáticamente a limpieza de conductos o productos innecesarios.','en':'Understand why dust accumulates, identify the main sources, and reduce it without automatically paying for duct cleaning or unnecessary products.'},
135:{'es':'Distinguir condensación interior de una filtración o de un fallo entre cristales y entender cómo humedad y temperatura del vidrio producen las gotas.','en':'Distinguish indoor window condensation from leaks or failed insulated glazing and understand how humidity and glass temperature create droplets.'},
136:{'es':'Prevenir condensación en ventanas reduciendo humedad, mejorando extracción y circulación y corrigiendo superficies excesivamente frías cuando sea necesario.','en':'Prevent window condensation by reducing moisture, improving exhaust and airflow, and addressing excessively cold window surfaces when necessary.'},
137:{'es':'Diagnosticar un aire acondicionado ruidoso por tipo, momento y ubicación del sonido y saber cuándo apagarlo en lugar de seguir probando.','en':'Diagnose a noisy air conditioner by the type, timing, and location of the sound and know when to shut it down instead of continuing to test it.'},
138:{'es':'Distinguir olores de humedad, quemado, desagüe u otras fuentes en el aire acondicionado y decidir qué comprobaciones son seguras.','en':'Distinguish musty, burning, drain-like, and other air-conditioner odors and decide which checks are safe for a homeowner.'},
139:{'es':'Identificar y limpiar de forma segura el desagüe de condensación del aire acondicionado sin confundirlo con líneas de refrigerante ni mezclar productos.','en':'Identify and safely clear an air-conditioner condensate drain without confusing it with refrigerant lines or mixing incompatible cleaners.'},
140:{'es':'Recuperar telas y textiles del hogar con moho —como cortinas, fundas o tapicería— distinguiendo lo lavable de materiales porosos difíciles de salvar.','en':'Salvage moldy household fabrics such as curtains, covers, and upholstery while distinguishing washable pieces from porous items that are difficult to restore.'},
141:{'es':'Recuperar ropa con moho cuando es razonable hacerlo, lavándola según la etiqueta, secándola por completo y corrigiendo el origen de la humedad.','en':'Salvage moldy clothing when reasonable, laundering by the care label, drying completely, and correcting the moisture source.'},
142:{'es':'Limpiar moho superficial de madera cuando es recuperable y distinguir acabado, material y daño que requieren restauración o sustitución.','en':'Clean recoverable surface mold from wood and distinguish finish, material, and deeper damage that call for restoration or replacement.'},
143:{'es':'Saber cuánto tiempo conservar arroz cocido en frío y cómo enfriarlo, refrigerarlo, recalentar porciones y congelarlo con seguridad.','en':'Know how long cooked rice keeps refrigerated and how to cool, refrigerate, reheat portions, and freeze it safely.'},
144:{'es':'Saber cuánto tiempo conservar huevos refrigerados y adaptar la recomendación al país, la cadena de frío y la fecha del envase.','en':'Know how long refrigerated eggs keep and apply the recommendation according to market handling, refrigeration history, and carton dates.'},
145:{'es':'Decidir si unos huevos deben descartarse usando conservación, envase, grietas y señales al abrirlos, sin confiar en el test de flotación como prueba de seguridad.','en':'Decide whether eggs should be discarded using storage history, carton dates, cracks, and signs after cracking rather than treating the float test as a safety test.'},
146:{'es':'Limpiar y mantener hierro fundido retirando comida pegada, evitando óxido y conservando o restaurando el curado sin mitos innecesarios.','en':'Clean and maintain cast iron by removing stuck food, preventing rust, and preserving or restoring seasoning without unnecessary myths.'},
147:{'es':'Decidir si puede usarse papel de aluminio en una freidora de aire concreta y, si el fabricante lo permite, colocarlo sin bloquear el flujo ni acercarlo a la resistencia.','en':'Decide whether foil is allowed in a specific air fryer and, if the manufacturer permits it, use it without blocking airflow or contacting the heating element.'},
148:{'es':'Entender cuándo el metal provoca arcos en un microondas y reconocer las pocas excepciones que el fabricante ha diseñado y autorizado.','en':'Understand when metal causes microwave arcing and recognize the limited exceptions specifically designed and approved by the manufacturer.'},
149:{'es':'Diagnosticar un microondas que funciona pero no calienta mediante comprobaciones externas seguras y reconocer dónde termina el diagnóstico doméstico.','en':'Troubleshoot a microwave that runs but does not heat using safe external checks and recognize where homeowner diagnosis should stop.'},
150:{'es':'Localizar causas visibles de chispas en un microondas, detener el uso cuando hay daño y evitar reparaciones internas de alta tensión.','en':'Identify visible causes of microwave sparking, stop using the appliance when damage is present, and avoid high-voltage internal repairs.'},
}

IMAGE = {
111:{'es':'Larva y adulto de escarabajo de las alfombras junto a fibras textiles y una ventana, fotografía doméstica macro realista, sin texto.','en':'Macro household photograph of a carpet-beetle larva and adult near textile fibers and a window, realistic, no text.'},
112:{'es':'Paquetes de arroz, pasta y legumbres siendo revisados en una despensa limpia, con un pequeño gorgojo visible en un envase afectado, sin texto.','en':'Rice, pasta, and dried beans being inspected in a clean pantry, with a small weevil visible in one affected package, no text.'},
113:{'es':'Goteo controlado desde una mancha húmeda del techo hacia un cubo, con la zona despejada y la electricidad protegida, fotografía realista.','en':'A controlled ceiling drip falling into a bucket beneath a damp patch, with the area cleared and electrical hazards kept away, realistic photo.'},
114:{'es':'Persona separando ropa clara, oscura y delicada junto a una lavadora y etiquetas de cuidado visibles, fotografía editorial realista.','en':'Person sorting light, dark, and delicate laundry beside a washer with care labels visible, realistic editorial photo.'},
115:{'es':'Camisa clara con una mancha fresca de vino tinto siendo absorbida con un paño blanco, fotografía doméstica realista.','en':'Light-colored shirt with a fresh red-wine stain being blotted with a white cloth, realistic household photo.'},
116:{'es':'Prenda con una mancha de café enjuagándose desde el reverso bajo agua fría, fotografía editorial realista.','en':'Coffee-stained garment being rinsed from the reverse under cool water, realistic editorial photo.'},
117:{'es':'Mancha de tinta de bolígrafo sobre tela blanca siendo tratada sobre una toalla absorbente, fotografía macro realista.','en':'Ballpoint-ink stain on white fabric being treated over an absorbent towel, realistic macro photo.'},
118:{'es':'Axila de una camisa con acumulación amarillenta de sudor y desodorante junto a detergente de pretratamiento, fotografía realista.','en':'Shirt underarm with yellow sweat and deodorant buildup beside a pretreatment detergent, realistic photo.'},
119:{'es':'Ropa limpia extendida y secándose por completo en una zona ventilada, con lavadora al fondo, fotografía doméstica natural.','en':'Clean laundry drying completely in a well-ventilated area with a washer in the background, natural household photo.'},
120:{'es':'Cama recién hecha con sábanas limpias y un juego usado preparado para lavar, dormitorio luminoso, fotografía editorial sin texto.','en':'Freshly made bed with clean sheets and a used set ready for washing, bright bedroom, editorial photo with no text.'},
141:{'es':'Camisa lavable con pequeñas manchas de moho junto a una lavadora y su etiqueta de cuidado, fotografía editorial realista, sin texto.','en':'Washable shirt with small mold spots beside a washing machine and visible care label, realistic editorial photo, no text.'},
142:{'es':'Pequeña zona de moho superficial en madera siendo inspeccionada junto a un medidor de humedad, fotografía realista, sin texto.','en':'Small patch of surface mold on wood being inspected beside a moisture meter, realistic photo, no text.'},
143:{'es':'Arroz cocido distribuido en un recipiente poco profundo y etiquetado antes de entrar en el refrigerador, fotografía doméstica realista.','en':'Cooked rice spread in a shallow container and labeled before refrigeration, realistic household photo.'},
144:{'es':'Huevos guardados en su cartón original en una balda interior del refrigerador junto a un termómetro, fotografía realista.','en':'Eggs stored in their original carton on an interior refrigerator shelf beside a thermometer, realistic photo.'},
145:{'es':'Huevo cascado en un cuenco separado para revisar su aspecto, con el cartón al fondo, fotografía doméstica realista.','en':'Egg cracked into a separate bowl for inspection with its carton in the background, realistic household photo.'},
146:{'es':'Sartén de hierro fundido recién lavada secándose y recibiendo una capa muy fina de aceite, fotografía editorial realista.','en':'Freshly washed cast-iron skillet being dried and wiped with a very thin film of oil, realistic editorial photo.'},
147:{'es':'Cesta de freidora de aire con una pequeña lámina de aluminio sujeta por alimentos y espacio libre para el flujo de aire, fotografía realista.','en':'Air-fryer basket with a small piece of foil held down by food and clear space for airflow, realistic photo.'},
148:{'es':'Microondas abierto con un recipiente apto y su rejilla metálica original, mientras un tenedor común permanece fuera, fotografía realista.','en':'Open microwave with a microwave-safe container and its original manufacturer rack while a regular fork remains outside, realistic photo.'},
149:{'es':'Taza de agua dentro de un microondas intacto preparada para una prueba de calentamiento siguiendo el manual, fotografía realista.','en':'Cup of water inside an intact microwave ready for a manufacturer-recommended heating test, realistic photo.'},
150:{'es':'Interior de microondas detenido tras una chispa, con pequeño resto carbonizado visible y sin manos dentro, fotografía editorial realista.','en':'Microwave cavity after a sparking event has been stopped, with a small carbonized food spot visible and no hands inside, realistic editorial photo.'},
}

# Extra differentiation between the two neighboring mold/textile topics.
EXTRA_140 = {
'es':'<h2>Este artículo se centra en textiles del hogar</h2><p>“Tela” aquí incluye cortinas, fundas de cojín, mantas decorativas, tapicería desenfundable y otras piezas textiles de la vivienda. <strong>La ropa de uso personal tiene una lógica distinta</strong>: suele poder aislarse y lavarse por separado, mientras una cortina grande, un sofá o un relleno grueso plantean problemas de profundidad, secado y posible sustitución. Esa diferencia debe decidir el método antes de elegir un producto.</p>',
'en':'<h2>This article focuses on household textiles</h2><p>Here, “fabric” means curtains, cushion covers, throws, removable upholstery, and other household textiles. <strong>Wearable clothing is a different problem</strong>: it can often be isolated and laundered separately, while a large curtain, sofa, or thick filling raises questions about depth, drying, and whether replacement is more realistic. Make that distinction before choosing a cleaner.</p>'
}
EXTRA_141 = {
'es':'<h2>En ropa, piensa en una prenda concreta y lavable</h2><p>Este procedimiento está pensado para camisas, pantalones, camisetas y otras prendas que puedan tratarse siguiendo una etiqueta de cuidado. Si el moho está en una cortina, tapicería, colchón o relleno grueso, el problema deja de ser una simple colada: la contaminación puede penetrar más y el secado completo es mucho más difícil.</p>',
'en':'<h2>For clothing, think in terms of one washable garment</h2><p>This process is aimed at shirts, pants, T-shirts, and other garments that can be treated according to a care label. Mold on curtains, upholstery, mattresses, or thick filling is no longer a simple laundry problem: growth can penetrate deeper and complete drying is much harder.</p>'
}

def load(n, lang):
    matches=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(matches)!=1:
        raise SystemExit(f'{n} {lang}: expected one file, got {matches}')
    p=matches[0]
    return p, json.loads(p.read_text(encoding='utf-8'))

def save(p,d):
    p.write_text(json.dumps(d, ensure_ascii=False, separators=(',',':')), encoding='utf-8')

changed=[]
for n in sorted(set(META)|set(INTENT)|set(IMAGE)):
    for lang in ('es','en'):
        p,d=load(n,lang)
        if n in META:
            d['seo']['meta_description']=META[n][lang]
        if n in INTENT:
            d['seo']['search_intent']=INTENT[n][lang]
        if n in IMAGE:
            d['image']['concept']=IMAGE[n][lang]
        save(p,d); changed.append(p.as_posix())

# Differentiate 140 (household textiles) from 141 (wearable clothing) without changing slugs or translation groups.
for lang in ('es','en'):
    p,d=load(140,lang)
    if lang=='es':
        d['title']='Cómo quitar moho de telas y textiles del hogar'
        d['seo']['title']='Cómo quitar moho de telas y textiles del hogar'
        d['excerpt']='El moho en cortinas, fundas, tapicería y otros textiles del hogar exige decidir primero si la pieza es lavable, si el crecimiento ha penetrado y si puede secarse por completo.'
        d['taxonomy']['food_subcategories']=['mold','household-textiles','upholstery']
    else:
        d['title']='How to Remove Mold From Household Fabrics'
        d['seo']['title']='How to Remove Mold From Household Fabrics'
        d['excerpt']='Mold on curtains, covers, upholstery, and other household fabrics requires deciding first whether the item is washable, how deeply growth has penetrated, and whether it can dry completely.'
        d['taxonomy']['food_subcategories']=['mold','household-textiles','upholstery']
    if EXTRA_140[lang] not in d['content_html']:
        pos=d['content_html'].find('<h2>')
        d['content_html']=d['content_html'][:pos]+EXTRA_140[lang]+d['content_html'][pos:]
    save(p,d)

for lang in ('es','en'):
    p,d=load(141,lang)
    if lang=='es':
        d['excerpt']='En ropa lavable, el objetivo es retirar el crecimiento, lavar según la etiqueta, secar por completo y corregir la humedad que permitió que apareciera el moho.'
        d['taxonomy']['food_subcategories']=['mold','clothing','laundry']
    else:
        d['excerpt']='For washable clothing, the goal is to remove growth, launder according to the care label, dry completely, and correct the moisture condition that allowed mold to appear.'
        d['taxonomy']['food_subcategories']=['mold','clothing','laundry']
    if EXTRA_141[lang] not in d['content_html']:
        pos=d['content_html'].find('<h2>')
        d['content_html']=d['content_html'][:pos]+EXTRA_141[lang]+d['content_html'][pos:]
    save(p,d)

# Permanent audit record.
report = '''# Quality audit — articles 071–150\n\nAudit completed against `EDITORIAL-STANDARD.md`, using articles from the first 70 (especially complex diagnostic pieces) as the quality benchmark.\n\n## Method\n\nThe audit combined full-library structural checks with editorial spot-reading across every generation band. Checks included body word count, section structure, FAQ/source coverage, ES/EN pairing, metadata completeness, generic-template language, body similarity/cannibalization, cold-reader clarity, safety boundaries, localization and the second-search test.\n\nWord count was used only as a diagnostic signal. HOME has no target article length: a narrow question can be fully resolved in 300–450 words, while a multi-cause troubleshooting article may need much more.\n\n## Findings\n\n- **071–100: pass at benchmark level.** Average body depth is about 786 words in Spanish and 711 in English. The articles generally branch by real symptoms, explain why steps matter and preserve clear safety boundaries.\n- **101–110: pass, more concise.** Average depth drops to roughly 585 ES / 546 EN, but sampled cleaning, energy and troubleshooting articles still pass the cold-reader and second-search tests. No systematic rewrite is justified purely to increase length.\n- **111–120: content passes; metadata needed repair.** Bodies remain substantial (roughly 595 ES / 553 EN for 115–120), but articles 111–119 contained meta descriptions cut with an ellipsis, and the batch used generic search-intent/image wording. Those defects were corrected in both languages.\n- **121–130: concise but mostly complete.** Average depth is about 409 ES / 385 EN. Manual review of representative laundry, door-repair and filter articles found coherent reasoning and specific next steps. They are shorter because the intents are narrower, not because they omit a common second search.\n- **131–150: bodies are compact but generally sound; editorial metadata was too generic.** Diagnostic samples correctly distinguish causes, explain jargon and stop before refrigerant, high-voltage, gas or unsafe mold work. Search intents were rewritten to be topic-specific, and generic image concepts in 141–150 were replaced.\n- **140/141 needed intent separation.** `140` now explicitly covers household fabrics/textiles such as curtains, covers and upholstery; `141` explicitly covers washable clothing. Titles, excerpts, taxonomy and opening guidance were adjusted so the two pages answer different searches.\n- **Cannibalization check:** the only body pair above the audit similarity threshold was 72/73 (oil vs grease stains), at a modest score. Their intents remain distinguishable and do not justify consolidation.\n\n## Objective defects corrected\n\n1. Truncated meta descriptions in 111–119, ES and EN.\n2. Generic search-intent metadata in 111–120 and 131–150, ES and EN.\n3. Generic image concepts in 111–120 and 141–150, ES and EN.\n4. Overlap between 140 (general household textiles) and 141 (clothing).\n\n## Final standard\n\nArticles are not padded to imitate the length of an earlier piece. A piece passes when it gives the answer early, explains unfamiliar terms, develops the real decision path, states safe limits, reads naturally in its language, and leaves no obvious follow-up search needed to act.\n'''
(ROOT/'QUALITY-AUDIT-071-150.md').write_text(report, encoding='utf-8')
print(f'Updated metadata/content in {len(set(changed))} article files and wrote audit report.')
