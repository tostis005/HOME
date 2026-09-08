# Quality audit — HOME articles 551–630

## Result

- Canonical topic intents reviewed: **80/80**.
- Editorial source entries validated: **79/79**; #616 is an intentional canonical exclusion.
- Published unique intents: **79**; bilingual article JSON files: **158/158 PASS**.
- FAQ answer-to-section mappings: **474/474 PASS**.
- Explicit canonical exclusion: **#616 is not published** because it duplicates #537; #537 remains the single URL for that intent.
- Schema, language/locale, IDs, slugs, translation groups, SEO fields, status, four H2 sections, three FAQs, image metadata, acronym rules, metadiscourse checks and minimum batch depth all pass.

## Depth metrics

- Spanish body words: min **193**, median **217**, max **252**.
- English body words: min **182**, median **210**, max **245**.
- The editorial standard has no fixed word-count target; the 160-word floor here is an additional batch guard against accidentally thin generated output.

## Inventory by range

| Range | Canonical topics | Published intents | ES | EN |
|---|---:|---:|---:|---:|
| 551–570 | 20 | 20 | 20 | 20 |
| 571–590 | 20 | 20 | 20 | 20 |
| 591–610 | 20 | 20 | 20 | 20 |
| 611–630 | 20 | 19 | 19 | 19 |

## Cannibalization decisions

- **#555 vs #353:** keep both. #353 is the general wall-crack repair page; #555 is specialized by substrate and distinguishes drywall joint/tape repair from traditional plaster adhesion failures.
- **#591 vs #298:** keep both. #591 diagnoses why a garbage disposal repeatedly jams; #298 is the hands-on unjamming procedure.
- **#616 vs #537:** block #616. Both resolve the same water-hammer / pipe-banging-when-water-stops intent, so #537 remains canonical.

## Sources

- Topic pairs whose source key resolved to a structured reference: **67**.
- Topic pairs intentionally published without a structured source because the editorial source field was blank or unmapped: **12**.
- Unmapped non-empty source keys observed: **gas, water_softener**. These articles retain an empty `sources` array rather than inventing a citation.

## Final editorial safeguards

- Spanish and English are generated from separately authored bilingual source paragraphs, not literal machine translation.
- FAQ answers are copied only from their explicitly mapped editorial sections and validated one by one.
- Safety boundaries remain in the authored source copy: no live electrical testing, refrigerant handling, hazardous chemical mixing, unsafe structural access, wildlife handling, or bypassing safety devices.
- Exact slug and translation-group collisions with already published articles are rejected before generation.
- Temporary generator, batch files and workflow must be removed before merge to `main`.
