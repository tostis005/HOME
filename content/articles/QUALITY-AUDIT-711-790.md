# Quality audit — HOME articles 711–790

## Result

- Canonical topic intents reviewed: **80/80**.
- Editorial source entries validated: **71/71**; **9** canonical exclusions.
- Published unique intents: **71**; bilingual article JSON files: **142/142 PASS**.
- FAQ answer-to-section mappings: **426/426 PASS**.
- Blocking errors: **0**. Warnings: **0**.

## Validation evidence

- Full generation + editorial validation: GitHub Actions run **34269702965** — PASS with `entries=71 articles=142 faq=426 errors=0 warnings=0`.
- Manual review covered safety-sensitive HVAC/gas/electrical/wet-area, microwave/food-storage, pest and household-chemical articles plus first/last samples and watched overlap pairs.
- Manual FAQ review found one semantic weakness in **#737**: the refrigerator-temperature FAQ originally described using a thermometer without stating the requested temperature. ES and EN were corrected to state **4 °C or less / 40°F (4°C) or below** directly.
- Independent read-only final audit: GitHub Actions run **34270217989** — PASS with `entries=71 articles=142 faq=426 errors=0 warnings=0`.
- The independent inventory check also confirmed exactly **71 intents / 142 articles**, all nine exclusions absent, ES/EN translation groups paired, `status: publish`, and the #737 semantic FAQ fix present in both languages.

## Canonical exclusions

- **#726 → #277:** Exact duplicate: finding the source of a bad smell in the home is already #277.
- **#733 → #664:** Same intent: an ice maker not working/not making ice is already fully covered by #664.
- **#735 → #453:** Same intent: storing fresh herbs so they last longer is already #453.
- **#736 → #568:** Same intent: organizing the refrigerator for food safety is already #568.
- **#739 → #517:** Same intent: smoke-alarm battery replacement frequency is already #517.
- **#749 → #481:** Same intent: cloudy tap water diagnosis is already #481.
- **#771 → #552:** Same intent: organizing clothing in a small closet is already #552.
- **#772 → #642:** Same intent: storing clothes without musty odor is already #642.
- **#788 → #718:** Same intent inside this block: what to do about mealybugs is fully resolved by #718.

## Depth metrics

- Spanish body words: min **205**, median **240**, max **266**.
- English body words: min **198**, median **229**, max **265**.
- The 160-word floor is only an incomplete-output regression guard, not an editorial target.

## Similarity diagnostics

- #711 vs #260: maximum ES/EN token Jaccard **0.159**.
- #712 vs #713: maximum ES/EN token Jaccard **0.187**.
- #716 vs #439: maximum ES/EN token Jaccard **0.161**.
- #717 vs #718: maximum ES/EN token Jaccard **0.203**.
- #719 vs #790: maximum ES/EN token Jaccard **0.176**.
- #722 vs #137: maximum ES/EN token Jaccard **0.184**.
- #724 vs #278: maximum ES/EN token Jaccard **0.182**.
- #728 vs #130: maximum ES/EN token Jaccard **0.180**.
- #728 vs #445: maximum ES/EN token Jaccard **0.137**.
- #737 vs #568: maximum ES/EN token Jaccard **0.206**.
- #738 vs #656: maximum ES/EN token Jaccard **0.370**.
- #738 vs #674: maximum ES/EN token Jaccard **0.335**.
- #738 vs #675: maximum ES/EN token Jaccard **0.207**.
- #742 vs #679: maximum ES/EN token Jaccard **0.234**.
- #746 vs #680: maximum ES/EN token Jaccard **0.180**.
- #747 vs #682: maximum ES/EN token Jaccard **0.258**.
- #748 vs #233: maximum ES/EN token Jaccard **0.185**.
- #757 vs #758: maximum ES/EN token Jaccard **0.163**.
- #758 vs #759: maximum ES/EN token Jaccard **0.140**.
- #759 vs #760: maximum ES/EN token Jaccard **0.104**.
- #761 vs #762: maximum ES/EN token Jaccard **0.160**.
- #761 vs #763: maximum ES/EN token Jaccard **0.186**.
- #762 vs #763: maximum ES/EN token Jaccard **0.112**.
- #767 vs #420: maximum ES/EN token Jaccard **0.135**.
- #774 vs #787: maximum ES/EN token Jaccard **0.210**.
- #778 vs #703: maximum ES/EN token Jaccard **0.167**.
- #778 vs #779: maximum ES/EN token Jaccard **0.149**.
- #779 vs #703: maximum ES/EN token Jaccard **0.216**.
- #781 vs #782: maximum ES/EN token Jaccard **0.168**.
- #782 vs #783: maximum ES/EN token Jaccard **0.186**.
- #783 vs #784: maximum ES/EN token Jaccard **0.063**.
- #785 vs #714: maximum ES/EN token Jaccard **0.133**.
- #789 vs #718: maximum ES/EN token Jaccard **0.276**.

## Editorial and safety safeguards

- Spanish and English are independently authored in the temporary editorial source rows; they share intent and structure but are not literal translations.
- Every article has four useful H2 sections and three reader-style FAQs whose answers are validated against explicitly mapped source sections.
- Meta descriptions must be complete first editorial sentences; character truncation is rejected.
- Gas, electrical, water, garage-door, microwave and structural content keeps clear stop points and avoids live testing, bypasses, unsafe spring/cable work or opening fuel-burning equipment.
- Pest and plant-pest pages prioritize identification, isolation, exclusion, sanitation, physical control and labeled lower-risk options before escalation.
- Exact slug, ID and translation-group collisions against the existing library are rejected.
- Temporary batch files, generator and workflow are excluded from the final PR and merge to `main`.
