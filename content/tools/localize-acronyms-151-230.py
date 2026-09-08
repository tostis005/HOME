#!/usr/bin/env python3
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]/'articles'/'es'

FIXES={
 204:[('La EPA sitúa el control de humedad','La Agencia de Protección Ambiental de EE. UU. (EPA) sitúa el control de humedad')],
 208:[('La EPA señala que materiales porosos','La Agencia de Protección Ambiental de EE. UU. (EPA) señala que materiales porosos')],
 209:[('La EPA recomienda valorar retirada','La Agencia de Protección Ambiental de EE. UU. (EPA) recomienda valorar la retirada')],
 210:[('La EPA recomienda considerar ayuda profesional','La Agencia de Protección Ambiental de EE. UU. (EPA) recomienda considerar ayuda profesional')],
 224:[('Las leches UHT sin abrir son una excepción hasta que se abren','La leche de tratamiento a temperatura ultra alta (UHT) sin abrir es una excepción hasta que se abre')],
 227:[
   ('automáticos y GFCI. Luces','automáticos y protección diferencial. Luces'),
   ('<h2>Busca un GFCI disparado en circuitos de zonas húmedas</h2><p>Un dispositivo GFCI puede desconectar','<h2>Busca un interruptor de circuito por falla a tierra (GFCI) disparado</h2><p>En instalaciones de Estados Unidos y Canadá, un GFCI puede desconectar')
  ],
}

for n,repls in FIXES.items():
    ms=list(ROOT.glob(f'{n:03d}-*.json'))
    if len(ms)!=1: raise SystemExit(f'Expected one ES #{n}, found {len(ms)}')
    p=ms[0]; o=json.loads(p.read_text(encoding='utf-8')); raw=json.dumps(o,ensure_ascii=False,separators=(',',':'))
    changed=False
    for old,new in repls:
        if old in raw:
            raw=raw.replace(old,new,1); changed=True
        elif new not in raw:
            raise SystemExit(f'Expected phrase not found in ES #{n}: {old}')
    if changed:
        p.write_text(raw+'\n',encoding='utf-8'); print(f'Localized acronyms ES #{n}')
