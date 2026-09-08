#!/usr/bin/env python3
import argparse
import html
import json
import re
import statistics
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "content" / "tools"
ARTICLES = ROOT / "content" / "articles"
ES_DIR = ARTICLES / "es"
EN_DIR = ARTICLES / "en"
REPORT = ARTICLES / "QUALITY-AUDIT-551-630.md"
START, END = 551, 630
BLOCKED = {616: "Canonical duplicate of #537; keep #537 as the single URL for water hammer / banging pipes when water is shut off."}
ALL_CANONICAL_NUMBERS = set(range(START, END + 1))
EXPECTED_SOURCE_NUMBERS = ALL_CANONICAL_NUMBERS - set(BLOCKED)
EXPECTED_PUBLISHED_NUMBERS = EXPECTED_SOURCE_NUMBERS

SOURCE_MAP = {
    "ipm": {
        "name": "U.S. Environmental Protection Agency — Integrated Pest Management (IPM) Principles",
        "url": "https://www.epa.gov/safepestcontrol/integrated-pest-management-ipm-principles",
        "es_note": "Principios de manejo integrado de plagas: prevención, exclusión, saneamiento y control de menor riesgo.",
        "en_note": "Integrated pest management principles emphasizing prevention, exclusion, sanitation, and lower-risk control."
    },
    "cleaning": {
        "name": "American Cleaning Institute — Cleaning Tips",
        "url": "https://www.cleaninginstitute.org/cleaning-tips",
        "es_note": "Buenas prácticas generales de limpieza doméstica y uso responsable de productos.",
        "en_note": "General household-cleaning practices and responsible product use."
    },
    "electrical": {
        "name": "U.S. Consumer Product Safety Commission — Electrical Safety",
        "url": "https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Electrical-Safety",
        "es_note": "Criterios de seguridad eléctrica doméstica y señales que requieren detener el uso o pedir ayuda profesional.",
        "en_note": "Household electrical-safety guidance and warning signs that call for stopping use or professional help."
    },
    "co": {
        "name": "U.S. Consumer Product Safety Commission — Carbon Monoxide Information Center",
        "url": "https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center",
        "es_note": "Riesgos del monóxido de carbono, alarmas y respuesta ante una posible exposición.",
        "en_note": "Carbon-monoxide hazards, alarms, and response to possible exposure."
    },
    "mold": {
        "name": "U.S. Environmental Protection Agency — A Brief Guide to Mold, Moisture and Your Home",
        "url": "https://www.epa.gov/mold/brief-guide-mold-moisture-and-your-home",
        "es_note": "Control de humedad, prevención del moho y límites de una limpieza doméstica segura.",
        "en_note": "Moisture control, mold prevention, and boundaries for safe household cleanup."
    },
    "water": {
        "name": "U.S. Environmental Protection Agency WaterSense — Home Maintenance",
        "url": "https://www.epa.gov/watersense/home-maintenance",
        "es_note": "Mantenimiento doméstico relacionado con agua, fugas y consumo eficiente.",
        "en_note": "Household maintenance related to water, leaks, and efficient use."
    },
    "energy": {
        "name": "U.S. Department of Energy — Energy Saver",
        "url": "https://www.energy.gov/energysaver",
        "es_note": "Información práctica sobre climatización, eficiencia y mantenimiento energético doméstico.",
        "en_note": "Practical information on home heating, cooling, efficiency, and energy maintenance."
    },
    "ladder": {
        "name": "U.S. Consumer Product Safety Commission — Ladder Safety",
        "url": "https://www.cpsc.gov/safety-education/safety-guides/home/ladder-safety",
        "es_note": "Seguridad básica cuando una tarea doméstica requiere trabajar en altura.",
        "en_note": "Basic safety when household maintenance requires working at height."
    },
    "plants": {
        "name": "University of Minnesota Extension — Houseplants",
        "url": "https://extension.umn.edu/houseplants",
        "es_note": "Cuidados, síntomas habituales y manejo de plantas de interior.",
        "en_note": "Houseplant care, common symptoms, and management."
    },
    "wifi": {
        "name": "Federal Communications Commission — Consumer Guides",
        "url": "https://www.fcc.gov/consumer-guides",
        "es_note": "Guías para consumidores sobre conectividad y redes domésticas.",
        "en_note": "Consumer guidance on connectivity and home networks."
    },
    "food": {
        "name": "USDA Food Safety and Inspection Service — Food Safety Basics",
        "url": "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics",
        "es_note": "Principios de manipulación y conservación segura de alimentos.",
        "en_note": "Basic safe food handling and storage principles."
    },
    "food_power": {
        "name": "USDA Food Safety and Inspection Service — Keeping Food Safe During an Emergency",
        "url": "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/emergencies/keeping-food-safe-during-emergency",
        "es_note": "Conservación de alimentos durante cortes de electricidad y otras emergencias.",
        "en_note": "Food safety during power outages and other emergencies."
    },
    "freezing": {
        "name": "USDA Food Safety and Inspection Service — Freezing and Food Safety",
        "url": "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/freezing-and-food-safety",
        "es_note": "Seguridad, calidad y recongelación de alimentos congelados.",
        "en_note": "Safety, quality, and refreezing guidance for frozen foods."
    },
    "fire": {
        "name": "U.S. Consumer Product Safety Commission — Fire Safety",
        "url": "https://www.cpsc.gov/Safety-Education/Safety-Guides/Home/Fire-Safety",
        "es_note": "Prevención de incendios domésticos y señales que requieren actuación inmediata.",
        "en_note": "Home-fire prevention and warning signs requiring immediate action."
    },
    "mattress": {
        "name": "Sleep Foundation — Mattress Information",
        "url": "https://www.sleepfoundation.org/mattress-information",
        "es_note": "Información general sobre soporte, desgaste y mantenimiento de colchones.",
        "en_note": "General information on mattress support, wear, and maintenance."
    },
}


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return re.sub(r"-+", "-", value)


