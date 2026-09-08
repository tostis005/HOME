#!/usr/bin/env python3
import json, re, math
from pathlib import Path
from collections import Counter, defaultdict
from difflib import SequenceMatcher

ROOT = Path('content/articles')
LO, HI = 71, 150
GENERIC_INTENTS = {
    'Resolver la consulta de forma práctica y segura, entendiendo la causa y qué hacer paso a paso.',
    'Solve the household question safely and practically, understanding the cause and what to do step by step.',
}

def strip_html(s):
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def words(s):
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ]+)?", strip_html(s).lower())

def tokens(s):
    stop = {'the','and','for','with','that','this','from','your','you','are','una','unos','unas','para','con','que','del','las','los','por','como','más','muy','sin','sobre','into','when','how','why','not','but','hay','puede','debe'}
    return {w for w in words(s) if len(w) > 3 and w not in stop}

rows=[]
by_lang={'es':{},'en':{}}
flags=[]
for lang in ('es','en'):
    for p in sorted((ROOT/lang).glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        n=int(d['article_number'])
        if not (LO <= n <= HI):
            continue
        body=d['content_html']
        wc=len(words(body))
        h2=body.count('<h2>')
        faq=len(d.get('faq') or [])
        src=len(d.get('sources') or [])
        meta=d.get('seo',{}).get('meta_description','')
        intent=d.get('seo',{}).get('search_intent','')
        image=(d.get('image') or {}).get('concept','')
        row=(n,lang,wc,h2,faq,src,len(meta),p.name)
        rows.append(row)
        by_lang[lang][n]=(d,p,tokens(body),wc)
        if meta.rstrip().endswith(('…','...')) or '…' in meta:
            flags.append((n,lang,'META_TRUNCATED',meta))
        if intent in GENERIC_INTENTS or intent.startswith('Resolver la consulta de forma práctica y segura'):
            flags.append((n,lang,'GENERIC_INTENT',intent))
        if 'relacionada con «' in image.lower() or 'related to “' in image.lower() or 'related to "' in image.lower():
            flags.append((n,lang,'GENERIC_IMAGE',image))
        # quality floor: do not fail narrow topics just for length; flag for human review.
        types=set((d.get('taxonomy') or {}).get('article_types') or [])
        complex_types={'diagnosis','diagnostics','troubleshooting','repair-guide','safety','moisture-control','energy-saving'}
        floor=600 if types & complex_types else 430
        if wc < floor:
            flags.append((n,lang,'DEPTH_REVIEW',f'{wc} words; types={sorted(types)}'))
        if faq < 3:
            flags.append((n,lang,'FAQ_REVIEW',str(faq)))
        if src < 1:
            flags.append((n,lang,'SOURCE_REVIEW',str(src)))

# Pair consistency
for n in range(LO,HI+1):
    if n not in by_lang['es'] or n not in by_lang['en']:
        flags.append((n,'pair','MISSING_PAIR',''))
        continue
    es=by_lang['es'][n][0]; en=by_lang['en'][n][0]
    if es['translation_group'] != en['translation_group']:
        flags.append((n,'pair','TRANSLATION_GROUP_MISMATCH',f"{es['translation_group']} != {en['translation_group']}"))

# Similarity / cannibalization: token Jaccard within each language
sims=[]
for lang in ('es','en'):
    nums=sorted(by_lang[lang])
    for i,a in enumerate(nums):
        ta=by_lang[lang][a][2]
        for b in nums[i+1:]:
            tb=by_lang[lang][b][2]
            if not ta or not tb: continue
            j=len(ta&tb)/max(1,len(ta|tb))
            if j >= 0.30:
                sims.append((j,lang,a,b))

print('QUALITY_AUDIT_071_150')
print('n lang words h2 faq src meta_len file')
for r in rows:
    print(*r)
print('\nFLAGS')
for f in sorted(flags):
    print('|'.join(map(str,f)))
print('\nTOP_SIMILARITIES')
for j,lang,a,b in sorted(sims, reverse=True)[:40]:
    print(f'{lang}|{a}|{b}|{j:.3f}')

# Aggregate bands
print('\nBANDS')
for start,end in [(71,100),(101,114),(115,120),(121,130),(131,150)]:
    for lang in ('es','en'):
        vals=[by_lang[lang][n][3] for n in range(start,end+1) if n in by_lang[lang]]
        print(f'{start}-{end}|{lang}|count={len(vals)}|avg={sum(vals)/len(vals):.1f}|min={min(vals)}|max={max(vals)}')
