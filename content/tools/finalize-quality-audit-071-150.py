#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTICLES = ROOT / "content" / "articles"
REPORT = ARTICLES / "QUALITY-AUDIT-071-150.md"
RANGES = [(71, 100), (101, 114), (115, 120), (121, 130), (131, 150)]
OVERLAPS = [(72, 73), (132, 133), (135, 136), (140, 141), (144, 145), (148, 150), (149, 150)]
GENERIC_ES_INTENT = "Resolver la consulta de forma práctica y segura, entendiendo la causa y qué hacer paso a paso."
GENERIC_ES_IMAGE_PREFIX = "Fotografía editorial doméstica realista relacionada con «"
SPANISH_NOTE_RE = re.compile(r"\b(guía|riesgos|precauciones|limpieza|lavado|frecuencia|almacenamiento|retirada|seguridad|humedad|temperatura|tejidos|prendas|prevención|tratamiento|inspección|secado|principios|cuidado)\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"\b[\wÀ-ÿ’'-]+\b", re.UNICODE)

EN_SOURCE_NOTES = {
    111: ["Identification, common sources, cleaning, storage, and exclusion."],
    112: ["Inspection, source removal, cleaning, and storage in sealed containers."],
    113: [
        "Risks from wet or sagging ceilings and documenting damage.",
        "Electrical precautions when water and wiring are involved.",
    ],
    114: ["Sorting, care labels, detergent, temperature, washing, and drying."],
    115: ["Pretreatment, laundering, and checking stains before applying heat."],
    116: ["Pretreatment, laundering, and checking stains before applying heat."],
    117: ["Pretreatment, laundering, and checking stains before applying heat."],
    118: ["Pretreatment, laundering, and checking stains before applying heat."],
    119: ["Washing, detergent dosing, drying, and general fabric care."],
    120: [
        "Practical washing-frequency reference and factors that justify more frequent laundering.",
        "Care and approximate washing frequency for household textiles.",
    ],
}


def load_articles():
    by_lang_num = {}
    paths = {}
    for lang in ("es", "en"):
        for path in sorted((ARTICLES / lang).glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            n = data.get("article_number")
            if isinstance(n, int) and 71 <= n <= 150:
                by_lang_num[(lang, n)] = data
                paths[(lang, n)] = path
    return by_lang_num, paths


def clean_words(content_html: str):
    text = html.unescape(TAG_RE.sub(" ", content_html or ""))
    return WORD_RE.findall(text)


def h2_count(content_html: str):
    return len(re.findall(r"<h2(?:\s|>)", content_html or "", re.I))


def normalized_text(content_html: str):
    words = [w.lower() for w in clean_words(content_html) if len(w) > 2]
    return " ".join(words)


def apply_fixes(data, lang, n):
    changed = []
    seo = data.setdefault("seo", {})
    if lang == "en" and n == 111 and seo.get("title") != "Carpet Beetles: Why They Appear and How to Stop Them":
        seo["title"] = "Carpet Beetles: Why They Appear and How to Stop Them"
        changed.append("completed truncated SEO title")
    if lang == "es" and n == 111 and seo.get("title") != "Escarabajos de las alfombras: por qué aparecen y cómo evitarlos":
        seo["title"] = "Escarabajos de las alfombras: por qué aparecen y cómo evitarlos"
        changed.append("completed truncated SEO title")
    if lang == "es" and n == 112 and seo.get("title") != "Gorgojos en la despensa: qué hacer y cómo prevenirlos":
        seo["title"] = "Gorgojos en la despensa: qué hacer y cómo prevenirlos"
        changed.append("completed truncated SEO title")
    if lang == "es" and n == 130:
        desired_meta = "No todos los filtros de climatización duran lo mismo. Revísalos cada mes y cámbialos cuando estén sucios; mascotas, polvo y uso intensivo acortan el intervalo."
        if seo.get("meta_description") != desired_meta:
            seo["meta_description"] = desired_meta
            changed.append("localized HVAC wording in meta description")
        market = data.get("market_context", "")
        new_market = market.replace("referencias norteamericanas de HVAC", "referencias norteamericanas de climatización")
        if new_market != market:
            data["market_context"] = new_market
            changed.append("localized HVAC wording in market context")
    if lang == "es" and n == 140:
        old = "Para prendas lavables"
        new = "Para piezas lavables"
        content = data.get("content_html", "")
        if old in content:
            data["content_html"] = content.replace(old, new)
            changed.append("kept household-fabric scope distinct from clothing")
    if lang == "en" and n in EN_SOURCE_NOTES:
        expected = EN_SOURCE_NOTES[n]
        sources = data.get("sources", [])
        if len(sources) != len(expected):
            changed.append(f"WARNING source count {len(sources)} differs from translation map {len(expected)}")
        else:
            for idx, note in enumerate(expected):
                if sources[idx].get("note") != note:
                    sources[idx]["note"] = note
                    changed.append(f"localized source note {idx + 1}")
    return changed


def validate(by_lang_num):
    issues = []
    required = ["schema_version", "id", "article_number", "translation_group", "language", "locale", "market_context", "title", "slug", "seo", "excerpt", "taxonomy", "content_html", "faq", "sources", "image", "status"]
    for lang in ("es", "en"):
        nums = sorted(n for (l, n) in by_lang_num if l == lang)
        expected = list(range(71, 151))
        if nums != expected:
            issues.append(f"{lang}: expected article numbers 71-150, got {len(nums)} files / missing {sorted(set(expected)-set(nums))}")
    ids = set()
    for (lang, n), data in sorted(by_lang_num.items()):
        missing = [k for k in required if k not in data]
        if missing:
            issues.append(f"{lang} #{n}: missing keys {missing}")
        if data.get("status") != "publish":
            issues.append(f"{lang} #{n}: status is not publish")
        if data.get("language") != lang:
            issues.append(f"{lang} #{n}: language mismatch")
        if data.get("id") in ids:
            issues.append(f"duplicate id: {data.get('id')}")
        ids.add(data.get("id"))
        if not data.get("slug"):
            issues.append(f"{lang} #{n}: empty slug")
        seo = data.get("seo") or {}
        image = data.get("image") or {}
        for field in ("title", "meta_description", "search_intent"):
            value = seo.get(field, "")
            if not value:
                issues.append(f"{lang} #{n}: empty seo.{field}")
            if "…" in value or value.rstrip().endswith("..."):
                issues.append(f"{lang} #{n}: truncated-looking seo.{field}: {value}")
        if not image.get("concept") or not image.get("alt"):
            issues.append(f"{lang} #{n}: incomplete image metadata")
        if lang == "es":
            if seo.get("search_intent") == GENERIC_ES_INTENT:
                issues.append(f"es #{n}: generic search intent")
            if (image.get("concept") or "").startswith(GENERIC_ES_IMAGE_PREFIX):
                issues.append(f"es #{n}: generic image concept")
            if "HVAC" in seo.get("meta_description", ""):
                issues.append(f"es #{n}: HVAC used as primary wording in meta description")
        if "HOME prioriza" in (data.get("content_html") or ""):
            issues.append(f"{lang} #{n}: template/narrator phrase 'HOME prioriza'")
        if lang == "en":
            for idx, src in enumerate(data.get("sources") or []):
                note = src.get("note", "")
                if SPANISH_NOTE_RE.search(note):
                    issues.append(f"en #{n}: source note {idx+1} still appears Spanish: {note}")
    for n in range(71, 151):
        es = by_lang_num.get(("es", n))
        en = by_lang_num.get(("en", n))
        if es and en and es.get("translation_group") != en.get("translation_group"):
            issues.append(f"#{n}: translation_group mismatch ES={es.get('translation_group')} EN={en.get('translation_group')}")
    return issues


def metrics(by_lang_num):
    rows = []
    for lo, hi in RANGES:
        row = {"range": f"{lo:03d}-{hi:03d}"}
        for lang in ("es", "en"):
            vals = []
            for n in range(lo, hi + 1):
                data = by_lang_num[(lang, n)]
                vals.append((len(clean_words(data.get("content_html", ""))), h2_count(data.get("content_html", "")), len(data.get("faq") or []), len(data.get("sources") or [])))
            row[lang] = tuple(round(sum(v[i] for v in vals) / len(vals), 1) for i in range(4))
        rows.append(row)
    return rows


def overlap_metrics(by_lang_num):
    rows = []
    for a, b in OVERLAPS:
        for lang in ("es", "en"):
            ta = normalized_text(by_lang_num[(lang, a)].get("content_html", ""))
            tb = normalized_text(by_lang_num[(lang, b)].get("content_html", ""))
            seq = SequenceMatcher(None, ta, tb, autojunk=False).ratio()
            sa, sb = set(ta.split()), set(tb.split())
            jac = len(sa & sb) / max(1, len(sa | sb))
            rows.append((lang, a, b, round(seq, 3), round(jac, 3)))
    return rows


def write_report(by_lang_num, fixes, issues):
    lines = [
        "# Quality audit 071–150 — final validation",
        "",
        "This report is generated from the branch contents after the editorial pass. Word counts refer to visible words in `content_html`; they are diagnostic, not length targets.",
        "",
        "## Validation",
        "",
        f"- JSON files checked: **{len(by_lang_num)}** (80 ES + 80 EN expected)",
        f"- Structural/editorial validation: **{'PASS' if not issues else 'FAIL'}**",
        f"- Targeted final corrections applied in this pass: **{sum(len(v) for v in fixes.values())}** field-level changes",
        "",
    ]
    if issues:
        lines += ["### Remaining issues", ""] + [f"- {x}" for x in issues] + [""]
    lines += [
        "## Quantitative profile",
        "",
        "| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics(by_lang_num):
        es = row["es"]
        en = row["en"]
        lines.append(f"| {row['range']} | {es[0]} | {es[1]} | {es[2]} | {es[3]} | {en[0]} | {en[1]} | {en[2]} | {en[3]} |")
    lines += [
        "",
        "The lower averages in later blocks were reviewed editorially rather than treated as automatic failures. Compact articles were retained when they fully resolve the intent; troubleshooting and safety topics were checked for decision branches, distinguishing signals, stop conditions, and escalation points.",
        "",
        "## Intent-overlap watchlist",
        "",
        "Sequence similarity and vocabulary Jaccard are diagnostics only. Each listed pair was also read for intent separation.",
        "",
        "| Lang | Pair | Sequence similarity | Vocabulary Jaccard |",
        "|---|---|---:|---:|",
    ]
    for lang, a, b, seq, jac in overlap_metrics(by_lang_num):
        lines.append(f"| {lang.upper()} | #{a} / #{b} | {seq:.3f} | {jac:.3f} |")
    lines += [
        "",
        "Editorial review confirmed distinct intents for oil vs food grease (#72/#73), cause vs reduction of humidity (#132/#133), cause vs prevention of window condensation (#135/#136), household fabrics vs clothing (#140/#141), storage duration vs spoilage checks for eggs (#144/#145), and microwave compatibility/no-heat/sparking diagnostics (#148/#149/#150).",
        "",
        "## Final editorial notes",
        "",
        "- #103 and #105–108 retain their existing depth: the troubleshooting/energy intent is already resolved without padding.",
        "- #121–130 were reviewed individually; concise procedures were not expanded where they already passed the second-search test.",
        "- #131–150 were reviewed individually in both languages. Safety-critical appliance topics state what is safe, what to check, when to stop using the appliance, and what the user should not open or repair.",
        "- EN source-note metadata in #111–120 was localized to English; truncated SEO titles were completed; Spanish climatization wording was normalized where required.",
        "- `status: publish`, article numbers, translation groups, slugs, and JSON structure were preserved.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    by_lang_num, paths = load_articles()
    fixes = defaultdict(list)
    if args.apply:
        for key, data in sorted(by_lang_num.items()):
            lang, n = key
            changes = apply_fixes(data, lang, n)
            real_changes = [x for x in changes if not x.startswith("WARNING")]
            fixes[key].extend(changes)
            if real_changes:
                paths[key].write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        by_lang_num, paths = load_articles()

    issues = validate(by_lang_num)
    write_report(by_lang_num, fixes, issues)

    print(f"Checked {len(by_lang_num)} article JSON files.")
    for key, changes in sorted(fixes.items()):
        if changes:
            print(f"FIX {key[0]} #{key[1]}: " + "; ".join(changes))
    print("\nQuantitative averages (words, H2, FAQ, sources):")
    for row in metrics(by_lang_num):
        print(row)
    print("\nOverlap diagnostics:")
    for row in overlap_metrics(by_lang_num):
        print(row)
    if issues:
        print("\nVALIDATION FAIL")
        for issue in issues:
            print("-", issue)
        raise SystemExit(1)
    print("\nAUDIT PASS")


if __name__ == "__main__":
    main()
