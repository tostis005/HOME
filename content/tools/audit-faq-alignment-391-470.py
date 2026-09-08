#!/usr/bin/env python3
from pathlib import Path
import json,re,html

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/'tools'; ART=ROOT/'articles'

EXPECTED={
391:[0,1,3],392:[0,2,3],393:[0,1,3],394:[0,1,3],395:[0,1,2],396:[0,1,2],397:[0,1,3],398:[0,1,2],399:[0,1,2],400:[0,1,2],
401:[0,1,3],402:[0,1,3],403:[0,2,3],404:[0,1,3],405:[0,1,3],406:[0,1,3],407:[0,1,3],408:[0,1,3],409:[0,1,2],410:[0,1,2],
411:[0,1,3],412:[0,1,2],413:[0,1,2],414:[0,1,2],415:[0,1,2],416:[0,1,3],417:[0,1,2],418:[0,1,3],419:[0,1,3],420:[0,1,3],
421:[0,1,3],422:[0,1,3],423:[0,1,2],424:[0,1,3],425:[0,1,3],426:[0,1,2],427:[0,1,2],428:[0,1,2],429:[0,1,3],430:[0,1,2],
431:[0,1,2],432:[0,1,3],433:[0,1,2],434:[0,1,3],435:[0,1,2],436:[0,1,3],437:[0,1,2],438:[0,1,2],439:[0,1,2],440:[0,1,3],
441:[0,1,2],442:[0,1,2],443:[0,1,3],444:[0,1,2],445:[0,1,3],446:[0,1,2],447:[0,1,3],448:[0,1,3],449:[0,1,3],450:[0,1,2],
451:[0,1,3],452:[0,1,3],453:[0,1,2],454:[0,1,3],455:[0,2,3],456:[0,1,2],457:[0,1,3],458:[0,2,3],459:[0,1,3],460:[0,1,3],
461:[0,1,3],462:[0,1,3],463:[0,1,2],464:[0,1,2],465:[0,1,2],466:[0,1,2],467:[0,2,3],468:[0,1,3],469:[0,1,3],470:[0,1,2]
}

records={}
for p in sorted(TOOLS.glob('batch-391-470-*.json')):
    for r in json.loads(p.read_text(encoding='utf-8')): records[r['n']]=r
errs=[]
if sorted(records)!=list(range(391,471)): errs.append(f'batch coverage is {len(records)}, expected 80')

def final_section_paragraphs(content_html):
    pairs=re.findall(r'<h2>.*?</h2><p>(.*?)</p>',content_html,flags=re.S)
    return [html.unescape(x) for x in pairs]

for n in range(391,471):
    r=records.get(n)
    if not r: continue
    if r.get('faq_sections')!=EXPECTED[n]: errs.append(f'#{n}: faq_sections {r.get("faq_sections")} != reviewed {EXPECTED[n]}')
    for lang in ('es','en'):
        fs=list((ART/lang).glob(f'{n:03d}-*.json'))
        if len(fs)!=1:
            errs.append(f'{lang} #{n}: article not found uniquely'); continue
        o=json.loads(fs[0].read_text(encoding='utf-8'))
        qs=r[f'faq_{lang}']; faq=o.get('faq',[]); sections=final_section_paragraphs(o.get('content_html',''))
        if len(sections)!=4: errs.append(f'{lang} #{n}: could not parse four final sections')
        if len(faq)!=3:
            errs.append(f'{lang} #{n}: expected 3 FAQ'); continue
        for i,(q,section_idx) in enumerate(zip(qs,EXPECTED[n])):
            if faq[i].get('question')!=q:
                errs.append(f'{lang} #{n} FAQ{i+1}: question changed from reviewed source')
            if section_idx>=len(sections) or faq[i].get('answer')!=sections[section_idx]:
                errs.append(f'{lang} #{n} FAQ{i+1}: answer is not final section {section_idx+1}')

print(f'FAQ answer-section audit: topics={len(records)} questions={len(records)*6} errors={len(errs)}')
for e in errs: print('ERROR:',e)
if errs: raise SystemExit(1)
print('FAQ ALIGNMENT PASS 480/480')
