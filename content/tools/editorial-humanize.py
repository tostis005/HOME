#!/usr/bin/env python3
"""Second-pass editorial humanization for HOME article JSON files.

The script deliberately limits itself to language/localization edits. It preserves
article_number, translation_group, slug, taxonomy, factual recommendations,
sources and publishing status.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "articles"


def replace_first(text: str, pattern: str, replacement: str, flags: int = 0) -> str:
    return re.sub(pattern, replacement, text, count=1, flags=flags)


def expand_first_es(text: str) -> str:
    institutions = [
        (r"\bUS EPA\b|\bU\.S\. EPA\b|\bEPA\b", "Agencia de Protección Ambiental de EE. UU. (EPA)"),
        (r"\bCDC\b", "Centros para el Control y la Prevención de Enfermedades de EE. UU. (CDC)"),
        (r"\bCPSC\b", "Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC)"),
        (r"\bUSDA\b", "Departamento de Agricultura de EE. UU. (USDA)"),
        (r"\bUSGS\b", "Servicio Geológico de EE. UU. (USGS)"),
        (r"\bDOE\b", "Departamento de Energía de EE. UU. (DOE)"),
        (r"\bIICRC\b", "Instituto de Certificación de Inspección, Limpieza y Restauración (IICRC)"),
    ]
    for pattern, full in institutions:
        acronym = full.rsplit("(", 1)[-1].rstrip(")")
        if acronym in text and full not in text:
            text = replace_first(text, pattern, full)
    return text


def expand_first_en(text: str) -> str:
    institutions = [
        (r"\bU\.S\. EPA\b|\bUS EPA\b|\bEPA\b", "U.S. Environmental Protection Agency (EPA)"),
        (r"\bCDC\b", "Centers for Disease Control and Prevention (CDC)"),
        (r"\bCPSC\b", "U.S. Consumer Product Safety Commission (CPSC)"),
        (r"\bUSDA\b", "U.S. Department of Agriculture (USDA)"),
        (r"\bDOE\b", "U.S. Department of Energy (DOE)"),
        (r"\bUSGS\b", "U.S. Geological Survey (USGS)"),
    ]
    for pattern, full in institutions:
        acronym = full.rsplit("(", 1)[-1].rstrip(")")
        if acronym in text and full not in text:
            text = replace_first(text, pattern, full)
    if "HVAC" in text and "heating, ventilation and air-conditioning (HVAC)" not in text:
        text = replace_first(text, r"\bHVAC\b", "heating, ventilation and air-conditioning (HVAC)")
    return text


def localize_units_es(text: str) -> str:
    pairs = {
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
    for old, new in pairs.items():
        text = text.replace(old, new)
    return text


def plain_language_es(text: str, number: int) -> str:
    text = expand_first_es(text)
    text = localize_units_es(text)

    # Common anglicisms and repair-language friction.
    text = re.sub(r"\bun power cycle\b", "un reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bel power cycle\b", "el reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bpower cycle\b", "reinicio eléctrico", text, flags=re.I)
    text = re.sub(r"\bfactory reset\b", "restablecimiento de fábrica", text, flags=re.I)
    text = re.sub(r"\bresetear\b", "reiniciar", text, flags=re.I)
    text = re.sub(r"\bresetea\b", "reinicia", text, flags=re.I)
    text = re.sub(r"\breseteando\b", "reiniciando", text, flags=re.I)
    text = re.sub(r"\bun reset\b", "un reinicio", text, flags=re.I)
    text = re.sub(r"\bel reset\b", "el reinicio", text, flags=re.I)

    text = text.replace("biocidas como la lejía", "productos químicos destinados a eliminar microorganismos, como la lejía")
    text = text.replace("biocidas, incluida la lejía con cloro", "productos biocidas —los destinados a eliminar organismos—, incluida la lejía con cloro")
    text = text.replace("remediación", "tratamiento profesional del moho")
    text = text.replace("sistema HVAC", "sistema de climatización")
    text = text.replace("del HVAC", "del sistema de climatización")
    text = text.replace("en HVAC", "en el sistema de climatización")
    text = text.replace("moho en HVAC", "moho en el sistema de climatización")
    text = text.replace("conductos HVAC", "conductos del sistema de climatización")
    text = text.replace("condensados", "agua de condensación")
    text = text.replace("condensado", "agua condensada")

    # Known metadiscourse found in the first 70 articles.
    text = text.replace(
        "HOME prioriza medidas de saneamiento, prevención y cuidado de la mascota antes de convertir la casa en un entorno cargado de pesticidas.",
        "Conviene priorizar la limpieza, la prevención y el cuidado de la mascota antes de recurrir a pesticidas por toda la casa.",
    )
    text = text.replace(
        "HOME prioriza confirmar, contener y entender el alcance.",
        "Lo prudente es confirmar, contener y entender el alcance antes de tratar.",
    )
    text = text.replace(
        "HOME no plantea estos artículos como instrucciones para exterminar. La prioridad es identificar riesgo, corregir condiciones de humedad y acceso y obtener una evaluación técnica.",
        "La prioridad es identificar el riesgo, corregir las condiciones de humedad y acceso y obtener una evaluación técnica, no improvisar un tratamiento químico estructural.",
    )
    text = text.replace(
        "HOME prioriza medidas que hacen la vivienda menos atractiva: secar, ordenar, guardar, sellar y observar.",
        "Suele ser más útil hacer la vivienda menos atractiva: secar, ordenar, guardar, sellar y observar.",
    )

    # Topic-specific explanations where a literal global replacement would be clumsy.
    if number == 10:
        text = text.replace("batería evaporadora", "serpentín interior —la parte fría por la que pasa el aire—")
        text = text.replace("las rejillas de impulsión", "las rejillas de salida, por donde entra el aire climatizado en las habitaciones")
        text = text.replace("Haz lo mismo con los retornos", "Haz lo mismo con las rejillas de retorno, por donde el sistema vuelve a recoger el aire")
        text = text.replace("compuertas, conductos", "compuertas internas que regulan el paso del aire, conductos")
        text = text.replace("condensadores o contactores", "condensadores eléctricos o contactores (componentes internos que ayudan a arrancar y alimentar el equipo)")
        text = text.replace("<h2>El diagnóstico doméstico debería terminar donde empieza el riesgo</h2>", "<h2>Hasta dónde merece la pena llegar por tu cuenta</h2>")

    if number == 12:
        text = text.replace(
            "El estándar Instituto de Certificación de Inspección, Limpieza y Restauración (IICRC) S300 trata precisamente la limpieza profesional de tapicerías teniendo en cuenta fibras, construcción, inspección previa, manchas y métodos de limpieza.",
            "Los estándares profesionales de limpieza de tapicerías tienen en cuenta el tipo de fibra, cómo está construido el mueble, las manchas y el método de limpieza antes de aplicar producto.",
        )
        text = text.replace("<h2>La regla que evita la mayoría de los daños</h2>", "<h2>Si dudas, vuelve al material antes que al producto</h2>")

    if number == 14:
        text = text.replace("garaje, sótano, cámara sanitaria y ático", "garaje, sótano, el espacio bajo el suelo de algunas viviendas (cámara sanitaria) y ático")

    if number == 16:
        text = text.replace("10 pies cuadrados, algo menos de 1 metro cuadrado", "unos 0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("10 pies cuadrados", "0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("un respirador N95 correctamente utilizado", "una mascarilla filtrante N95 bien ajustada")
        text = text.replace("un biocida", "un producto biocida, es decir, destinado a eliminar organismos")

    if number == 18:
        text = text.replace("Programas como Air Only, Air Fluff, Refresh o equivalentes", "Programas sin calor —que pueden aparecer en el panel como Air Only, Air Fluff, Refresh o nombres similares—")
        text = text.replace("Un fusible térmico puede abrirse", "Un fusible térmico —una pieza de seguridad que corta el circuito si detecta demasiado calor— puede abrirse")

    if number in {26, 47, 48}:
        text = text.replace("10 pies cuadrados —aproximadamente 0,9 m²—", "unos 0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("10 pies cuadrados —unos 0,9 m²—", "unos 0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("10 ft² —unos 0,9 m²—", "unos 0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("10 ft², unos 0,9 m²", "unos 0,9 m² (aproximadamente 10 pies cuadrados)")
        text = text.replace("respirador N95", "mascarilla filtrante N95")
        text = text.replace("punto de rocío", "temperatura a la que la humedad del aire empieza a condensarse (punto de rocío)")

    if number == 31:
        text = text.replace("Start/Pause, Power/Cancel", "Inicio/Pausa o Encendido/Cancelar (Start/Pause o Power/Cancel, según el panel)")
        text = text.replace("Start/Pause o Power/Cancel", "Inicio/Pausa o Encendido/Cancelar")

    if number == 32:
        text = text.replace("Cancel/Drain o una función equivalente", "Cancelar/Desaguar (Cancel/Drain, si así aparece en el panel) o una función equivalente")
        text = text.replace("Cancel/Drain", "Cancelar/Desaguar")
        text = text.replace("Control Lock", "bloqueo de controles")
        text = text.replace("<h2>La secuencia que evita borrar pistas</h2>", "<h2>Antes de volver a intentarlo, conserva las pistas</h2>")

    if number == 38:
        text = text.replace("mosquitos del sustrato o fungus gnats", "mosquitos del sustrato (conocidos en inglés como fungus gnats)")
        text = text.replace("Los adultos de fungus gnat", "Los adultos de estos mosquitos del sustrato")
        text = text.replace("los fungus gnats", "los mosquitos del sustrato")
        text = text.replace("fungus gnats", "mosquitos del sustrato")

    if number == 45:
        text = text.replace("un contactor o condensador defectuoso", "un contactor o un condensador eléctrico defectuoso —componentes internos del arranque y la alimentación—")
        text = text.replace("No intentes probar condensadores", "No intentes comprobar condensadores eléctricos")
        text = text.replace("interruptor de seguridad de agua de condensación", "interruptor de seguridad que detiene el equipo cuando el agua de condensación no puede evacuar")
        text = text.replace("<h2>La secuencia que ahorra tiempo</h2>", "<h2>Si has llegado hasta aquí y sigue sin arrancar</h2>")

    if number == 46:
        text = text.replace("El serpentín interior condensa vapor de agua", "El serpentín interior —la superficie fría por la que pasa el aire— hace que parte del vapor de agua se convierta en gotas")
        text = text.replace("serpentín congelado", "serpentín interior congelado")
        text = text.replace("bandeja primaria", "bandeja principal")
        text = text.replace("bandeja secundaria", "bandeja secundaria o de emergencia")
        text = text.replace("flotador de seguridad", "flotador de seguridad, que actúa como un interruptor cuando sube demasiado el nivel de agua")

    if number == 51:
        text = text.replace("Cooling Off, Showroom o Demo", "modo de refrigeración desactivada o de exposición (Cooling Off, Showroom o Demo, según el panel)")
        text = text.replace("<h2>Cuándo dejar de resetear</h2>", "<h2>Cuándo dejar de reiniciar</h2>")

    if number == 52:
        text = text.replace("detergente HE", "detergente para lavadoras de alta eficiencia (HE, por sus siglas en inglés)")

    if number == 58:
        text = text.replace("También es diferente de TDS, o sólidos disueltos totales.", "También es diferente de los sólidos disueltos totales (TDS, por sus siglas en inglés).")
        text = text.replace("un medidor TDS", "un medidor de sólidos disueltos totales (TDS)")
        text = text.replace("grains per gallon", "granos por galón (grains per gallon, unidad habitual en EE. UU.)")
        text = text.replace("mg/L como CaCO3", "mg/L expresados como carbonato cálcico (CaCO3)")

    if number in {61, 62}:
        text = text.replace("45 a 60 psi", "aproximadamente 3,1 a 4,1 bar (45–60 psi)")
        text = text.replace("45–60 psi", "3,1–4,1 bar (45–60 psi)")
        text = text.replace("una válvula reductora o PRV", "una válvula reductora de presión (PRV, por sus siglas en inglés)")
        text = text.replace("un PRV", "un regulador de presión")
        text = text.replace("la PRV", "el regulador de presión")
        text = text.replace("EPA WaterSense", "el programa WaterSense de la agencia ambiental estadounidense")
        text = text.replace("WaterSense evalúa", "El programa WaterSense evalúa")
        text = text.replace("una alcachofa WaterSense", "una alcachofa certificada por WaterSense")
        text = text.replace("<h2>La secuencia que encuentra la causa más rápido</h2>", "<h2>Ordena las pistas antes de tocar la instalación</h2>")

    if number == 63:
        text = text.replace("Un tankless", "Un calentador sin depósito (tankless, como puede aparecer en manuales estadounidenses)")
        text = text.replace("Vacation, Away, Eco", "vacaciones, ausencia o ahorro (Vacation, Away o Eco, según el panel)")

    if number == 64:
        text = text.replace("Un tankless", "Un calentador sin depósito (tankless, como puede aparecer en manuales estadounidenses)")
        text = text.replace("Las bombas de calor", "Los calentadores con bomba de calor")

    if number == 65:
        text = text.replace("consumo en kilovatios-hora", "consumo en kilovatios-hora (kWh)")
        text = text.replace("sistema HVAC", "sistema de climatización")
        text = text.replace("Auxiliary o Emergency Heat", "calor auxiliar o de emergencia (Auxiliary o Emergency Heat, según el termostato)")
        text = text.replace("<h2>La secuencia que encuentra la causa más rápido</h2>", "<h2>Cómo ordenar la investigación sin perderte en detalles</h2>")

    if number == 66:
        text = text.replace("EPA recomienda", "La Agencia de Protección Ambiental de EE. UU. recomienda") if "Agencia de Protección Ambiental de EE. UU. (EPA)" not in text else text

    if number == 67:
        text = text.replace("cámaras sanitarias", "espacios bajo el suelo de algunas viviendas (cámaras sanitarias)")

    if number == 68:
        text = text.replace("higrómetro", "higrómetro, un pequeño medidor de humedad ambiental")

    if number == 69:
        text = text.replace("Los firebrats o pececillos de fuego", "Los pececillos de fuego (firebrats, en inglés)")

    return text


def transform_spanish(data: dict) -> dict:
    number = int(data["article_number"])
    data["content_html"] = plain_language_es(data["content_html"], number)

    # Localize numeric units in reader-facing summary fields without expanding agency names there.
    for key in ("excerpt",):
        data[key] = localize_units_es(data[key])
    data["seo"]["meta_description"] = localize_units_es(data["seo"]["meta_description"])
    for item in data.get("faq", []):
        item["question"] = localize_units_es(item["question"])
        item["answer"] = localize_units_es(item["answer"])
        item["answer"] = item["answer"].replace("45–60 psi", "3,1–4,1 bar (45–60 psi)")
        item["answer"] = item["answer"].replace("45 a 60 psi", "aproximadamente 3,1 a 4,1 bar (45–60 psi)")
    return data


def transform_english(data: dict) -> dict:
    data["content_html"] = expand_first_en(data["content_html"])
    data["content_html"] = data["content_html"].replace(
        "HOME prioritizes", "A practical approach prioritizes"
    )
    return data


def main() -> None:
    changed = []
    remaining_meta = []

    for language in ("es", "en"):
        for path in sorted((ROOT / language).glob("*.json")):
            original_text = path.read_text(encoding="utf-8")
            data = json.loads(original_text)
            invariants = {
                key: data[key]
                for key in ("article_number", "translation_group", "language", "locale", "slug", "status")
            }

            if language == "es":
                data = transform_spanish(data)
            else:
                data = transform_english(data)

            for key, value in invariants.items():
                if data[key] != value:
                    raise RuntimeError(f"Invariant changed in {path}: {key}")

            if "HOME " in data.get("content_html", ""):
                remaining_meta.append(str(path.relative_to(ROOT.parent)))

            new_text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
            if new_text != original_text:
                path.write_text(new_text, encoding="utf-8")
                changed.append(str(path.relative_to(ROOT.parent)))

    # Validate every JSON after rewriting.
    for path in ROOT.glob("*/*.json"):
        json.loads(path.read_text(encoding="utf-8"))

    print(f"Editorial humanization changed {len(changed)} files.")
    for path in changed:
        print(path)
    if remaining_meta:
        print("WARNING: publication-name metadiscourse remains in:")
        for path in remaining_meta:
            print(path)


if __name__ == "__main__":
    main()