def clean_title_for_slug(title: str) -> str:
    return title.strip().lstrip("¿¡").rstrip("?!.")


def first_sentence(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    sentence = parts[0].strip()
    if len(sentence) <= 175:
        return sentence
    cut = sentence[:172].rsplit(" ", 1)[0].rstrip(" ,;:")
    return cut + "."


def source_entries(key: str, lang: str):
    if not key:
        return []
    item = SOURCE_MAP.get(key)
    if not item:
        return []
    return [{
        "name": item["name"],
        "url": item["url"],
        "note": item["es_note" if lang == "es" else "en_note"],
    }]


def search_intent(kind: str, title: str, lang: str) -> str:
    plain = clean_title_for_slug(title)
    diagnostic = kind in {"why", "diagnostic", "troubleshooting", "problem"} or title.strip().startswith(("¿Por qué", "Why "))
    safety = kind in {"safety", "safety-guide", "emergency"}
    if lang == "es":
        if diagnostic:
            return f"Identificar las causas más probables de «{plain}», distinguir señales útiles y decidir qué comprobar primero y cuándo pedir ayuda."
        if safety:
            return f"Tomar una decisión segura sobre «{plain}», reconocer riesgos y saber cuándo detenerse, evacuar o pedir ayuda profesional."
        return f"Resolver de forma práctica y segura «{plain}», siguiendo un orden claro y sabiendo cuándo conviene detenerse o cambiar de estrategia."
    if diagnostic:
        return f"Identify the most likely causes of “{plain},” use distinguishing clues, and decide what to check first and when to get help."
    if safety:
        return f"Make a safe decision about “{plain},” recognize important risks, and know when to stop, leave, or get professional help."
    return f"Handle “{plain}” with a practical, safe sequence and know when to stop or change approach."


def build_article(entry: dict, lang: str) -> dict:
    n = entry["n"]
    if lang == "es":
        title = entry["es_title"]
        intro = entry["intro_es"]
    else:
        title = entry["en_title"]
        intro = entry["intro_en"]
    es_slug = slugify(clean_title_for_slug(entry["es_title"]))
    en_slug = slugify(clean_title_for_slug(entry["en_title"]))
    slug = es_slug if lang == "es" else en_slug
    translation_group = f"{n}-{en_slug}"
    sections = entry["sections"]
    h_index = 0 if lang == "es" else 1
    p_index = 2 if lang == "es" else 3
    body = [f"<p>{html.escape(intro)}</p>"]
    for section in sections:
        body.append(f"<h2>{html.escape(section[h_index])}</h2><p>{html.escape(section[p_index])}</p>")
    faq_questions = entry["faq_es" if lang == "es" else "faq_en"]
    faq_sections = entry["faq_sections"]
    faq = []
    for question, section_index in zip(faq_questions, faq_sections):
        answer = sections[section_index][p_index]
        faq.append({"question": question, "answer": answer})
    family = entry.get("family", "home")
    kind = entry.get("kind", "guide")
    first_heading = sections[0][h_index]
    if lang == "es":
        market_context = "Español internacional; guía doméstica práctica, segura y comprensible para hogares de España y Latinoamérica."
        image_concept = f"Fotografía editorial doméstica realista sobre «{clean_title_for_slug(title)}», mostrando de forma clara {first_heading.lower()} como acción o pista principal; entorno cotidiano natural, sin texto ni marcas."
    else:
        market_context = "U.S./Canadian English; practical household guidance with locally familiar terminology and clear safety boundaries."
        image_concept = f"Realistic household editorial photograph about “{clean_title_for_slug(title)},” clearly showing {first_heading.lower()} as the main action or clue; natural home setting, no text or branding."
    return {
        "schema_version": 1,
        "id": f"{lang}-{n}-{slug}",
        "article_number": n,
        "translation_group": translation_group,
        "language": lang,
        "locale": "es-ES" if lang == "es" else "en-US",
        "market_context": market_context,
        "title": title,
        "slug": slug,
        "seo": {
            "title": title,
            "meta_description": first_sentence(intro),
            "search_intent": search_intent(kind, title, lang),
        },
        "excerpt": intro,
        "taxonomy": {
            "food_family": family,
            "food_subcategories": [slug],
            "article_types": [kind, family],
            "primary_article_type": kind,
        },
        "content_html": "".join(body),
        "faq": faq,
        "sources": source_entries(entry.get("source", ""), lang),
        "image": {"concept": image_concept, "alt": clean_title_for_slug(title)},
        "status": "publish",
    }


def load_entries():
    entries = []
    batch_files = sorted(TOOLS.glob("batch-*.json"))
    for path in batch_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            raise SystemExit(f"Could not parse {path}: {exc}")
        if not isinstance(data, list):
            continue
        for entry in data:
            if isinstance(entry, dict) and isinstance(entry.get("n"), int) and START <= entry["n"] <= END:
                entries.append(entry)
    nums = [e["n"] for e in entries]
    duplicates = sorted({n for n in nums if nums.count(n) > 1})
    blocked_present = sorted(set(nums) & set(BLOCKED))
    missing = sorted(EXPECTED_SOURCE_NUMBERS - set(nums))
    extra = sorted(set(nums) - EXPECTED_SOURCE_NUMBERS)
    if duplicates or blocked_present or missing or extra or len(entries) != len(EXPECTED_SOURCE_NUMBERS):
        raise SystemExit(
            f"Input inventory mismatch: duplicates={duplicates}, blocked_present={blocked_present}, "
            f"missing={missing}, extra={extra}, count={len(entries)}"
        )
    required = {"n", "es_title", "en_title", "family", "kind", "intro_es", "intro_en", "sections", "faq_es", "faq_en", "faq_sections"}
    for entry in entries:
        missing_keys = required - set(entry)
        if missing_keys:
            raise SystemExit(f"#{entry.get('n')} missing keys: {sorted(missing_keys)}")
        if len(entry["sections"]) != 4 or any(len(s) != 4 for s in entry["sections"]):
            raise SystemExit(f"#{entry['n']} must contain exactly four bilingual sections")
        if len(entry["faq_es"]) != 3 or len(entry["faq_en"]) != 3 or len(entry["faq_sections"]) != 3:
            raise SystemExit(f"#{entry['n']} must contain exactly three FAQs per language and three mappings")
        if len(set(entry["faq_sections"])) != 3 or any(i not in range(4) for i in entry["faq_sections"]):
            raise SystemExit(f"#{entry['n']} has invalid FAQ section mapping: {entry['faq_sections']}")
    return sorted(entries, key=lambda e: e["n"])


def range_json_files(directory: Path):
    found = []
    for path in directory.glob("*.json"):
        m = re.match(r"^(\d+)-", path.name)
        if m and START <= int(m.group(1)) <= END:
            found.append(path)
    return sorted(found)


def existing_identity_sets():
    slugs = {"es": set(), "en": set()}
    groups = set()
    for lang, directory in (("es", ES_DIR), ("en", EN_DIR)):
        for path in directory.glob("*.json"):
            m = re.match(r"^(\d+)-", path.name)
            if m and START <= int(m.group(1)) <= END:
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if data.get("slug"):
                slugs[lang].add(data["slug"])
            if data.get("translation_group"):
                groups.add(data["translation_group"])
    return slugs, groups


def generate(entries):
    existing_slugs, existing_groups = existing_identity_sets()
    for directory in (ES_DIR, EN_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        for old in range_json_files(directory):
            old.unlink()
    seen_slugs = {"es": set(), "en": set()}
    seen_groups = set()
    unknown_source_keys = set()
    for entry in entries:
        n = entry["n"]
        source_key = entry.get("source", "")
        if source_key and source_key not in SOURCE_MAP:
            unknown_source_keys.add(source_key)
        pair = {}
        for lang, directory in (("es", ES_DIR), ("en", EN_DIR)):
            article = build_article(entry, lang)
            slug = article["slug"]
            if slug in existing_slugs[lang]:
                raise SystemExit(f"#{n} {lang} slug duplicates an existing published article: {slug}")
            if slug in seen_slugs[lang]:
                raise SystemExit(f"Duplicate generated {lang} slug: {slug}")
            seen_slugs[lang].add(slug)
            group = article["translation_group"]
            if group in existing_groups:
                raise SystemExit(f"#{n} translation_group duplicates an existing published group: {group}")
            if group in seen_groups:
                raise SystemExit(f"Duplicate generated translation_group: {group}")
            seen_groups.add(group)
            pair[lang] = article
            out = directory / f"{n:03d}-{slug}.json"
            out.write_text(json.dumps(article, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        if pair["es"]["translation_group"] != pair["en"]["translation_group"]:
            raise SystemExit(f"#{n} translation group mismatch")
    return unknown_source_keys


def count_words_from_html(value: str) -> int:
    text = re.sub(r"<[^>]+>", " ", value)
    return len(re.findall(r"\b[\wÀ-ÿ'-]+\b", html.unescape(text), flags=re.UNICODE))


def check_acronyms(article: dict, errors: list):
    text = html.unescape(re.sub(r"<[^>]+>", " ", article["content_html"]))
    lang = article["language"]
    n = article["article_number"]
    if lang == "es":
        rules = {
            "EPA": ["Agencia de Protección Ambiental de EE. UU. (EPA)"],
            "CDC": ["Centros para el Control y la Prevención de Enfermedades de EE. UU. (CDC)"],
            "USDA": ["Departamento de Agricultura de EE. UU. (USDA)"],
            "CPSC": ["Comisión de Seguridad de Productos del Consumidor de EE. UU. (CPSC)"],
            "GFCI": ["falla a tierra (GFCI)"],
            "CO": ["monóxido de carbono (CO)"],
        }
    else:
        rules = {
            "EPA": ["Environmental Protection Agency (EPA)"],
            "CDC": ["Centers for Disease Control and Prevention (CDC)"],
            "USDA": ["Department of Agriculture (USDA)"],
            "CPSC": ["Consumer Product Safety Commission (CPSC)"],
            "GFCI": ["circuit interrupter (GFCI)"],
            "CO": ["carbon monoxide (CO)"],
        }
    for acronym, expansions in rules.items():
        if re.search(rf"\b{re.escape(acronym)}\b", text) and not any(exp in text for exp in expansions):
            errors.append(f"#{n} {lang}: unexplained acronym {acronym}")


def validate_files(entries):
    errors = []
    stats = {"es": [], "en": []}
    faq_checks = 0
    faq_expected = len(EXPECTED_PUBLISHED_NUMBERS) * 2 * 3
    by_n = {e["n"]: e for e in entries}
    files = {"es": range_json_files(ES_DIR), "en": range_json_files(EN_DIR)}
    for lang in ("es", "en"):
        nums = []
        if len(files[lang]) != len(EXPECTED_PUBLISHED_NUMBERS):
            errors.append(f"{lang}: expected {len(EXPECTED_PUBLISHED_NUMBERS)} files, found {len(files[lang])}")
        for path in files[lang]:
            try:
                article = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                errors.append(f"{path}: invalid JSON: {exc}")
                continue
            n = article.get("article_number")
            nums.append(n)
            if n not in EXPECTED_PUBLISHED_NUMBERS:
                errors.append(f"{path}: unexpected article_number {n}")
                continue
            expected = by_n[n]
            expected_title = expected["es_title" if lang == "es" else "en_title"]
            if article.get("title") != expected_title:
                errors.append(f"#{n} {lang}: title drift")
            expected_slug = slugify(clean_title_for_slug(expected_title))
            expected_group = f"{n}-{slugify(clean_title_for_slug(expected['en_title']))}"
            if article.get("slug") != expected_slug or path.name != f"{n:03d}-{expected_slug}.json":
                errors.append(f"#{n} {lang}: slug/filename mismatch")
            if article.get("translation_group") != expected_group:
                errors.append(f"#{n} {lang}: translation_group mismatch")
            if article.get("language") != lang:
                errors.append(f"#{n} {lang}: language mismatch")
            if article.get("locale") != ("es-ES" if lang == "es" else "en-US"):
                errors.append(f"#{n} {lang}: locale mismatch")
            if article.get("status") != "publish" or article.get("schema_version") != 1:
                errors.append(f"#{n} {lang}: publish/schema mismatch")
            seo = article.get("seo", {})
            if seo.get("title") != expected_title or not seo.get("meta_description") or not seo.get("search_intent"):
                errors.append(f"#{n} {lang}: incomplete SEO")
            if "…" in seo.get("title", "") or seo.get("title", "").endswith("..."):
                errors.append(f"#{n} {lang}: truncated SEO title")
            body = article.get("content_html", "")
            if body.count("<h2>") != 4:
                errors.append(f"#{n} {lang}: expected exactly four H2 sections")
            wc = count_words_from_html(body)
            stats[lang].append(wc)
            if wc < 160:
                errors.append(f"#{n} {lang}: body too thin for this batch ({wc} words)")
            faq = article.get("faq", [])
            if len(faq) != 3:
                errors.append(f"#{n} {lang}: expected exactly three FAQs")
            else:
                p_index = 2 if lang == "es" else 3
                questions = expected["faq_es" if lang == "es" else "faq_en"]
                for i, item in enumerate(faq):
                    expected_section = expected["faq_sections"][i]
                    expected_answer = expected["sections"][expected_section][p_index]
                    if item.get("question") != questions[i]:
                        errors.append(f"#{n} {lang} FAQ {i+1}: question drift")
                    if item.get("answer") != expected_answer:
                        errors.append(f"#{n} {lang} FAQ {i+1}: answer does not match mapped editorial section")
                    else:
                        faq_checks += 1
            lowered = html.unescape(body).lower()
            forbidden = ["home prioriza", "home recomienda", "en este artículo hemos decidido", "home prioritizes", "home recommends", "in this article we decided"]
            for phrase in forbidden:
                if phrase in lowered:
                    errors.append(f"#{n} {lang}: editorial metadiscourse '{phrase}'")
            check_acronyms(article, errors)
            image = article.get("image", {})
            if not image.get("concept") or not image.get("alt"):
                errors.append(f"#{n} {lang}: incomplete image metadata")
        if set(nums) != EXPECTED_PUBLISHED_NUMBERS:
            errors.append(f"{lang}: published number set mismatch; missing={sorted(EXPECTED_PUBLISHED_NUMBERS-set(nums))}, extra={sorted(set(nums)-EXPECTED_PUBLISHED_NUMBERS)}")
    if faq_checks != faq_expected:
        errors.append(f"FAQ mapping checks: expected {faq_expected}, passed {faq_checks}")
    for n in BLOCKED:
        for lang, directory in (("es", ES_DIR), ("en", EN_DIR)):
            if list(directory.glob(f"{n:03d}-*.json")):
                errors.append(f"#{n} {lang}: blocked duplicate was generated")
    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    return stats, faq_checks


def make_report(entries, stats, faq_checks, unknown_source_keys):
    source_entries_count = sum(1 for e in entries if e.get("source") in SOURCE_MAP and e.get("source"))
    no_source_count = len(EXPECTED_PUBLISHED_NUMBERS) - source_entries_count
    groups = [(551, 570), (571, 590), (591, 610), (611, 630)]
    lines = [
        "# Quality audit — HOME articles 551–630",
        "",
        "## Result",
        "",
        "- Canonical topic intents reviewed: **80/80**.",
        "- Editorial source entries validated: **79/79**; #616 is an intentional canonical exclusion.",
        "- Published unique intents: **79**; bilingual article JSON files: **158/158 PASS**.",
        f"- FAQ answer-to-section mappings: **{faq_checks}/{len(EXPECTED_PUBLISHED_NUMBERS)*2*3} PASS**.",
        "- Explicit canonical exclusion: **#616 is not published** because it duplicates #537; #537 remains the single URL for that intent.",
        "- Schema, language/locale, IDs, slugs, translation groups, SEO fields, status, four H2 sections, three FAQs, image metadata, acronym rules, metadiscourse checks and minimum batch depth all pass.",
        "",
        "## Depth metrics",
        "",
        f"- Spanish body words: min **{min(stats['es'])}**, median **{int(statistics.median(stats['es']))}**, max **{max(stats['es'])}**.",
        f"- English body words: min **{min(stats['en'])}**, median **{int(statistics.median(stats['en']))}**, max **{max(stats['en'])}**.",
        "- The editorial standard has no fixed word-count target; the 160-word floor here is an additional batch guard against accidentally thin generated output.",
        "",
        "## Inventory by range",
        "",
        "| Range | Canonical topics | Published intents | ES | EN |",
        "|---|---:|---:|---:|---:|",
    ]
    for a, b in groups:
        canonical = b-a+1
        published = len([n for n in EXPECTED_PUBLISHED_NUMBERS if a <= n <= b])
        lines.append(f"| {a}–{b} | {canonical} | {published} | {published} | {published} |")
    lines += [
        "",
        "## Cannibalization decisions",
        "",
        "- **#555 vs #353:** keep both. #353 is the general wall-crack repair page; #555 is specialized by substrate and distinguishes drywall joint/tape repair from traditional plaster adhesion failures.",
        "- **#591 vs #298:** keep both. #591 diagnoses why a garbage disposal repeatedly jams; #298 is the hands-on unjamming procedure.",
        "- **#616 vs #537:** block #616. Both resolve the same water-hammer / pipe-banging-when-water-stops intent, so #537 remains canonical.",
        "",
        "## Sources",
        "",
        f"- Topic pairs whose source key resolved to a structured reference: **{source_entries_count}**.",
        f"- Topic pairs intentionally published without a structured source because the editorial source field was blank or unmapped: **{no_source_count}**.",
    ]
    if unknown_source_keys:
        lines.append(f"- Unmapped non-empty source keys observed: **{', '.join(sorted(unknown_source_keys))}**. These articles retain an empty `sources` array rather than inventing a citation.")
    else:
        lines.append("- No unmapped non-empty source keys were observed.")
    lines += [
        "",
        "## Final editorial safeguards",
        "",
        "- Spanish and English are generated from separately authored bilingual source paragraphs, not literal machine translation.",
        "- FAQ answers are copied only from their explicitly mapped editorial sections and validated one by one.",
        "- Safety boundaries remain in the authored source copy: no live electrical testing, refrigerant handling, hazardous chemical mixing, unsafe structural access, wildlife handling, or bypassing safety devices.",
        "- Exact slug and translation-group collisions with already published articles are rejected before generation.",
        "- Temporary generator, batch files and workflow must be removed before merge to `main`.",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    entries = load_entries()
    unknown = set()
    if not args.validate_only:
        unknown = generate(entries)
    stats, faq_checks = validate_files(entries)
    if not args.validate_only:
        make_report(entries, stats, faq_checks, unknown)
    print(f"PASS: 80 canonical intents reviewed; 79 source entries validated; 79 unique intents published; 158 article JSON files; {faq_checks}/474 FAQ mappings valid.")
    print(f"ES words min/median/max: {min(stats['es'])}/{int(statistics.median(stats['es']))}/{max(stats['es'])}")
    print(f"EN words min/median/max: {min(stats['en'])}/{int(statistics.median(stats['en']))}/{max(stats['en'])}")
    if unknown:
        print("UNMAPPED SOURCE KEYS:", ", ".join(sorted(unknown)))


if __name__ == "__main__":
    main()
