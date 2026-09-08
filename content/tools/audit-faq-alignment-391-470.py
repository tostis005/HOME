#!/usr/bin/env python3
from pathlib import Path
import json,re,unicodedata

ROOT=Path(__file__).resolve().parents[1]
records=[]
for p in sorted((ROOT/'tools').glob('batch-391-470-*.json')):
    records.extend(json.loads(p.read_text(encoding='utf-8')))

STOP={
'es':{'que','qué','como','cómo','cuando','cuándo','cual','cuál','por','para','una','uno','unos','unas','del','las','los','con','sin','hay','debo','puedo','puede','conviene','sirve','son','esta','este','esa','ese','muy','más','menos','se','el','la','en','a','y','o','mi','un','es'},
'en':{'what','why','how','when','which','can','could','should','do','does','is','are','the','a','an','my','your','to','of','in','on','for','with','and','or','i','it','be','from'}
}

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.findall(r'[a-z0-9]+',s)

def stem(w):
    for suf in ('mente','ciones','cion','ando','iendo','ados','adas','idos','idas','es','s','ing','ed','ly'):
        if len(w)>len(suf)+4 and w.endswith(suf): return w[:-len(suf)]
    return w

def toks(s,lang):
    return {stem(w) for w in norm(s) if len(w)>2 and w not in STOP[lang]}

def score(q,s,lang):
    qt=toks(q,lang); ht=toks(s[f'{lang}_h'],lang); pt=toks(s[f'{lang}_p'],lang)
    return 4*len(qt&ht)+len(qt&pt)

flags=[]
for r in records:
    configured=r.get('faq_sections',[0,1,3])
    for lang in ('es','en'):
        qs=r[f'faq_{lang}']
        for qi,q in enumerate(qs):
            scores=[score(q,s,lang) for s in r['sections']]
            cur=configured[qi]
            best=max(range(4),key=lambda i:scores[i])
            # Flag when another section has clearly stronger lexical support.
            if best!=cur and scores[best]>=scores[cur]+2 and scores[best]>=3:
                flags.append((r['n'],lang,qi+1,cur,best,scores,q))

print(f'FAQ semantic-alignment heuristic: {len(flags)} flagged question(s)')
for n,lang,qi,cur,best,scores,q in flags:
    print(f'FLAG #{n} {lang} FAQ{qi}: section {cur+1} -> likely {best+1}; scores={scores}; {q}')
