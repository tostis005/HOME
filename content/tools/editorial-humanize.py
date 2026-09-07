#!/usr/bin/env python3
"""Human-language second pass for HOME articles 001–070.

This pass changes wording/localization only. It preserves identifiers, slugs,
search intent, taxonomy, sources and publishing state. It is intentionally
idempotent: running it twice must not keep expanding the same wording.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

ARTICLES = Path(__file__).resolve().parents[1] / "articles"

UNITS_ES = {
    "40 °F / 4,4 °C": "4,4 °C / 40 °F",
    "40 °F / 4.4 °C": "4,4 °C / 40 °F",
    "37 °F / 3 °C": "3 °C / 37 °F",
    "34 °F / 1 °C": "1 °C / 34 °F",
    "90 °F / 32 °C": "32 °C / 90 °F",
    "165 °F / 74 °C": "74 °C / 165 °F",
    "120 °F / 49 °C": "49 °C / 120 °F",
    "0 °F / -17,8 °C": "-17,8 °C / 0 °F",
    "0 °F / −17,8 °C": "−17,8 °C / 0 °F",
    "0 °F / -18 °C": "-18 °C / 0 °F",
    "0 °F / −18 °C": "−18 °C / 0 °F",
}

AGENCIES_ES = [
    (r"\b(?:US EPA|U\.S\. EPA|EPA)\b", "EPA", "la Agencia de Protección Ambiental de Estados Unidos (EPA)"),
    (r"\bCDC\b", "CDC", "los Centros para el Control y la Prevención de Enfermedades de Estados Unidos (CDC)"),
    (r"\bCPSC\b", "CPSC", "la Comisión de Seguridad de Productos del Consumidor de Estados Unidos (CPSC)"),
    (r"\bUSDA\b", "USDA", "el Departamento de Agricultura de Estados Unidos (USDA)"),
    (r"\bUSGS\b", "USGS", "el Servicio Geológico de Estados Unidos (USGS)"),
    (r"\bDOE\b", "DOE", "el Departamento de Energía de Estados Unidos (DOE)"),
]


def metric_first(text: str) -> str:
    for old, new in UNITS_ES.items():
        text = text.replace(old, new)
    return text


def capitalize_for_position(text: str, start: int, phrase: str) -> str:
    before = text[:start]
    sentence_start = (
        start == 0
        or before.endswith("<p>")
        or before.endswith("<li>")
        or bool(re.search(r"[.!?]\s*$", before))
    )
    return phrase[0].upper() + phrase[1:] if sentence_start else phrase


def expand_first_agencies(text: str) -> str:
    for pattern, acronym, phrase in AGENCIES_ES:
        if f"({acronym})" in text:
            continue
        match = re.search(pattern, text)
        if not match:
            continue
        replacement = capitalize_for_position(text, match.start(), phrase)
        text = text[:match.start()] + replacement + text[match.end():]

        # The full CDC name is plural in Spanish; repair common verbs that
        # were singular when the sentence subject was the acronym "CDC".
        if acronym == "CDC":
            for singular, plural in {
                "señala": "señalan",
                "recomienda": "recomiendan",
                "advierte": "advierten",
                "indica": "indican",
                "explica": "explican",
                "describe": "describen",
            }.items():
                text = text.replace(f"(CDC) {singular}", f"(CDC) {plural}", 1)
    return text


def remove_metadiscourse(text: str) -> str:
    replacements = {
        "HOME prioriza medidas de saneamiento, prevención y cuidado de la mascota antes de convertir la casa en un entorno cargado de pesticidas.":
            "Conviene priorizar la limpieza, la prevención y el cuidado de la mascota antes de recurrir a pesticidas por toda la casa.",
        "HOME prioriza confirmar, contener y entender el alcance.":
            "Lo prudente es confirmar, contener y entender el alcance antes de tratar.",
        "HOME no plantea estos artículos como instrucciones para exterminar. La prioridad es identificar riesgo, corregir condiciones de humedad y acceso y obtener una evaluación técnica.":
            "La prioridad es identificar el riesgo, corregir las condiciones de humedad y acceso y obtener una evaluación técnica, no improvisar un tratamiento químico estructural.",
        "HOME prioriza medidas que hacen la vivienda menos atractiva: secar, ordenar, guardar, sellar y observar.":
            "Suele ser más útil hacer la vivienda menos atractiva: secar, ordenar, guardar, sellar y observar.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def common_spanish(text: str) -> str:
    text = metric_first(text)
    text = remove_metadiscourse(text)

    # Replace English reset jargon while retaining labels only when the user
    # may actually see them on an appliance panel.
    text = re.sub(r"\bun power cycle\b", "un reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bel power cycle\b", "el reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bpower cycle\b", "reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bfactory reset\b", "restablecimiento de fábrica", text, flags=re.I)
    text = re.sub(r"\bresetear\b", "reiniciar", text, flags=re.I)
    text = re.sub(r"\bresetea\b", "reinicia", text, flags=re.I)
    text = re.sub(r"\breseteando\b", "reiniciando", text, flags=re.I)
    text = re.sub(r"\bun reset\b", "un reinicio", text, flags=re.I)
    text = re.sub(r"\bel reset\b", "el reinicio", text, flags=re.I)

    # Terms whose English acronym adds no value in normal Spanish prose.
    text = re.sub(r"\bsistema HVAC\b", "sistema de climatización", text, flags=re.I)
    text = re.sub(r"\bdel HVAC\b", "del sistema de climatización", text, flags=re.I)
    text = re.sub(r"\ben HVAC\b", "en el sistema de climatización", text, flags=re.I)
    text = re.sub(r"\bHVAC\b", "sistema de climatización", text)
    text = text.replace("remediación", "tratamiento profesional")

    # Explain MERV the first time without removing a label readers may need
    # when buying a replacement filter.
    if "MERV" in text and "escala MERV" not in text:
        text = text.replace("MERV", "escala MERV (que indica la capacidad del filtro para retener partículas)", 1)

    return text


def topic_specific_es(text: str, number: int) -> str:
    # Run before acronym expansion where exact source wording contains acronyms.
    if number == 10:
        text = text.replace("batería evaporadora", "serpentín interior —la parte fría por la que pasa el aire—", 1)
        text = text.replace("rejillas de impulsión", "rejillas de salida, por donde entra el aire climatizado en las habitaciones")
        text = text.replace("Haz lo mismo con los retornos", "Haz lo mismo con las rejillas de retorno, por donde el sistema vuelve a recoger el aire")
        text = text.replace("compuertas, conductos", "compuertas que regulan el paso del aire, conductos")
        text = text.replace("bobinas sucias", "serpentines sucios")
        text = text.replace("condensadores o contactores", "condensadores eléctricos o contactores —componentes internos del sistema de arranque—")
        text = text.replace("<h2>El diagnóstico doméstico debería terminar donde empieza el riesgo</h2>", "<h2>Hasta dónde merece la pena llegar por tu cuenta</h2>")

    elif number == 12:
        text = text.replace(
            "El estándar IICRC S300 trata precisamente la limpieza profesional de tapicerías teniendo en cuenta fibras, construcción, inspección previa, manchas y métodos de limpieza. Esa complejidad explica por qué no existe un único método correcto para cualquier sofá.",
            "La limpieza profesional de tapicerías tiene en cuenta el tipo de fibra, cómo está construido el mueble, las manchas y el método que admite el tejido. Esa variedad explica por qué no existe un único procedimiento correcto para cualquier sofá.",
        )
        text = text.replace("<h2>La regla que evita la mayoría de los daños</h2>", "<h2>Si dudas, vuelve al material antes que al producto</h2>")

    elif number == 14:
        text = text.replace("garaje, sótano, cámara sanitaria y ático", "garaje, sótano, el espacio bajo el suelo de algunas viviendas (cámara sanitaria) y ático")

    elif number == 16:
        text = text.replace("un respirador N95 correctamente utilizado", "una mascarilla filtrante N95 bien ajustada")
        text = text.replace("biocidas como la lejía", "productos biocidas —productos destinados a controlar organismos—, como la lejía")
        text = text.replace("un biocida", "un producto biocida")

    elif number == 18:
        text = text.replace("Programas como Air Only, Air Fluff, Refresh o equivalentes", "Programas sin calor —que pueden aparecer en el panel como Air Only, Air Fluff, Refresh o nombres similares—")
        text = text.replace("Un fusible térmico puede abrirse", "Un fusible térmico —una pieza de seguridad que corta el circuito si detecta demasiado calor— puede abrirse")

    elif number == 19:
        # This article already explains the North-American air-gap concept well.
        pass

    elif number == 30:
        text = text.replace("NSF ha señalado", "NSF, una organización independiente especializada en salud pública y certificación, ha señalado")

    elif number == 31:
        text = text.replace("Start/Pause, Power/Cancel o un botón equivalente", "Inicio/Pausa o Encendido/Cancelar (Start/Pause o Power/Cancel, según el panel) o un botón equivalente")
        text = text.replace("Start/Pause o Power/Cancel", "Inicio/Pausa o Encendido/Cancelar")

    elif number == 32:
        text = text.replace("Cancel/Drain o una función equivalente", "Cancelar/Desaguar (Cancel/Drain, si así aparece en el panel) o una función equivalente")
        text = text.replace("Cancel/Drain", "Cancelar/Desaguar")
        text = text.replace("Control Lock", "bloqueo de controles")
        text = text.replace("<h2>La secuencia que evita borrar pistas</h2>", "<h2>Antes de volver a intentarlo, conserva las pistas</h2>")

    elif number == 36:
        text = text.replace("Poison Control señala", "Poison Control, un servicio estadounidense de información toxicológica, señala", 1)
        text = text.replace("Poison Control advierte", "Poison Control advierte", 1)

    elif number == 38:
        text = text.replace("mosquitos del sustrato o fungus gnats", "mosquitos del sustrato (conocidos en inglés como fungus gnats)")
        text = text.replace("Los adultos de fungus gnat", "Los adultos de estos mosquitos del sustrato")
        text = text.replace("los fungus gnats", "los mosquitos del sustrato")

    elif number == 45:
        text = text.replace("un contactor o condensador defectuoso", "un contactor o un condensador eléctrico defectuoso —componentes internos que ayudan a arrancar y alimentar el equipo—")
        text = text.replace("No intentes probar condensadores", "No intentes comprobar condensadores eléctricos")
        text = text.replace("interruptor de seguridad de condensados", "interruptor de seguridad que detiene el equipo si el agua de condensación no puede evacuar")
        text = text.replace("<h2>La secuencia que ahorra tiempo</h2>", "<h2>Si has llegado hasta aquí y sigue sin arrancar</h2>")

    elif number == 46:
        text = text.replace("el serpentín interior condensa vapor de agua", "el serpentín interior —la superficie fría por la que pasa el aire— hace que parte del vapor de agua se convierta en gotas")
        text = text.replace("drenaje de condensados", "desagüe del agua de condensación")
        text = text.replace("línea de condensados", "tubo de desagüe del agua de condensación")
        text = text.replace("bomba de condensados", "bomba que evacua el agua de condensación")
        text = text.replace("bandeja primaria", "bandeja principal")
        text = text.replace("bandeja secundaria", "bandeja secundaria o de emergencia")
        text = text.replace("flotador de seguridad", "flotador de seguridad, que actúa como interruptor cuando sube demasiado el nivel de agua")

    elif number in {47, 48}:
        text = text.replace("respirador N95", "mascarilla filtrante N95")
        if number == 48:
            text = text.replace("por debajo del punto de rocío", "hasta el punto en que la humedad del aire empieza a condensarse (el llamado punto de rocío)")

    elif number == 51:
        text = text.replace("Cooling Off, Showroom o Demo", "un modo que desactiva la refrigeración para exposición (Cooling Off, Showroom o Demo, según el panel)")
        text = text.replace("<h2>Cuándo dejar de resetear</h2>", "<h2>Cuándo dejar de reiniciar</h2>")

    elif number == 52:
        text = text.replace("detergente HE", "detergente para lavadoras de alta eficiencia (HE, por sus siglas en inglés)")

    elif number == 54:
        text = text.replace("sensor, termistor, compuerta de aire", "sensor de temperatura (termistor), compuerta que regula el paso del aire")

    elif number == 58:
        text = text.replace("TDS, o sólidos disueltos totales", "sólidos disueltos totales (TDS, por sus siglas en inglés)")
        text = text.replace("un medidor de TDS", "un medidor de sólidos disueltos totales (TDS)")
        text = text.replace("grains per gallon", "granos por galón (grains per gallon, una unidad habitual en Estados Unidos)")
        text = text.replace("mg/L como CaCO3", "mg/L expresados como carbonato cálcico (CaCO3)")

    elif number == 61:
        text = text.replace("EPA WaterSense", "el programa WaterSense de la Agencia de Protección Ambiental de Estados Unidos (EPA)")
        text = text.replace("aproximadamente entre 45 y 60 psi", "aproximadamente entre 3,1 y 4,1 bar (45–60 psi)")
        text = text.replace("una válvula reductora o PRV", "una válvula reductora de presión (PRV, por sus siglas en inglés)")
        text = text.replace("un PRV sospechoso", "un regulador de presión sospechoso")
        text = text.replace("<h2>La secuencia que encuentra la causa más rápido</h2>", "<h2>Ordena las pistas antes de tocar la instalación</h2>")

    elif number == 62:
        text = text.replace("EPA WaterSense", "el programa WaterSense de la Agencia de Protección Ambiental de Estados Unidos (EPA)")
        text = text.replace("45–60 psi", "3,1–4,1 bar (45–60 psi)", 1)
        text = text.replace("WaterSense evalúa", "El programa WaterSense evalúa")
        text = text.replace("una alcachofa WaterSense", "una alcachofa certificada por WaterSense")
        text = text.replace("PRV", "regulador de presión")

    elif number == 63:
        text = text.replace("Vacation, Away, Eco", "vacaciones, ausencia o ahorro (Vacation, Away o Eco, según el panel)")
        text = text.replace("Un tankless", "Un calentador sin depósito (tankless, como puede aparecer en manuales estadounidenses)")

    elif number == 64:
        text = text.replace("Un tankless", "Un calentador sin depósito (tankless, como puede aparecer en manuales estadounidenses)")

    elif number == 65:
        text = text.replace("consumo en kilovatios-hora", "consumo en kilovatios-hora (kWh)", 1)
        text = text.replace("Auxiliary o Emergency Heat", "calor auxiliar o de emergencia (Auxiliary o Emergency Heat, según el termostato)")
        text = text.replace("<h2>La secuencia que encuentra la causa más rápido</h2>", "<h2>Cómo ordenar la investigación sin perderte en detalles</h2>")

    elif number == 67:
        text = text.replace("sótanos, cámaras sanitarias y uniones", "sótanos, espacios bajo el suelo de algunas viviendas (cámaras sanitarias) y uniones")

    elif number == 68:
        text = text.replace("un higrómetro", "un higrómetro, un pequeño medidor de humedad ambiental", 1)

    elif number == 69:
        text = text.replace("Los firebrats o pececillos de fuego", "Los pececillos de fuego (firebrats, en inglés)")

    return text


def transform_es(data: dict) -> dict:
    number = int(data["article_number"])
    text = data["content_html"]
    text = topic_specific_es(text, number)
    text = common_spanish(text)
    text = expand_first_agencies(text)
    data["content_html"] = text

    data["excerpt"] = metric_first(data["excerpt"])
    data["seo"]["meta_description"] = metric_first(data["seo"]["meta_description"])
    for item in data.get("faq", []):
        item["question"] = metric_first(item["question"])
        item["answer"] = metric_first(item["answer"])
        if number == 61:
            item["answer"] = item["answer"].replace("aproximadamente entre 45 y 60 psi", "aproximadamente entre 3,1 y 4,1 bar (45–60 psi)")
        if number == 62:
            item["answer"] = item["answer"].replace("45–60 psi", "3,1–4,1 bar (45–60 psi)", 1)
    return data


def transform_en(data: dict) -> dict:
    # English copies were already naturally localized in the audit. Only
    # remove publication metadiscourse if it exists; do not mechanically
    # rewrite otherwise-natural U.S./Canadian prose.
    text = data["content_html"]
    text = text.replace("HOME prioritizes", "A practical approach prioritizes")
    text = text.replace("HOME does not frame these articles as", "This is not intended as")
    data["content_html"] = text
    return data


def main() -> None:
    changed = []
    for language in ("es", "en"):
        for path in sorted((ARTICLES / language).glob("*.json")):
            original_text = path.read_text(encoding="utf-8")
            original = json.loads(original_text)
            data = copy.deepcopy(original)
            invariants = {k: original[k] for k in ("article_number", "translation_group", "language", "locale", "slug", "status")}

            data = transform_es(data) if language == "es" else transform_en(data)

            for key, value in invariants.items():
                if data[key] != value:
                    raise RuntimeError(f"Invariant changed in {path}: {key}")

            if data == original:
                continue

            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            changed.append(str(path.relative_to(ARTICLES.parent)))

    # Parse/validate all article JSON files after the pass.
    files = sorted(ARTICLES.glob("*/*.json"))
    if len(files) < 140:
        raise RuntimeError(f"Expected at least 140 article JSON files, found {len(files)}")
    seen = set()
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        key = (data["article_number"], data["language"])
        if key in seen:
            raise RuntimeError(f"Duplicate article/language pair: {key}")
        seen.add(key)

    print(f"Editorial humanization changed {len(changed)} files.")
    for path in changed:
        print(path)


if __name__ == "__main__":
    main()
