#!/usr/bin/env python3
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]/'articles'

def clean_title(title,lang):
    t=title.strip('¿?¡! ')
    if lang=='es': t=t.replace(' Causas comunes y soluciones','')
    else: t=t.replace(' Common Causes and Fixes','')
    return t.strip('¿?¡! ')

def intent(title,kind,lang):
    t=clean_title(title,lang).lower()
    if lang=='es':
        if 'safety' in kind or 'emergency' in kind:
            return f'Tomar una decisión segura sobre «{t}», reconocer señales que obligan a detenerse o escalar y saber cuándo corresponde desechar, evacuar o pedir ayuda.'
        if 'diagnostic' in kind or 'troubleshooting' in kind:
            return f'Identificar las causas probables de «{t}», usar señales observables para decidir qué comprobar primero y saber cuándo la solución deja de ser una comprobación doméstica.'
        if kind in ('how-to','maintenance','prevention'):
            action=t[5:] if t.startswith('cómo ') else t
            return f'Aplicar un método práctico y seguro para {action}, evitando errores que dañan materiales o equipos, generan riesgos o hacen que el problema reaparezca.'
        return f'Entender «{t}» y convertir la explicación en una decisión doméstica práctica, clara y segura.'
    if 'safety' in kind or 'emergency' in kind:
        return f'Make a safe decision about “{t},” recognize signals that require stopping or escalating, and know when to discard, evacuate, or get help as appropriate.'
    if 'diagnostic' in kind or 'troubleshooting' in kind:
        return f'Identify the likely causes of “{t},” use observable clues to decide what to check first, and know when the problem is no longer basic household troubleshooting.'
    if kind in ('how-to','maintenance','prevention'):
        action=t[7:] if t.startswith('how to ') else t
        return f'Use a practical, safe method to {action}, avoiding mistakes that damage materials or equipment, create hazards, or allow the problem to return.'
    return f'Understand “{t}” and turn the explanation into a practical, clear, and safe household decision.'

for lang in ('es','en'):
  for n in range(231,311):
    ms=list((ROOT/lang).glob(f'{n:03d}-*.json'))
    if len(ms)!=1: raise SystemExit(f'{lang} #{n}: expected one file')
    p=ms[0]; o=json.loads(p.read_text(encoding='utf-8'))
    kind=o.get('taxonomy',{}).get('primary_article_type','')
    o['seo']['search_intent']=intent(o['title'],kind,lang)
    o['image']['alt']=clean_title(o['title'],lang)
    if lang=='es' and n==280:
        old='Gas, humo o monóxido de carbono son emergencia'
        new='Gas, humo o monóxido de carbono son señales de emergencia'
        o['content_html']=o['content_html'].replace(f'<h2>{old}</h2>',f'<h2>{new}</h2>')
        o['image']['concept']=o['image']['concept'].replace(old,new)
        for f in o['faq']:
            f['question']=f['question'].replace(old,new)
    p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
print('Refined search intents, image alt text, and final heading polish for 231-310')
