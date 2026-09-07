#!/usr/bin/env python3
"""One-time reviewed cleanup for HOME articles 001–070 after the language pass."""

from __future__ import annotations
import copy, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'articles' / 'es'

AGENCIES = [
    (r'\bEPA\b', 'EPA', 'la Agencia de Protección Ambiental de Estados Unidos (EPA)'),
    (r'\bCDC\b', 'CDC', 'los Centros para el Control y la Prevención de Enfermedades de Estados Unidos (CDC)'),
    (r'\bCPSC\b', 'CPSC', 'la Comisión de Seguridad de Productos del Consumidor de Estados Unidos (CPSC)'),
    (r'\bUSDA\b', 'USDA', 'el Departamento de Agricultura de Estados Unidos (USDA)'),
    (r'\bUSGS\b', 'USGS', 'el Servicio Geológico de Estados Unidos (USGS)'),
    (r'\bDOE\b', 'DOE', 'el Departamento de Energía de Estados Unidos (DOE)'),
]

def expand_summary(text: str) -> str:
    for pattern, acronym, phrase in AGENCIES:
        if f'({acronym})' in text:
            continue
        m = re.search(pattern, text)
        if not m:
            continue
        before = text[:m.start()]
        cap = m.start() == 0 or bool(re.search(r'[.!?]\s*$', before))
        repl = (phrase[0].upper() + phrase[1:]) if cap else phrase
        text = text[:m.start()] + repl + text[m.end():]
        if acronym == 'CDC':
            for a,b in {'señala':'señalan','recomienda':'recomiendan','advierte':'advierten','indica':'indican'}.items():
                text = text.replace(f'(CDC) {a}', f'(CDC) {b}', 1)
    return text

def clean_common(text: str) -> str:
    replacements = {
        'resets': 'reinicios',
        'botón de “reset”': 'botón de “reinicio”',
        'botón de reset': 'botón de reinicio',
        'del reset': 'del reinicio',
        'tras el reset': 'tras el reinicio',
        'después del reset': 'después del reinicio',
        'otro reset': 'otro reinicio',
        'un buen reset': 'un buen reinicio',
        'Un buen reset': 'Un buen reinicio',
        'El éxito del reset': 'El éxito del reinicio',
        'reset práctico': 'reinicio práctico',
        'power cycle': 'reinicio eléctrico',
        'control lock': 'bloqueo de controles',
        'DIY': 'por tu cuenta',
    }
    for a,b in replacements.items():
        text = text.replace(a,b)
    text = text.replace('. un reinicio', '. Un reinicio')
    text = text.replace('. bloqueo de controles', '. El bloqueo de controles')
    return text

