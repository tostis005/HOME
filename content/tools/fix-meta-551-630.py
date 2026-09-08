#!/usr/bin/env python3
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'content' / 'articles'
REPORT = ART / 'QUALITY-AUDIT-551-630.md'
EXPECTED = set(range(551,631)) - {616}
changed = 0
lengths = {'es': [], 'en': []}
for lang in ('es','en'):
    files = []
    for p in (ART/lang).glob('*.json'):
        m = re.match(r'^(\d+)-', p.name)
        if m and int(m.group(1)) in EXPECTED:
            files.append(p)
    nums = {int(re.match(r'^(\d+)-', p.name).group(1)) for p in files}
    if nums != EXPECTED or len(files) != 79:
        raise SystemExit(f'{lang}: inventory mismatch')
    for p in files:
        d = json.loads(p.read_text(encoding='utf-8'))
        excerpt = d.get('excerpt','').strip()
        if not excerpt:
            raise SystemExit(f'{p}: missing excerpt')
        full = re.split(r'(?<=[.!?])\s+', excerpt, maxsplit=1)[0].strip()
        if not full or full[-1] not in '.!?':
            raise SystemExit(f'{p}: first excerpt sentence is not complete: {full!r}')
        if d.get('seo',{}).get('meta_description') != full:
            d['seo']['meta_description'] = full
            p.write_text(json.dumps(d, ensure_ascii=False, separators=(',',':'))+'\n', encoding='utf-8')
            changed += 1
        lengths[lang].append(len(full))
# second pass: exact semantic validation
for lang in ('es','en'):
    for p in (ART/lang).glob('*.json'):
        m = re.match(r'^(\d+)-', p.name)
        if not m or int(m.group(1)) not in EXPECTED:
            continue
        d = json.loads(p.read_text(encoding='utf-8'))
        full = re.split(r'(?<=[.!?])\s+', d['excerpt'].strip(), maxsplit=1)[0].strip()
        if d['seo']['meta_description'] != full:
            raise SystemExit(f'{p}: meta description mismatch after fix')
text = REPORT.read_text(encoding='utf-8').rstrip()
marker = '## Post-merge meta-description stabilization'
if marker not in text:
    text += f"\n\n{marker}\n\n- Re-audited all **158/158** bilingual article meta descriptions after final publication.\n- Replaced character-truncated descriptions with the complete first editorial sentence from each article excerpt; **{changed}** JSON files required correction.\n- Semantic validation now requires every meta description to equal a complete sentence ending in punctuation.\n- Result: **158/158 PASS**.\n"
    REPORT.write_text(text, encoding='utf-8')
print(f'PASS: 158/158 meta descriptions are complete sentences; changed={changed}; ES chars {min(lengths["es"])}-{max(lengths["es"])}; EN chars {min(lengths["en"])}-{max(lengths["en"])}')
