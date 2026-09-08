# Quality audit — HOME articles 631–710

## Result

- Canonical topic intents reviewed: **80/80**.
- Editorial source entries validated: **78/78**; #635 and #659 are intentional canonical exclusions.
- Published unique intents: **78**; bilingual article JSON files: **156/156 PASS**.
- FAQ answer-to-section mappings: **468/468 PASS**.
- Explicit exclusions: **#635 → #561** and **#659 → #260** to preserve one canonical URL per search intent.
- Schema, language/locale, IDs, slugs, translation groups, SEO fields, status, four H2 sections, three FAQs, image metadata, acronym rules, metadiscourse checks, safety anti-patterns and batch depth all pass.
- Meta descriptions are validated as complete editorial sentences; character truncation is not permitted.
- Final reproducible validation run: **34262301742 — PASS**, including the independent second validation and final language-regression checks.
- Blocking errors: **0**. Final warnings: **0**.

## Depth metrics

- Spanish body words: min **191**, median **215**, max **247**.
- English body words: min **183**, median **207**, max **233**.
- The editorial standard has no fixed word-count target; the 160-word floor is only a guard against accidentally incomplete output.

## Inventory by range

| Range | Canonical topics | Published intents | ES | EN |
|---|---:|---:|---:|---:|
| 631–650 | 20 | 19 | 19 | 19 |
| 651–670 | 20 | 19 | 19 | 19 |
| 671–690 | 20 | 20 | 20 | 20 |
| 691–710 | 20 | 20 | 20 | 20 |

## Cannibalization decisions

- **#635 vs #561:** block #635. #561 already resolves preventing color loss during washing, including temperature, friction, separation and drying heat.
- **#659 vs #260:** block #659. #260 already resolves detergent dosage by concentration, load, water hardness and washer type.
- **#631 vs #706:** keep both. #631 covers towels mixed with clothing generally; #706 focuses specifically on sheets plus towels and their bulk/drying interaction.
- **#636 vs #637:** keep both. #636 prevents pilling; #637 removes pills already present.
- **#652 vs #578:** keep both. #652 is the direct fuel-gas safety response; #578 distinguishes rotten-egg odor among fuel gas, drains and hot water sulfur.
- **#684 vs #604:** keep both. #684 diagnoses continued dripping after shutoff and points toward the valve; #604 repairs a leaking showerhead/connection.
- **#690 vs #691:** keep both. #690 is the shutoff procedure; #691 is the location guide.

### Similarity diagnostics (maximum ES/EN token Jaccard)

- #631 vs #706: **0.253**
- #636 vs #637: **0.088**
- #638 vs #640: **0.207**
- #643 vs #644: **0.133**
- #649 vs #574: **0.316**
- #650 vs #279: **0.184**
- #651 vs #276: **0.185**
- #652 vs #578: **0.286**
- #656 vs #675: **0.232**
- #674 vs #286: **0.302**
- #673 vs #291: **0.311**
- #676 vs #677: **0.164**
- #677 vs #678: **0.156**
- #681 vs #621: **0.218**
- #682 vs #245: **0.242**
- #682 vs #246: **0.290**
- #684 vs #604: **0.200**
- #690 vs #691: **0.200**
- #694 vs #695: **0.112**
- #697 vs #698: **0.146**
- #699 vs #251: **0.190**
- #701 vs #554: **0.254**
- #710 vs #260: **0.241**

## Sources

- Topic pairs with a directly relevant structured reference: **59**.
- Topic pairs intentionally published without a structured source because no directly supporting source was mapped: **19**.
- No non-empty source key is silently treated as authoritative when it lacks a mapping.

## Manual cold-read review

- Reviewed high-risk and overlap-sensitive samples in both the generated output and their FAQ mappings, including **#631/#706, #649, #652, #656/#675, #667/#674, #684, #699/#700, #705 and #710**.
- #652 keeps the fuel-gas response first: evacuate, avoid switches/flames/phones indoors, contact the gas utility or emergency service from outside, and do not re-enter until cleared.
- #667 distinguishes brief orange flicker from persistent poor-combustion signs and does not encourage gas-system adjustment.
- #674 requires direct wall-outlet connection for a portable space heater and preserves clearance/overheating boundaries.
- #699 follows wet/disinfect-first rodent-dropping cleanup rather than dry sweeping or vacuuming.
- #700 distinguishes drywood-termite pellets from other debris without encouraging destructive probing of structural wood.
- Spanish question-title metadata was normalized so `search_intent` and image concepts do not retain an unmatched opening `¿`.
- Final language regressions block residual `HVAC`, `pellets`, incomplete Spanish question quoting and the specific awkward phrases found during cold reading.

## Final editorial safeguards

- Spanish and English use separately authored bilingual source paragraphs rather than literal machine translation.
- FAQ answers are copied only from their explicitly mapped editorial sections and validated one by one.
- Safety boundaries include no live electrical testing, gas-system adjustment, bypassing safety devices, unsafe spring/cable work, hazardous chemical mixing, or unsafe structural access.
- Pest articles prioritize exclusion, sanitation, moisture control and professional escalation over indiscriminate chemical treatment.
- Exact slug, ID and translation-group collisions with already published articles are rejected.
- Temporary generator, all eight batch files and the temporary workflow were removed before PR review.
