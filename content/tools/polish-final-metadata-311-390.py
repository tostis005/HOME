#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'articles'; changed=0
for lang in ('es','en'):
    for n in range(311,391):
        fs=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(fs)!=1: raise SystemExit(f'{lang} #{n}: expected one file')
        p=fs[0]; o=json.loads(p.read_text(encoding='utf-8')); title=o['title'].rstrip('?').strip(); old=o['seo']['search_intent']
        if lang=='es' and old.startswith('Seguir un método práctico para '):
            low=title.lower()
            if low.startswith('cómo '):
                action=low[5:]
                new=f'Aplicar un método práctico y seguro para {action}, protegiendo materiales y equipos y sabiendo cuándo detenerse o cambiar de estrategia.'
            elif low.startswith('cada cuánto '):
                new=f'Determinar {low}, combinando las indicaciones del fabricante con el uso real y señales observables del hogar.'
            else:
                new=f'Resolver {low} con un método práctico, seguro y adaptado al equipo o material concreto.'
            o['seo']['search_intent']=new
        elif lang=='en' and old.startswith('Use a practical method for '):
            low=title.lower()
            if low.startswith('how to '):
                action=low[7:]
                new=f'Use a practical, safe method to {action}, protecting materials and equipment and knowing when to stop or change approach.'
            elif low.startswith('how often should you '):
                action=low[len('how often should you '):]
                new=f'Determine how often to {action} using manufacturer guidance, actual household use, and observable signs rather than a one-size-fits-all interval.'
            elif low.startswith('where should you '):
                action=low[len('where should you '):]
                new=f'Choose where to {action} using practical placement criteria that improve performance and avoid common household obstacles.'
            elif low.startswith('which way should '):
                subject=low[len('which way should '):]
                new=f'Determine which way {subject} and apply the equipment’s airflow markings correctly without forcing an incompatible installation.'
            elif low.startswith('can you '):
                action=low[len('can you '):]
                new=f'Determine whether you can {action} and, when appropriate, use a safe method that preserves quality and avoids preventable food-safety mistakes.'
            else:
                new=f'Resolve {low} with a practical, safe method suited to the specific material, appliance, or household situation.'
            o['seo']['search_intent']=new
        # Final Spanish wording found during manual sample review.
        if lang=='es' and n==387:
            o['content_html']=o['content_html'].replace('Ricotta, queso crema, cottage y algunos quesos frescos','Ricota, queso crema, queso cottage y algunos quesos frescos')
        if o['seo']['search_intent']!=old or (lang=='es' and n==387):
            p.write_text(json.dumps(o,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8'); changed+=1
report=ART/'QUALITY-AUDIT-311-390.md'; text=report.read_text(encoding='utf-8')
marker='## Final metadata-language pass'
if marker not in text:
    text += '\n\n## Final metadata-language pass\n\n- Search-intent metadata was normalized so how-to and maintenance pages use natural ES/EN syntax rather than constructions such as `para cómo...` or `for how to...`.\n- Final manual language review also normalized the Spanish cheese wording in #387.\n'
    report.write_text(text,encoding='utf-8')
print(f'Applied final metadata/language polish to {changed} article versions')