def clean_article(data: dict) -> dict:
    n = int(data['article_number'])
    body = clean_common(data['content_html'])

    if n == 10:
        body = body.replace('modo “Cool”', 'modo frío (Cool, si así aparece en el termostato)')
        body = body.replace('o frío y ajusta', 'y ajusta')
        body = body.replace('ventilador en Auto, no On', 'ventilador en automático (Auto) y no en funcionamiento continuo (On)')

    elif n == 16:
        body = body.replace('una superficie de aproximadamente 10 pies cuadrados, algo menos de 1 metro cuadrado', 'una superficie de algo menos de 1 m² (aproximadamente 10 pies cuadrados)')
        body = body.replace('cuando el área afectada supere aproximadamente 10 pies cuadrados', 'cuando el área afectada supere unos 0,9 m² (aproximadamente 10 pies cuadrados)')

    elif n == 31:
        body = body.replace('Inicio/Pausa o Encendido/Cancelar (Inicio/Pausa o Encendido/Cancelar, según el panel)', 'Inicio/Pausa o Encendido/Cancelar (Start/Pause o Power/Cancel, según el panel)')
        body = body.replace('“control reset”', '“reinicio de controles” (control reset, si así lo llama el manual)')
        body = body.replace('otro reset', 'otro reinicio')

    elif n == 32:
        body = body.replace('<h2>Antes del reset, anota cualquier código o patrón de luces</h2>', '<h2>Antes de reiniciar, anota cualquier código o patrón de luces</h2>')
        body = body.replace('Cancelar/Desaguar (Cancelar/Desaguar, si así aparece en el panel)', 'Cancelar/Desaguar (Cancel/Drain, si así aparece en el panel)')
        body = body.replace('pulsa Start según', 'pulsa Inicio (Start, si así aparece en el panel) según')

    elif n == 45:
        body = body.replace('no repetir reinicios ni rearmar protecciones', 'no reiniciar el equipo ni rearmar protecciones una y otra vez')
        body = body.replace('modo “Cool” o frío', 'modo frío (Cool, si así aparece en el termostato)')
        body = body.replace('un seccionador junto a la unidad exterior', 'un interruptor de corte junto a la unidad exterior (también llamado seccionador)')
        body = body.replace('un interruptor de seguridad que detiene el equipo si el agua de condensación no puede evacuar detecta una bandeja llena o un drenaje bloqueado', 'un interruptor de seguridad que detiene el equipo cuando la bandeja de agua se llena o el desagüe de condensación se bloquea')
        body = body.replace('<h2>No uses el botón de reset como estrategia repetitiva</h2>', '<h2>No conviertas el botón de reinicio en una estrategia</h2>')
        body = body.replace('. un reinicio puede recuperar', '. Un reinicio puede recuperar')

    elif n == 46:
        body = body.replace('produciendo condensado durante horas', 'produciendo agua de condensación durante horas')
        body = body.replace('la tubo de desagüe del agua de condensación', 'el tubo de desagüe del agua de condensación')
        body = body.replace('bandeja secundaria o de emergencia de emergencia', 'bandeja secundaria o de emergencia')
        body = body.replace('Una bomba que evacua el agua de condensación que falla deja de mover el agua', 'Si la bomba de desagüe falla, el agua deja de salir')
        body = body.replace('una pequeña bomba eleva el condensado hasta un desagüe', 'una pequeña bomba impulsa el agua hasta un desagüe')
        body = body.replace('Una tubería exterior de condensados', 'Una tubería exterior de desagüe')
        body = body.replace('una ruta de condensados segura', 'una ruta segura para evacuar el agua de condensación')

    elif n == 47:
        body = body.replace('aproximadamente 10 pies cuadrados —unos 0,9 m²—', 'unos 0,9 m² (aproximadamente 10 pies cuadrados)')

    elif n == 48:
        body = body.replace('aproximadamente 10 ft² —unos 0,9 m²—', 'unos 0,9 m² (aproximadamente 10 pies cuadrados)')

    elif n == 51:
        body = body.replace('botón universal de reset', 'botón universal de reinicio')
        body = body.replace('modo un modo que desactiva la refrigeración para exposición', 'un modo que desactiva la refrigeración para exposición')
        body = body.replace('El éxito del reinicio se evalúa', 'El resultado del reinicio se evalúa')
        body = body.replace('Un buen reinicio termina', 'Un reinicio correcto termina')

    elif n == 58:
        body = body.replace('TDS, o sólidos disueltos totales', 'sólidos disueltos totales (TDS, por sus siglas en inglés)')

    elif n == 61:
        body = body.replace('<p>el programa WaterSense', '<p>El programa WaterSense')
        body = body.replace('de aproximadamente 45 a 60 psi', 'de aproximadamente 3,1 a 4,1 bar (45–60 psi)')

    elif n == 62:
        body = body.replace('<p>el programa WaterSense', '<p>El programa WaterSense')
        body = body.replace('presión de servicio aproximada de 45–60 psi', 'presión de servicio aproximada de 3,1–4,1 bar (45–60 psi)')

    # Reader-facing summaries should not present an unexplained institution.
    data['excerpt'] = expand_summary(clean_common(data['excerpt']))
    data['content_html'] = body

    if n == 16:
        for item in data.get('faq', []):
            item['answer'] = item['answer'].replace('EPA usa aproximadamente 10 pies cuadrados, algo menos de 1 m²', 'La Agencia de Protección Ambiental de Estados Unidos (EPA) usa algo menos de 1 m² (aproximadamente 10 pies cuadrados)')
    if n == 31:
        for item in data.get('faq', []):
            item['question'] = clean_common(item['question'])
            item['answer'] = clean_common(item['answer'])
            item['answer'] = item['answer'].replace('botón Reset', 'botón de reinicio')
    if n == 32:
        data['seo']['meta_description'] = data['seo']['meta_description'].replace('power cycle', 'reinicio eléctrico')
        data['seo']['search_intent'] = data['seo']['search_intent'].replace('reset', 'reinicio')
        data['excerpt'] = data['excerpt'].replace('Control Lock', 'el bloqueo de controles')
        for item in data.get('faq', []):
            item['question'] = clean_common(item['question'])
            item['answer'] = clean_common(item['answer'])
            item['answer'] = item['answer'].replace('Control Lock', 'el bloqueo de controles')
    if n == 46:
        data['seo']['meta_description'] = data['seo']['meta_description'].replace('desagüe de condensados', 'desagüe del agua de condensación').replace('serpentín congelado', 'serpentín interior congelado')
        data['excerpt'] = data['excerpt'].replace('drenaje de condensados', 'desagüe del agua de condensación').replace('bomba de condensados', 'bomba que evacua el agua de condensación').replace('hielo en el serpentín', 'hielo en el serpentín interior')
        for item in data.get('faq', []):
            item['answer'] = item['answer'].replace('bandeja primaria', 'bandeja principal')
    if n == 51:
        data['excerpt'] = data['excerpt'].replace('power cycle', 'reinicio eléctrico').replace('resetear', 'reiniciar')
        for item in data.get('faq', []):
            item['question'] = item['question'].replace('resetearlo', 'reiniciarlo').replace('reset', 'reinicio')
            item['answer'] = item['answer'].replace('reset', 'reinicio')
    if n == 61:
        data['excerpt'] = data['excerpt'].replace('aproximadamente entre 45 y 60 psi', 'aproximadamente entre 3,1 y 4,1 bar (45–60 psi)')
    return data

def main():
    changed=[]
    for path in sorted(ROOT.glob('*.json')):
        raw=path.read_text(encoding='utf-8')
        original=json.loads(raw)
        data=clean_article(copy.deepcopy(original))
        for k in ('article_number','translation_group','language','locale','slug','status'):
            assert data[k] == original[k], (path,k)
        if data != original:
            path.write_text(json.dumps(data, ensure_ascii=False, separators=(',',':'))+'\n', encoding='utf-8')
            changed.append(path.name)
    # final parse check
    for p in ROOT.glob('*.json'):
        json.loads(p.read_text(encoding='utf-8'))
    print(f'Cleanup changed {len(changed)} Spanish articles')
    for p in changed: print(p)

if __name__ == '__main__':
    main()
