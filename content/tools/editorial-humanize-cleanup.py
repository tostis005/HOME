#!/usr/bin/env python3
"""Final contextual cleanup for the HOME 001–070 editorial pass."""
from __future__ import annotations
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "articles" / "es"


def replace_faq(data, question=None, old_answer=None, new_question=None, new_answer=None):
    for item in data.get("faq", []):
        if question is not None and item.get("question") == question:
            if new_question is not None:
                item["question"] = new_question
            if new_answer is not None:
                item["answer"] = new_answer
        elif old_answer is not None and item.get("answer") == old_answer and new_answer is not None:
            item["answer"] = new_answer


def clean(data):
    n = int(data["article_number"])
    body = data["content_html"]

    if n == 16:
        replace_faq(
            data,
            question="¿Hace falta lejía para quitar el moho del baño?",
            new_answer="No como práctica rutinaria. La Agencia de Protección Ambiental de Estados Unidos (EPA) recomienda limpiar el moho de superficies duras con detergente y agua y secar por completo; los productos biocidas como la lejía no se recomiendan de forma rutinaria.",
        )
        replace_faq(
            data,
            question="¿Puedo pintar encima del moho?",
            new_answer="No debería hacerse sin limpiar y secar primero. La Agencia de Protección Ambiental de Estados Unidos (EPA) advierte que pintar sobre superficies con moho puede hacer que el recubrimiento vuelva a fallar.",
        )

    elif n == 31:
        replace_faq(
            data,
            question="¿Hay un botón Reset en todas las lavadoras?",
            new_question="¿Hay un botón de reinicio en todas las lavadoras?",
        )

    elif n == 32:
        replace_faq(
            data,
            question="¿Un reset arregla un error de desagüe?",
            new_question="¿Un reinicio arregla un error de desagüe?",
        )

    elif n == 45:
        body = body.replace(
            "no reiniciar el equipo ni rearmar protecciones una y otra vez una y otra vez",
            "no reiniciar el equipo ni rearmar protecciones una y otra vez",
        )
        body = body.replace(
            "Algunos sistemas también se detienen cuando un interruptor de seguridad que detiene el equipo cuando la bandeja de agua se llena o el desagüe de condensación se bloquea.",
            "Algunos sistemas también incorporan un interruptor de seguridad que detiene el equipo cuando la bandeja de agua se llena o el desagüe de condensación se bloquea.",
        )
        body = body.replace(
            "un condensador, motor, cableado o circuito frigorífico defectuoso",
            "un condensador eléctrico, un motor, el cableado o el circuito de refrigeración cuando alguno de ellos está averiado",
        )
        for item in data.get("faq", []):
            if item["question"] == "¿Por qué funciona el ventilador pero no la unidad exterior?":
                item["answer"] = "Puede haber un problema de alimentación exterior o un fallo interno en piezas como el contactor o el condensador eléctrico. Ese diagnóstico suele requerir un técnico."

    elif n == 46:
        data["excerpt"] = data["excerpt"].replace(
            "una bomba que evacua el agua de condensación que no funciona",
            "una bomba de desagüe averiada",
        )
        body = body.replace(
            "No todos los drenajes son iguales",
            "No todos los sistemas evacuan el agua de la misma manera",
        )
        body = body.replace(
            "otros usan una bomba que evacua el agua de condensación",
            "otros usan una pequeña bomba para llevar esa agua hasta un desagüe",
        )
        body = body.replace(
            "no puedes identificar una ruta segura para evacuar el agua de condensación para revisar",
            "no puedes identificar con seguridad por dónde debería evacuarse el agua",
        )
        body = body.replace(
            "ya no solo tienes un problema de sistema de climatización",
            "ya no solo tienes un problema de climatización",
        )

    elif n == 51:
        body = body.replace(
            "ese número puede ser el objetivo programado",
            "ese número puede ser solo la temperatura objetivo programada",
        )

    elif n == 58:
        data["seo"]["search_intent"] = data["seo"]["search_intent"].replace(
            "TDS, hierro",
            "sólidos disueltos totales (TDS), hierro",
        )
        body = body.replace(
            "También es diferente de sólidos disueltos totales (TDS, por sus siglas en inglés).",
            "También es diferente de los sólidos disueltos totales (TDS, por sus siglas en inglés).",
        )
        replace_faq(
            data,
            question="¿Un medidor TDS sirve para medir dureza?",
            new_question="¿Un medidor de TDS sirve para medir la dureza del agua?",
            new_answer="No de forma específica. TDS significa sólidos disueltos totales y engloba muchos minerales e iones distintos; para conocer la dureza necesitas una prueba específica de dureza total o de calcio y magnesio.",
        )
        replace_faq(
            data,
            question="¿A partir de qué valor se considera agua dura?",
            new_answer="El Servicio Geológico de Estados Unidos (USGS) clasifica como agua dura la que tiene entre 121 y 180 mg/L expresados como carbonato cálcico (CaCO3), y como muy dura la que supera 180 mg/L. Entre 61 y 120 mg/L se considera moderadamente dura.",
        )

    elif n == 61:
        replace_faq(
            data,
            question="¿Qué presión de agua es normal en una casa?",
            new_answer="Como referencia, el programa WaterSense de la Agencia de Protección Ambiental de Estados Unidos (EPA) señala que muchos accesorios domésticos funcionan bien con una presión aproximada de 3,1 a 4,1 bar (45–60 psi).",
        )

    elif n == 62:
        replace_faq(
            data,
            question="¿Qué presión general debería tener la casa?",
            new_answer="Como referencia, el programa WaterSense de la Agencia de Protección Ambiental de Estados Unidos (EPA) señala que muchos accesorios domésticos funcionan bien con una presión aproximada de 3,1 a 4,1 bar (45–60 psi).",
        )

    elif n == 67:
        body = body.replace("tratamiento químico DIY", "tratamiento químico por tu cuenta")

    elif n == 68:
        data["seo"]["meta_description"] = data["seo"]["meta_description"].replace(
            "sótano, textiles o HVAC",
            "sótano, textiles o sistema de climatización",
        )
        data["excerpt"] = data["excerpt"].replace(
            "sótanos o cámaras sanitarias",
            "sótanos o espacios bajo el suelo de algunas viviendas (cámaras sanitarias)",
        )
        body = body.replace(
            "un higrómetro, un pequeño medidor de humedad ambiental ayuda",
            "un higrómetro —un pequeño medidor de humedad ambiental— ayuda",
        )
        body = body.replace(
            "al encender sistema de climatización",
            "al encender el sistema de climatización",
        )
        replace_faq(
            data,
            question="¿El olor a humedad significa que hay moho?",
            new_answer="Puede ser una señal de crecimiento de moho, como indica la Agencia de Protección Ambiental de Estados Unidos (EPA), pero otros materiales húmedos o algunos desagües pueden producir olores parecidos. Hay que investigar la fuente.",
        )
        replace_faq(
            data,
            question="¿Qué humedad relativa conviene mantener?",
            new_answer="La Agencia de Protección Ambiental de Estados Unidos (EPA) recomienda mantener la humedad interior por debajo del 60 % y, cuando sea posible, aproximadamente entre el 30 y el 50 %.",
        )
        replace_faq(
            data,
            question="¿Hay que hacer una prueba de moho?",
            new_answer="En muchas situaciones con moho visible u olor claro, la Agencia de Protección Ambiental de Estados Unidos (EPA) no considera necesario empezar por un muestreo. Lo prioritario es localizar la humedad y corregirla.",
        )

    data["content_html"] = body
    return data


def main():
    changed = []
    for path in sorted(ROOT.glob("*.json")):
        raw = path.read_text(encoding="utf-8")
        original = json.loads(raw)
        data = clean(copy.deepcopy(original))
        for key in ("article_number", "translation_group", "language", "locale", "slug", "status"):
            assert data[key] == original[key], (path, key)
        if data != original:
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
            changed.append(path.name)
    for path in ROOT.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    print(f"Final contextual cleanup changed {len(changed)} Spanish articles")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
