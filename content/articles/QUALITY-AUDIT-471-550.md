# HOME — Quality audit 471–550

## Result

- Canonical topic numbers reviewed: **80 / 80**.
- Unique publishable intents: **77 / 80**.
- JSON checked: **154 / 154** (77 ES + 77 EN).
- Structural/editorial validation: **PASS**.
- Explicit FAQ validation: **PASS 462 / 462**.
- Hand-reviewed FAQ answer-section alignment: **PASS 462 / 462**.
- Final metadata/localization regression validation: **PASS**.
- Blocking errors: **0**.
- Non-blocking warnings: **0**.
- Dedicated final audit run before cleanup: **34243990615**.

## Canonical duplicate exceptions

- **#477 → #402**: exact duplicate title and search intent (`Cómo limpiar el filtro de la campana extractora`). Publishing #477 with the same slug would cause the importer to overwrite #402; publishing a different slug would create SEO cannibalization. No #477 JSON is emitted.
- **#480 → #472**: semantically identical slow-shower-drain query with word order changed. #472 is the single published URL; no #480 JSON is emitted.
- **#499 → #263**: `¿Por qué las toallas huelen mal después de lavarlas?` repeats the already-published diagnosis `¿Por qué las toallas huelen mal incluso después de lavarlas?`. #263 remains the single diagnostic URL; no #499 JSON is emitted.

These numbers remain documented in the canonical inventory and in this audit; they are not silently renumbered or replaced.

## Scope and editorial criteria

- Spanish and English share article number and translation group while using independently localized prose.
- FAQ questions are explicit editorial inputs and each answer is grounded in the article body.
- Every one of the **462 FAQ** was reviewed against the exact article section supplying its answer. Manual review caught and corrected real mismatches in #484, #489, #498, #500, #512, #514, #515, #520, #531 and #542 before release.
- Electrical, gas, appliance, food, wildlife and water-quality pages include concrete stop conditions and escalation boundaries.
- Search-intent metadata is checked for natural ES/EN syntax, including regressions such as `Identify why are…`, `Decide whether can…` and `para cómo…`.
- Close topics are separated by reader decision and next action rather than superficial wording.

## Quantitative profile

| Range | ES words | ES H2 | ES FAQ | ES sources | EN words | EN H2 | EN FAQ | EN sources |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 471–490 | 219.5 | 4.0 | 3.0 | 1.0 | 211.4 | 4.0 | 3.0 | 1.0 |
| 491–510 | 209.5 | 4.0 | 3.0 | 0.8 | 198.4 | 4.0 | 3.0 | 0.8 |
| 511–530 | 208.9 | 4.0 | 3.0 | 1.0 | 201.2 | 4.0 | 3.0 | 1.0 |
| 531–550 | 200.1 | 4.0 | 3.0 | 0.9 | 195.6 | 4.0 | 3.0 | 0.9 |

## Cannibalization distinctions

- #471 vs #470: bad taste is a quality/source diagnosis; slow flow remains a restriction/pressure diagnosis.
- #472/#480: one published slow-shower-drain page only; #480 is blocked as duplicate.
- #475 vs #411: liner-specific material care vs cleaning the full shower curtain.
- #479 vs #235/#398: bathroom-sink slow-drain diagnosis vs unclogging procedure/general sink diagnosis.
- #491 vs #436: why paint peels vs how to repair peeling paint.
- #498 vs #262/#263: prevention of musty towel odor vs removing existing odor/diagnosing why it persists.
- #499 vs #263: one diagnostic page only; #499 is blocked as duplicate.
- #505/#506: repotting procedure vs decision about when repotting is needed.
- #510/#511: whether vents should be open vs whether closing them saves energy.
- #513/#514/#515: general smoke residue vs cigarette residue vs cooking odor.
- #516 vs #306/#388: dead outlet with breaker apparently normal vs one-room outage vs GFCI reset procedure.
- #517 vs #287/#579: battery replacement interval vs chirping diagnosis vs whole-alarm replacement interval.
- #520 vs prior freezer-outage guidance: frost diagnosis does not duplicate food-safety outage decisions.
- #521/#522: oven no-start vs individual gas-burner ignition diagnosis.
- #523 vs #462: coffee-maker leaking vs not brewing.
- #526/#527/#528: separate refreezing decisions for poultry, fish and ice cream because thaw method and food characteristics differ.
- #529/#530: bulbs burning out vs LED flicker.
- #534/#535: what boiling does to hardness vs whether a whole-home softener is warranted.
- #544/#545/#546: brown sediment/rust vs yellow iron/organics vs white microbubbles.

## Manual review priorities

Both languages were reviewed for water-quality, wildlife/pests, smoke/odor, electrical/gas, food-safety, heating/cooling and appliance topics. Reject any page that encourages live electrical work, repeated breaker resets, unsafe gas troubleshooting, tasting questionable food, opening refrigerant circuits, sealing active wildlife nests, or treating unknown water contamination by appearance alone.

## Warnings

- None.
